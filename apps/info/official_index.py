"""Read-only index of the official site's user-supplied public sitemaps.

These are URLs, not copies of the records themselves. Sitemap membership does
not prove that a linked page remains available, complete or current.
"""
import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote, urlsplit

SNAPSHOT = Path(__file__).resolve().parent / 'data' / 'official_sitemap_snapshot.json'
KINDS = {'page': 'Page', 'post': 'Post', 'category': 'Category archive'}


def normalized(value):
    return unicodedata.normalize('NFKC', value).casefold()


@lru_cache(maxsize=1)
def sitemap_entries():
    data = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    entries = []
    for url, kind, last_modified in data['entries']:
        parts = urlsplit(url)
        if parts.scheme != 'https' or parts.netloc != 'kabankalancity.gov.ph' or parts.query or parts.fragment or kind not in KINDS:
            raise ValueError('Unexpected official sitemap entry')
        # A readable URL path is not necessarily the document's actual title.
        path = unicodedata.normalize('NFKC', unquote(parts.path)).strip('/')
        label = path.replace('-', ' ').replace('_', ' ').replace('/', ' / ') or 'City government homepage'
        entries.append({'url': url, 'label': label, 'kind': kind,
                        'kind_label': KINDS[kind], 'modified': last_modified,
                        'search': normalized(label + ' ' + url)})
    return tuple(entries)


def search_entries(query, kind):
    term = normalized(query.strip())
    return [entry for entry in sitemap_entries()
            if (not kind or entry['kind'] == kind) and (not term or term in entry['search'])]
