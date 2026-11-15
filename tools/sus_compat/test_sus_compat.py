"""Retire only SUS on an isolated simulation of the reviewed Windows project."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixture = load('compat_fixture', 'tools/clean_design_compat/test_compat.py')
sus = load('sus_compat', 'tools/sus_compat/apply_remove_sus_compat.py')


class SusCompatTests(unittest.TestCase):
    def setUp(self):
        self.fx = fixture.CompatTests(methodName='test_reviewed_base_and_preservation')
        self.fx.setUp()
        self.addCleanup(self.fx.doCleanups)
        self.root = self.fx.root
        fixture.u.apply(self.root, Path(self.fx.temp.name))
        admin = self.root / 'apps/info/admin.py'
        admin.parent.mkdir(parents=True, exist_ok=True)
        admin.write_bytes(fixture.git_file('29bf9cf', 'apps/info/admin.py'))
        self.db = self.root / 'db.sqlite3'
        self.db.write_bytes(b'survey, review and relevance records')
        self.extra = self.root / 'apps/visits/urls.py'
        self.extra.parent.mkdir(parents=True, exist_ok=True)
        self.extra.write_text('legacy visits remain intact')

    def test_retirement_preserves_records_routes_and_notice(self):
        before_home = (self.root / 'templates/home.html').read_bytes()
        backup = sus.apply(self.root, Path(self.fx.temp.name))
        self.assertTrue(backup.is_dir())
        urls = (self.root / 'mysite/urls.py').read_text()
        self.assertIn("include('apps.visits.urls')", urls)
        self.assertIn("include('apps.itineraries.urls')", urls)
        self.assertNotIn('apps.evaluation.urls', urls)
        admin = (self.root / 'apps/info/admin.py').read_text()
        self.assertNotIn('SusResponse', admin)
        self.assertIn('RecommendationRating', admin)
        privacy = (self.root / 'templates/privacy/notice.html').read_text()
        self.assertIn('trip plans', privacy)
        self.assertIn('visit reports', privacy)
        self.assertIn('answers submitted before the survey was retired', privacy)
        self.assertNotIn('evaluation:sus_', (self.root / 'templates/theme/public_base.html').read_text())
        self.assertEqual((self.root / 'templates/home.html').read_bytes(), before_home)
        self.assertEqual(self.extra.read_text(), 'legacy visits remain intact')
        self.assertEqual(self.db.read_bytes(), b'survey, review and relevance records')
        self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media untouched')
        self.assertIsNone(sus.apply(self.root, Path(self.fx.temp.name)))

    def test_unreviewed_admin_stops_before_writing(self):
        admin = self.root / 'apps/info/admin.py'
        admin.write_bytes(admin.read_bytes() + b'\n# local edit\n')
        urls = (self.root / 'mysite/urls.py').read_bytes()
        with self.assertRaisesRegex(ValueError, 'Unexpected local version'):
            sus.apply(self.root, Path(self.fx.temp.name))
        self.assertEqual((self.root / 'mysite/urls.py').read_bytes(), urls)

    def test_unexpected_survey_reference_stops(self):
        for relative in ('templates/extra.html', 'apps/core/extra.py', 'static/js/extra.js'):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('evaluation:sus_survey')
            with self.assertRaisesRegex(ValueError, 'Unexpected survey reference'):
                sus.apply(self.root, Path(self.fx.temp.name))
            path.unlink()
        self.assertIn('apps.evaluation.urls', (self.root / 'mysite/urls.py').read_text())

    def test_windows_line_endings_and_rollback(self):
        urls = self.root / 'mysite/urls.py'
        urls.write_bytes(urls.read_bytes().replace(b'\n', b'\r\n'))
        before = {name: (self.root / name).read_bytes() for name in sus.COMPAT}
        replace = sus.os.replace
        calls = 0
        def fail_second(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated failure')
            return replace(src, dst)
        with patch.object(sus.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                sus.apply(self.root, Path(self.fx.temp.name))
        for name, data in before.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        backup = sus.apply(self.root, Path(self.fx.temp.name))
        self.assertEqual((backup / 'mysite/urls.py').read_bytes(), before['mysite/urls.py'])


if __name__ == '__main__':
    unittest.main()
