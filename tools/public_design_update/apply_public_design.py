#!/usr/bin/env python3
"""Safely apply the pinned public interface design system to an existing ZIP copy.

Backs up the specific existing code files, refuses unexpected edits, verifies
all downloads, and never touches the database, project media, or user photos.
Run from the project folder containing manage.py; stop the Django server first.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import urllib.request

TARGET_COMMIT = 'de690ac960aaf41b80ffaf0b7c796f59d5eeea7c'
BASE_URL = ('https://raw.githubusercontent.com/'
            'JohnTechBytes/BSIT3A-DJANGO-ExploreKabankalanon/' + TARGET_COMMIT + '/')
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024

# Exact baseline and target hashes. Unexpected edits are never overwritten.
FILES = {
    'templates/theme/public_base.html': (('8ac6d3bd50044e934dfe6b1758289dde12d98d7ee9aae532c112871017cb29ba',), '3c56a2484ec32572204a7697e9dcab765bed9484843945ff460ec0d19a972f28'),
    'templates/registration/auth_base.html': (('37977851624583f4450c669ecd22722f0234ee03a47875a362f1beae94bf12f6',), 'b9a990ae834680fbb59b32ff9abead41d09f8651ac3aefb9d68343e0a0373ebf'),
    'templates/errors/404.html': (('1656b3a9ebe986740b5f540ffeb9199025a549c529ee187565283893b3546cf5',), 'ec1da3ac77847725fd245f6cbcab60d76dcbe83a3142a8f2152522e2690949d7'),
    'templates/errors/500.html': (('b17240bd79955999ce41ca7a0bc1e0ddfc316481056dd830475422c05dc6a13a',), 'e936e3815e2116019179fe2492468f488a73d03631b34a33d6c1b9cff48356b4'),
    'templates/places/attraction_carousel.html': (('87759f950eaef825bf72fcc81f24d359ca8bd74917aed0840c197f10c237515b',), '63513ad1ff350a5a063c61930be930aacf99000379c9c9f46e9915bab16c32cc'),
    'static/css/public-system.css': ((None,), '1ef32e84bc66d26731036244de1695e1a8ea7e20735f4a60aea8f04eb2cec8db'),
}
# Read-only guard: this shared stylesheet must be the exact reviewed version.
PREREQUISITES = {
    'static/css/explore.css': '394b4eb54d2d12d333aa1377d494b9cea9b5314c5f9bbb9e7b01c8601d9fd64a',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] not in ('README.md', 'apps', 'mysite', 'static', 'templates'):
        raise ValueError('unsafe update path: ' + name)
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlinks are not accepted: ' + name)
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError('update path leaves the project: ' + name)
    return current


def download(name):
    request = urllib.request.Request(BASE_URL + name, headers={'User-Agent': 'ExploreKabankalan-local-update/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError('download too large: ' + name)
    return data


def inspect(root, files):
    states = {}
    for name, (old_hash, new_hash) in files.items():
        path = safe_path(root, name)
        if path.exists() and not path.is_file():
            raise ValueError('not a regular file: ' + name)
        original = path.read_bytes() if path.exists() else None
        actual = digest(original) if original is not None else None
        if actual not in (*old_hash, new_hash):
            raise ValueError('unexpected local version, will not overwrite: ' + name + '; ask for help before proceeding')
        states[name] = (original, actual)
    return states


def verify_prerequisites(root):
    for name, expected in PREREQUISITES.items():
        path = safe_path(root, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise ValueError('reviewed stylesheet changed; will not overwrite or install: ' + name)


def apply(root, backup_parent, files=FILES, downloader=download):
    root = root.resolve()
    if not (root / 'manage.py').is_file():
        raise ValueError('open PowerShell in the project folder containing manage.py')
    verify_prerequisites(root)
    states = inspect(root, files)
    pending = [name for name, (_, current_hash) in states.items() if current_hash != files[name][1]]
    if not pending:
        print('Public design system already present. No files changed.')
        return None

    print('Verifying', len(pending), 'update files. No project files have changed yet.', flush=True)
    downloads = {}
    for name in pending:
        data = downloader(name)
        if digest(data) != files[name][1]:
            raise ValueError('download hash mismatch: ' + name)
        downloads[name] = data
        print('Verified:', name, flush=True)

    # Recheck immediately before backing up and writing.
    verify_prerequisites(root)
    if inspect(root, files) != states:
        raise ValueError('local files changed during download; nothing installed')
    backup = backup_parent / ('EK_code_backup_public_design_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    backup.mkdir(parents=True, exist_ok=False)
    metadata = {}
    for name in pending:
        original, old_hash = states[name]
        metadata[name] = {'previous_sha256': old_hash, 'new_sha256': files[name][1]}
        if original is not None:
            dest = backup / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(original)
            if digest(dest.read_bytes()) != old_hash:
                raise ValueError('backup verification failed: ' + name)
    (backup / 'manifest.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print('Code backup:', backup, flush=True)

    changed = []
    try:
        for name in pending:
            dest = safe_path(root, name)
            original, original_hash = states[name]
            current = digest(dest.read_bytes()) if dest.is_file() else None
            if current != original_hash:
                raise ValueError('local file changed before installation: ' + name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Write in the destination directory so replacement is atomic.
            tmp_name = None
            try:
                with tempfile.NamedTemporaryFile(prefix='.ek-update-', dir=dest.parent, delete=False) as tmp:
                    tmp_name = tmp.name
                    tmp.write(downloads[name])
                os.replace(tmp_name, dest)
                tmp_name = None
            finally:
                if tmp_name and os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            changed.append(name)
            if digest(dest.read_bytes()) != files[name][1]:
                raise ValueError('installed file failed verification: ' + name)
            print('Updated:', name, flush=True)
    except Exception:
        # Restore only files still matching this update; never overwrite a new
        # change from another process. The backup is kept for manual recovery.
        for name in reversed(changed):
            dest = safe_path(root, name)
            if not dest.is_file() or digest(dest.read_bytes()) != files[name][1]:
                print('Manual recovery needed for:', name, flush=True)
                continue
            original, _ = states[name]
            if original is None:
                dest.unlink()
            else:
                dest.write_bytes(original)
            print('Rolled back:', name, flush=True)
        print('Backup retained at:', backup, flush=True)
        raise
    print('Update installed. Database and project media were not changed.')
    return backup


def main():
    print('This updates only verified code and static files, not your database or media.')
    print('Stop the Django server first. A code backup will be created in your user folder.')
    answer = input('Type APPLY DESIGN to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY DESIGN':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
