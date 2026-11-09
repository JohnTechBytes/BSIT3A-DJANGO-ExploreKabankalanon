"""Safety checks for the approved, backup-gated laptop update."""
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch, Mock

from django.db.models.query import QuerySet
from django.test import TestCase

from apps.cities.models import City
from apps.places.models import Place
from tools.visitor_updates.apply_first_visitor_changes import (
    APPROVED_PLAN, apply_plan, backup_database, check_dump, plan_group, validate_places,
)


class ApprovedVisitorUpdateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        grouped = plan_group(APPROVED_PLAN)
        for pk, items in grouped.items():
            item = items[0]
            place = Place.objects.create(pk=pk, city=city, title=item['title'], slug=item['slug'],
                                         address='Address not independently verified',
                                         phone='', email='', website='', barangay='',
                                         is_active=True, is_verified=True)
            # Unselected fields are deliberately nonempty to test preservation.
            selected = {x['field'] for x in items}
            if 'phone' not in selected:
                place.phone = 'preserve existing'
            if 'email' not in selected:
                place.email = 'preserve@example.com'
            place.save()

    def test_exact_approved_fields_update_and_others_are_preserved(self):
        self.assertEqual((len(APPROVED_PLAN), len(plan_group(APPROVED_PLAN))), (29, 23))
        before = {p.pk: (p.phone, p.email, p.category_id, p.is_verified) for p in Place.objects.all()}
        self.assertEqual(apply_plan(Place, APPROVED_PLAN), (29, 23))
        grouped = plan_group(APPROVED_PLAN)
        for p in Place.objects.all():
            selected = {x['field'] for x in grouped[p.pk]}
            for item in grouped[p.pk]:
                self.assertEqual(getattr(p, item['field']), item['proposed'])
            old_phone, old_email, old_category, old_verified = before[p.pk]
            if 'phone' not in selected:
                self.assertEqual(p.phone, old_phone)
            if 'email' not in selected:
                self.assertEqual(p.email, old_email)
            self.assertEqual((p.category_id, p.is_verified), (old_category, old_verified))

    def test_changed_field_or_identity_stops_everything(self):
        item = APPROVED_PLAN[0]
        place = Place.objects.get(pk=item['id'])
        setattr(place, item['field'], 'changed since review')
        place.save()
        with self.assertRaisesRegex(ValueError, 'changed since preview'):
            apply_plan(Place, APPROVED_PLAN)
        self.assertEqual(Place.objects.get(pk=item['id']).__getattribute__(item['field']), 'changed since review')
        for other in APPROVED_PLAN[1:]:
            if (other['id'], other['field']) != (item['id'], item['field']):
                self.assertEqual(getattr(Place.objects.get(pk=other['id']), other['field']), other['expected'])
        place.refresh_from_db()
        setattr(place, item['field'], item['expected'])
        place.slug = 'osm-node-mismatch'
        place.save()
        with self.assertRaisesRegex(ValueError, 'identity changed'):
            apply_plan(Place, APPROVED_PLAN)

    def test_failure_after_first_update_rolls_back(self):
        original = QuerySet.update
        calls = []
        def update_or_fail(queryset, **kwargs):
            calls.append(kwargs)
            if len(calls) == 2:
                raise ValueError('simulated failure')
            return original(queryset, **kwargs)
        with patch.object(QuerySet, 'update', update_or_fail):
            with self.assertRaisesRegex(ValueError, 'simulated failure'):
                apply_plan(Place, APPROVED_PLAN)
        self.assertEqual(len(calls), 2)
        for item in APPROVED_PLAN:
            self.assertEqual(getattr(Place.objects.get(pk=item['id']), item['field']), item['expected'])

    def test_dump_requires_completion_and_each_base_table(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / 'dump.sql'
            path.write_bytes(b'-- MariaDB dump\nCREATE TABLE `explore_places` (x INT);\n-- Dump completed on 2026-11-06\n')
            digest, length = check_dump(path, {'explore_places'})
            self.assertEqual(len(digest), 64)
            self.assertEqual(length, path.stat().st_size)
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                check_dump(path, {'explore_places', 'another_table'})
            path.write_bytes(b'CREATE TABLE `explore_places` (x INT);\n')
            with self.assertRaisesRegex(ValueError, 'incomplete'):
                check_dump(path, {'explore_places'})

    def test_backup_uses_settings_credentials_without_command_line_password(self):
        cursor = MagicMock()
        cursor.fetchall.return_value = [('explore_places', 'BASE TABLE')]
        cursor.fetchone.return_value = ('InnoDB',)
        conn = MagicMock()
        conn.cursor.return_value.__enter__.return_value = cursor
        db = {'NAME': 'exploreanywhere', 'USER': 'root', 'PASSWORD': 'test-secret', 'PORT': '3306'}
        with TemporaryDirectory() as temp:
            root = Path(temp)
            exe = root / 'mysqldump.exe'
            exe.touch()
            def fake_dump(args, **kwargs):
                self.assertFalse(any('test-secret' in value for value in args))
                self.assertEqual(kwargs['env']['MYSQL_PWD'], 'test-secret')
                output = next(a.split('=', 1)[1] for a in args if a.startswith('--result-file='))
                Path(output).write_bytes(b'CREATE TABLE `explore_places` (x INT);\n-- Dump completed on today\n')
                return Mock(returncode=0)
            with patch('tools.visitor_updates.apply_first_visitor_changes.subprocess.run', side_effect=fake_dump):
                folder, path, digest = backup_database(db, conn, root, exe)
            self.assertTrue(path.is_file())
            self.assertEqual(len(digest), 64)
            self.assertNotIn('test-secret', (folder / 'backup_manifest.json').read_text())

    def test_duplicate_or_nonblank_expected_values_rejected(self):
        with self.assertRaises(ValueError):
            plan_group(APPROVED_PLAN + [APPROVED_PLAN[0]])
        invalid = dict(APPROVED_PLAN[0], expected='already set')
        with self.assertRaises(ValueError):
            plan_group([invalid])
