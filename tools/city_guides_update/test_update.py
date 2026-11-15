"""Guarded installer tests with disposable files and synthetic data."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
VIEW = 'apps/info/views.py'
TEMPLATE = 'templates/info/city_information.html'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


u = load('city_guides_updater', 'tools/city_guides_update/apply_city_guides.py')
compat = load('design_compat', 'tools/clean_design_compat/apply_compat.py')
buttons = load('button_update', 'tools/city_info_buttons_update/apply_city_info_buttons.py')
filters = load('filter_update', 'tools/city_info_filters_update/apply_city_info_filters.py')


class CityGuideUpdaterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('')
        for name in (VIEW, TEMPLATE):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        self.old_view = subprocess.check_output(['git', 'show', '29bf9cf:' + VIEW], cwd=ROOT)
        self.assertEqual(u.digest(self.old_view), u.FILES[VIEW][0][0])
        (self.root / VIEW).write_bytes(self.old_view)
        (self.root / TEMPLATE).write_bytes(compat.download(TEMPLATE))
        (self.root / 'db.sqlite3').write_bytes(b'database untouched')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'media untouched')

    def test_three_reviewed_versions_install_and_preserve_other_data(self):
        for template in (compat.download(TEMPLATE), buttons.download(TEMPLATE), filters.download(TEMPLATE)):
            with self.subTest(old_template=u.digest(template)):
                originals = {VIEW: self.old_view.replace(b'\n', b'\r\n'),
                             TEMPLATE: template.replace(b'\n', b'\r\n')}
                for name, data in originals.items():
                    (self.root / name).write_bytes(data)
                backup = u.apply(self.root, self.base)
                for name, data in originals.items():
                    self.assertEqual((backup / name).read_bytes(), data)
                    self.assertEqual((self.root / name).read_bytes(), u.download(name))
                self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database untouched')
                self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media untouched')
                self.assertIsNone(u.apply(self.root, self.base))

    def test_changed_file_and_corrupt_payload_stop_before_any_write(self):
        for name in (VIEW, TEMPLATE):
            p = self.root / name
            original = p.read_bytes()
            p.write_bytes(original + b'\nlocal change')
            other = TEMPLATE if name == VIEW else VIEW
            before = (self.root / other).read_bytes()
            with self.assertRaisesRegex(ValueError, 'unexpected local version'):
                u.apply(self.root, self.base)
            self.assertEqual((self.root / other).read_bytes(), before)
            p.write_bytes(original)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            u.apply(self.root, self.base, downloader=lambda _: b'bad payload')
        self.assertEqual((self.root / VIEW).read_bytes(), self.old_view)

    def test_second_write_failure_rolls_back_and_retains_backup(self):
        before = {name: (self.root / name).read_bytes() for name in (VIEW, TEMPLATE)}
        replace = u.os.replace
        calls = 0
        def fail_second(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return replace(src, dst)
        with patch.object(u.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.base)
        backups = list(self.base.glob('EK_code_backup_city_guides_*'))
        self.assertEqual(len(backups), 1)
        for name, original in before.items():
            self.assertEqual((self.root / name).read_bytes(), original)
            self.assertEqual((backups[0] / name).read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
