"""Offline installer tests using disposable project files only."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
NAME = 'templates/info/city_information.html'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


u = load('city_filter_updater', 'tools/city_info_filters_update/apply_city_info_filters.py')
old = load('city_button_updater', 'tools/city_info_buttons_update/apply_city_info_buttons.py')
compat = load('design_compat', 'tools/clean_design_compat/apply_compat.py')


class CityFilterInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('')
        self.template = self.root / NAME
        self.template.parent.mkdir(parents=True)
        (self.root / 'db.sqlite3').write_bytes(b'database unchanged')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'media unchanged')

    def test_both_reviewed_pc_versions_preserve_data_and_backup(self):
        # Both the original design template and the previous one-row update are
        # accepted, regardless of which the visitor actually installed.
        for reviewed in (compat.download(NAME), old.download(NAME)):
            with self.subTest(old_hash=u.digest(reviewed)):
                original = reviewed.replace(b'\n', b'\r\n')
                self.template.write_bytes(original)
                backup = u.apply(self.root, self.base)
                self.assertEqual((backup / NAME).read_bytes(), original)
                self.assertEqual(self.template.read_bytes(), (ROOT / NAME).read_bytes())
                self.assertNotIn(b'aria-label="City guide types"', self.template.read_bytes())
                self.assertNotIn(b'aria-label="Explore city information by category"', self.template.read_bytes())
                self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database unchanged')
                self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media unchanged')
                self.assertIsNone(u.apply(self.root, self.base))

    def test_incompatible_or_corrupt_payload_stops_before_writing(self):
        changed = compat.download(NAME) + b'\nlocal edits'
        self.template.write_bytes(changed)
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            u.apply(self.root, self.base)
        self.assertEqual(self.template.read_bytes(), changed)
        self.template.write_bytes(old.download(NAME))
        before = self.template.read_bytes()
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'invalid payload')
        self.assertEqual(self.template.read_bytes(), before)

    def test_failure_keeps_original_and_backup(self):
        original = compat.download(NAME)
        self.template.write_bytes(original)
        with patch.object(u.os, 'replace', side_effect=OSError('simulated failure')):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.base)
        self.assertEqual(self.template.read_bytes(), original)
        backups = list(self.base.glob('EK_code_backup_city_info_filters_*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / NAME).read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
