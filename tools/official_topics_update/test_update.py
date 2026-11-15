"""Test the code-only topic installer in disposable project directories."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VIEW = 'apps/info/views.py'
INDEX = 'apps/info/official_index.py'
TEMPLATE = 'templates/info/city_information.html'
SNAPSHOT = 'apps/info/data/official_sitemap_snapshot.json'
spec = importlib.util.spec_from_file_location('official_topics_installer', ROOT / 'tools/official_topics_update/apply_official_topics.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)


class OfficialTopicsInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('')
        (self.root / 'db.sqlite3').write_bytes(b'database untouched')
        (self.root / 'media').mkdir()
        (self.root / 'media/test.jpg').write_bytes(b'media untouched')
        for name in (VIEW, INDEX, TEMPLATE, SNAPSHOT):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        (self.root / SNAPSHOT).write_bytes((ROOT / SNAPSHOT).read_bytes())

    def baseline(self, revision):
        originals = {}
        for name in (VIEW, INDEX, TEMPLATE):
            data = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)
            originals[name] = data.replace(b'\n', b'\r\n')
            (self.root / name).write_bytes(originals[name])
        return originals

    def test_both_reviewed_template_versions_backup_and_idempotency(self):
        snapshot = (self.root / SNAPSHOT).read_bytes()
        for revision in ('ddd35f8', '95602fe'):
            with self.subTest(revision=revision):
                originals = self.baseline(revision)
                backup = u.apply(self.root, self.base)
                for name, data in originals.items():
                    self.assertEqual((backup / name).read_bytes(), data)
                    self.assertEqual((self.root / name).read_bytes(), u.download(name))
                self.assertEqual((self.root / SNAPSHOT).read_bytes(), snapshot)
                self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database untouched')
                self.assertEqual((self.root / 'media/test.jpg').read_bytes(), b'media untouched')
                self.assertIsNone(u.apply(self.root, self.base))

    def test_unknown_code_snapshot_and_payload_are_rejected(self):
        originals = self.baseline('95602fe')
        for name in (VIEW, INDEX, TEMPLATE):
            (self.root / name).write_bytes(originals[name] + b' local change')
            with self.assertRaisesRegex(ValueError, 'unexpected local version'):
                u.apply(self.root, self.base)
            (self.root / name).write_bytes(originals[name])
        snapshot = (self.root / SNAPSHOT).read_bytes()
        (self.root / SNAPSHOT).write_bytes(b'changed data')
        with self.assertRaisesRegex(ValueError, 'required reviewed file'):
            u.apply(self.root, self.base)
        (self.root / SNAPSHOT).write_bytes(snapshot)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'wrong')
        for name, data in originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)

    def test_failed_third_replacement_rolls_back_all_code(self):
        originals = self.baseline('95602fe')
        replace = u.os.replace
        calls = 0
        def fail_third(src, dst):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('simulated failure')
            return replace(src, dst)
        with patch.object(u.os, 'replace', side_effect=fail_third):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.base)
        backups = list(self.base.glob('EK_code_backup_official_topics_*'))
        self.assertEqual(len(backups), 1)
        for name, data in originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)
            self.assertEqual((backups[0] / name).read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
