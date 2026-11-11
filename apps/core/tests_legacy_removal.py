"""Safety tests use fresh disposable databases only, never the user's dump."""
import importlib.util
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('clean_dump', ROOT / 'tools/database_cleanup/build_clean_copy.py')
clean_dump = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean_dump)


class DumpCleaningTests(TestCase):
    def sample(self):
        parts = [b'CREATE TABLE `django_migrations` (`id` INT);\n',
                 b"CREATE TABLE `explore_places` (`title` TEXT);\nINSERT INTO `explore_places` VALUES ('semi;colon and \\\'quote');\n"]
        for table in sorted(clean_dump.TARGETS):
            n = table.encode()
            parts += [b'CREATE TABLE `' + n + b'` (`id` INT);\n',
                      b'INSERT INTO `' + n + b'` VALUES (1);\n',
                      b'ALTER TABLE `' + n + b'` ADD PRIMARY KEY (`id`);\n']
        return b''.join(parts)

    def test_only_target_statements_are_removed_and_source_is_unchanged(self):
        source = self.sample()
        output, counts = clean_dump.build(source)
        self.assertEqual(len(counts), 9)
        self.assertIn(b"INSERT INTO `explore_places` VALUES ('semi;colon and \\\'quote');", output)
        for table in clean_dump.TARGETS:
            self.assertNotIn(b'CREATE TABLE `' + table.encode() + b'`', output)
        for _, migration in clean_dump.MIGRATIONS:
            self.assertIn(migration.encode(), output)
        self.assertIn(b'CREATE TABLE `dashboard_user_hobbies`', source)

    def test_missing_table_unexpected_operation_and_retained_fk_stop(self):
        source = self.sample()
        with self.assertRaises(ValueError):
            clean_dump.build(source.replace(b'CREATE TABLE `dashboard_user_hobbies`', b'CREATE TABLE `unknown`'))
        with self.assertRaises(ValueError):
            clean_dump.build(source + b'DROP TABLE `dashboard_user_hobbies`;')
        with self.assertRaises(ValueError):
            clean_dump.build(source + b'ALTER TABLE `other` ADD FOREIGN KEY (`x`) REFERENCES `explore_itineraries` (`id`);')


class RemovalMigrationTests(TestCase):
    def test_guard_stops_then_approved_migration_preserves_unrelated_tables(self):
        with TemporaryDirectory() as tmp:
            database = Path(tmp) / 'isolated.sqlite3'
            env = os.environ.copy()
            env.update(DJANGO_DB_ENGINE='django.db.backends.sqlite3', DJANGO_DB_NAME=str(database))
            env.pop('EK_APPROVE_LEGACY_REMOVAL', None)
            def manage(*args, env=env):
                return subprocess.run([sys.executable, 'manage.py', *args, '--noinput'], cwd=ROOT,
                                      env=env, capture_output=True, text=True, timeout=60)
            for target in [('itineraries', '0002'), ('visits', '0001')]:
                result = manage('migrate', *target)
                self.assertEqual(result.returncode, 0, result.stderr)
            with sqlite3.connect(database) as db:
                db.execute('PRAGMA foreign_keys=OFF')
                # Minimal representative legacy row; no real user data.
                db.execute('CREATE TABLE dashboard_user_hobbies (id integer primary key, user_id integer, hobby_id integer)')
                db.execute('INSERT INTO dashboard_user_hobbies VALUES (1, 1, 1)')
                db.execute('CREATE TABLE preserved_marker (value text)')
                db.execute("INSERT INTO preserved_marker VALUES ('keep')")
            failed = manage('migrate')
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('EK_APPROVE_LEGACY_REMOVAL=1', failed.stderr)
            with sqlite3.connect(database) as db:
                tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertIn('dashboard_user_hobbies', tables)
                self.assertIn('explore_itineraries', tables)
                self.assertIn('explore_visit_checkins', tables)
                self.assertEqual(db.execute('SELECT count(*) FROM dashboard_user_hobbies').fetchone()[0], 1)
            approved = env | {'EK_APPROVE_LEGACY_REMOVAL': '1'}
            result = manage('migrate', env=approved)
            self.assertEqual(result.returncode, 0, result.stderr)
            with sqlite3.connect(database) as db:
                tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertTrue(clean_dump.TARGETS.isdisjoint(tables))
                self.assertEqual(db.execute('SELECT value FROM preserved_marker').fetchone()[0], 'keep')
                self.assertIn('explore_places', tables)
                self.assertIn('explore_reviews', tables)
                self.assertIn('explore_saved_places', tables)
