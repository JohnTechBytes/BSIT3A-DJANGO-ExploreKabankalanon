"""Test the duplicate-nav fix against temporary files only."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = 'templates/info/city_information.html'
spec = importlib.util.spec_from_file_location('city_nav_fix', ROOT / 'tools/city_nav_fix/apply_city_nav_fix.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class CityNavFixTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_bytes(b'')
        self.template = self.root / TEMPLATE
        self.template.parent.mkdir(parents=True, exist_ok=True)
        data = subprocess.check_output(['git', 'show', '378e922:' + TEMPLATE], cwd=ROOT)
        self.template.write_bytes(data.replace(b'\n', b'\r\n'))
        (self.root / 'db.sqlite3').write_bytes(b'database untouched')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'media untouched')
        self.header = self.root / 'templates/theme/public_base.html'
        self.header.parent.mkdir(parents=True, exist_ok=True)
        self.header.write_bytes(b'public header unchanged')

    def test_install_backs_up_and_keeps_everything_else(self):
        old = self.template.read_bytes()
        backup = u.apply(self.root, self.base)
        self.assertEqual((backup / TEMPLATE).read_bytes(), old)
        self.assertEqual(self.template.read_bytes(), u.download(TEMPLATE))
        self.assertEqual(self.header.read_bytes(), b'public header unchanged')
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database untouched')
        self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media untouched')
        self.assertIsNone(u.apply(self.root, self.base))

    def test_unexpected_version_and_bad_payload_fail_safely(self):
        old = self.template.read_bytes()
        self.template.write_bytes(old + b'\nlocal change')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            u.apply(self.root, self.base)
        self.assertEqual(self.template.read_bytes(), old + b'\nlocal change')
        self.template.write_bytes(old)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'bad')
        self.assertEqual(self.template.read_bytes(), old)

    def test_failed_verification_rolls_back(self):
        old = self.template.read_bytes()
        original_digest = u.digest
        count = 0
        def digest(data):
            nonlocal count
            if data == u.download(TEMPLATE):
                count += 1
                if count == 2:
                    return 'bad'
            return original_digest(data)
        with patch.object(u, 'digest', side_effect=digest):
            with self.assertRaisesRegex(ValueError, 'installed file failed verification'):
                u.apply(self.root, self.base)
        self.assertEqual(self.template.read_bytes(), old)
        self.assertEqual(len(list(self.base.glob('EK_code_backup_city_nav_fix_*'))), 1)


if __name__ == '__main__':
    unittest.main()
