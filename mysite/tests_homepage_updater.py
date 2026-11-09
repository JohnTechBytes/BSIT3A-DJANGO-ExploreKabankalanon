"""Safe code-only ZIP installer tests, using temporary project files."""
import importlib.util
from pathlib import Path
import tempfile
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('homepage_updater', ROOT / 'tools/homepage_update/apply_homepage_pilot.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class HomepageUpdaterTests(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('# test')
        self.home = self.root / 'templates/home.html'
        self.home.parent.mkdir()
        self.home.write_bytes(b'old')
        self.css = self.root / 'static/css/homepage-pilot.css'
        self.files = {'templates/home.html': (updater.digest(b'old'), updater.digest(b'new')),
                      'static/css/homepage-pilot.css': (None, updater.digest(b'css'))}
        self.data = {'templates/home.html': b'new', 'static/css/homepage-pilot.css': b'css'}
        self.media = self.root / 'media/photo.jpg'
        self.media.parent.mkdir()
        self.media.write_bytes(b'photo')
        self.db = self.root / 'db.sqlite3'
        self.db.write_bytes(b'database')

    def test_apply_backs_up_and_never_touches_user_data(self):
        backup = updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((backup / 'templates/home.html').read_bytes(), b'old')
        self.assertEqual(self.home.read_bytes(), b'new')
        self.assertEqual(self.css.read_bytes(), b'css')
        self.assertEqual(self.media.read_bytes(), b'photo')
        self.assertEqual(self.db.read_bytes(), b'database')
        self.assertIsNone(updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get))

    def test_unknown_local_file_and_wrong_download_stop_before_changes(self):
        self.home.write_bytes(b'custom')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual(self.home.read_bytes(), b'custom')
        self.home.write_bytes(b'old')
        with self.assertRaisesRegex(ValueError, 'download hash mismatch'):
            updater.apply(self.root, Path(self.tmp.name), self.files, lambda _: b'bad')
        self.assertEqual(self.home.read_bytes(), b'old')
        self.assertFalse(self.css.exists())

    def test_new_stylesheet_collision_is_not_overwritten(self):
        self.css.parent.mkdir(parents=True)
        self.css.write_bytes(b'user stylesheet')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual(self.css.read_bytes(), b'user stylesheet')
        self.assertEqual(self.home.read_bytes(), b'old')
