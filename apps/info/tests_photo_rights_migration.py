"""Photo-rights schema compatibility is tested in disposable SQLite databases."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = r'''
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

mode = os.environ['PHOTO_MIGRATION_CASE']
before = ('info', '0004_cityinformation_photo_credit')
after = ('info', '0005_cityinformation_photo_rights_compat')
executor = MigrationExecutor(connection)
executor.migrate([before])
apps = executor.loader.project_state([before]).apps
City = apps.get_model('cities', 'City')
Guide = apps.get_model('info', 'CityInformation')
city = City.objects.create(name='Kabankalan', slug='kabankalan', province='Negros Occidental', latitude=0, longitude=0)
guide = Guide.objects.create(city=city, title='Existing guide', description='existing',
                             thumbnail_url='', photo_credit='Existing credit', is_published=True)
with connection.cursor() as cursor:
    if mode in ('full', 'partial', 'incompatible', 'extra'):
        length = 10 if mode == 'incompatible' else 100
        cursor.execute('ALTER TABLE explore_city_information ADD COLUMN photo_license varchar(%d) NOT NULL DEFAULT ""' % length)
        cursor.execute('UPDATE explore_city_information SET photo_license = %s WHERE id = %s', ['license', guide.pk])
    if mode == 'extra':
        cursor.execute('ALTER TABLE explore_city_information ADD COLUMN unreviewed_column varchar(20) NOT NULL DEFAULT "kept"')
    if mode == 'full':
        cursor.execute('ALTER TABLE explore_city_information ADD COLUMN photo_license_url varchar(1000) NOT NULL DEFAULT ""')
        cursor.execute('ALTER TABLE explore_city_information ADD COLUMN photo_source_url varchar(1000) NOT NULL DEFAULT ""')
        cursor.execute('UPDATE explore_city_information SET photo_license_url = %s, photo_source_url = %s WHERE id = %s',
                       ['https://example.com/license', 'https://example.com/source', guide.pk])
executor = MigrationExecutor(connection)
if mode in ('incompatible', 'extra'):
    try:
        executor.migrate([after])
        raise AssertionError('incompatible columns were accepted')
    except RuntimeError as exc:
        expected_error = 'incompatible definition' if mode == 'incompatible' else 'Unexpected extra columns'
        assert expected_error in str(exc), str(exc)
    with connection.cursor() as cursor:
        cursor.execute('SELECT photo_license, title FROM explore_city_information WHERE id = %s', [guide.pk])
        assert cursor.fetchone() == ('license', 'Existing guide')
        names = {col.name for col in connection.introspection.get_table_description(cursor, 'explore_city_information')}
        assert 'photo_license_url' not in names and 'photo_source_url' not in names
else:
    executor.migrate([after])
    with connection.cursor() as cursor:
        cursor.execute('SELECT photo_license, photo_license_url, photo_source_url, photo_credit FROM explore_city_information WHERE id = %s', [guide.pk])
        row = cursor.fetchone()
    expected = ('license' if mode in ('full', 'partial') else '',
                'https://example.com/license' if mode == 'full' else '',
                'https://example.com/source' if mode == 'full' else '', 'Existing credit')
    assert row == expected, (row, expected)
    from apps.info.models import CityInformation
    item = CityInformation.objects.get(pk=guide.pk)
    assert item.title == 'Existing guide' and item.is_published
    CityInformation.objects.create(city_id=city.pk, title='New event', info_type='event', description='x', is_published=True)
    print('PASS', mode)
'''


class PhotoRightsCompatibilityMigrationTests(SimpleTestCase):
    def test_existing_and_missing_columns_without_data_loss(self):
        for case in ('fresh', 'full', 'partial', 'incompatible', 'extra'):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                env = os.environ.copy()
                env.update(DJANGO_DB_ENGINE='django.db.backends.sqlite3',
                           DJANGO_DB_NAME=str(Path(directory) / 'isolated.sqlite3'),
                           DJANGO_SETTINGS_MODULE='mysite.settings', PHOTO_MIGRATION_CASE=case)
                result = subprocess.run([sys.executable, '-c', PROGRAM], cwd=ROOT, env=env,
                                        capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 0, result.stdout + '\n' + result.stderr)
