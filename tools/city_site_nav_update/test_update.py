"""Site navigation installer tests; only disposable local files are used."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = 'templates/info/city_information.html'
VIEW = 'apps/info/views.py'
spec = importlib.util.spec_from_file_location('city_site_nav', ROOT / 'tools/city_site_nav_update/apply_city_nav.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class SiteNavInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_bytes(b'')
        for name in (TEMPLATE, VIEW):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(subprocess.check_output(['git', 'show', '8a30837:' + name], cwd=ROOT).replace(b'\n', b'\r\n'))
        (self.root / 'db.sqlite3').write_bytes(b'keep database')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'keep media')

    def test_install_back_up_and_idempotence(self):
        old = (self.root / TEMPLATE).read_bytes()
        view = (self.root / VIEW).read_bytes()
        backup = u.apply(self.root, self.base)
        self.assertEqual((backup / TEMPLATE).read_bytes(), old)
        self.assertEqual((self.root / TEMPLATE).read_bytes(), (ROOT / TEMPLATE).read_bytes())
        self.assertEqual((self.root / VIEW).read_bytes(), view)
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'keep database')
        self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'keep media')
        self.assertIsNone(u.apply(self.root, self.base))

    def test_modified_files_or_invalid_payload_stop_without_changes(self):
        for name in (TEMPLATE, VIEW):
            path = self.root / name
            old = path.read_bytes()
            path.write_bytes(old + b'\nlocal changes')
            with self.assertRaises(ValueError):
                u.apply(self.root, self.base)
            self.assertEqual(path.read_bytes(), old + b'\nlocal changes')
            path.write_bytes(old)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'bad')

    def test_failed_post_write_verification_restores_template(self):
        path = self.root / TEMPLATE
        original = path.read_bytes()
        real_digest = u.digest
        calls = 0
        def digest(data):
            nonlocal calls
            # Corrupt just the first verification after replacement; rollback
            # then recognizes the installed payload and restores the original.
            if data == (ROOT / TEMPLATE).read_bytes():
                calls += 1
                if calls == 2:
                    return 'failed verification'
            return real_digest(data)
        with patch.object(u, 'digest', side_effect=digest):
            with self.assertRaisesRegex(ValueError, 'installed file failed verification'):
                u.apply(self.root, self.base)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(len(list(self.base.glob('EK_code_backup_city_site_nav_*'))), 1)


if __name__ == '__main__':
    unittest.main()
