"""Offline compatibility checks against isolated files, not a real database."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('compat', ROOT / 'tools/clean_design_compat/apply_compat.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)

PILOT = b'''
/* REDESIGN PILOT: LANDING PAGE HERO */
.landing-page .hero { padding-block: 60px 80px; }
.landing-page #hero-title { font-size: var(--ek-text-60); line-height: 1.1; margin-bottom: 24px; }
.landing-page #hero-title em { font-style: normal; color: var(--ek-primary); }
.landing-page .hero-description { font-size: var(--ek-text-20); line-height: var(--ek-leading-body); color: var(--ek-muted); margin-bottom: 40px; max-width: 540px; }
.landing-page .search-row { padding: 6px; background: var(--ek-surface); border: 1px solid var(--ek-line); border-radius: 16px; display: flex; align-items: center; }
.landing-page .search-row input { border: none; padding: 12px 16px; font-size: var(--ek-text-16); }
.landing-page .search-row button { border-radius: 12px; }

'''


def git_file(revision, path):
    return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)


class CompatTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('')
        for name in {*u.FILES, *u.PREREQUISITES}:
            rev = '59c53a8f4e' if name == 'templates/privacy/notice.html' else '29bf9cf'
            data = git_file(rev, name)
            if name == 'static/css/explore.css':
                data += PILOT
            if name == 'mysite/urls.py':
                data = data.replace(b'urlpatterns = [\n', b"urlpatterns = [\n    path('visits/', include('apps.visits.urls')),  # ExploreAnywhere phase3f visits-and-rewards v1\n    path('itineraries/', include('apps.itineraries.urls')),  # ExploreAnywhere phase3d itinerary integration v1\n", 1)
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        (self.root / 'db.sqlite3').write_bytes(b'database untouched')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'media untouched')

    def test_reviewed_base_and_preservation(self):
        for name, expected in u.PREREQUISITES.items():
            self.assertEqual(u.digest((self.root / name).read_bytes()), expected, name)
        original = {name: (self.root / name).read_bytes() for name in u.PREREQUISITES}
        backup = u.apply(self.root, Path(self.temp.name))
        for name, (old_hashes, target) in u.FILES.items():
            self.assertEqual(u.digest((self.root / name).read_bytes()), target)
            self.assertIn(u.digest((backup / name).read_bytes()), old_hashes)
        for name, data in original.items():
            self.assertEqual((self.root / name).read_bytes(), data, name)
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'database untouched')
        self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'media untouched')
        self.assertIn(b'id="ea-inline-sort"', (self.root / 'templates/places/attraction_carousel.html').read_bytes())
        self.assertNotIn(b'evaluation:sus_survey', (self.root / 'templates/home.html').read_bytes())
        self.assertEqual((self.root / 'templates/theme/public_base.html').read_bytes().count(b'evaluation:sus_survey'), 2)
        self.assertIsNone(u.apply(self.root, Path(self.temp.name)))

    def test_changed_prerequisite_stops_before_writes(self):
        for name in ('static/css/explore.css', 'templates/privacy/notice.html', 'mysite/urls.py', 'apps/evaluation/urls.py', 'static/js/ea-voice.js'):
            p = self.root / name
            original = p.read_bytes()
            p.write_bytes(original + b'\nlocal change\n')
            before = (self.root / 'templates/home.html').read_bytes()
            with self.assertRaisesRegex(ValueError, 'required reviewed file missing or changed'):
                u.apply(self.root, Path(self.temp.name))
            self.assertEqual((self.root / 'templates/home.html').read_bytes(), before)
            p.write_bytes(original)

    def test_changed_template_stops_before_writes(self):
        p = self.root / 'templates/home.html'
        p.write_bytes(b'local edits')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            u.apply(self.root, Path(self.temp.name))
        self.assertEqual(p.read_bytes(), b'local edits')

    def test_windows_line_endings(self):
        p = self.root / 'mysite/urls.py'
        p.write_bytes(p.read_bytes().replace(b'\n', b'\r\n'))
        self.assertIsNotNone(u.apply(self.root, Path(self.temp.name)))

    def test_interrupted_install_rolls_back(self):
        before = {n: (self.root / n).read_bytes() for n in u.FILES}
        real_replace = u.os.replace
        calls = 0
        def fail_second(src, dst):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated write failure')
            return real_replace(src, dst)
        with patch.object(u.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(OSError, 'simulated write failure'):
                u.apply(self.root, Path(self.temp.name))
        for name, data in before.items():
            self.assertEqual((self.root / name).read_bytes(), data, name)


if __name__ == '__main__':
    unittest.main()
