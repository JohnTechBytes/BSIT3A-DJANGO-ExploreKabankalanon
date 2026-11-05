"""Fetch a read-only, boundary-scoped OSM candidate report for staff review.

Never inserts, updates or deletes database rows. OSM is incomplete and a
mapping is not proof that a place exists, is open, or is correctly located.
"""
import csv
from datetime import datetime, timezone
import json
import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from apps.cities.models import City
from apps.places.models import Place
from apps.places.management.commands.discover_kabankalan_businesses import (
    ATTRIBUTION, CITY_ID, OVERPASS_ENDPOINTS, address_label,
    discover_boundary_nominatim, normalized,
)

# Separate bounded OSM-area requests keep queries small. Categories overlap:
# a café that is also tagged as a shop may appear in both sections.
FILTERS = {
    'malls': ('["shop"~"^(mall|department_store)$"]["name"]',),
    'waterfalls': ('["natural"="waterfall"]["name"]', '["waterway"="waterfall"]["name"]'),
    'food_cafes': (
        '["amenity"~"^(restaurant|cafe|fast_food|food_court|ice_cream|bar|pub)$"]["name"]',
        '["shop"~"^(bakery|coffee|confectionery|pastry)$"]["name"]',
    ),
    'shops_services': (
        '["shop"]["name"]',
        '["amenity"~"^(bank|pharmacy|clinic|dentist|doctors|hospital|fuel|car_wash|marketplace|atm|veterinary|post_office|police|fire_station|townhall|courthouse|social_facility|community_centre|library|bureau_de_change|charging_station|internet_cafe|taxi|bus_station)$"]["name"]',
        '["office"]["name"]',
        '["craft"]["name"]',
        '["leisure"~"^(sports_centre|bowling_alley|fitness_centre)$"]["name"]',
    ),
}
COLUMNS = ('name', 'categories', 'osm_type', 'osm_id', 'osm_url', 'latitude', 'longitude',
           'osm_address', 'osm_tags', 'review_status', 'possible_existing_ids', 'review_notes',
           'fetched_at_utc', 'boundary_relation_id', 'source_attribution')
MAX_ITEMS = 6000
SCHOOL_WORDS = re.compile(r'\b(high\s*school|school|college|university|academy|seminary|institute)\b', re.I)


def safe_cell(value):
    """Prevent spreadsheet formula execution when opening untrusted OSM text."""
    text = str(value or '').replace('\r', ' ').replace('\n', ' ')
    if text.lstrip().startswith(('=', '+', '-', '@')) or text.startswith(('\t', '\r')):
        return "'" + text
    return text


def overpass_request(query, endpoint):
    request = Request(endpoint, data=urlencode({'data': query}).encode(), headers={
        'User-Agent': 'ExploreKabankalan-DirectoryReview/1.0 (https://github.com/JohnTechBytes/BSIT3A-DJANGO-ExploreKabankalanon)',
        'Accept': 'application/json',
    })
    try:
        with urlopen(request, timeout=115) as response:
            body = json.load(response)
    except HTTPError as exc:
        raise CommandError(f'Overpass HTTP {exc.code}. No report or database changes; do not repeatedly retry.') from exc
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise CommandError(f'Overpass request failed: {exc}. No report or database changes.') from exc
    if not isinstance(body, dict) or not isinstance(body.get('elements'), list) or body.get('remark'):
        raise CommandError('Overpass returned an incomplete or invalid response. No report or database changes.')
    return body['elements']


def fetch_candidates(relation_id, endpoint):
    if not isinstance(relation_id, int) or relation_id < 1:
        raise CommandError('Invalid Kabankalan boundary relation.')
    area = overpass_request(f'[out:json][timeout:25];relation({relation_id});map_to_area->.kab;.kab out ids;', endpoint)
    if not any(row.get('type') == 'area' and row.get('id') == 3600000000 + relation_id for row in area if isinstance(row, dict)):
        raise CommandError('OSM has no matching Kabankalan area. No report or database changes.')
    combined = {}
    for key, filters in FILTERS.items():
        time.sleep(2)  # Do not repeatedly retry or flood a public Overpass instance.
        expression = ' '.join(f'nwr(area.kab){item};' for item in filters)
        query = f'[out:json][timeout:75];relation({relation_id});map_to_area->.kab;({expression});out center tags;'
        for item in overpass_request(query, endpoint):
            if not isinstance(item, dict):
                raise CommandError('Unexpected Overpass item. No report or database changes.')
            kind, ident = item.get('type'), item.get('id')
            if kind not in ('node', 'way', 'relation') or isinstance(ident, bool) or not isinstance(ident, int) or ident < 1:
                continue
            entry = combined.setdefault((kind, ident), {'item': item, 'categories': set()})
            entry['categories'].add(key)
            if len(combined) > MAX_ITEMS:
                raise CommandError('Unexpectedly large response; refusing to write a partial report.')
    return combined


