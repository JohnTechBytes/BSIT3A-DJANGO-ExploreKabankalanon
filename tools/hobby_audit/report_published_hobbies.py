#!/usr/bin/env python3
"""Export a read-only review of published Kabankalan place/hobby data.

Run from the laptop project folder. Never changes the database or imports places.
The CSV files contain public listing information, not account/search-log data.
"""
import csv
from collections import Counter
from datetime import datetime
import os
from pathlib import Path
import sys


def spreadsheet_safe(value):
    """Prevent spreadsheet formula execution without mutating the database."""
    value = str(value or '')
    if value.lstrip().startswith(('=', '+', '-', '@')):
        return "'" + value
    return value


def write_csv(path, columns, rows):
    with path.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: spreadsheet_safe(row[key]) for key in columns})


def collect_places(places):
    rows = []
    categories = Counter()
    hobbies = Counter()
    for place in places:
        name = place.category.name if place.category else 'Not assigned'
        tag_names = sorted((hobby.name for hobby in place.hobbies.all()), key=str.casefold)
        tagged = bool(tag_names)
        if place.cover_image:
            cover = 'local reference recorded'
        elif place.cover_image_url:
            cover = 'external URL recorded'
        else:
            cover = 'no cover recorded'
        rows.append({
            'place_id': place.pk,
            'place': place.title,
            'category': name,
            'address': place.address,
            'barangay': place.barangay,
            'hobbies': ' | '.join(tag_names),
            'hobby_count': len(tag_names),
            'review_status': 'Has assigned tags; verify suitability' if tagged else 'No hobby tags; review',
            'cover_status': cover,
        })
        categories[(name, 'total')] += 1
        if not tagged:
            categories[(name, 'no_tags')] += 1
        hobbies.update(tag_names)
    return rows, categories, hobbies


def export_report(folder, places):
    rows, categories, hobbies = collect_places(places)
    write_csv(folder / 'places_and_hobbies.csv', [
        'place_id', 'place', 'category', 'address', 'barangay', 'hobbies',
        'hobby_count', 'review_status', 'cover_status',
    ], rows)
    names = sorted({category for category, _ in categories}, key=str.casefold)
    write_csv(folder / 'category_summary.csv', ['category', 'published', 'without_hobby_tags'], [
        {'category': name, 'published': categories[(name, 'total')],
         'without_hobby_tags': categories[(name, 'no_tags')]}
        for name in names
    ])
    write_csv(folder / 'hobby_summary.csv', ['hobby', 'places_with_tag'], [
        {'hobby': hobby, 'places_with_tag': hobbies[hobby]}
        for hobby in sorted(hobbies, key=str.casefold)
    ])
    return len(rows), sum(row['hobby_count'] == 0 for row in rows)


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

    database = settings.DATABASES['default']
    if (database['ENGINE'] != 'django.db.backends.mysql'
            or database['NAME'] != 'exploreanywhere'
            or str(database.get('HOST', '')).lower() not in ('localhost', '127.0.0.1', '::1')):
        raise SystemExit('Stopped: expected the local MySQL/MariaDB exploreanywhere database. No changes made.')

    # Only public catalogue fields are selected; no account, review or query log.
    places = (Place.objects.filter(city_id=2, is_active=True, is_verified=True)
              .select_related('category').prefetch_related('hobbies').order_by('title', 'pk'))
    folder = Path.home() / 'EK_hobby_audits' / datetime.now().strftime('published_%Y%m%d_%H%M%S_%f')
    folder.mkdir(parents=True, exist_ok=False)
    count, missing = export_report(folder, places)
    print('Published Kabankalan places:', count)
    print('Without hobby tags:', missing)
    print('With at least one hobby tag:', count - missing)
    print('Report folder:', folder)
    print('Files: places_and_hobbies.csv, category_summary.csv, hobby_summary.csv')
    print('READ ONLY: no database changes. Tags and listings still require review;')
    print('a missing tag does not mean a place is irrelevant. Recorded covers are not verified photos.')
    print('Spreadsheet cells starting with formula characters are prefixed with an apostrophe for safety.')


if __name__ == '__main__':
    main()
