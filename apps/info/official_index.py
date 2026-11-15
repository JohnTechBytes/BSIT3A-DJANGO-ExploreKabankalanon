"""Read-only index of the official site's user-supplied public sitemaps.

These are URLs, not copies of the records themselves. Sitemap membership does
not prove that a linked page remains available, complete or current.
"""
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote, urlsplit

SNAPSHOT = Path(__file__).resolve().parent / 'data' / 'official_sitemap_snapshot.json'
KINDS = {'page': 'Page', 'post': 'Post', 'category': 'Category archive'}

# The sitemaps do not contain article categories or full content. These are
# word matches in URL paths, not official classifications; multiple topics may
# match a URL and an unrecognisable slug stays under Other / unclassified.
TOPIC_RULES = {
    'tourism': ('tourism', 'tourist', 'eco tourism', 'cultural heritage', 'sinulog', 'udyakan', 'festival', 'festivals', 'resort', 'resorts', 'falls', 'attraction', 'attractions'),
    'barangays': ('barangay', 'barangays', 'city profile', 'about us', 'history', 'city seal', 'city hymn', 'vision and mission', 'maps'),
    'services': ('citizens charter', 'office', 'offices', 'services', 'health', 'hospital', 'registrar', 'permit', 'contact', 'directory', 'job', 'employment'),
    'documents': ('ordinance', 'ordinances', 'resolution', 'resolutions', 'executive order', 'executive orders', 'memorandum', 'financial documents', 'full disclosure', 'transparency'),
    'resolutions': ('resolution', 'resolutions'),
    'ordinances': ('ordinance', 'ordinances', 'executive order', 'executive orders', 'memorandum'),
    'procurement': ('bid', 'bids', 'bidding', 'itb', 'notice of award', 'notice of awards', 'procurement'),
    'community': ('news', 'updates', 'announcement', 'happening', 'community', 'celebration'),
}
TOPICS = {
    'tourism': 'Tourism and festivals',
    'barangays': 'Barangays and city profile',
    'services': 'City services and offices',
    'documents': 'All official documents',
    'resolutions': 'Resolutions',
    'ordinances': 'Ordinances, orders and memoranda',
    'procurement': 'Bids and awards',
    'community': 'News and community',
    'other': 'Other / unclassified',
}


def normalized(value):
    return unicodedata.normalize('NFKC', value).casefold()


def topics_for_path(path):
    # Word boundaries avoid treating, for example, "bid" inside another word
    # as a procurement item. The URL has already been percent-decoded.
    words = ' ' + re.sub(r'[\W_]+', ' ', normalized(path)).strip() + ' '
    matched = tuple(topic for topic, phrases in TOPIC_RULES.items()
                    if any(' ' + phrase + ' ' in words for phrase in phrases))
    return matched or ('other',)


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
                        'topics': topics_for_path(path),
                        'search': normalized(label + ' ' + url)})
    return tuple(entries)


def search_entries(query, kind, topic=''):
    term = normalized(query.strip())
    return [entry for entry in sitemap_entries()
            if (not kind or entry['kind'] == kind)
            and (not topic or topic in entry['topics'])
            and (not term or term in entry['search'])]
