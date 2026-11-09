#!/usr/bin/env python3
"""Safely apply the pinned cinematic public experience to an existing ZIP copy.

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

TARGET_COMMIT = '79644b7c2869f9e1ace435a7310c4edb551348d1'
BASE_URL = ('https://raw.githubusercontent.com/'
            'JohnTechBytes/BSIT3A-DJANGO-ExploreKabankalanon/' + TARGET_COMMIT + '/')
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024

# Exact baseline and target hashes. Unexpected edits are never overwritten.
FILES = {'templates/home.html': (('2c7a64768f16ccd34c0905c1fd1c29fcc2cac0e4e5e172490eafb315a0323aa6',
                          'daea5b77fd69e85f0fa87b5a16afe544ea82ae002fad32a9ad0b3b4f3978716f',
                          '5fc8a5396f9f3758dff86ed1969dded0f0d0aafbb2898cbf6d5f28e3c4d2e79c',
                          'cd2ed840cb5343a9ddfce4e27066c6fad42a43da480a35d36a6d33309db3be26',
                          '76971f9aa89e9bc45636f338596d8ec02d08eef8bce39bc721c94bbea5122f8e',
                          'bc3b23b348c1bdf085c295affc605e601178bda41a29283893b5e7f82c12995e',
                          'd10b91fc80fd94ac2e9ed92cd6dc034c61096bc60d33acee93b79d1f8b004b7c'),
                         '9e9391aef7052b243334aba4b21669439a3cfabaa82e8565f6fbafe01d71e54f'),
 'static/css/homepage-pilot.css': ((None,
                                    '23c7b8915853d5afa74c56b90230328a6166e882caf798a4ee9edc79c252e2dd',
                                    '0db26a08a11d529731fd085cae4b50ee1e679cc69a20b137ad82031884292528',
                                    '8e1fda3541376405822858e7b44ae58b02e8cfe6733b8e5459703e3a86c792fd',
                                    '4ff0c09ef2c0feb51b0c832aab012b95a03fbcb3e3b1be8df94c0078223e6fd2'),
                                   'bea520af0830407dea2676ae123a7efa15ab60bd24ba17c07ddac5b5b06b5b07'),
 'templates/theme/public_base.html': (('8ac6d3bd50044e934dfe6b1758289dde12d98d7ee9aae532c112871017cb29ba',
                                       '3c56a2484ec32572204a7697e9dcab765bed9484843945ff460ec0d19a972f28'),
                                      'b9acd398c007d359f991386409e0c575119ba2fc9f2a5a92ff969d249748d711'),
 'templates/registration/auth_base.html': (('37977851624583f4450c669ecd22722f0234ee03a47875a362f1beae94bf12f6',
                                            'b9a990ae834680fbb59b32ff9abead41d09f8651ac3aefb9d68343e0a0373ebf'),
                                           '7214513d0c89a15362ef6f766251f935131d3e028049669502daf84d9165ae48'),
 'templates/errors/404.html': (('1656b3a9ebe986740b5f540ffeb9199025a549c529ee187565283893b3546cf5',
                                'ec1da3ac77847725fd245f6cbcab60d76dcbe83a3142a8f2152522e2690949d7'),
                               '50da068ab17146a20783d7695d6a763ef2d0a81c7138bdc7da53e78e0ac0cc76'),
 'templates/errors/500.html': (('b17240bd79955999ce41ca7a0bc1e0ddfc316481056dd830475422c05dc6a13a',
                                'e936e3815e2116019179fe2492468f488a73d03631b34a33d6c1b9cff48356b4'),
                               '23cadfc5123832a700e7a71da194f06e73a1bd68112b62b65a4ef04ceceb9a36'),
 'templates/places/attraction_carousel.html': (('87759f950eaef825bf72fcc81f24d359ca8bd74917aed0840c197f10c237515b',
                                                '63513ad1ff350a5a063c61930be930aacf99000379c9c9f46e9915bab16c32cc'),
                                               'e0d14b2770c9390a7d0438a21b026ede7227bd13901dfb1d9c77cfce76f4055f'),
 'static/css/public-system.css': ((None,), '1ef32e84bc66d26731036244de1695e1a8ea7e20735f4a60aea8f04eb2cec8db'),
 'templates/components/place_card.html': (('8353f5a09d6cd5afe7042a35e9dbb24880b07330958c56b4cc5b5d83d0b8c62f',),
                                          'e72e51a7814874062ff303ad771a6117d3e31bea4a0761f6ceed6ecb3e49daee'),
 'static/css/public-experience.css': ((None,), '4d7aef8ee25daef7570622c6106fb38bef495234aaa930d0ec6813d45392632c'),
 'static/js/public-experience-photo.js': ((None,), 'ee88da9b4d2286d27c94c0e982f1c9eeb360ffc3c8225e683df31f6dadcdd3ed')}
# Dependencies are checked, never changed.
PREREQUISITES = {'static/css/explore.css': ('2cee77014154c4190cc36dd103331758b058ff91b92bdb684bfcddd1f3bd95be', '394b4eb54d2d12d333aa1377d494b9cea9b5314c5f9bbb9e7b01c8601d9fd64a'),
 'static/css/browse.css': '2d5777090d462cf7788aae56feb4507ca506204dae5736f1000d8e59e4a6c989',
 'static/css/browse-guide.css': '5b4c4cf9bcf83058df614d7b45e48b89e1c3b8cd916c52f4ac2864a93696d491',
 'static/css/nearby.css': '57a2b28996cd231be368c0a856fe31604dbd84ef4fe6f904fc316dd57a15c2d4',
 'static/js/landing-carousel.js': '7c7abf02831bf64bd7175f729f7fe87e97a04c870ce8d740fdab2bdd04c9075c',
 'static/js/landing-map.js': '57a63242f7ffb611370dab655391854d4c26eedd7bed14499a1050b3d5c9a476',
 'static/js/motion.js': '0d794465181369c445339df68fac26c0414b7b0e18ac77479a742d365703eece',
 'static/js/place-photo-fallback.js': '2318a419388846ea395e5a82e4ca9c9fd5aac40c88f9c1685fe2379677cb8c5a',
 'templates/components/button.html': '349e150d679c65670a30784354e2284b11c0ea01bd4793bc3cbd2d143604ee22',
 'templates/components/chip.html': '21bf625960cab11b3b5810f97b33568beefea9bf2b721c07cd7352a37b26d2bf',
 'templates/components/input.html': 'c1bce70813e4270bf2c38aceb83ad430cd54d3923b5ab03a820fd0fab23f0f3b',
 'templates/components/badge.html': '06310204288984b180a069f0af66e492b71a2b417d5155ad5bdbac8e5871ac18',
 'static/img/places/new-kabankalan-cathedral.jpg': '7bb847bd7c4a13315485414fdfa33f65fab41ddbb0be98baa94c6938e0d2b5b6',
 'static/fonts/plus-jakarta-sans-variable.ttf': '89b3fb38aa0d275d7a731d0d817a4f1622b316b4d7fbdedcf02ee9099ff68bc8',
 'static/fonts/inter-variable.ttf': '29160a80ff49ddcab2c97711247e08b1fab27a484a329ce8b813d820dc559031'}


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
        print('Public experience already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_public_experience_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    answer = input('Type APPLY EXPERIENCE to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY EXPERIENCE':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
