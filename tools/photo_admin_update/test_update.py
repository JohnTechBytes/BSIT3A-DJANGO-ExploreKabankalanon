"""Guarded photo-admin installer tests with disposable files, never a real DB."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('photo_admin_update', ROOT / 'tools/photo_admin_update/apply_photo_admin.py')
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)

REVIEWED = {
    'id': 'bigint(20)', 'title': 'varchar(255)', 'info_type': 'varchar(20)',
    'description': 'longtext', 'thumbnail_url': 'varchar(200)', 'order': 'int(10) unsigned',
    'created_at': 'datetime(6)', 'city_id': 'bigint(20)', 'is_published': 'tinyint(1)',
    'photo_credit': 'varchar(500)', 'photo_license': 'varchar(100)',
    'photo_license_url': 'varchar(1000)', 'photo_source_url': 'varchar(1000)',
}


class PhotoAdminInstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'manage.py').write_bytes(b'')
        for name, (old, _) in u.FILES.items():
            if old == (None,):
                continue
            data = subprocess.check_output(['git', 'show', 'fe2c90f:' + name], cwd=ROOT)
            self.assertEqual(u.digest(data), old[0])
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data.replace(b'\n', b'\r\n'))
        (self.root / 'db.sqlite3').write_bytes(b'unchanged database')
        (self.root / 'media').mkdir()
        (self.root / 'media/photo.jpg').write_bytes(b'unchanged photo')

    def test_reviewed_versions_install_back_up_and_preserve_data(self):
        originals = {name: (self.root / name).read_bytes() for name in u.FILES if (self.root / name).exists()}
        checks = []
        backup = u.apply(self.root, self.base, verifier=lambda root: checks.append(root))
        self.assertEqual(len(checks), 2)
        for name, data in originals.items():
            self.assertEqual((backup / name).read_bytes(), data)
        for name in u.FILES:
            self.assertEqual((self.root / name).read_bytes(), (ROOT / name).read_bytes())
        self.assertEqual((self.root / 'db.sqlite3').read_bytes(), b'unchanged database')
        self.assertEqual((self.root / 'media/photo.jpg').read_bytes(), b'unchanged photo')
        self.assertIsNone(u.apply(self.root, self.base))

    def test_changed_file_or_schema_stops_before_writes(self):
        name = 'apps/places/admin.py'
        p = self.root / name
        data = p.read_bytes()
        p.write_bytes(data + b'\nlocal change')
        with self.assertRaisesRegex(ValueError, 'unexpected local version'):
            u.apply(self.root, self.base)
        self.assertEqual(p.read_bytes(), data + b'\nlocal change')
        p.write_bytes(data)
        def stop(_):
            raise ValueError('simulated schema change')
        with self.assertRaisesRegex(ValueError, 'simulated schema change'):
            u.apply(self.root, self.base, verifier=stop)
        self.assertEqual(p.read_bytes(), data)
        self.assertFalse((self.root / 'apps/info/migrations/0005_cityinformation_photo_rights_compat.py').exists())

    def test_failure_rolls_back_and_keeps_backup(self):
        originals = {name: (self.root / name).read_bytes() for name in u.FILES if (self.root / name).exists()}
        real = u.os.replace
        calls = 0
        def fail_third(src, dst):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('simulated failure')
            return real(src, dst)
        with patch.object(u.os, 'replace', side_effect=fail_third):
            with self.assertRaisesRegex(OSError, 'simulated failure'):
                u.apply(self.root, self.base)
        backups = list(self.base.glob('EK_code_backup_photo_admin_*'))
        self.assertEqual(len(backups), 1)
        for name, data in originals.items():
            self.assertEqual((self.root / name).read_bytes(), data)
            self.assertEqual((backups[0] / name).read_bytes(), data)

    def test_schema_validation_rejects_missing_extra_or_incompatible_columns(self):
        rows = [(name, kind, 'NO', '', None, 'auto_increment' if name == 'id' else '')
                for name, kind in REVIEWED.items()]
        u.verify_columns(rows)
        for bad in (rows[:-1], rows + [('extra', 'varchar(1)', 'NO', '', None, '')],
                    [('id', 'varchar(20)', 'NO', '', None, 'auto_increment')] + rows[1:]):
            with self.subTest(rows=bad), self.assertRaises(ValueError):
                u.verify_columns(bad)


if __name__ == '__main__':
    unittest.main()
