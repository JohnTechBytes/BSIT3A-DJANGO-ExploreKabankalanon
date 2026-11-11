"""Isolated tests of the laptop code-only updater; no live DB or media."""
import importlib.util
from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('nearby_updater', ROOT / 'tools/nearby_update/apply_nearby_update.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class NearbyUpdaterTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('# project')
        # Real post-update files stand in for an already updated installation;
        # the tests below patch the manifest with small known old/new bytes.
        for name in ('apps/places/sample_images.py', 'apps/places/templatetags/attraction_photos.py',
                     'static/js/place-photo-fallback.js', 'static/img/samples/generic.jpg'):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / name).read_bytes())
        self.name = 'apps/places/nearby.py'
        self.path = self.root / self.name
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(b'old code')
        self.files = {self.name: (updater.digest(b'old code'), updater.digest(b'new code'))}
        self.media = self.root / 'media' / 'photo.jpg'
        self.media.parent.mkdir()
        self.media.write_bytes(b'private photo')
        self.db = self.root / 'database.sqlite3'
        self.db.write_bytes(b'private database')

    def test_backup_update_and_idempotence_without_touching_data(self):
        backup = updater.apply(self.root, Path(self.temp.name), self.files, lambda _: b'new code')
        self.assertEqual((backup / self.name).read_bytes(), b'old code')
        self.assertEqual(self.path.read_bytes(), b'new code')
        self.assertEqual(self.media.read_bytes(), b'private photo')
        self.assertEqual(self.db.read_bytes(), b'private database')
        self.assertIsNone(updater.apply(self.root, Path(self.temp.name), self.files, lambda _: b'bad'))

    def test_modified_code_or_wrong_download_never_overwrites(self):
        self.path.write_bytes(b'custom')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            updater.apply(self.root, Path(self.temp.name), self.files, lambda _: b'new code')
        self.assertEqual(self.path.read_bytes(), b'custom')
        self.path.write_bytes(b'old code')
        with self.assertRaisesRegex(ValueError, 'download hash mismatch'):
            updater.apply(self.root, Path(self.temp.name), self.files, lambda _: b'corrupt')
        self.assertEqual(self.path.read_bytes(), b'old code')

    def test_missing_illustration_prerequisite_stops_before_download(self):
        (self.root / 'static/img/samples/generic.jpg').unlink()
        with self.assertRaisesRegex(ValueError, 'prerequisite'):
            updater.apply(self.root, Path(self.temp.name), self.files, lambda _: self.fail('downloaded'))
        self.assertEqual(self.path.read_bytes(), b'old code')

    def test_local_change_during_download_is_not_overwritten(self):
        def download(_):
            self.path.write_bytes(b'concurrent edit')
            return b'new code'
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            updater.apply(self.root, Path(self.temp.name), self.files, download)
        self.assertEqual(self.path.read_bytes(), b'concurrent edit')
