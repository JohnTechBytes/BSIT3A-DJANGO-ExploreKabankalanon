"""SUS-only updater tests use temporary project trees, never a real database."""
import importlib.util
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sus_retirement_update', ROOT / 'tools/sus_retirement/apply_remove_sus.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class SusRetirementUpdaterTests(TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def make_project(self, ref):
        root = self.folder / ref[:7]
        root.mkdir()
        (root / 'manage.py').write_text('')
        for name in updater.COMPAT:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(subprocess.check_output(['git', 'show', f'{ref}:{name}'], cwd=ROOT))
        (root / 'db.sqlite3').write_bytes(b'real data sentinel')
        (root / 'media').mkdir()
        (root / 'media/image.jpg').write_bytes(b'photo sentinel')
        (root / 'static/js').mkdir(parents=True)
        (root / 'static/js/ea-voice.js').write_bytes(b'voice sentinel')
        return root

    def test_original_and_clean_design_projects_apply_without_touching_data(self):
        for ref in ('29bf9cf9c7d05ea6d759fc93eac4203f655cea07', 'dd54bf3e28af139a55f66f5ebe749bbcf59c6bdd'):
            with self.subTest(ref=ref):
                root = self.make_project(ref)
                backup = updater.apply(root, self.folder)
                self.assertTrue(backup.is_dir())
                self.assertNotIn('evaluation:sus_', (root / 'templates/theme/public_base.html').read_text())
                self.assertNotIn('evaluation:sus_', (root / 'templates/home.html').read_text())
                self.assertNotIn('apps.evaluation.urls', (root / 'mysite/urls.py').read_text())
                self.assertIn('places:my_reviews', (root / 'templates/theme/public_base.html').read_text())
                self.assertIn('RecommendationRating', (root / 'apps/info/admin.py').read_text())
                self.assertEqual((root / 'db.sqlite3').read_bytes(), b'real data sentinel')
                self.assertEqual((root / 'media/image.jpg').read_bytes(), b'photo sentinel')
                self.assertEqual((root / 'static/js/ea-voice.js').read_bytes(), b'voice sentinel')
                self.assertIsNone(updater.apply(root, self.folder))

    def test_unknown_version_stops_before_writing(self):
        root = self.make_project('29bf9cf9c7d05ea6d759fc93eac4203f655cea07')
        changed = root / 'templates/home.html'
        changed.write_bytes(changed.read_bytes() + b'\nlocal edit')
        old = (root / 'mysite/urls.py').read_bytes()
        with self.assertRaisesRegex(ValueError, 'Unexpected local version'):
            updater.apply(root, self.folder)
        self.assertEqual((root / 'mysite/urls.py').read_bytes(), old)

    def test_unknown_survey_template_stops_before_writing(self):
        root = self.make_project('29bf9cf9c7d05ea6d759fc93eac4203f655cea07')
        (root / 'templates/extra.html').write_text("{% url 'evaluation:sus_survey' %}")
        with self.assertRaisesRegex(ValueError, 'Unexpected survey reference'):
            updater.apply(root, self.folder)
        self.assertIn('apps.evaluation.urls', (root / 'mysite/urls.py').read_text())

    def test_windows_line_endings_and_rollback(self):
        root = self.make_project('29bf9cf9c7d05ea6d759fc93eac4203f655cea07')
        target = root / 'mysite/urls.py'
        target.write_bytes(target.read_bytes().replace(b'\n', b'\r\n'))
        original = target.read_bytes()
        replace = updater.os.replace
        calls = 0
        def fail_second(src, dest):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return replace(src, dest)
        with patch.object(updater.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                updater.apply(root, self.folder)
        self.assertEqual(target.read_bytes(), original)
        backup = updater.apply(root, self.folder)
        self.assertEqual((backup / 'mysite/urls.py').read_bytes(), original)
