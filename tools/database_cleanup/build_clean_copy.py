#!/usr/bin/env python3
"""Produce a separate cleaned phpMyAdmin SQL dump; never connect to a database.

Only reviewed CREATE/INSERT/ALTER statements for the nine approved tables are
removed. Other statements remain byte-for-byte unchanged. The added migration
records match the code version that removed these tables. Keep the original
export and never import the output over an existing database.
"""
import argparse
from collections import Counter
from pathlib import Path
import re

TARGETS = frozenset({
    'explore_itinerary_stops', 'explore_itineraries', 'explore_visit_checkins',
    'dashboard_itinerary_places', 'dashboard_user_itineraries',
    'dashboard_saved_places', 'dashboard_search_history', 'dashboard_user_hobbies',
    'dashboard_user_reviews',
})
MIGRATIONS = (('core', '0002_legacy_removal_guard'),
              ('itineraries', '0003_remove_itineraries'),
              ('visits', '0002_remove_visits'),
              ('core', '0003_remove_legacy_dashboard'))


def statements(raw):
    """Split on semicolons outside SQL strings, backtick names and comments."""
    start = i = 0
    state = None
    while i < len(raw):
        c = raw[i]
        n = raw[i + 1] if i + 1 < len(raw) else 0
        if state in (39, 34, 96):
            if c == 92 and state != 96:
                i += 2
                continue
            if c == state:
                if n == state:
                    i += 2
                    continue
                state = None
        elif state == 'line':
            if c in (10, 13):
                state = None
        elif state == 'block':
            if c == 42 and n == 47:
                state = None
                i += 2
                continue
        elif c in (39, 34, 96):
            state = c
        elif c == 35 or (c == 45 and n == 45 and (i + 2 == len(raw) or raw[i + 2] in b' \t\r\n')):
            state = 'line'
        elif c == 47 and n == 42:
            state = 'block'
            i += 2
            continue
        elif c == 59:
            yield raw[start:i + 1]
            start = i + 1
        i += 1
    if state in (39, 34, 96, 'block'):
        raise ValueError('Unterminated SQL string or comment; no output written')
    if start < len(raw):
        yield raw[start:]


def unprefixed(statement):
    # Remove only leading whitespace/comments to identify the SQL command.
    return re.sub(rb'\A(?:\s+|--[^\r\n]*(?:\r?\n|\Z)|#[^\r\n]*(?:\r?\n|\Z)|/\*(?!\!)[\s\S]*?\*/)*', b'', statement)


def build(raw):
    kept = []
    removed = Counter()
    creates = set()
    for part in statements(raw):
        command = unprefixed(part)
        m = re.match(rb'(CREATE\s+TABLE|INSERT\s+INTO|ALTER\s+TABLE)\s+`([^`]+)`', command, re.I)
        # This tool deliberately accepts only the reviewed dump structure.
        # Variants such as INSERT IGNORE or CREATE TABLE IF NOT EXISTS need
        # manual review instead of potentially leaving references behind.
        if re.match(rb'(?:CREATE|INSERT|ALTER)\b', command, re.I) and not m:
            raise ValueError('Unsupported CREATE/INSERT/ALTER statement; review required')
        if m and m.group(2).decode('ascii') in TARGETS:
            table = m.group(2).decode('ascii')
            removed[table] += 1
            if m.group(1).upper().startswith(b'CREATE'):
                if table in creates:
                    raise ValueError('Duplicate target CREATE TABLE: ' + table)
                creates.add(table)
            continue
        # Do not silently preserve an unfamiliar operation on a target table.
        other = re.match(rb'(?:DROP\s+TABLE(?:\s+IF\s+EXISTS)?|REPLACE\s+INTO|UPDATE|DELETE\s+FROM|TRUNCATE(?:\s+TABLE)?)\s+`([^`]+)`', command, re.I)
        if other and other.group(1).decode('ascii') in TARGETS:
            raise ValueError('Unexpected SQL operation on target table; review required')
        if m and m.group(1).upper().startswith(b'ALTER') and m.group(2).decode('ascii') not in TARGETS:
            for target in TARGETS:
                if re.search(rb'REFERENCES\s+`' + target.encode() + rb'`', command, re.I):
                    raise ValueError('A retained table references an approved removal table: ' + target)
        kept.append(part)
    if creates != TARGETS:
        raise ValueError('Unexpected set of target CREATE TABLE statements; review required')
    joined = b''.join(kept)
    if not re.search(rb'CREATE\s+TABLE\s+`django_migrations`', joined, re.I):
        raise ValueError('Migration recorder missing')
    for app, migration in MIGRATIONS:
        if migration.encode() in joined:
            raise ValueError('Removal migration is already present in the input')
    values = ',\n'.join("('%s','%s',CURRENT_TIMESTAMP)" % pair for pair in MIGRATIONS)
    marker = ('\n-- Records for the reviewed removal migrations; original export preserved separately.\n'
              'INSERT INTO `django_migrations` (`app`,`name`,`applied`) VALUES\n' + values + ';\n').encode()
    return joined + marker, removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        raise SystemExit('Refusing to overwrite an existing file or the input')
    try:
        result, removed = build(args.input.read_bytes())
        # Exclusive creation; default to user-only access on Unix.
        import os
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as f:
            f.write(result)
    except Exception as exc:
        raise SystemExit('STOPPED: ' + str(exc))
    print('Wrote separate cleaned copy:', args.output)
    print('Removed SQL statements from', len(removed), 'approved tables; no database was modified.')

if __name__ == '__main__':
    main()
