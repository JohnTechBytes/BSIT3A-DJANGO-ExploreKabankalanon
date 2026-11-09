"""Isolated checks of the laptop-specific homepage updater."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('reviewed_homepage_update', ROOT / 'tools/homepage_update/apply_reviewed_homepage.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class ReviewedHomepageUpdateTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        (self.root / 'templates').mkdir(parents=True)
        (self.root / 'static/css').mkdir(parents=True)
        (self.root / 'manage.py').write_text('')
        (self.root / 'templates/home.html').write_bytes(b'old')
        (self.root / 'static/css/explore.css').write_bytes(b'reviewed')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo').write_bytes(b'private')
        (self.root / 'db.sqlite3').write_bytes(b'data')
        self.manifest = {'templates/home.html': (updater.digest(b'old'), updater.digest(b'new')),
                         'static/css/homepage-pilot.css': (None, updater.digest(b'css'))}
        self.data = {'templates/home.html': b'new', 'static/css/homepage-pilot.css': b'css'}
        self.guard = patch.object(updater, 'PREREQUISITES', {'static/css/explore.css': updater.digest(b'reviewed')})
        self.guard.start()
        self.addCleanup(self.guard.stop)

    def test_backup_install_and_no_data_changes(self):
        backup = updater.apply(self.root, Path(self.temp.name), self.manifest, self.data.get)
        self.assertEqual((backup / 'templates/home.html').read_bytes(), b'old')
        self.assertEqual((self.root / 'templates/home.html').read_bytes(), b'new')
        self.assertEqual((self.root / 'static/css/explore.css').read_bytes(), b'reviewed')
        self.assertEqual((self.root / 'static/css/homepage-pilot.css').read_bytes(), b'css')
        self.assertEqual((self.root / 'media/photo').read_bytes(), b'private')
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'data')
        self.assertIsNone(updater.apply(self.root, Path(self.temp.name), self.manifest, self.data.get))

    def test_unreviewed_shared_css_or_template_stops(self):
        path = self.root / 'static/css/explore.css'
        path.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'reviewed stylesheet changed'):
            updater.apply(self.root, Path(self.temp.name), self.manifest, self.data.get)
        path.write_bytes(b'reviewed')
        (self.root / 'templates/home.html').write_bytes(b'user edits')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            updater.apply(self.root, Path(self.temp.name), self.manifest, self.data.get)
        self.assertFalse((self.root / 'static/css/homepage-pilot.css').exists())

    def test_shared_css_change_during_download_stops_before_writes(self):
        def download(name):
            (self.root / 'static/css/explore.css').write_bytes(b'changed')
            return self.data[name]
        with self.assertRaisesRegex(ValueError, 'reviewed stylesheet changed'):
            updater.apply(self.root, Path(self.temp.name), self.manifest, download)
        self.assertEqual((self.root / 'templates/home.html').read_bytes(), b'old')
        self.assertFalse((self.root / 'static/css/homepage-pilot.css').exists())
