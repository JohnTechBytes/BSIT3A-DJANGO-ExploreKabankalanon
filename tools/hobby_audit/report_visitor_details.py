#!/usr/bin/env python3
"""Export currently displayed public visitor information for review only.

Run from the laptop project folder. No database writes or imports are made.
The report includes public listing contacts, not account or search-log data.
"""
import csv
from datetime import datetime
import os
from pathlib import Path
import sys


def spreadsheet_safe(value):
    value = str(value if value is not None else '')
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def address_status(value):
    text = (value or '').strip()
    if not text or text.casefold() == 'address not independently verified':
        return 'Missing or placeholder; research needed'
    return 'Recorded; accuracy not verified'


def hours_text(opening_hours):
    entries = []
    for hours in opening_hours:
        if hours.is_closed:
            detail = 'Closed'
        elif hours.open_time and hours.close_time:
            detail = f'{hours.open_time:%H:%M}-{hours.close_time:%H:%M}'
        else:
            detail = 'Hours not specified'
        entries.append(f'{hours.get_weekday_display()}: {detail}')
    return ' | '.join(entries)


COLUMNS = (
    'place_id', 'place', 'osm_slug', 'category', 'address', 'address_status',
    'barangay', 'contact_displayed', 'website', 'latitude', 'longitude', 'opening_hours',
)


def export_report(path, places):
    count = 0
    with path.open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for place in places:
            row = {
                'place_id': place.pk,
                'place': place.title,
                'osm_slug': place.slug,
                'category': place.category.name if place.category else '',
                'address': place.address,
                'address_status': address_status(place.address),
                'barangay': place.barangay,
                # Match the public detail page: email is displayed only when phone is blank.
                'contact_displayed': place.phone or place.email,
                'website': place.website,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'opening_hours': hours_text(place.opening_hours.all()),
            }
            writer.writerow({key: spreadsheet_safe(row[key]) for key in COLUMNS})
            count += 1
    return count


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

    # This excludes accounts, user activity, reviews and unpublished places.
    places = (Place.objects.filter(city_id=2, is_active=True, is_verified=True)
              .select_related('category').prefetch_related('opening_hours')
              .only('id', 'city_id', 'title', 'slug', 'category__name', 'address',
                    'barangay', 'phone', 'email', 'website', 'latitude', 'longitude')
              .order_by('title', 'pk'))
    folder = Path.home() / 'EK_visitor_reports' / datetime.now().strftime('published_%Y%m%d_%H%M%S_%f')
    folder.mkdir(parents=True, exist_ok=False)
    report = folder / 'visitor_information.csv'
    count = export_report(report, places)
    print('Published Kabankalan places:', count)
    print('Report:', report)
    print('READ ONLY: no database or project media changes.')
    print('The CSV includes public listing contacts but no account or search-log data.')
    print('Recorded details and publication status do not prove accuracy or permission.')
    print('Review the file before sharing; spreadsheet formula-like cells are escaped.')


if __name__ == '__main__':
    main()
