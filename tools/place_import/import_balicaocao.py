#!/usr/bin/env python3
"""Add one user-requested place to a confirmed local database, or stop safely.

Never updates or deletes existing rows, never runs migrations, never imports
photos. Run from the project root with its own virtual environment, and take
a private backup of the configured database and media first.
"""
from decimal import Decimal
import os
from pathlib import Path
import re
import sys
import unicodedata

LATITUDE = Decimal('9.956680')
LONGITUDE = Decimal('122.858250')
TITLE = 'Balicaocao Eco-Park'
ADDRESS = 'Sitio Balicaocao, Barangay Orong, Kabankalan City, Negros Occidental'
SEARCH_RADIUS_DEGREES = Decimal('0.0012')


def normalized(value):
    value = unicodedata.normalize('NFKD', value or '').casefold()
    return re.sub(r'[^a-z0-9]', '', value)


def find_candidates(city):
    """Find name variants and nearby records, including unpublished imports."""
    from apps.places.models import Place
    matches = []
    for row in Place.objects.filter(city=city).values('pk', 'title', 'slug', 'latitude', 'longitude', 'is_active', 'is_verified'):
        name = normalized(row['title']) + normalized(row['slug'])
        name_match = 'balicaocao' in name
        lat, lon = row['latitude'], row['longitude']
        near = (lat is not None and lon is not None
                and abs(lat - LATITUDE) <= SEARCH_RADIUS_DEGREES
                and abs(lon - LONGITUDE) <= SEARCH_RADIUS_DEGREES)
        if name_match or near:
            matches.append(row)
    return matches


def create_place(city_id, category_id=None):
    """Create one new row after rechecking under a lock; never update a match."""
    from django.db import transaction
    from apps.cities.models import City
    from apps.core.models import Category
    from apps.places.models import Place

    with transaction.atomic():
        city = City.objects.select_for_update().get(pk=city_id)
        if city.pk != 2 or normalized(city.name) not in ('kabankalan', 'kabankalancity', 'cityofkabankalan') or normalized(city.province) != 'negrosoccidental':
            raise ValueError('City 2 is not confirmed as Kabankalan, Negros Occidental.')
        candidates = find_candidates(city)
        if candidates:
            raise ValueError('A matching or nearby listing already exists. No place was added; inspect the admin and OSM review queue.')
        category = Category.objects.get(pk=category_id) if category_id is not None else None
        place = Place(city=city, category=category, title=TITLE, slug='balicaocao-eco-park',
                      address=ADDRESS, barangay='Orong', latitude=LATITUDE, longitude=LONGITUDE,
                      description='Also known as Balicaocao Highland Resort.',
                      is_active=True, is_verified=True)
        place.full_clean()
        place.save(force_insert=True)
        return place.pk


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file() or not (root / 'mysite' / 'settings.py').is_file():
        raise ValueError('Run from the project folder containing manage.py.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    if os.environ['DJANGO_SETTINGS_MODULE'] != 'mysite.settings':
        raise ValueError('Unexpected Django settings module. No place was added.')
    import django
    django.setup()
    from django.db import connection
    from apps.cities.models import City
    from apps.core.models import Category

    db = connection.settings_dict
    if connection.vendor != 'mysql' or str(db.get('NAME', '')).casefold() != 'exploreanywhere':
        raise ValueError('Configured database is not the expected MySQL/MariaDB exploreanywhere. No place was added; ask for help.')
    print('Configured database:', db['NAME'], '(MySQL/MariaDB).', flush=True)
    print('This adds one published place; it does not change or delete existing data, import photos, or run migrations.')
    print('Stop Django first; keep XAMPP MariaDB running. Use phpMyAdmin to export a private database backup and copy media first.')
    if input('Type BACKUP DONE after making your backup, or press Enter to cancel: ').strip() != 'BACKUP DONE':
        print('Cancelled. No place was added.')
        return
    city = City.objects.get(pk=2)
    if normalized(city.name) not in ('kabankalan', 'kabankalancity', 'cityofkabankalan') or normalized(city.province) != 'negrosoccidental':
        raise ValueError('City 2 is not confirmed as Kabankalan, Negros Occidental. No place was added.')
    candidates = find_candidates(city)
    if candidates:
        print('Possible existing or nearby places, including unpublished rows:')
        for row in candidates:
            print('  ID:', row['pk'], '|', row['title'], '| active:', row['is_active'], '| verified:', row['is_verified'], '| coordinates:', row['latitude'], row['longitude'])
        raise ValueError('No place was added. Check these records in the admin and OSM review queue to avoid a duplicate.')
    categories = list(Category.objects.order_by('name').values_list('pk', 'name'))
    print('\nCategories already in your database:')
    for pk, name in categories:
        print(' ', pk, '-', name)
    choice = input('Enter the ID of the appropriate existing category, or press Enter to leave it unassigned: ').strip()
    if choice and (not choice.isascii() or not choice.isdecimal() or int(choice) not in {pk for pk, _ in categories}):
        raise ValueError('Category ID was not in the displayed list. No place was added.')
    category_id = int(choice) if choice else None
    print('\nProposed place:', TITLE)
    print('Address:', ADDRESS)
    print('Latitude:', LATITUDE, '| Longitude:', LONGITUDE)
    print('Category:', next((name for pk, name in categories if pk == category_id), 'Unassigned'))
    print('Status: active and verified (public). This flag does not prove independent verification.')
    print('No photograph, opening hours, or contact details will be added.')
    print('The supplied DMS and Plus Code describe slightly different points. Confirm this decimal point is suitable before continuing.')
    if input('Type PUBLISH BALICAOCAO to add this one place, or press Enter to cancel: ').strip() != 'PUBLISH BALICAOCAO':
        print('Cancelled. No place was added.')
        return
    pk = create_place(city.pk, category_id)
    print('Added one place. ID:', pk)
    print('Open Explore Places and the map to verify the result. Existing records and media were not changed.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('STOPPED:', exc)
        sys.exit(1)
