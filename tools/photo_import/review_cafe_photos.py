#!/usr/bin/env python3
"""Download candidate cafe photos for review only. Never imports or edits places.

Run with the project's Python from the Windows project folder. The output is a
new folder under the user's home directory, separate from project media. Image
identity, branch and rights require review; existing covers are never replaced.
"""
import csv
from datetime import datetime
import hashlib
import html
import io
import os
from pathlib import Path
import sys
import urllib.request
import warnings
import webbrowser

# Photo URLs are research leads, not verification or licenses. A listing may
# contain a photo of a different branch, a menu, people, or an old interior.
CAFES = (
    (7622, 'Calle Ramos', '', 'https://restaurantguru.com/Calle-Ramos-Snacks-and-Beyond-Kabankalan', 'Food-only lead; not a place photo.'),
    (7623, 'Coffee & Talk', 'https://img02.restaurantguru.com/c5ac-Restaurant-Coffee-and-Talk-interior.jpg', 'https://restaurantguru.com/Coffee-and-Talk-Kabankalan', 'Interior; check venue and branch.'),
    (7624, 'Cofioca', 'https://img02.restaurantguru.com/caca-Restaurant-Cofioca-Kabankalan-exterior.jpg', 'https://restaurantguru.com/Cofioca-Kabankalan-Kabankalan', 'Exterior lead; check venue and branch.'),
    (7625, 'daily brew', 'https://img02.restaurantguru.com/c0f7-Daily-Brew-Coffee-House-Kabankalan-interior.jpg', 'https://restaurantguru.com/Daily-Brew-Kabankalan', 'Interior; check venue and branch.'),
    (7628, "Park 'On Woods", '', 'https://philippines-streets.openalfa.com/kabankalan-city/eating-drinking', 'No usable place-photo lead found.'),
    (7629, 'Redbucks', 'https://s3-media0.fl.yelpcdn.com/bphoto/Q0l9hQcGVpbkzzXdWJxPYg/l.jpg', 'https://www.yelp.com/biz/redbuck-s-cafe-kabankalan', 'Cash register/menu; identity and suitability uncertain.'),
    (7630, 'Regals Refreshments', 'https://img02.restaurantguru.com/c2d3-Restaurant-Regals-exterior.jpg', 'https://restaurantguru.com/Regals-Kabankalan', 'Exterior lead; check name, venue and branch.'),
    (7631, "Sol's Garden Café", 'https://img02.restaurantguru.com/c824-Sols-Garden-Cafe-Kabankalan-view.jpg', 'https://restaurantguru.com/Sols-Garden-Cafe-Kabankalan', 'Review alongside the photo you provided in chat.'),
    (7632, 'Taste & See', '', 'https://philippines-streets.openalfa.com/kabankalan-city/eating-drinking', 'No usable place-photo lead found.'),
)
MAX_BYTES = 20 * 1024 * 1024


def eligibility(place, expected_name):
    if not place:
        return 'SKIPPED: place ID not found'
    if (place.title != expected_name or place.city_id != 2
            or not place.is_active or not place.is_verified):
        return 'SKIPPED: title, city or publication status differs'
    if place.cover_image:
        try:
            present = place.cover_image.storage.exists(place.cover_image.name)
            detail = 'file found in this project media' if present else 'file missing from this project media'
        except Exception:
            detail = 'file availability could not be checked'
        return f'SKIPPED: existing local cover reference ({detail}); do not replace automatically'
    if place.cover_image_url:
        return 'SKIPPED: existing external cover URL; not checked or replaced'
    if any((place.photo_credit, place.photo_source_url, place.photo_license, place.photo_license_url)):
        return 'SKIPPED: existing photo attribution; review before any changes'
    return ''


def download_jpeg(url):
    from PIL import Image
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; LocalCafePhotoReview/1.0)'})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(MAX_BYTES + 1)
    if not data or len(data) > MAX_BYTES:
        raise ValueError('empty response or image exceeds 20 MB')
    Image.MAX_IMAGE_PIXELS = 50_000_000
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as image:
            if image.format != 'JPEG':
                raise ValueError('response is not a JPEG image')
            size = image.size
            image.verify()
    return data, size


