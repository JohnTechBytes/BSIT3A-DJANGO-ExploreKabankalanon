"""City-section installer tests on disposable files."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = 'templates/info/city_information.html'
VIEW = 'apps/info/views.py'
spec = importlib.util.spec_from_file_location('city_sections_update', ROOT / 'tools/city_sections_update/apply_city_sections.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class CitySectionsInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_bytes(b'')
        for name in (TEMPLATE, VIEW):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        self.view = subprocess.check_output(['git', 'show', 'e647830:' + VIEW], cwd=ROOT)
        (self.root / VIEW).write_bytes(self.view)
        (self.root / 'db.sqlite3').write_bytes(b'database untouched')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'media untouched')

    def old_template(self, revision):
        data = subprocess.check_output(['git', 'show', revision + ':' + TEMPLATE], cwd=ROOT)
        (self.root / TEMPLATE).write_bytes(data.replace(b'\n', b'\r\n'))
        return (self.root / TEMPLATE).read_bytes()

    def test_all_reviewed_versions_install_without_touching_data(self):
        for revision in ('8a30837', '378e922', 'd80ec22'):
            with self.subTest(revision=revision):
                old = self.old_template(revision)
                backup = u.apply(self.root, self.base)
                self.assertEqual((backup / TEMPLATE).read_bytes(), old)
                self.assertEqual((self.root / TEMPLATE).read_bytes(), u.download(TEMPLATE))
                self.assertEqual((self.root / VIEW).read_bytes(), self.view)
                self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database untouched')
                self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media untouched')
                self.assertIsNone(u.apply(self.root, self.base))

    def test_changed_prerequisite_and_template_and_bad_payload_stop(self):
        old = self.old_template('8a30837')
        for name in (TEMPLATE, VIEW):
            path = self.root / name
            data = path.read_bytes()
            path.write_bytes(data + b'\nlocal change')
            with self.assertRaises(ValueError):
                u.apply(self.root, self.base)
            self.assertEqual(path.read_bytes(), data + b'\nlocal change')
            path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'bad')
        self.assertEqual((self.root / TEMPLATE).read_bytes(), old)

    def test_failed_verification_rolls_back(self):
        old = self.old_template('378e922')
        real = u.digest
        calls = 0
        def digest(data):
            nonlocal calls
            if data == u.download(TEMPLATE):
                calls += 1
                if calls == 2:
                    return 'failure'
            return real(data)
        with patch.object(u, 'digest', side_effect=digest):
            with self.assertRaisesRegex(ValueError, 'installed file failed verification'):
                u.apply(self.root, self.base)
        self.assertEqual((self.root / TEMPLATE).read_bytes(), old)
        self.assertEqual(len(list(self.base.glob('EK_code_backup_city_sections_*'))), 1)


if __name__ == '__main__':
    unittest.main()
