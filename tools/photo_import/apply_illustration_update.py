#!/usr/bin/env python3
"""Safely apply the pinned illustration-only code update to an existing ZIP copy.

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

TARGET_COMMIT = 'ad28fba8cae95fa58a5be3335d613e0c45139a3d'
BASE_URL = ('https://raw.githubusercontent.com/'
            'JohnTechBytes/BSIT3A-DJANGO-ExploreKabankalanon/' + TARGET_COMMIT + '/')
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024

# (SHA-256 from merged main e5fb5b0, SHA-256 from TARGET_COMMIT).
# None means the file did not exist in that main snapshot.
FILES = {
    'README.md': ('18fac7d93867639814549e4efd7197eafa26a49963ca40909eef67412672449d', '5e619878d0a9c9665993fd98f8cf96ecec5839ac9924a8823d3f87559e7a478d'),
    'apps/core/management/commands/verify_enrichment.py': ('da0ef473ab5c931ea7b2b5285e7d1bf1468d2c9053826cb247a33401a7ffa1fa', 'c70c8ed5140153eb779658db2fff044a3d7eedb358f6f63c994831b92f4bd2fa'),
    'apps/places/sample_images.py': ('a363a95b5ac381d266c94310f179a3769a3c70182253e19d593c1c6e72e97032', '612f7a651fcec2a97f7a6e01642c1631dd78e45df357fb3c098ebb7262adcd8c'),
    'apps/places/templatetags/attraction_photos.py': ('afdef98504593d87c4ee2105c7f249ecddf5388c9dc4c36e07071a9fc3580d0e', '46249b40ee0168b2c278cc14de33b0273ded82e7c3ab1fad170ccb4c0d26cc2c'),
    'apps/places/tests.py': ('c3306a38cda4625ae4886ca7b429d813e739481e257cfc5a10134fe28b7cb187', '74668094628170266ac463667d361464ae945e80b2d3493bf4f94f05836cd34e'),
    'apps/places/tests_illustrative_photos.py': (None, 'de03b94ed9bea1cfe68a8f7e4f6885924debe5d16df035508930fcbfd24b24cf'),
    'mysite/tests.py': ('6a65165fdda1ffaa485764a98abf80560266281d4be3202962c929c8b1d213da', 'c9d47a04167fe47089b4a00fc2fc1c5572f8d387dd06f94ca52c1fec57134b74'),
    'mysite/tests_editorial.py': ('cfd012d7fd754cd718f355d16ff9b7d488ea40ad97638081a69f508586a8c7a3', '33dcef384b4046bd44cc031d1716b4737b8349b22c516b9766652c02dbcb3219'),
    'static/css/explore.css': ('fc50824f83623fc21f93a1fd69c2fbff68dd9c12bbb578ab64ea9fbf6220092c', '2cee77014154c4190cc36dd103331758b058ff91b92bdb684bfcddd1f3bd95be'),
    'static/img/samples/generic.jpg': (None, '087810c24dbb3acac37133704fc35dbf81f6c1ca421a0a2027ea9340606c7d6b'),
    'static/js/place-photo-fallback.js': ('83b4986aa5d9188ec7f3424270853e7476a8152a3b1ca9d1eea619b74ac43ccf', '2318a419388846ea395e5a82e4ca9c9fd5aac40c88f9c1685fe2379677cb8c5a'),
    'templates/components/place_card.html': ('aff4977e59c0aed64e4bdc83e7055e168a2637362658c209abb5f1e3e6ce2212', '8353f5a09d6cd5afe7042a35e9dbb24880b07330958c56b4cc5b5d83d0b8c62f'),
    'templates/home.html': ('604f5b02cfe2f730158ea9f92d69548f9bb8013e49d0fa7242a9a0b102e2d38d', '2c7a64768f16ccd34c0905c1fd1c29fcc2cac0e4e5e172490eafb315a0323aa6'),
    'templates/info/city_information.html': ('4f41cd44e1f1ef210f2d2078b254a2f0501c3777e58698fba572c6f684261337', '819671f281e79739c171c9124eaafe3bcbd37af1cd838057057404e647119f09'),
    'templates/places/attraction_carousel.html': ('be492120bb2924982333ff12d8950474d62d708557ea81cf7837a5aae5fb9bac', '87759f950eaef825bf72fcc81f24d359ca8bd74917aed0840c197f10c237515b'),
    'templates/places/city_discover.html': ('243611c4022e494fa4608da89969af74fdab9df423f354967b71ab1446ef64b2', 'cf7642d2e3f6b7d1afa7f03d79a04dc7e35af6065f5f000bd96cf8fb9f6d2411'),
    'templates/places/nearby_places.html': ('2ce85c59d01abdeb2c8ee6c69d7a0baf858c3115bad6a70e3f203a85b3011fa6', '4b82a5c8846f720ef067114a83dab627580c651d08a013f4675633f11de1cbe4'),
    'templates/places/place_detail.html': ('2e58a816e7c0a6686abe4c97da831caf3a02a69376aa3fe4694df28475409644', '22015a4d4b87687dd023e260a6ca599f3ddb427707e135c42d1712fd379123ac'),
    'templates/places/saved_places.html': ('124fe0cbeb1f7a3a7c623dc6b07f0d478c507ece6a17bb107edb13c990683852', 'ac802d4dda39dab69ffc9b50800e7c60e2b305aecad4d26468d3432de9687950'),
    'templates/theme/public_base.html': ('14a174d92390712c86b2e70ca0b7206d4b45766019cb381fbdbc192cce40ca56', '8ac6d3bd50044e934dfe6b1758289dde12d98d7ee9aae532c112871017cb29ba'),
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
            raise ValueError('unexpected local version, will not overwrite: ' + name)
        states[name] = (original, actual)
    return states


def apply(root, backup_parent, files=FILES, downloader=download):
    root = root.resolve()
    if not (root / 'manage.py').is_file():
        raise ValueError('open PowerShell in the project folder containing manage.py')
    states = inspect(root, files)
    pending = [name for name, (_, current_hash) in states.items() if current_hash != files[name][1]]
    if not pending:
        print('Illustration update already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_illustrations_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
