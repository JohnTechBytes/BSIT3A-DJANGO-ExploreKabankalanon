#!/usr/bin/env python3
"""Retire SUS safely on supported local copies without modifying survey data.

Only the reviewed legacy-route and compatibility-design versions are accepted. Reviews,
recommendations, other features, JS, database records and media are untouched.
"""
from datetime import datetime
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import tempfile

COMPAT = {'apps/info/admin.py': {'818e3a7f5b8fb79dff8563927e50464dceed07b3dc047c77cb3b12b86d501b2a': 'f3656fe57d9dc57f87a325a374b5217b56f3a6ca0daa69d8ed7e85a8ac942d53'},
 'mysite/urls.py': {'ec0c2db91dc5d613d446b2ac0267181626b63e81ab3d2ed3166855977dee3bc4': '154e0cac7ed4f575f705719c057082845aeb0ef491efb637a0217027300b86cd'},
 'templates/home.html': {'a1a365a3fe446d7e773dd4a84842d650ba675d61c7723514ed1901bc8eed5cf9': 'a1a365a3fe446d7e773dd4a84842d650ba675d61c7723514ed1901bc8eed5cf9'},
 'templates/privacy/notice.html': {'f7811f16bcf33725b381edd989341f8e28b6946c79fbde1125f8b89d41df824c': 'c36185db60dcca5d520c60e06f19476f70c53e3c6d76746ea47dddede36da294'},
 'templates/theme/public_base.html': {'48247a5822b03c367b1739b35620c670cfdd5a206a65faf8d43dd2f0e15d2dc7': '971b0e7fedd7b24d05f61f609d6ad03cb01eb283dcd6987b0d3d971bc0aa7853'}}


def digest(data):
    # Reviewed files are text; allow Windows CRLF without ignoring other edits.
    return hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()


def safe_path(root, name):
    parts = PurePosixPath(name)
    if parts.is_absolute() or '..' in parts.parts or parts.parts[0] not in ('apps', 'mysite', 'templates', 'static'):
        raise ValueError('Unsafe update path: ' + name)
    path = root
    for component in parts.parts:
        path = path / component
        if path.is_symlink():
            raise ValueError('Symlink not supported: ' + name)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path leaves project: ' + name)
    return path


def replace_once(text, old, new=''):
    if text.count(old) != 1:
        raise ValueError('Expected code pattern was not found exactly once; nothing installed.')
    return text.replace(old, new, 1)


def transform(name, data):
    text = data.decode('utf-8').replace('\r\n', '\n')
    if name == 'mysite/urls.py':
        text = replace_once(text, '    path("evaluation/", include("apps.evaluation.urls")),\n')
    elif name == 'apps/info/admin.py':
        text = replace_once(text, '    SusResponse,\n')
        text = replace_once(text, '@admin.register(SusResponse)\nclass SusResponseAdmin(admin.ModelAdmin):\n    list_display = ("id", "user", "score", "created_at")\n    list_filter = ("created_at",)\n    readonly_fields = ("score", "created_at")\n\n\n')
    elif name == 'templates/home.html':
        line = '                <a href="{% url \'evaluation:sus_survey\' %}">Usability survey</a>\n'
        if line in text:
            text = replace_once(text, line)
    elif name == 'templates/theme/public_base.html':
        text = replace_once(text, '                        <a href="{% url \'evaluation:sus_survey\' %}">Usability Survey</a>\n')
        text = replace_once(text, '            <a href="{% url \'evaluation:sus_survey\' %}">Usability survey</a>\n')
    elif name == 'templates/privacy/notice.html':
        text = replace_once(text, 'the searches you run, your relevance ratings and your usability survey answers.', 'the searches you run, your relevance ratings and any usability survey answers submitted before the survey was retired.')
        text = replace_once(text, 'You see your own saved places, plans, reviews, visits, searches and survey\n      answers on your own pages. Authorized staff can access records according to\n      their dashboard permissions. Your username, rating and review appear on', 'You see your own saved places, plans, reviews and visits on your own pages.\n      Authorized staff can access available records according to their dashboard\n      permissions. Your username, rating and review appear on')
    else:
        raise ValueError('Unknown update file: ' + name)
    return text.encode('utf-8')


