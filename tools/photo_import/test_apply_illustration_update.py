"""Offline tests: code-only update, backups, checks, and rollback."""
import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from tools.photo_import import apply_illustration_update as update


def h(data):
    return update.digest(data)


class IllustrationUpdaterTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_text('existing project')
        (self.root / 'media').mkdir()
        (self.root / 'media' / 'photo.jpg').write_bytes(b'private original')
        self.path = 'static/css/explore.css'
        self.new_file = 'static/img/samples/generic.jpg'
        (self.root / self.path).parent.mkdir(parents=True)
        (self.root / self.path).write_bytes(b'old code')
        self.files = {self.path: (h(b'old code'), h(b'new code')),
                      self.new_file: (None, h(b'image'))}
        self.downloads = {self.path: b'new code', self.new_file: b'image'}

    def test_updates_code_only_and_backs_up_prior_file(self):
        with contextlib.redirect_stdout(io.StringIO()):
            backup = update.apply(self.root, self.base, self.files, self.downloads.__getitem__)
        self.assertEqual((self.root / self.path).read_bytes(), b'new code')
        self.assertEqual((self.root / self.new_file).read_bytes(), b'image')
        self.assertEqual((backup / self.path).read_bytes(), b'old code')
        self.assertTrue((backup / 'manifest.json').is_file())
        self.assertEqual((self.root / 'media' / 'photo.jpg').read_bytes(), b'private original')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertIsNone(update.apply(self.root, self.base, self.files, self.downloads.__getitem__))

    def test_unexpected_local_edit_stops_before_any_download_or_backup(self):
        (self.root / self.path).write_bytes(b'my edits')
        downloader = unittest.mock.Mock()
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            update.apply(self.root, self.base, self.files, downloader)
        downloader.assert_not_called()
        self.assertEqual((self.root / self.path).read_bytes(), b'my edits')
        self.assertFalse(list(self.base.glob('EK_code_backup_*')))

    def test_bad_download_stops_before_backup_or_writes(self):
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, 'hash mismatch'):
            update.apply(self.root, self.base, self.files, lambda name: b'incorrect')
        self.assertEqual((self.root / self.path).read_bytes(), b'old code')
        self.assertFalse(list(self.base.glob('EK_code_backup_*')))

    def test_failure_on_second_write_rolls_back_first(self):
        real_replace = update.os.replace
        count = 0
        def fail_second(source, destination):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError('simulated failure')
            return real_replace(source, destination)
        with patch.object(update.os, 'replace', side_effect=fail_second), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                update.apply(self.root, self.base, self.files, self.downloads.__getitem__)
        self.assertEqual((self.root / self.path).read_bytes(), b'old code')
        self.assertFalse((self.root / self.new_file).exists())
        self.assertTrue(list(self.base.glob('EK_code_backup_*')))
        self.assertEqual((self.root / 'media' / 'photo.jpg').read_bytes(), b'private original')

    def test_unsafe_paths_rejected(self):
        for path in ('media/photo.jpg', '../media/photo.jpg', '/etc/passwd', 'static/../media/photo.jpg'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                update.safe_path(self.root, path)


if __name__ == '__main__':
    unittest.main()
