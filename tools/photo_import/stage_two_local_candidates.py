#!/usr/bin/env python3
"""Stage a small, rights-unverified photo batch for PRIVATE LOCAL TESTING ONLY.

This does not edit the database or import any photos. URLs and venue matches
are research leads, not verified permissions or verified image identities.
"""
import csv
import datetime
import html
import io
import os
import shutil
import sys
import urllib.request
import warnings
from pathlib import Path

# Research leads only. Gaisano/Unitop are 2008 watermarked search thumbnails;
# their photographer and rights are recorded as printed on those images.
CANDIDATES = [
    (7636, 'Gaisano Grand Mall Kabankalan', 'https://imgs.search.brave.com/VpUt5HQMo08ycWbeLrPQv73R3jw7N3hhKXl-pDAX8Bs/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly93d3cu/YW1ib3QtYWguY29t/L3dwL3dwLWNvbnRl/bnQvdXBsb2Fkcy8y/MDA4LzA0LzI0MDEz/NzcxNjlfZjJlNDc1/NDgwNi5qcGc', 'https://www.ambot-ah.com/west-central-negros-road-trip-first-time-in-kabankalan-april-2008/'),
    (7765, 'Unitop', 'https://imgs.search.brave.com/n8eTSzOFOUgUJxEgdbclTZ5ynUshdK6N0NpoTDmvpZI/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly93d3cu/YW1ib3QtYWguY29t/L3dwL3dwLWNvbnRl/bnQvdXBsb2Fkcy8y/MDA4LzA0LzI0MDIy/MDQ0ODZfNmE4NDI4/MTkzNi5qcGc', 'https://www.ambot-ah.com/west-central-negros-road-trip-first-time-in-kabankalan-april-2008/'),
]
RIGHTS = {
    7636: 'Image watermark: copyright Marcos Caratao Jr., all rights reserved. Permission not established; private local testing only.',
    7765: 'Image watermark: copyright Marcos Caratao Jr., all rights reserved. Permission not established; private local testing only.',
}

LIMIT = 20 * 1024 * 1024


def download_jpeg(url):
    from PIL import Image
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; LocalPhotoReview/1.0)'})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = response.read(LIMIT + 1)
    if not data or len(data) > LIMIT:
        raise ValueError('empty image or exceeds 20 MB')
    Image.MAX_IMAGE_PIXELS = 50_000_000
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as image:
            if image.format != 'JPEG':
                raise ValueError('response is not a JPEG image')
            size = image.size
            image.verify()
    return data, size


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file():
        raise SystemExit('Open PowerShell in the project folder containing manage.py.')
    importer = root / 'photo_import' / 'import_photos'
    if not importer.is_file():
        raise SystemExit('Missing photo_import/import_photos. No photos staged.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    import django
    django.setup()
    from django.conf import settings
    from apps.places.models import Place
    db = settings.DATABASES['default']
    if (db['ENGINE'] != 'django.db.backends.mysql' or db['NAME'] != 'exploreanywhere'
            or str(db.get('HOST', '')).lower() not in ('localhost', '127.0.0.1', '::1')):
        raise SystemExit('Stopped: expected local MySQL exploreanywhere database.')
    places = {p.pk: p for p in Place.objects.filter(pk__in=[x[0] for x in CANDIDATES])}
    directory = root / 'photo_import' / ('two_review_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    images = directory / 'images'
    images.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(importer, directory / 'import_photos')
    rows = []
    for pk, name, url, source in CANDIDATES:
        p = places.get(pk)
        status, dims = '', ''
        if not p or p.title != name or p.city_id != 2 or not p.is_active or not p.is_verified:
            status = 'SKIPPED: ID, title, city or publication status differs'
        elif p.cover_image or p.cover_image_url or any((p.photo_credit, p.photo_source_url, p.photo_license, p.photo_license_url)):
            status = 'SKIPPED: existing cover or attribution'
        else:
            try:
                data, (width, height) = download_jpeg(url)
                (images / f'{pk}.jpg').write_bytes(data)
                dims = f'{width} x {height}'
                status = 'STAGED: identity and rights still require review'
            except Exception as exc:
                status = 'FAILED: ' + str(exc)[:300]
        rows.append({'id': pk, 'place': name, 'status': status, 'size': dims, 'source_page': source, 'image_url': url, 'rights': RIGHTS[pk]})
        print(f'{pk} {name}: {status} {dims}', flush=True)
    with (directory / 'sources.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    e = html.escape
    cards = []
    for row in rows:
        img = f'<img src="images/{row["id"]}.jpg" alt="Candidate photo for {e(row["place"], quote=True)}">' if row['status'].startswith('STAGED:') else ''
        cards.append(f'<article><h2>{e(row["place"])} · {row["id"]}</h2>{img}<p>{e(row["status"])}</p><p>{e(row["size"])}</p><p>{e(row["rights"])}</p><a href="{e(row["source_page"], quote=True)}">Source page</a></article>')
    (directory / 'review.html').write_text('''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Local photo trial review</title><style>body{font:16px system-ui;margin:2rem;background:#f7f6ef;color:#153a2d}main{max-width:1100px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}article{background:white;padding:1rem;border-radius:12px}img{max-width:100%;height:200px;object-fit:contain}a{color:#076144}</style><main><h1>Private local photo trial</h1><p>Review each candidate as a batch before importing. The Gaisano and Unitop images are watermarked all rights reserved by Marcos Caratao Jr. Their reuse permission is not established. The cached images may differ from the source and require review. The 2008 images may be outdated; the Unitop image shows a street rather than a clear shop sign. Confirm subject and branch before use. Do not publish these images. Remove any wrong image from the images folder before the dry run. The CSV records source pages and the visible copyright notice.</p><div class="grid">''' + ''.join(cards) + '</div></main>', encoding='utf-8')
    print('\nNo database records or existing covers were changed.')
    print('Review folder:', directory)
    print('Open review.html and review all candidates. Sources are in sources.csv.')
    print('For a dry run from the project folder, run:')
    print(f'.\\.venv\\Scripts\\python.exe "{directory}\\import_photos"')
    print('Do not use --apply before reviewing and backing up the database and media.')


if __name__ == '__main__':
    main()
