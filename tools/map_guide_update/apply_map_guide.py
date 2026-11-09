#!/usr/bin/env python3
"""Safely apply the pinned straight-line guide and palette to an existing ZIP copy.

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

TARGET_COMMIT = 'd581a87db1cf8405d6c899d45b0233db6c554fba'
BASE_URL = ('https://raw.githubusercontent.com/'
            'JohnTechBytes/BSIT3A-DJANGO-ExploreKabankalanon/' + TARGET_COMMIT + '/')
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024

# Each accepted baseline is an exact reviewed version; unknown edits stop the update.
FILES = {'templates/home.html': (('9e9391aef7052b243334aba4b21669439a3cfabaa82e8565f6fbafe01d71e54f',
                          'b6751af17658e8bdbf1cd3a059f70472e5c88eb48a00a43323245cc6efcb6365'),
                         '9a17844e6cb770d5d9278f4739d23eb3c9dc4a95a2243ffc2007c25f17e1e770'),
 'templates/theme/public_base.html': (('b9acd398c007d359f991386409e0c575119ba2fc9f2a5a92ff969d249748d711',
                                       '4d0fcec5626d4c86da318a7ce97b9e200fca3977a7f99455605c2d3c1d754bb2'),
                                      '4d0fcec5626d4c86da318a7ce97b9e200fca3977a7f99455605c2d3c1d754bb2'),
 'templates/registration/auth_base.html': (('7214513d0c89a15362ef6f766251f935131d3e028049669502daf84d9165ae48',
                                            'aaa7e6f8eb3dec9def68b7e2b536c1da1bf98cd23732b9652b7f69ad5ea1fc44'),
                                           'aaa7e6f8eb3dec9def68b7e2b536c1da1bf98cd23732b9652b7f69ad5ea1fc44'),
 'templates/errors/404.html': (('50da068ab17146a20783d7695d6a763ef2d0a81c7138bdc7da53e78e0ac0cc76',
                                'a66591e43ee94493e9d03d3757629f8f2374441ee4eadcfce3caf76a2911ea77'),
                               'a66591e43ee94493e9d03d3757629f8f2374441ee4eadcfce3caf76a2911ea77'),
 'templates/errors/500.html': (('23cadfc5123832a700e7a71da194f06e73a1bd68112b62b65a4ef04ceceb9a36',
                                '8a4d7a1c7df8956123002d17f285aed05eaff0e3edc1f264466d08f54b24edf0'),
                               '8a4d7a1c7df8956123002d17f285aed05eaff0e3edc1f264466d08f54b24edf0'),
 'templates/places/nearby_places.html': (('cba64693d0aa89447437c9b769af7a4acdf05140e9960c2953985b20df60f09b',
                                          'c274ef955099efa7794ac6533544b4cec59b027f352b3890aa405c0e1320139e'),
                                         'da60fa34966ffc0db242e68d6b2b5a8a841b92c0f0aeb77edf909d90be5b279d'),
 'static/css/public-palette.css': ((None, '7f250fbcbc0504cf715f22c487d23fc785455c3112920e71ee1a3394f6e0476d'),
                                   '7f250fbcbc0504cf715f22c487d23fc785455c3112920e71ee1a3394f6e0476d'),
 'templates/places/attraction_carousel.html': (('e0d14b2770c9390a7d0438a21b026ede7227bd13901dfb1d9c77cfce76f4055f',),
                                               '5de54ead6de7cc29d7ed1c7c2060e8d49d7fe6af5a57c4dd22cc983521fddf13'),
 'static/css/nearby.css': (('57a2b28996cd231be368c0a856fe31604dbd84ef4fe6f904fc316dd57a15c2d4',),
                           '283f2a3bed7ebe700e521b5448f7433773c547bf12ef15f123188a6441500687'),
 'static/css/map-guide.css': ((None,), '2c657614f386c7cc474d64e1cb557fa08b435e67597808ae84f8d59f127f8ef9'),
 'static/js/map-guide.js': ((None,), '85a72004c218899ce891d386d75b0c9344207b6a907578e110e9529dcb279dab')}

# Dependencies are checked, never changed.
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
 'static/vendor/leaflet/leaflet.js': 'db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a'}

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
        print('Map guide and palette already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_map_guide_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    answer = input('Type APPLY MAP to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY MAP':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