def spreadsheet_safe(value):
    value = str(value or '')
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def write_report(folder, rows):
    columns = ('id', 'place', 'status', 'size', 'note', 'source_page', 'image_url', 'rights', 'sha256')
    with (folder / 'sources.csv').open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: spreadsheet_safe(row.get(key, '')) for key in columns})
    esc = html.escape
    cards = []
    for row in rows:
        photo = f'<img src="images/{row["id"]}.jpg" alt="Unverified candidate for {esc(row["place"], quote=True)}">' if row['sha256'] else ''
        source = f'<a href="{esc(row["source_page"], quote=True)}">Source page</a>' if row['source_page'] else ''
        cards.append(f'<article><h2>{esc(row["place"])} · {row["id"]}</h2>{photo}'
                     f'<p><strong>{esc(row["status"])}</strong> {esc(row["size"])}</p>'
                     f'<p>{esc(row["note"])}</p>{source}</article>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Café photo review</title><style>body{font:16px system-ui;background:#f7f6ef;color:#153a2d;margin:1.5rem}main{max-width:1100px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem}article{background:#fff;padding:1rem;border-radius:12px}img{max-width:100%;height:220px;object-fit:contain}a{color:#076144}</style><main><h1>Café photo candidates</h1><p>Review only: no database or project media changes. These images are not independently verified; check place and branch, date, watermarks and privacy. Rights are unknown: private local test only, not public reuse without permission. The source listing is not proof of ownership.</p><p>Existing covers or attribution are skipped, including missing local files. A local reference may belong to another project folder; do not replace it automatically. For the photo shared in chat, no upload has been copied here.</p><div class="grid">''' + ''.join(cards) + '</div></main></html>'
    (folder / 'review.html').write_text(page, encoding='utf-8')


def stage(folder, places, downloader=download_jpeg):
    images = folder / 'images'
    images.mkdir()
    rows = []
    for pk, name, url, source, note in CAFES:
        row = {'id': pk, 'place': name, 'status': eligibility(places.get(pk), name),
               'size': '', 'note': note, 'source_page': source, 'image_url': url,
               'rights': 'Unknown; private local review only', 'sha256': ''}
        if not row['status'] and not url:
            row['status'] = 'NO IMAGE LEAD: research needed'
        elif not row['status']:
            try:
                data, (width, height) = downloader(url)
                (images / f'{pk}.jpg').write_bytes(data)
                row.update(status='STAGED: verify identity and rights', size=f'{width} x {height}',
                           sha256=hashlib.sha256(data).hexdigest())
            except Exception as exc:
                row['status'] = 'DOWNLOAD FAILED: ' + str(exc)[:200]
        rows.append(row)
        print(f"{pk} {name}: {row['status']} {row['size']}", flush=True)
    write_report(folder, rows)
    return rows


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file():
        raise SystemExit('Open PowerShell in the project folder containing manage.py.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    import django
    django.setup()
    from django.conf import settings
    from apps.places.models import Place
    db = settings.DATABASES['default']
    if (db['ENGINE'] != 'django.db.backends.mysql' or db['NAME'] != 'exploreanywhere'
            or str(db.get('HOST', '')).lower() not in ('localhost', '127.0.0.1', '::1')):
        raise SystemExit('Stopped: expected local MySQL/MariaDB exploreanywhere. No changes made.')
    places = {p.pk: p for p in Place.objects.filter(pk__in=[item[0] for item in CAFES])}
    folder = Path.home() / 'EK_photo_reviews' / datetime.now().strftime('cafes_%Y%m%d_%H%M%S_%f')
    folder.mkdir(parents=True, exist_ok=False)
    stage(folder, places)
    print('\nReview folder:', folder)
    print('Open review.html and keep sources.csv. No database or project media was changed.')
    print('Do not import or replace files yet; tell the assistant which candidates match.')
    try:
        webbrowser.open((folder / 'review.html').as_uri())
    except Exception:
        pass


if __name__ == '__main__':
    main()
