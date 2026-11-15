"""Compatibility installer tests against temporary files only."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixture = load('clean_fixture', 'tools/clean_design_compat/test_compat.py')
u = load('mode_updater', 'tools/discovery_mode_update/apply_discovery_modes.py')


class ModeInstallerTests(unittest.TestCase):
    def setUp(self):
        self.fx = fixture.CompatTests(methodName='test_reviewed_base_and_preservation')
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.root = self.fx.root
        fixture.u.apply(self.root, Path(self.fx.temp.name))
        for name in ('apps/places/search_intents.py', 'apps/places/nearby_intent.py',
                     'apps/places/urls.py', 'templates/places/_discovery_modes.html'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(fixture.git_file('29bf9cf', name))
        self.backup_parent = Path(self.fx.temp.name)

    def test_apply_preserves_every_other_prerequisite_and_data(self):
        original = {name: (self.root / name).read_bytes() for name in u.PREREQUISITES}
        backup = u.apply(self.root, self.backup_parent)
        for name, (old, new) in u.FILES.items():
            self.assertEqual(u.digest((backup / name).read_bytes()), old[0])
            self.assertEqual(u.digest((self.root / name).read_bytes()), new)
            self.assertEqual((self.root / name).read_bytes(), (ROOT / name).read_bytes())
        for name, data in original.items():
            self.assertEqual((self.root / name).read_bytes(), data, name)
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database untouched')
        self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media untouched')
        self.assertIsNone(u.apply(self.root, self.backup_parent))

    def test_changed_local_backend_or_microphone_stops(self):
        for name in ('apps/places/views.py', 'static/js/ea-voice.js', 'apps/places/nearby_intent.py'):
            p = self.root / name
            original = p.read_bytes()
            p.write_bytes(original + b'\nlocal changes')
            before = (self.root / 'templates/places/nearby_places.html').read_bytes()
            with self.assertRaises(ValueError):
                u.apply(self.root, self.backup_parent)
            self.assertEqual((self.root / 'templates/places/nearby_places.html').read_bytes(), before)
            p.write_bytes(original)

    def test_crlf_and_rollback_on_second_write(self):
        p = self.root / 'apps/places/views.py'
        p.write_bytes(p.read_bytes().replace(b'\n', b'\r\n'))
        before = {n: (self.root / n).read_bytes() for n in u.FILES}
        original_replace = u.os.replace
        calls = 0
        def fail_second(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return original_replace(src, dst)
        with patch.object(u.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.backup_parent)
        for name, data in before.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        backup = u.apply(self.root, self.backup_parent)
        self.assertEqual((backup / 'apps/places/views.py').read_bytes(), before['apps/places/views.py'])


if __name__ == '__main__':
    unittest.main()
