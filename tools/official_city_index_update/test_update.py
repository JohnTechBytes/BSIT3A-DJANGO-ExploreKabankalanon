"""Exercise the installer only in disposable project directories."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VIEW = 'apps/info/views.py'
TEMPLATE = 'templates/info/city_information.html'
NEW_FILES = ('apps/info/official_index.py', 'apps/info/data/official_sitemap_snapshot.json')
spec = importlib.util.spec_from_file_location('official_index_installer', ROOT / 'tools/official_city_index_update/apply_official_index.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class OfficialIndexInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('')
        for name in (VIEW, TEMPLATE):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        (self.root / 'db.sqlite3').write_bytes(b'db unchanged')
        (self.root / 'media').mkdir()
        (self.root / 'media/image.jpg').write_bytes(b'photo unchanged')

    def baseline(self, revision):
        originals = {}
        for name in (VIEW, TEMPLATE):
            data = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)
            originals[name] = data.replace(b'\n', b'\r\n')
            (self.root / name).write_bytes(originals[name])
        for name in NEW_FILES:
            (self.root / name).unlink(missing_ok=True)
        return originals

    def test_prior_reviewed_versions_and_idempotency(self):
        for revision in ('8a30837', '378e922', 'd80ec22', 'bb8ee6a', '24bc9ff'):
            with self.subTest(revision=revision):
                originals = self.baseline(revision)
                backup = u.apply(self.root, self.base)
                for name, data in originals.items():
                    self.assertEqual((backup / name).read_bytes(), data)
                for name in u.FILES:
                    self.assertEqual((self.root / name).read_bytes(), u.download(name))
                self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'db unchanged')
                self.assertEqual((self.root / 'media/image.jpg').read_bytes(), b'photo unchanged')
                self.assertIsNone(u.apply(self.root, self.base))

    def test_unknown_file_and_payload_are_rejected(self):
        originals = self.baseline('24bc9ff')
        for name in (VIEW, TEMPLATE) + NEW_FILES:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'local modification')
            with self.assertRaisesRegex(ValueError, 'unexpected local version'):
                u.apply(self.root, self.base)
            self.assertEqual(path.read_bytes(), b'local modification')
            if name in originals:
                path.write_bytes(originals[name])
            else:
                path.unlink()
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'bad')
        self.assertEqual((self.root / VIEW).read_bytes(), originals[VIEW])

    def test_failure_rolls_back_replacements_and_created_file(self):
        originals = self.baseline('24bc9ff')
        real_replace = u.os.replace
        calls = 0
        def fail_fourth(src, dst):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError('simulated failure')
            return real_replace(src, dst)
        with patch.object(u.os, 'replace', side_effect=fail_fourth):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.base)
        backups = list(self.base.glob('EK_code_backup_official_city_index_*'))
        self.assertEqual(len(backups), 1)
        for name, data in originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)
            self.assertEqual((backups[0] / name).read_bytes(), data)
        for name in NEW_FILES:
            self.assertFalse((self.root / name).exists())


if __name__ == '__main__':
    unittest.main()
