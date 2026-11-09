#!/usr/bin/env python3
"""Safely apply the pinned Nearby map and search code update to an existing ZIP copy.

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

TARGET_COMMIT = '292b808eee959d5d7cd9c501da12a51eed32fc24'
BASE_URL = ('https://raw.githubusercontent.com/'
            'JohnTechBytes/BSIT3A-DJANGO-ExploreKabankalanon/' + TARGET_COMMIT + '/')
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024

# Exact baseline and target hashes. Unexpected edits are never overwritten.
FILES = {
    'apps/places/nearby.py': ('3a3fb07f45733e24af1f37189163560f893329f36689047ec565e360bb9d293b', '6d3f0d9d3dae228942cc902e8d602af3f2cf2d45caad7a160c489d43791c336c'),
    'apps/places/nearby_intent.py': ('587873f202bf4a455bb8cbf6647921311f4e1f46ccb3c6aabcf8d9b28ebfb9f6', '6017b22e5ebbe4b6f23acc7a16e7c43e8a8ca3a194f6bf1d6c5eff41493d668f'),
    'apps/places/search_intents.py': ('6b6c5dcd7bc0384b9f285d5ab5143cf194ffe85030093b3aa6c9e2f1bd12e1cd', 'c7246a8202c048c3ea0f4e85fa9e8371a415c97b08451d10a376d2200ddce609'),
    'templates/places/nearby_places.html': ('4b82a5c8846f720ef067114a83dab627580c651d08a013f4675633f11de1cbe4', 'cba64693d0aa89447437c9b769af7a4acdf05140e9960c2953985b20df60f09b'),
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
        if actual not in (old_hash, new_hash):
            raise ValueError('unexpected local version, will not overwrite: ' + name + '; if your illustration update is not installed, install it first or ask for help')
        states[name] = (original, actual)
    return states


def apply(root, backup_parent, files=FILES, downloader=download):
    root = root.resolve()
    if not (root / 'manage.py').is_file():
        raise ValueError('open PowerShell in the project folder containing manage.py')
    prerequisites = {
        'apps/places/sample_images.py': '612f7a651fcec2a97f7a6e01642c1631dd78e45df357fb3c098ebb7262adcd8c',
        'apps/places/templatetags/attraction_photos.py': '46249b40ee0168b2c278cc14de33b0273ded82e7c3ab1fad170ccb4c0d26cc2c',
        'static/js/place-photo-fallback.js': '2318a419388846ea395e5a82e4ca9c9fd5aac40c88f9c1685fe2379677cb8c5a',
        'static/img/samples/generic.jpg': '087810c24dbb3acac37133704fc35dbf81f6c1ca421a0a2027ea9340606c7d6b',
    }
    for name, expected in prerequisites.items():
        path = safe_path(root, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise ValueError('illustration update prerequisite missing or changed: ' + name + '; do not override, ask for help')
    states = inspect(root, files)
    pending = [name for name, (_, current_hash) in states.items() if current_hash != files[name][1]]
    if not pending:
        print('Nearby map and search update already present. No files changed.')
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
    if inspect(root, files) != states:
        raise ValueError('local files changed during download; nothing installed')
    backup = backup_parent / ('EK_code_backup_nearby_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    answer = input('Type APPLY to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