def verify_other_templates(root):
    templates = safe_path(root, 'templates')
    for path in templates.rglob('*.html'):
        relative = path.relative_to(root).as_posix()
        if relative.startswith('templates/evaluation/') or relative in COMPAT:
            continue  # archived, unrouted pages or known update files
        if path.is_symlink():
            raise ValueError('Symlink not supported: ' + relative)
        text = path.read_text(encoding='utf-8')
        if 'evaluation:sus_' in text or '/evaluation/sus/' in text:
            raise ValueError('Unexpected survey reference, will not install: ' + relative)


def verify_other_code(root):
    # A stale reverse() or hard-coded URL outside the retired implementation
    # could break another feature after the route is removed. Stop for review.
    for directory, pattern in (('apps', '*.py'), ('mysite', '*.py'), ('static/js', '*.js')):
        base = safe_path(root, directory)
        if not base.is_dir():
            continue
        for path in base.rglob(pattern):
            relative = path.relative_to(root).as_posix()
            if (relative.startswith('apps/evaluation/') or '/migrations/' in relative
                    or path.name.startswith('test') or '/tests/' in relative):
                continue
            if path.is_symlink():
                raise ValueError('Symlink not supported: ' + relative)
            text = path.read_text(encoding='utf-8')
            if 'evaluation:sus_' in text or '/evaluation/sus/' in text:
                raise ValueError('Unexpected survey reference, will not install: ' + relative)


def apply(root, backup_parent):
    root = root.resolve()
    if not (root / 'manage.py').is_file():
        raise ValueError('Run from the project folder containing manage.py.')
    verify_other_templates(root)
    verify_other_code(root)
    states, updates = {}, {}
    for name, variants in COMPAT.items():
        path = safe_path(root, name)
        if not path.is_file():
            raise ValueError('Required file is missing: ' + name)
        original = path.read_bytes()
        before = digest(original)
        states[name] = original
        if before in variants.values():
            continue
        if before not in variants:
            raise ValueError('Unexpected local version; no files changed: ' + name)
        result = transform(name, original)
        if digest(result) != variants[before]:
            raise ValueError('Output verification failed; no files changed: ' + name)
        updates[name] = result
    if not updates:
        print('SUS is already retired. No files changed.')
        return None

    verify_other_templates(root)
    verify_other_code(root)
    for name, original in states.items():
        if safe_path(root, name).read_bytes() != original:
            raise ValueError('A file changed while checking; no files changed: ' + name)
    backup = backup_parent / ('EK_code_backup_sus_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    backup.mkdir(parents=True, exist_ok=False)
    for name in updates:
        dest = backup / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(states[name])
        if dest.read_bytes() != states[name]:
            raise ValueError('Backup verification failed: ' + name)
    (backup / 'manifest.json').write_text(json.dumps({name: {'before': digest(states[name]), 'after': digest(data)} for name, data in updates.items()}, indent=2), encoding='utf-8')
    print('Code backup:', backup, flush=True)

    changed = []
    try:
        for name, data in updates.items():
            dest = safe_path(root, name)
            if dest.read_bytes() != states[name]:
                raise ValueError('A file changed during installation: ' + name)
            temp = None
            try:
                with tempfile.NamedTemporaryFile(prefix='.ek-sus-', dir=dest.parent, delete=False) as output:
                    temp = output.name
                    output.write(data)
                os.replace(temp, dest)
                temp = None
            finally:
                if temp and os.path.exists(temp):
                    os.unlink(temp)
            changed.append(name)
            if dest.read_bytes() != data:
                raise ValueError('Installed file failed verification: ' + name)
            print('Updated:', name, flush=True)
    except Exception:
        for name in reversed(changed):
            dest = safe_path(root, name)
            if dest.is_file() and dest.read_bytes() == updates[name]:
                dest.write_bytes(states[name])
                print('Rolled back:', name, flush=True)
            else:
                print('Manual recovery needed for:', name, flush=True)
        print('Backup retained at:', backup, flush=True)
        raise
    print('SUS retired. Existing responses, reviews, database and media were not changed.')
    return backup


def main():
    print('Stops SUS public pages and admin entry. Existing responses and all reviews are retained.')
    print('Stop the Django server first. A code backup will be made in your user folder.')
    if input('Type REMOVE SUS to continue, or press Enter to cancel: ').strip() != 'REMOVE SUS':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
