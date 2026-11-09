"""Installer tests use temporary files only; no real database or network."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('road_route_update', ROOT / 'tools/road_route_update/apply_road_route.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class RoadRouteUpdaterTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        (self.root / 'templates').mkdir(parents=True)
        (self.root / 'static/css').mkdir(parents=True)
        (self.root / 'manage.py').write_text('')
        (self.root / 'templates/page.html').write_bytes(b'old')
        (self.root / 'static/css/explore.css').write_bytes(b'reviewed')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo').write_bytes(b'photo')
        (self.root / 'db.sqlite3').write_bytes(b'db')
        self.data = {'templates/page.html': b'new', 'static/css/public-system.css': b'css'}
        self.files = {'templates/page.html': ((updater.digest(b'old'),), updater.digest(b'new')),
                      'static/css/public-system.css': ((None,), updater.digest(b'css'))}
        patcher = patch.object(updater, 'PREREQUISITES', {'static/css/explore.css': updater.digest(b'reviewed')})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_backup_apply_and_idempotence(self):
        backup = updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((backup / 'templates/page.html').read_bytes(), b'old')
        self.assertEqual((self.root / 'static/css/public-system.css').read_bytes(), b'css')
        self.assertEqual((self.root / 'media/photo').read_bytes(), b'photo')
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'db')
        self.assertIsNone(updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get))

    def test_unexpected_local_edits_or_bad_download_stop_before_writing(self):
        (self.root / 'templates/page.html').write_bytes(b'my local edits')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((self.root / 'templates/page.html').read_bytes(), b'my local edits')
        (self.root / 'templates/page.html').write_bytes(b'old')
        with self.assertRaisesRegex(ValueError, 'download hash mismatch'):
            updater.apply(self.root, Path(self.tmp.name), self.files, lambda _: b'bad')
        self.assertEqual((self.root / 'templates/page.html').read_bytes(), b'old')
        self.assertFalse((self.root / 'static/css/public-system.css').exists())

    def test_changed_prerequisite_stops(self):
        (self.root / 'static/css/explore.css').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'required reviewed file missing or changed'):
            updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((self.root / 'templates/page.html').read_bytes(), b'old')

    def test_write_failure_restores_previously_replaced_files(self):
        original_replace = updater.os.replace
        calls = 0
        def fail_second(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return original_replace(src, dst)
        with patch.object(updater.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                updater.apply(self.root, Path(self.tmp.name), self.files, self.data.get)
        self.assertEqual((self.root / 'templates/page.html').read_bytes(), b'old')
        self.assertFalse((self.root / 'static/css/public-system.css').exists())

    def test_prior_design_palette_and_map_guide_baselines_apply_in_isolation(self):
        import subprocess
        for baseline in ('6ba9487', '6525ba6', 'aacdcb2'):
            with self.subTest(baseline=baseline):
                root = Path(self.tmp.name) / baseline
                root.mkdir()
                (root / 'manage.py').write_text('')
                fresh = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(fresh)
                for name in fresh.PREREQUISITES:
                    dest = root / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(subprocess.check_output(['git', 'show', '6525ba6:' + name], cwd=ROOT))
                for name, (old, target) in updater.FILES.items():
                    try:
                        data = subprocess.check_output(['git', 'show', baseline + ':' + name], cwd=ROOT, stderr=subprocess.DEVNULL)
                    except subprocess.CalledProcessError:
                        data = None
                    if data is not None:
                        self.assertIn(updater.digest(data), (*old, target), name)
                        dest = root / name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_bytes(data)
                (root / 'media').mkdir()
                (root / 'media/photo').write_bytes(b'personal photo')
                (root / 'db.sqlite3').write_bytes(b'personal database')
                with patch.object(updater, 'PREREQUISITES', fresh.PREREQUISITES):
                    backup = updater.apply(root, Path(self.tmp.name), downloader=lambda name: subprocess.check_output(['git', 'show', updater.TARGET_COMMIT + ':' + name], cwd=ROOT))
                    self.assertIsNotNone(backup)
                    for name, (_, target) in updater.FILES.items():
                        self.assertEqual(updater.digest((root / name).read_bytes()), target, name)
                    self.assertEqual((root / 'media/photo').read_bytes(), b'personal photo')
                    self.assertEqual((root / 'db.sqlite3').read_bytes(), b'personal database')
                    self.assertIsNone(updater.apply(root, Path(self.tmp.name), downloader=lambda name: self.fail('unexpected download')))
