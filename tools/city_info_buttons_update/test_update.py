"""Offline, disposable-project tests for the City Information button update."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


u = load('city_button_updater', 'tools/city_info_buttons_update/apply_city_info_buttons.py')
c = load('design_compat', 'tools/clean_design_compat/apply_compat.py')
NAME = 'templates/info/city_information.html'


class CityButtonInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'project'
        self.project.mkdir()
        (self.project / 'manage.py').write_text('')
        self.template = self.project / NAME
        self.template.parent.mkdir(parents=True)
        self.template.write_bytes(c.download(NAME))
        self.db = self.project / 'db.sqlite3'
        self.db.write_bytes(b'database untouched')
        self.media = self.project / 'media' / 'photo.jpg'
        self.media.parent.mkdir()
        self.media.write_bytes(b'media untouched')

    def test_verified_update_backup_preservation_and_repeat(self):
        old = self.template.read_bytes().replace(b'\n', b'\r\n')
        self.template.write_bytes(old)
        backup = u.apply(self.project, self.base)
        self.assertEqual((backup / NAME).read_bytes(), old)
        self.assertEqual(self.template.read_bytes(), (ROOT / NAME).read_bytes())
        self.assertEqual(self.db.read_bytes(), b'database untouched')
        self.assertEqual(self.media.read_bytes(), b'media untouched')
        self.assertEqual({p.relative_to(backup).as_posix() for p in backup.rglob('*') if p.is_file()},
                         {NAME, 'manifest.json'})
        self.assertIsNone(u.apply(self.project, self.base))

    def test_unknown_template_or_bad_payload_stops_before_writing(self):
        before = self.template.read_bytes() + b'\nlocal changes'
        self.template.write_bytes(before)
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            u.apply(self.project, self.base)
        self.assertEqual(self.template.read_bytes(), before)
        self.template.write_bytes(c.download(NAME))
        before = self.template.read_bytes()
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.project, self.base, downloader=lambda _: b'invalid payload')
        self.assertEqual(self.template.read_bytes(), before)

    def test_write_failure_keeps_original_and_backup(self):
        before = self.template.read_bytes()
        with patch.object(u.os, 'replace', side_effect=OSError('simulated failure')):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.project, self.base)
        self.assertEqual(self.template.read_bytes(), before)
        backups = list(self.base.glob('EK_code_backup_city_info_buttons_*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / NAME).read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
