"""ZIP installer safety checks without real database, media, or network."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('modern_homepage_update', ROOT / 'tools/homepage_update/apply_modern_homepage.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class ModernHomepageUpdaterTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        (self.root / 'templates').mkdir(parents=True)
        (self.root / 'static/css').mkdir(parents=True)
        (self.root / 'manage.py').write_text('')
        (self.root / 'static/css/explore.css').write_bytes(b'reviewed')
        (self.root / 'templates/home.html').write_bytes(b'original')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo').write_bytes(b'photo')
        (self.root / 'db.sqlite3').write_bytes(b'db')
        self.data = {'templates/home.html': b'new', 'static/css/homepage-pilot.css': b'newcss'}
        self.files = {'templates/home.html': ((updater.digest(b'original'), updater.digest(b'forest')), updater.digest(b'new')),
                      'static/css/homepage-pilot.css': ((None, updater.digest(b'forestcss')), updater.digest(b'newcss'))}
        guards = {'static/css/explore.css': updater.digest(b'reviewed')}
        pairs = {(updater.digest(b'original'), None), (updater.digest(b'forest'), updater.digest(b'forestcss')),
                 (updater.digest(b'new'), updater.digest(b'newcss'))}
        for name, value in [('PREREQUISITES', guards), ('VALID_PAIRS', pairs)]:
            p = patch.object(updater, name, value)
            p.start()
            self.addCleanup(p.stop)

    def test_apply_original_and_repeat_without_data_changes(self):
        backup = updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((backup / 'templates/home.html').read_bytes(), b'original')
        self.assertEqual((self.root / 'static/css/homepage-pilot.css').read_bytes(), b'newcss')
        self.assertEqual((self.root / 'static/css/explore.css').read_bytes(), b'reviewed')
        self.assertEqual((self.root / 'media/photo').read_bytes(), b'photo')
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'db')
        self.assertIsNone(updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get))

    def test_forest_pair_is_backed_up(self):
        (self.root / 'templates/home.html').write_bytes(b'forest')
        (self.root / 'static/css/homepage-pilot.css').write_bytes(b'forestcss')
        backup = updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((backup / 'templates/home.html').read_bytes(), b'forest')
        self.assertEqual((backup / 'static/css/homepage-pilot.css').read_bytes(), b'forestcss')

    def test_mismatched_pair_and_changed_stylesheet_stop(self):
        (self.root / 'static/css/homepage-pilot.css').write_bytes(b'forestcss')
        with self.assertRaisesRegex(ValueError, 'versions do not match'):
            updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        (self.root / 'static/css/homepage-pilot.css').unlink()
        (self.root / 'static/css/explore.css').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'stylesheet changed'):
            updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((self.root / 'templates/home.html').read_bytes(), b'original')

    def test_bad_download_stops_before_writing(self):
        with self.assertRaisesRegex(ValueError, 'download hash mismatch'):
            updater.apply(self.root, Path(self.tmp.name), self.files, lambda _: b'wrong')
        self.assertEqual((self.root / 'templates/home.html').read_bytes(), b'original')
        self.assertFalse((self.root / 'static/css/homepage-pilot.css').exists())
