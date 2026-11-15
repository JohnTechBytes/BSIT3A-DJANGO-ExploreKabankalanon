"""Test the template-only installer against disposable project copies."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
NAME = 'templates/info/city_information.html'
spec = importlib.util.spec_from_file_location('city_contrast_installer', ROOT / 'tools/city_contrast_fix/apply_city_contrast.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class CityContrastInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        (self.root / 'templates/info').mkdir(parents=True)
        (self.root / 'manage.py').write_text('')
        self.original = subprocess.check_output(['git', 'show', 'ddd35f8:' + NAME], cwd=ROOT).replace(b'\n', b'\r\n')
        (self.root / NAME).write_bytes(self.original)
        (self.root / 'db.sqlite3').write_bytes(b'untouched database')
        (self.root / 'media').mkdir()
        (self.root / 'media/test.jpg').write_bytes(b'untouched media')

    def test_install_backup_and_idempotency(self):
        backup = u.apply(self.root, self.base)
        self.assertEqual((backup / NAME).read_bytes(), self.original)
        self.assertEqual((self.root / NAME).read_bytes(), u.download(NAME))
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'untouched database')
        self.assertEqual((self.root / 'media/test.jpg').read_bytes(), b'untouched media')
        self.assertIsNone(u.apply(self.root, self.base))

    def test_unknown_template_and_bad_payload_are_not_overwritten(self):
        (self.root / NAME).write_bytes(self.original + b'local change')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            u.apply(self.root, self.base)
        self.assertEqual((self.root / NAME).read_bytes(), self.original + b'local change')
        (self.root / NAME).write_bytes(self.original)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'wrong')
        self.assertEqual((self.root / NAME).read_bytes(), self.original)

    def test_failed_atomic_replacement_preserves_original_and_backup(self):
        with patch.object(u.os, 'replace', side_effect=OSError('simulated failure')):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.base)
        self.assertEqual((self.root / NAME).read_bytes(), self.original)
        backups = list(self.base.glob('EK_code_backup_city_contrast_*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / NAME).read_bytes(), self.original)


if __name__ == '__main__':
    unittest.main()
