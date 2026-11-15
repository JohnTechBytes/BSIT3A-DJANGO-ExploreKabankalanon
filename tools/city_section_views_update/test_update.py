"""Installer guard and rollback tests using temporary files only."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VIEW = 'apps/info/views.py'
TEMPLATE = 'templates/info/city_information.html'
spec = importlib.util.spec_from_file_location('city_section_views', ROOT / 'tools/city_section_views_update/apply_city_views.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class CityViewsInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_bytes(b'')
        for name in (VIEW, TEMPLATE):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        (self.root / 'db.sqlite3').write_bytes(b'database untouched')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'media untouched')

    def baseline(self, revision):
        originals = {}
        for name in (VIEW, TEMPLATE):
            data = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)
            originals[name] = data.replace(b'\n', b'\r\n')
            (self.root / name).write_bytes(originals[name])
        return originals

    def test_all_reviewed_versions_keep_database_and_media(self):
        for revision in ('8a30837', '378e922', 'd80ec22', 'bb8ee6a'):
            with self.subTest(revision=revision):
                originals = self.baseline(revision)
                backup = u.apply(self.root, self.base)
                for name, original in originals.items():
                    self.assertEqual((backup / name).read_bytes(), original)
                    self.assertEqual((self.root / name).read_bytes(), u.download(name))
                self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database untouched')
                self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media untouched')
                self.assertIsNone(u.apply(self.root, self.base))

    def test_unexpected_file_and_bad_payload_stop_safely(self):
        originals = self.baseline('bb8ee6a')
        for name in (VIEW, TEMPLATE):
            path = self.root / name
            path.write_bytes(originals[name] + b'\nlocal change')
            with self.assertRaisesRegex(ValueError, 'unexpected local version'):
                u.apply(self.root, self.base)
            self.assertEqual(path.read_bytes(), originals[name] + b'\nlocal change')
            path.write_bytes(originals[name])
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'bad')
        for name, original in originals.items():
            self.assertEqual((self.root / name).read_bytes(), original)

    def test_second_write_failure_rolls_back_first_and_keeps_backup(self):
        originals = self.baseline('bb8ee6a')
        real_replace = u.os.replace
        calls = 0
        def fail_second(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return real_replace(src, dst)
        with patch.object(u.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.base)
        backups = list(self.base.glob('EK_code_backup_city_section_views_*'))
        self.assertEqual(len(backups), 1)
        for name, original in originals.items():
            self.assertEqual((self.root / name).read_bytes(), original)
            self.assertEqual((backups[0] / name).read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