def make_rows(combined, existing):
    by_slug = defaultdict(list)
    by_name = defaultdict(list)
    for place in existing:
        if place['slug']:
            by_slug[place['slug']].append(place)
        if normalized(place['title']):
            by_name[normalized(place['title'])].append(place)
    rows, excluded = [], 0
    for (kind, ident), entry in combined.items():
        item = entry['item']
        tags = item.get('tags') or {}
        if not isinstance(tags, dict):
            continue
        name = str(tags.get('name') or '').strip()
        if not name or len(name) > 255:
            continue
        # An explicit education amenity is outside the agreed scope. Ambiguous
        # names (e.g. 'School Supplies') stay in the report for manual review.
        if tags.get('amenity') in ('school', 'college', 'university', 'kindergarten'):
            excluded += 1
            continue
        needs_scope_review = bool(SCHOOL_WORDS.search(name))
        center = item.get('center') or item
        try:
            lat, lon = float(center['lat']), float(center['lon'])
            if not math.isfinite(lat) or not math.isfinite(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                continue
        except (TypeError, ValueError, KeyError):
            continue
        slug = f'osm-{kind}-{ident}'
        exact_osm = by_slug.get(slug, [])
        same_name = by_name.get(normalized(name), [])
        matched = list({p['id']: p for p in exact_osm + same_name}.values())
        status = 'existing_osm_id' if exact_osm else 'possible_duplicate_name' if same_name else 'candidate_needs_review'
        flags = []
        if needs_scope_review:
            status = 'school_scope_review'
            flags.append('Education-like name: verify scope; do not import an educational institution')
        if any(place['id'] not in {p['id'] for p in exact_osm} for place in same_name):
            flags.append('Same name exists; compare location and branch before treating as new')
        if any(k.startswith(('disused:', 'abandoned:', 'demolished:', 'closed:')) for k in tags) or tags.get('disused') == 'yes':
            flags.append('May be closed or disused')
        if not flags:
            flags.append('Confirm identity, location, current operation, relevance and photo rights')
        label_tags = json.dumps(tags, ensure_ascii=False, sort_keys=True)
        rows.append({
            'name': name, 'categories': ', '.join(sorted(entry['categories'])),
            'osm_type': kind, 'osm_id': ident, 'osm_url': f'https://www.openstreetmap.org/{kind}/{ident}',
            'latitude': f'{lat:.6f}', 'longitude': f'{lon:.6f}', 'osm_address': address_label(tags),
            'osm_tags': label_tags, 'review_status': status,
            'possible_existing_ids': ', '.join(str(p['id']) for p in matched), 'review_notes': '; '.join(flags),
            'fetched_at_utc': '', 'boundary_relation_id': '', 'source_attribution': ATTRIBUTION,
        })
    names = Counter(normalized(row['name']) for row in rows)
    for row in rows:
        if names[normalized(row['name'])] > 1:
            row['review_notes'] += '; same name appears in the OSM candidates—compare before adding'
    rows.sort(key=lambda row: (row['review_status'], normalized(row['name']), row['osm_id']))
    return rows, excluded


class Command(BaseCommand):
    help = 'Fetch a read-only OSM review CSV for malls, waterfalls, food/cafes and shops/services; never write to the database.'

    def add_arguments(self, parser):
        parser.add_argument('--output', required=True, help='New CSV file to create; existing files are never overwritten.')
        parser.add_argument('--overpass-endpoint', choices=OVERPASS_ENDPOINTS, default=OVERPASS_ENDPOINTS[0])

    def handle(self, *args, **options):
        city = City.objects.filter(pk=CITY_ID, name__iexact='Kabankalan', province__iexact='Negros Occidental').first()
        if not city:
            raise CommandError('Expected Kabankalan city ID 2. No report or database changes.')
        output = Path(options['output']).expanduser().resolve()
        if output.exists():
            raise CommandError('Output file already exists; choose a new filename. No database changes.')
        try:
            relation_id, name, _ = discover_boundary_nominatim()
        except CommandError as exc:
            message = str(exc).replace(
                'Try a different network later or provide a manually verified --relation-id.',
                'Try again later from a network that can reach Nominatim.',
            )
            raise CommandError(message) from exc
        self.stdout.write(f'Confirmed OSM administrative relation {relation_id}: {name}.')
        combined = fetch_candidates(relation_id, options['overpass_endpoint'])
        existing = list(Place.objects.filter(city=city).values('id', 'title', 'slug'))
        rows, excluded = make_rows(combined, existing)
        fetched_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
        for row in rows:
            row['fetched_at_utc'] = fetched_at
            row['boundary_relation_id'] = relation_id
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with output.open('x', encoding='utf-8-sig', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=COLUMNS)
                writer.writeheader()
                for row in rows:
                    writer.writerow({key: safe_cell(row[key]) for key in COLUMNS})
        except FileExistsError as exc:
            raise CommandError('Output file already exists. No database changes.') from exc
        counts = Counter(row['review_status'] for row in rows)
        self.stdout.write(f'Saved {len(rows)} OSM candidate(s) to {output}. Status counts: {dict(counts)}. Explicit education amenities excluded: {excluded}.')
        self.stdout.write(f'Fetched at {fetched_at}; boundary relation {relation_id}. {ATTRIBUTION}')
        self.stdout.write('REVIEW ONLY: no database changes. OSM is incomplete; no result is independently verified. Matching names may be different branches. Inspect every candidate before any future draft import.')
