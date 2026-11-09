#!/usr/bin/env python3
"""Apply only the user's approved 29 visitor fields, after a new DB backup.

Stop the Django server first, keep XAMPP MySQL running. This script leaves media,
other fields, existing values, categories and publication flags untouched. The
backup is private and must not be shared. A dump check is not a test restore.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime
from collections import defaultdict

APPROVED_PLAN = [
  {
    "id": 7631,
    "title": "Sol's Garden Caf\u00e9",
    "slug": "osm-node-12137330729",
    "field": "address",
    "proposed": "Don Emilio Village Phase 1, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7631,
    "title": "Sol's Garden Caf\u00e9",
    "slug": "osm-node-12137330729",
    "field": "barangay",
    "proposed": "Barangay 9",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7771,
    "title": "Ample Corner",
    "slug": "osm-node-4567883293",
    "field": "address",
    "proposed": "Cordova Street, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7771,
    "title": "Ample Corner",
    "slug": "osm-node-4567883293",
    "field": "barangay",
    "proposed": "Barangay 5",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7635,
    "title": "CityMall Kabankalan",
    "slug": "osm-way-519017326",
    "field": "barangay",
    "proposed": "Talubangi",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7636,
    "title": "Gaisano Grand Mall Kabankalan",
    "slug": "osm-way-247293840",
    "field": "barangay",
    "proposed": "Barangay 1",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7654,
    "title": "BPI",
    "slug": "osm-way-1374319930",
    "field": "website",
    "proposed": "https://www.bpi.com.ph/",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7687,
    "title": "Holy Mother of Mercy Hospital",
    "slug": "osm-node-12136667737",
    "field": "barangay",
    "proposed": "Barangay 9",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7787,
    "title": "Melting Pot",
    "slug": "osm-node-5487360540",
    "field": "barangay",
    "proposed": "Barangay 7",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7790,
    "title": "Perico",
    "slug": "osm-node-4567933293",
    "field": "address",
    "proposed": "Justice J.Y. Perez Highway, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 1703,
    "title": "Mag Aso Falls",
    "slug": "osm-node-3369728379",
    "field": "barangay",
    "proposed": "Oringao",
    "document": "VISITOR_INFORMATION_RESEARCH.md",
    "expected": ""
  },
  {
    "id": 7649,
    "title": "Bantayan Public Market",
    "slug": "osm-way-283651062",
    "field": "barangay",
    "proposed": "Bantayan",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md",
    "expected": ""
  },
  {
    "id": 7661,
    "title": "Camingawan Public Market",
    "slug": "osm-way-246338355",
    "field": "barangay",
    "proposed": "Camingawan",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md",
    "expected": ""
  },
  {
    "id": 7696,
    "title": "Kabankalan City Hospital",
    "slug": "osm-way-838905925",
    "field": "barangay",
    "proposed": "Tabugon",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md",
    "expected": ""
  },
  {
    "id": 7703,
    "title": "Landbank",
    "slug": "osm-node-4579207691",
    "field": "address",
    "proposed": "Jomabo Building, Tan Lorenzo corner Guanzon Streets, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7703,
    "title": "Landbank",
    "slug": "osm-node-4579207691",
    "field": "barangay",
    "proposed": "Barangay 3",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_2.md",
    "expected": ""
  },
  {
    "id": 7671,
    "title": "DBP",
    "slug": "osm-node-4567933304",
    "field": "address",
    "proposed": "DBP Building, corner Lirazan and Bonifacio Streets, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7735,
    "title": "PNB",
    "slug": "osm-way-247033114",
    "field": "address",
    "proposed": "NOAC National Highway corner Guanzon Street, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7768,
    "title": "Yamaha 3S Shop",
    "slug": "osm-node-4567933307",
    "field": "barangay",
    "proposed": "Barangay 3",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_3.md",
    "expected": ""
  },
  {
    "id": 7626,
    "title": "Kape Centrale",
    "slug": "osm-node-12159153690",
    "field": "address",
    "proposed": "Guanzon corner Rizal Street, Kabankalan Public Plaza, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7626,
    "title": "Kape Centrale",
    "slug": "osm-node-12159153690",
    "field": "email",
    "proposed": "kapecentrale@gmail.com",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": ""
  },
  {
    "id": 7697,
    "title": "Kabankalan Public Market",
    "slug": "osm-way-624985029",
    "field": "barangay",
    "proposed": "Barangay 1",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": ""
  },
  {
    "id": 7750,
    "title": "Shell",
    "slug": "osm-way-247030664",
    "field": "phone",
    "proposed": "(034) 471-2510",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": ""
  },
  {
    "id": 7753,
    "title": "Super A's",
    "slug": "osm-node-4567883297",
    "field": "address",
    "proposed": "Lirazan Street, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7753,
    "title": "Super A's",
    "slug": "osm-node-4567883297",
    "field": "website",
    "proposed": "https://www.superascommercial.com/",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": ""
  },
  {
    "id": 7776,
    "title": "Chicken Ati-Atihan",
    "slug": "osm-node-4579156693",
    "field": "address",
    "proposed": "Guanzon Street, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7776,
    "title": "Chicken Ati-Atihan",
    "slug": "osm-node-4579156693",
    "field": "barangay",
    "proposed": "Barangay 2",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_4.md",
    "expected": ""
  },
  {
    "id": 7656,
    "title": "Breadbox",
    "slug": "osm-node-4579156694",
    "field": "address",
    "proposed": "Guanzon Street, Kabankalan City",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_5.md",
    "expected": "Address not independently verified"
  },
  {
    "id": 7688,
    "title": "Honda 3S Shop",
    "slug": "osm-node-4567931199",
    "field": "barangay",
    "proposed": "Barangay 3",
    "document": "VISITOR_INFORMATION_RESEARCH_BATCH_5.md",
    "expected": ""
  }
]
ALLOWED_FIELDS = {'address', 'barangay', 'phone', 'email', 'website'}
DUMP_EXE = Path(r'C:\xampp\mysql\bin\mysqldump.exe')


def plan_group(plan):
    grouped = defaultdict(list)
    keys = set()
    for item in plan:
        key = (item['id'], item['field'])
        if key in keys or item['field'] not in ALLOWED_FIELDS:
            raise ValueError('Invalid or duplicate field in plan.')
        if not item['proposed'] or not item['slug'].startswith('osm-'):
            raise ValueError('Invalid proposal identity or value.')
        if item['expected'] != ('Address not independently verified' if item['field'] == 'address' else ''):
            raise ValueError('Only the reviewed blank or placeholder values may be changed.')
        keys.add(key)
        grouped[item['id']].append(item)
    return dict(grouped)


def validate_places(places, plan):
    grouped = plan_group(plan)
    if set(places) != set(grouped):
        raise ValueError('A selected record is missing; no changes made.')
    for pk, items in grouped.items():
        p = places[pk]
        if not (p.pk == pk and p.city_id == 2 and p.is_active and p.is_verified):
            raise ValueError(f'Record {pk} changed scope or publication status; no changes made.')
        for item in items:
            if p.title != item['title'] or p.slug != item['slug']:
                raise ValueError(f'Record {pk} name or OSM identity changed; no changes made.')
            if getattr(p, item['field']) != item['expected']:
                raise ValueError(f'Record {pk} {item["field"]} changed since preview; no changes made.')
            max_length = p._meta.get_field(item['field']).max_length
            if max_length and len(item['proposed']) > max_length:
                raise ValueError(f'Record {pk} proposed {item["field"]} is too long; no changes made.')
    return grouped


def apply_plan(place_model, plan):
    """Lock and validate every row before changing any; one transaction."""
    from django.db import transaction
    grouped = plan_group(plan)
    with transaction.atomic():
        locked = {p.pk: p for p in place_model.objects.select_for_update().filter(pk__in=grouped).order_by('pk')}
        validate_places(locked, plan)
        for pk, items in sorted(grouped.items()):
            changes = {item['field']: item['proposed'] for item in items}
            count = place_model.objects.filter(pk=pk).update(**changes)
            if count != 1:
                raise ValueError(f'Record {pk} update failed; transaction rolled back.')
        # Verify results before committing the transaction.
        actual = {p.pk: p for p in place_model.objects.filter(pk__in=grouped)}
        for pk, items in grouped.items():
            for item in items:
                if getattr(actual[pk], item['field']) != item['proposed']:
                    raise ValueError(f'Record {pk} did not persist the expected value; transaction rolled back.')
    return len(plan), len(grouped)


def check_dump(path, expected_tables):
    """Check completion marker, SHA-256 and each base table definition.

    This checks the dump file, not that a restore has been tested.
    """
    if not path.is_file():
        raise ValueError('Database dump file missing.')
    digest = hashlib.sha256()
    tables = set()
    completed = False
    total = 0
    pattern = re.compile(rb'^CREATE TABLE `(.*?)`', re.IGNORECASE)
    with path.open('rb') as f:
        for line in f:
            digest.update(line)
            total += len(line)
            match = pattern.match(line)
            if match:
                tables.add(match.group(1).decode('utf-8'))
            if line.startswith(b'-- Dump completed on '):
                completed = True
    if not total or not completed or not expected_tables or not set(expected_tables) <= tables:
        raise ValueError('Database dump incomplete or missing tables; no changes made.')
    # Re-read independently to detect file changes during verification.
    digest2 = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest2.update(chunk)
    if digest.hexdigest() != digest2.hexdigest():
        raise ValueError('Database dump changed during verification; no changes made.')
    return digest.hexdigest(), total


def backup_database(db, connection, backup_root, dump_exe=DUMP_EXE):
    if not dump_exe.is_file():
        raise ValueError('XAMPP mysqldump.exe not found; no changes made.')
    with connection.cursor() as cursor:
        cursor.execute('SHOW FULL TABLES')
        expected_tables = {name for name, kind in cursor.fetchall() if kind.upper() == 'BASE TABLE'}
        cursor.execute("SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s", [db['NAME'], 'explore_places'])
        engine = cursor.fetchone()
    if not engine or str(engine[0]).lower() != 'innodb':
        raise ValueError('Place table is not InnoDB; cannot guarantee atomic updates. No changes made.')
    folder = backup_root / ('EK_db_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    folder.mkdir(parents=True, exist_ok=False)
    dump = folder / 'exploreanywhere.sql'
    args = [str(dump_exe), '--host=127.0.0.1', '--port=' + str(db.get('PORT') or '3306'),
            '--user=' + str(db['USER']), '--single-transaction', '--quick', '--routines', '--triggers',
            '--default-character-set=utf8mb4', '--result-file=' + str(dump), '--databases', 'exploreanywhere']
    env = os.environ.copy()
    if db.get('PASSWORD'):
        env['MYSQL_PWD'] = str(db['PASSWORD'])
    else:
        env.pop('MYSQL_PWD', None)
    print('Creating fresh database backup in', folder, flush=True)
    result = subprocess.run(args, env=env, capture_output=True, timeout=300, check=False)
    if result.returncode != 0:
        # Avoid printing subprocess output, which might contain sensitive details.
        raise ValueError(f'Database dump failed (exit {result.returncode}); no changes made. Backup folder: {folder}')
    sha, size = check_dump(dump, expected_tables)
    (folder / 'backup_manifest.json').write_text(json.dumps({'file': dump.name, 'sha256': sha, 'bytes': size,
        'base_table_count': len(expected_tables), 'restore_tested': False}, indent=2), encoding='utf-8')
    return folder, dump, sha


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file():
        raise SystemExit('STOP: open PowerShell in the project folder containing manage.py.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    import django
    django.setup()
    from django.conf import settings
    from django.db import connection
    from apps.places.models import Place
    db = settings.DATABASES['default']
    if (db['ENGINE'] != 'django.db.backends.mysql' or db['NAME'] != 'exploreanywhere'
            or str(db.get('HOST', '')).lower() not in ('localhost', '127.0.0.1', '::1')):
        raise ValueError('Expected local MySQL/MariaDB exploreanywhere; no changes made.')
    if len(APPROVED_PLAN) != 29 or len(plan_group(APPROVED_PLAN)) != 23:
        raise ValueError('Unexpected plan length; no changes made.')
    initial = {p.pk: p for p in Place.objects.filter(pk__in=plan_group(APPROVED_PLAN))}
    validate_places(initial, APPROVED_PLAN)
    print('Approved plan: 29 fields on 23 existing places. No other fields will change.')
    for item in APPROVED_PLAN:
        print(f'{item["id"]} {item["title"]} | {item["field"]} | {item["expected"] or "(blank)"} -> {item["proposed"]}')
    print('Stop Django and other database writers first. Keep XAMPP MySQL running.')
    print('A fresh database dump will be checked and kept privately; a restore is not tested.')
    if input('Type APPLY 29 to continue, or press Enter to cancel: ').strip() != 'APPLY 29':
        print('Cancelled. No changes made.')
        return
    folder, dump, sha = backup_database(db, connection, Path.home())
    print('Backup created:', dump)
    print('Backup SHA-256:', sha)
    print('Dump checked for completion and table definitions; restore not tested.')
    # The journal is written before the transaction so it survives any failure.
    journal = folder / 'approved_changes.json'
    journal.write_text(json.dumps(APPROVED_PLAN, ensure_ascii=False, indent=2), encoding='utf-8')
    changed_fields, changed_places = apply_plan(Place, APPROVED_PLAN)
    print('SUCCESS:', changed_fields, 'fields updated across', changed_places, 'places.')
    print('Backup and approved changes journal:', folder)
    print('No other fields, place records, media or publication flags were changed.')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('STOPPED:', exc)
        print('Keep any backup private. If SUCCESS was not printed, check the current data before retrying.')
        raise SystemExit(1)
