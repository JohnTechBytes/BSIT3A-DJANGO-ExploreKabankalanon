#!/usr/bin/env python3
"""Safely apply the pinned carousel sizing fix to an existing public field-guide ZIP copy.

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

TARGET_COMMIT = '4072b225b95ea357011884fa24ff229444a2e826'
BASE_URL = ('https://raw.githubusercontent.com/'
            'JohnTechBytes/BSIT3A-DJANGO-ExploreKabankalanon/' + TARGET_COMMIT + '/')
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024

# Exact public field-guide baselines (and reviewed test versions).
FILES = {'templates/home.html': (('1cc5445ac655bdceb6a173c6910c959afcdb6a1c2caefc4b70bd74d2b3d4d733',),
                         '371f14b0cc3e41559393594b33be712ad3bad8893f9140550dcaa1a5d533283b'),
 'templates/theme/public_base.html': (('33364eccf979f56a5ad96e1b794274fe8113a88a58f36b3e84840ca84dde7965',),
                                      '78e812240e929c27815e1fd939b4ed8615a0d5da69cbd257c2d98c7ab06bd439'),
 'templates/places/attraction_carousel.html': (('d35f34fb896882968b552b3904ff196103c17a4fb7bea14bf1edeb72ab609343',),
                                               '92abe99387b7b92813f5a35938df36e434d15e0852043939af247b73497479bc'),
 'static/css/landing-field-guide.css': (('34f4aa2f12599ee42b9367f78a5416d4f05d4033e455a69b0a2a6bf100468f63',),
                                        '94ecb3913e63e8c228341908ee2a2f0b30a02f54a778b851de33b80e184a1a78'),
 'static/css/public-field-guide.css': (('aaf292095b8a01368ebfb081d81e07e235735765c30021e813423dbbcb21cc28',),
                                       '9fe1792e4fde2fe93f903af46db5fffeaf1ad234c1f5c22fa14195ac79dd1513'),
 'mysite/tests.py': (('4ef004ebf1ba829903e95f6f44d2d3ced7ffa0570d4e0c4e0192b454d2bd52f5',
                      'c9d47a04167fe47089b4a00fc2fc1c5572f8d387dd06f94ca52c1fec57134b74'),
                     '7e12b4681e2d38f21fec6dc5f7b0c70ace12bb7df3a44d997d754e906ead0271'),
 'mysite/tests_public_system.py': (('e59e92bfdb8f8efcedb108e0ae55ca5a4216650ee96beec7f80af399937f1445', None),
                                   '780c797b1558a59b34bc1d793a8a377c4584f587fe1a40c8a386920c6c7fe530'),
 'apps/places/tests_flows.py': (('58fe79e7a46a8e379c192ca98088f550482f90512363ad698001e3a6ea38e9e3',
                                 'f42ed9075d614f0e39a03650517dbb14fe7bb93dcafd2747fafabcd6b5d94445'),
                                'c3b6bc1166e5930b5c50ff90230cd685288e2369c3989f4f1600e7653b219724')}

# Required reviewed files are checked, not changed.
PREREQUISITES = {'static/css/public-system.css': '1ef32e84bc66d26731036244de1695e1a8ea7e20735f4a60aea8f04eb2cec8db',
 'static/css/public-experience.css': '4d7aef8ee25daef7570622c6106fb38bef495234aaa930d0ec6813d45392632c',
 'static/css/homepage-pilot.css': 'bea520af0830407dea2676ae123a7efa15ab60bd24ba17c07ddac5b5b06b5b07',
 'static/js/ea-voice.js': '70b9e155cc4c3f61759f4967b019c285f37f46079f31c127c057880aa99ba050',
 'static/js/public-experience-photo.js': 'ee88da9b4d2286d27c94c0e982f1c9eeb360ffc3c8225e683df31f6dadcdd3ed',
 'static/js/place-photo-fallback.js': '2318a419388846ea395e5a82e4ca9c9fd5aac40c88f9c1685fe2379677cb8c5a',
 'static/css/explore.css': ('2cee77014154c4190cc36dd103331758b058ff91b92bdb684bfcddd1f3bd95be',
                            '394b4eb54d2d12d333aa1377d494b9cea9b5314c5f9bbb9e7b01c8601d9fd64a'),
 'static/css/browse.css': '2d5777090d462cf7788aae56feb4507ca506204dae5736f1000d8e59e4a6c989',
 'static/css/browse-guide.css': '5b4c4cf9bcf83058df614d7b45e48b89e1c3b8cd916c52f4ac2864a93696d491',
 'static/js/landing-carousel.js': '7c7abf02831bf64bd7175f729f7fe87e97a04c870ce8d740fdab2bdd04c9075c',
 'static/vendor/leaflet/leaflet.css': 'a7837102824184820dfa198d1ebcd109ff6d0ff9a2672a074b9a1b4d147d04c6',
 'static/vendor/leaflet/leaflet.js': 'db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a',
 'static/img/places/new-kabankalan-cathedral.jpg': '7bb847bd7c4a13315485414fdfa33f65fab41ddbb0be98baa94c6938e0d2b5b6'}

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
        accepted = (expected,) if isinstance(expected, str) else expected
        if not path.is_file() or digest(path.read_bytes()) not in accepted:
            raise ValueError('required reviewed file missing or changed; will not overwrite or install: ' + name)


def apply(root, backup_parent, files=FILES, downloader=download):
    root = root.resolve()
    if not (root / 'manage.py').is_file():
        raise ValueError('open PowerShell in the project folder containing manage.py')
    verify_prerequisites(root)
    states = inspect(root, files)
    pending = [name for name, (_, current_hash) in states.items() if current_hash != files[name][1]]
    if not pending:
        print('Carousel sizing fix already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_carousel_size_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('First install the previous APPLY PUBLIC update. Stop the Django server before proceeding.')
    print('A code backup will be created in your user folder.')
    answer = input('Type APPLY SIZE to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY SIZE':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
