"""Exercise the clean design installer on temporary files, never a real database."""
import importlib.util
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('clean_design_updater', ROOT / 'tools/clean_design_update/apply_clean_design.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class CleanDesignUpdaterTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('')
        for name in (*updater.FILES, *updater.PREREQUISITES):
            data = subprocess.check_output(['git', 'show', '29bf9cf9c7d05ea6d759fc93eac4203f655cea07:' + name], cwd=ROOT)
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        (self.root / 'media').mkdir()
        (self.root / 'media/photo').write_bytes(b'original photo')
        (self.root / 'db.sqlite3').write_bytes(b'original database')

    def test_applies_reversibly_and_preserves_feature_code_and_data(self):
        for name in updater.PREREQUISITES:
            self.assertEqual(updater.digest((self.root / name).read_bytes()), updater.PREREQUISITES[name])
        backup = updater.apply(self.root, Path(self.tmp.name))
        for name, (_, target) in updater.FILES.items():
            self.assertEqual(updater.digest((self.root / name).read_bytes()), target)
            self.assertEqual(updater.digest((backup / name).read_bytes()), updater.FILES[name][0][0])
        for name, target in updater.PREREQUISITES.items():
            self.assertEqual(updater.digest((self.root / name).read_bytes()), target)
        self.assertEqual((self.root / 'media/photo').read_bytes(), b'original photo')
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'original database')
        self.assertIsNone(updater.apply(self.root, Path(self.tmp.name)))

    def test_changed_local_code_stops_without_writes(self):
        name = 'templates/home.html'
        (self.root / name).write_text('local edits')
        before = (self.root / 'templates/theme/public_base.html').read_bytes()
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            updater.apply(self.root, Path(self.tmp.name))
        self.assertEqual((self.root / name).read_text(), 'local edits')
        self.assertEqual((self.root / 'templates/theme/public_base.html').read_bytes(), before)

    def test_changed_microphone_code_stops_without_writes(self):
        (self.root / 'static/js/ea-voice.js').write_text('local voice changes')
        before = (self.root / 'templates/home.html').read_bytes()
        with self.assertRaisesRegex(ValueError, 'required reviewed file missing or changed'):
            updater.apply(self.root, Path(self.tmp.name))
        self.assertEqual((self.root / 'templates/home.html').read_bytes(), before)

    def test_windows_line_endings_are_accepted(self):
        p = self.root / 'templates/home.html'
        p.write_bytes(p.read_bytes().replace(b'\n', b'\r\n'))
        backup = updater.apply(self.root, Path(self.tmp.name))
        self.assertIn(b'\r\n', (backup / 'templates/home.html').read_bytes())

    def test_failure_rolls_back_previous_writes(self):
        original_replace = updater.os.replace
        calls = 0
        def fail_second(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return original_replace(src, dst)
        original = (self.root / 'static/css/landing-field-guide.css').read_bytes()
        with patch.object(updater.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                updater.apply(self.root, Path(self.tmp.name))
        self.assertEqual((self.root / 'static/css/landing-field-guide.css').read_bytes(), original)
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'original database')
