#!/usr/bin/env python3
"""Add the confirmed campsite and photographer-supplied image, or stop.

No updates to existing records, migrations or unrelated media. This standalone
script must be run from the local Django project with its configured database.
"""
from decimal import Decimal
import hashlib
import os
from pathlib import Path
import re
import sys
import unicodedata
from uuid import uuid4

TITLE = "Wilfredo's Campsite"
ADDRESS = 'Upstream of Mag-aso Falls, Barangay Oringao, Kabankalan City, Negros Occidental'
LATITUDE = Decimal('9.900833')
LONGITUDE = Decimal('122.894188')
IMAGE_HASH = 'fa96d06593f930869ffd2c4806d7e8230903d4d6154aba930250dc5f4373ce8a'
IMAGE_SIZE = 31352
SEARCH_RADIUS = Decimal('0.0012')
DESCRIPTION = (
    'A rustic campsite and waterfall area upstream of the main Mag-aso Falls, '
    'with smaller cascades and natural lagoons. Visitor-supplied details, not '
    'independently verified: tent pitching approximately PHP 100, open cottages '
    'PHP 400, basic rooms PHP 400 to PHP 1,000, day entrance approximately '
    'PHP 25, and an on-site sari-sari store. Prices and availability may change; '
    'confirm locally before visiting.'
)


def normalized(value):
    value = unicodedata.normalize('NFKD', value or '').casefold()
    return re.sub(r'[^a-z0-9]', '', value)


def read_photo(filename):
    p = Path(filename).expanduser()
    if not p.is_file() or p.stat().st_size != IMAGE_SIZE:
        raise ValueError('Photo not found or does not match the supplied image. Nothing was added.')
    data = p.read_bytes()
    if (len(data) != IMAGE_SIZE or hashlib.sha256(data).hexdigest() != IMAGE_HASH
            or not data.startswith(b'\x89PNG\r\n\x1a\n')):
        raise ValueError('Photo does not match the supplied image. Nothing was added.')
    return data


def find_candidates(city):
    from apps.places.models import Place
    candidates = []
    for row in Place.objects.filter(city=city).values('pk', 'title', 'slug', 'latitude', 'longitude', 'is_active', 'is_verified'):
        name = normalized(row['title']) + normalized(row['slug'])
        lat, lon = row['latitude'], row['longitude']
        near = (lat is not None and lon is not None
                and abs(lat - LATITUDE) <= SEARCH_RADIUS and abs(lon - LONGITUDE) <= SEARCH_RADIUS)
        if 'wilfredo' in name or near:
            candidates.append(row)
    return candidates


def is_reviewed_mag_aso(row):
    """Match only the exact nearby record reported by this user's PC."""
    return (row['pk'] == 1703 and row['title'] == 'Mag Aso Falls'
            and row['latitude'] == Decimal('9.900694')
            and row['longitude'] == Decimal('122.893451')
            and row['is_active'] is True and row['is_verified'] is True
            and 'wilfredo' not in normalized(row['slug']))


def reviewed_candidates(city):
    """Allow that one separately confirmed falls only; stop on every other match."""
    rows = find_candidates(city)
    if len(rows) != 1 or not is_reviewed_mag_aso(rows[0]):
        print('Current matching or nearby records (including unpublished):')
        for row in rows:
            print(' ID:', row['pk'], '|', row['title'], '| active:', row['is_active'],
                  '| verified:', row['is_verified'], '| coordinates:', row['latitude'], row['longitude'])
        raise ValueError('Expected Mag Aso Falls 1703 alone was not found; nothing was added. Ask for review.')
    return rows[0]


def photo_directory():
    """Only use a local, reviewed Django media directory; never overwrite a file."""
    from django.conf import settings
    from django.core.files.storage import FileSystemStorage
    from apps.places.models import Place
    storage = Place._meta.get_field('cover_image').storage
    root = Path(settings.MEDIA_ROOT).absolute()
    if not isinstance(storage, FileSystemStorage) or Path(storage.location).resolve() != root.resolve():
        raise ValueError('The configured photo storage is not the expected local media folder. Nothing was added.')
    if root.is_symlink():
        raise ValueError('Symlinked media folders are not supported. Nothing was added.')
    root.mkdir(parents=True, exist_ok=True)
    current = root
    for part in ('places', 'covers'):
        current = current / part
        if current.is_symlink():
            raise ValueError('Symlinked media folders are not supported. Nothing was added.')
        current.mkdir(exist_ok=True)
        if not current.is_dir() or not current.resolve().is_relative_to(root.resolve()):
            raise ValueError('Unsafe media folder. Nothing was added.')
    return current


