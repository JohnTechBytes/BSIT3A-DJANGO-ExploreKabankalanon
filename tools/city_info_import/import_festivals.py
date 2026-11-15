#!/usr/bin/env python3
"""Safely add two requested Kabankalan festival guides to a local database.

Run from the project's root, using its Python environment. Back up the database
first and stop Django and any other database editors. This script never updates
or deletes records, adds photos, imports media, or runs migrations.
"""
import os
from pathlib import Path
import re
import sys
import unicodedata

# Historical reports, not a current event schedule:
# https://digicastnegros.com/kabankalan-celebrates-46th-sinulog/
# https://www.sunstar.com.ph/more-articles/kabankalan-city-celebrates-9th-udyakan-festival-today
GUIDES = (
    {
        'title': 'Sinulog sa Kabankalan',
        'description': (
            'Sinulog sa Kabankalan is a local celebration in honor of the Santo Niño, '
            'with religious and cultural activities. Schedules and programs may change; '
            'check the city’s announcements for current details.'
        ),
        'order': 1,
    },
    {
        'title': 'Udyakan sa Kabankalan',
        'description': (
            'Udyakan sa Kabankalan is a cultural festival associated with the city’s '
            'Charter Day celebration. Schedules and programs may change; check the '
            'city’s announcements for current details.'
        ),
        'order': 2,
    },
)
MATCH_TERMS = ('sinulog', 'udyakan')


def normalized(value):
    value = unicodedata.normalize('NFKD', value or '').casefold()
    return re.sub(r'[^a-z0-9]', '', value)


def validate_city(city):
    if (city.pk != 2 or normalized(city.name) != 'kabankalan'
            or normalized(city.province) != 'negrosoccidental'):
        raise ValueError('City 2 is not Kabankalan, Negros Occidental. No guides were added.')


def find_candidates(city, lock=False):
    """Check all guide types and publication states, including descriptions."""
    from apps.info.models import CityInformation
    rows = CityInformation.objects.filter(city=city).order_by('pk')
    if lock:
        rows = rows.select_for_update()
    found = []
    for row in rows.values('pk', 'title', 'description', 'info_type', 'is_published'):
        content = normalized(row['title']) + normalized(row['description'])
        if any(term in content for term in MATCH_TERMS):
            found.append(row)
    return found


def add_guides(city_id):
    """Insert both guides atomically or leave the database unchanged."""
    from django.db import transaction
    from apps.cities.models import City
    from apps.info.models import CityInformation

    with transaction.atomic():
        city = City.objects.select_for_update().get(pk=city_id)
        validate_city(city)
        if find_candidates(city, lock=True):
            raise ValueError('A possible existing festival guide was found. No guides were added.')
        ids = []
        for data in GUIDES:
            guide = CityInformation(city=city, title=data['title'],
                                    description=data['description'], order=data['order'],
                                    info_type=CityInformation.InfoType.EVENT,
                                    thumbnail_url='', photo_credit='', is_published=True)
            guide.full_clean()
            guide.save(force_insert=True)
            ids.append(guide.pk)
        return ids


def check_storage(connection):
    """Require transactional tables and no visible insert-side triggers."""
    from apps.cities.models import City
    from apps.info.models import CityInformation

    city_table = City._meta.db_table
    guide_table = CityInformation._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES '
            'WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN (%s, %s)',
            [city_table, guide_table],
        )
        engines = {str(name).casefold(): str(engine or '').casefold() for name, engine in cursor.fetchall()}
        if any(engines.get(name.casefold()) != 'innodb' for name in (city_table, guide_table)):
            raise ValueError('City or guide table is missing or not InnoDB; no guides were added.')
        cursor.execute(
            'SELECT TRIGGER_NAME FROM information_schema.TRIGGERS '
            'WHERE TRIGGER_SCHEMA = DATABASE() AND EVENT_OBJECT_TABLE = %s AND EVENT_MANIPULATION = %s',
            [guide_table, 'INSERT'],
        )
        if cursor.fetchall():
            raise ValueError('An INSERT trigger exists on City Information; no guides were added. Ask for help.')


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file() or not (root / 'mysite' / 'settings.py').is_file():
        raise ValueError('Run from the project folder containing manage.py.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    if os.environ['DJANGO_SETTINGS_MODULE'] != 'mysite.settings':
        raise ValueError('Unexpected settings module. No guides were added.')
    import django
    django.setup()
    from django.db import connection
    from apps.cities.models import City

    db = connection.settings_dict
    host = str(db.get('HOST') or '').strip().casefold()
    if (connection.vendor != 'mysql' or str(db.get('NAME', '')).casefold() != 'exploreanywhere'
            or host not in ('', 'localhost', '127.0.0.1', '::1')):
        raise ValueError('Expected local MySQL/MariaDB database exploreanywhere; no guides were added.')
    check_storage(connection)
    print('Configured database:', db['NAME'], '| host:', host or '(local default)')
    print('This adds TWO published Event / Festival guides. Existing records and photos are not changed.')
    print('Stop Django and other database editors; keep XAMPP MariaDB running.')
    print('Export a private full database backup with phpMyAdmin before continuing.')
    if input('Type BACKUP DONE after making the backup, or press Enter to cancel: ').strip() != 'BACKUP DONE':
        print('Cancelled. No guides were added.')
        return
    city = City.objects.get(pk=2)
    validate_city(city)
    candidates = find_candidates(city)
    if candidates:
        print('Possible existing festival guides (including unpublished entries):')
        for row in candidates:
            print('  ID:', row['pk'], '|', row['title'], '| type:', row['info_type'], '| published:', row['is_published'])
        raise ValueError('No guides were added. Review the existing records before trying again.')
    print('\nPlease review the two guides before publishing:')
    for data in GUIDES:
        print('\nTitle:', data['title'])
        print('Description:', data['description'])
    print('\nType: Event / Festival | Status: published | Photos: none')
    print('No dates, schedules, media files, migrations, or other records are added or changed.')
    if input('Type PUBLISH BOTH FESTIVALS to add both, or press Enter to cancel: ').strip() != 'PUBLISH BOTH FESTIVALS':
        print('Cancelled. No guides were added.')
        return
    ids = add_guides(city.pk)
    print('Added two published guides. IDs:', ', '.join(map(str, ids)))
    print('Refresh City Information to see them under Event / Festival.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('STOPPED:', exc)
        sys.exit(1)