def create_place(city_id, category_id, image, *, separate_mag_aso_confirmed=False):
    """Recheck duplicates under a city lock; add only this row and one new file."""
    from django.db import transaction
    from apps.cities.models import City
    from apps.core.models import Category
    from apps.places.models import Place

    if (len(image) != IMAGE_SIZE or hashlib.sha256(image).hexdigest() != IMAGE_HASH
            or not image.startswith(b'\x89PNG\r\n\x1a\n')):
        raise ValueError('Photo verification failed. Nothing was added.')
    if separate_mag_aso_confirmed is not True:
        raise ValueError('The separate Mag Aso Falls listing was not confirmed. Nothing was added.')
    created_photo = None
    place = None
    try:
        with transaction.atomic():
            city = City.objects.select_for_update().get(pk=city_id)
            if city.pk != 2 or normalized(city.name) not in ('kabankalan', 'kabankalancity', 'cityofkabankalan') or normalized(city.province) != 'negrosoccidental':
                raise ValueError('City 2 is not confirmed as Kabankalan, Negros Occidental.')
            # Revalidate inside the transaction; no other matches are allowed.
            reviewed_candidates(city)
            category = Category.objects.get(pk=category_id) if category_id is not None else None
            place = Place(city=city, category=category, title=TITLE, slug='wilfredos-campsite',
                          address=ADDRESS, barangay='Oringao', latitude=LATITUDE, longitude=LONGITUDE,
                          description=DESCRIPTION, photo_credit='Photo provided by the photographer',
                          is_active=True, is_verified=True)
            place.full_clean()
            directory = photo_directory()
            name = 'wilfredos-campsite-' + uuid4().hex + '.png'
            path = directory / name
            with path.open('xb') as output:
                created_photo = path
                output.write(image)
            if hashlib.sha256(path.read_bytes()).hexdigest() != IMAGE_HASH:
                raise ValueError('Saved photo failed verification.')
            place.cover_image.name = 'places/covers/' + name
            place.full_clean()
            place.save(force_insert=True)
            return place.pk
    except BaseException:
        if created_photo and created_photo.exists():
            # A database error while committing may leave the commit outcome
            # uncertain. Do not remove a photo referenced by a committed row,
            # or if the database cannot confirm that no such row exists.
            safe_to_remove = True
            if place is not None and place.pk is not None:
                try:
                    safe_to_remove = not Place.objects.filter(pk=place.pk, cover_image=place.cover_image.name).exists()
                except Exception:
                    safe_to_remove = False
            if not safe_to_remove:
                print('Record may have been saved; photo retained for review:', created_photo, flush=True)
            else:
                try:
                    # Never delete a file another process has subsequently changed.
                    current = created_photo.read_bytes()
                    if current == image or (len(current) < len(image) and image.startswith(current)):
                        created_photo.unlink()
                    else:
                        print('Manual photo recovery may be needed:', created_photo, flush=True)
                except OSError:
                    print('Manual photo recovery may be needed:', created_photo, flush=True)
        raise


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file() or not (root / 'mysite/settings.py').is_file():
        raise ValueError('Run from the project folder containing manage.py.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    if os.environ['DJANGO_SETTINGS_MODULE'] != 'mysite.settings':
        raise ValueError('Unexpected Django settings module. Nothing was added.')
    import django
    django.setup()
    from django.db import connection
    from apps.cities.models import City
    from apps.core.models import Category
    db = connection.settings_dict
    if connection.vendor != 'mysql' or str(db.get('NAME', '')).casefold() != 'exploreanywhere':
        raise ValueError('Configured database is not the expected MySQL/MariaDB exploreanywhere. Nothing was added.')
    host = str(db.get('HOST') or '').strip().casefold()
    if host not in ('', 'localhost', '127.0.0.1', '::1'):
        raise ValueError('Database host is not local; nothing was added. Ask for help before continuing.')
    print('Configured database:', db['NAME'], '(local MySQL/MariaDB).')
    print('Adds one public place and one new photo. No existing data is changed and no migrations run.')
    print('Stop Django first; keep MariaDB running. Back up the database and media before proceeding.')
    if input('Type BACKUP DONE after making a current backup, or press Enter to cancel: ').strip() != 'BACKUP DONE':
        print('Cancelled. Nothing was added.')
        return
    city = City.objects.get(pk=2)
    if normalized(city.name) not in ('kabankalan', 'kabankalancity', 'cityofkabankalan') or normalized(city.province) != 'negrosoccidental':
        raise ValueError('City 2 is not confirmed as Kabankalan, Negros Occidental. Nothing was added.')
    reviewed_candidates(city)
    print('Nearby existing place: ID 1703, Mag Aso Falls, at 9.900694 122.893451.')
    print('This place will not be changed. No other matching or nearby records are allowed.')
    if input('Type SEPARATE 1703 to confirm the campsite is a different place, or press Enter to cancel: ').strip() != 'SEPARATE 1703':
        print('Cancelled. Nothing was added.')
        return
    categories = list(Category.objects.order_by('name').values_list('pk', 'name'))
    print('\nExisting categories:')
    for pk, name in categories:
        print(' ', pk, '-', name)
    choice = input('Enter the appropriate existing category ID, or press Enter to leave it unassigned: ').strip()
    if choice and (not choice.isascii() or not choice.isdecimal() or int(choice) not in {pk for pk, _ in categories}):
        raise ValueError('Category ID was not in the displayed list. Nothing was added.')
    category_id = int(choice) if choice else None
    filename = input('Full path to the same PNG photo you supplied: ').strip()
    if len(filename) >= 2 and filename[0] == filename[-1] and filename[0] in ('"', "'"):
        filename = filename[1:-1]
    image = read_photo(filename)
    print('\nProposed place:', TITLE)
    print('Address:', ADDRESS)
    print('Coordinates from the directions destination:', LATITUDE, LONGITUDE)
    print('Category:', next((name for pk, name in categories if pk == category_id), 'Unassigned'))
    print('Photo: supplied image, 108 x 108 pixels; credited to its photographer.')
    print('Description:', DESCRIPTION)
    print('Status: active and verified (public). This flag does not prove independent verification.')
    print('Confirm the destination, photo and reported prices are suitable before publishing.')
    if input('Type PUBLISH WILFREDO to add this one place and photo, or press Enter to cancel: ').strip() != 'PUBLISH WILFREDO':
        print('Cancelled. Nothing was added.')
        return
    pk = create_place(city.pk, category_id, image, separate_mag_aso_confirmed=True)
    print('Added one place and photo. Place ID:', pk)
    print('Check the listing and map. Existing places and media were not changed.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('STOPPED:', exc)
        sys.exit(1)
