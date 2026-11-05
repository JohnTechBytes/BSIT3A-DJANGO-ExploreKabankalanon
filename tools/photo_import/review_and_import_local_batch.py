#!/usr/bin/env python3
"""Review a small research batch and optionally import it into local testing only.

Place matches and image rights are NOT verified. This is not a publication tool.
"""
import csv
import datetime
import hashlib
import html
import io
import os
import shutil
import subprocess
import sys
import urllib.request
import warnings
import webbrowser
from pathlib import Path

# Listings name the place and (where checked) are close to the historical
# inventory pin. Listings can be stale, have incorrect photos, or move. The
# gallery requires explicit human review before any import.
CANDIDATES = [
    (7630, 'Regals Refreshments', 'https://img02.restaurantguru.com/c2d3-Restaurant-Regals-exterior.jpg', 'https://restaurantguru.com/Regals-Kabankalan'),
    (7631, "Sol's Garden Café", 'https://img02.restaurantguru.com/c824-Sols-Garden-Cafe-Kabankalan-view.jpg', 'https://restaurantguru.com/Sols-Garden-Cafe-Kabankalan'),
    (7709, "Lopue's", 'https://lh3.googleusercontent.com/grass-cs/AABkmLfg_KOK8BVdvqqtY0DyNO_ZDAA7yxmf7U_Uf_yJkx7rPPU8YwY-Iq1mwp90O0FahLltnQKwcjTIWfvb0j_er1LZxF3wFj2iCQJL1653tSb3MwqFtr4LmeRyCgBxyHSfz1oMbvPK=s1600-w100', 'https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/lopues-department-store?to=place.ChIJzcrDwtYQrDMRxORj77TFoUk'),
    (7739, 'Puregold', 'https://venue-image.waze.com/thumbs/thumb100_80c5c42f-305f-4a49-a567-9fab3e259182', 'https://www.waze.com/live-map/directions/puregold-kabankalan-guanzon?to=place.w.80478308.804848615.17494056'),
    (7765, 'Unitop', 'https://lh3.googleusercontent.com/grass-cs/AABkmLei_q7l1PdGTRRYEPYVo7gfNKjS4_isfbupwkUryRBz7lj5BORQzZVD5_k-bAWMZ3PSuK_-MT4lYnyELP4jrZV-iJJzYREOAdeAkyycd56SBt3rii9slh3YYCK72Rv-kMlTJnzq=s1600-w100', 'https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/unitop?to=place.ChIJ_QFuEygRrDMRK5bYhWkuHMk'),
    (7780, 'Golden Plate Pizza', 'https://img02.restaurantguru.com/c18d-Restaurant-Golden-Plate-Pizza-Kabankalan-interior.jpg', 'https://restaurantguru.com/Golden-Plate-Pizza-Kabankalan-Kabankalan'),
    (7790, 'Perico', 'https://img02.restaurantguru.com/cb3b-Perico-Restaurant-and-Travel-Beans-Kabankalan-interior.jpg', 'https://restaurantguru.com/Perico-Kabankalan'),
]
IMPORTER_HASH = 'c3ca2bb6432f930095417b515d10ca85b6e8b9e8861c33cb6841e3338a9db949'
LIMIT = 20 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def eligibility(place, name):
    if not place or place.title != name or place.city_id != 2 or not place.is_active or not place.is_verified:
        return 'ID, title, city or publication status differs'
    if place.cover_image or place.cover_image_url or any((place.photo_credit, place.photo_source_url, place.photo_license, place.photo_license_url)):
        return 'existing cover or attribution'
    return ''


def download_jpeg(url):
    from PIL import Image
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; LocalPhotoReview/1.0)'})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read(LIMIT + 1)
    if not data or len(data) > LIMIT:
        raise ValueError('empty image or over 20 MB')
    Image.MAX_IMAGE_PIXELS = 50_000_000
    with warnings.catch_warnings():
        warnings.simplefilter('error', Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as image:
            if image.format != 'JPEG':
                raise ValueError('response is not a JPEG')
            size = image.size
            image.verify()
    return data, size


def write_report(folder, rows, missing_count):
    with (folder / 'sources.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['id', 'place', 'status', 'size', 'source_page', 'image_url', 'rights', 'sha256'])
        writer.writeheader()
        writer.writerows(rows)
    esc = html.escape
    cards = []
    for row in rows:
        img = f'<img src="images/{row["id"]}.jpg" alt="Candidate for {esc(row["place"], quote=True)}">' if row['sha256'] else ''
        cards.append(f'<article><h2>{esc(row["place"])} · {row["id"]}</h2>{img}<p>{esc(row["status"])} {esc(row["size"])}</p><a href="{esc(row["source_page"], quote=True)}">Source listing</a></article>')
    page = '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Local test photo batch</title><style>body{font:16px system-ui;margin:2rem;background:#f7f6ef;color:#153a2d}main{max-width:1100px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}article{background:white;padding:1rem;border-radius:12px}img{max-width:100%;height:220px;object-fit:contain}a{color:#076144}</style><main><h1>Private local photo review</h1><p>These are unverified research leads, not licensed or independently verified photos. Check every visible image for the right place/branch, image quality and watermarks. Some are tiny thumbnails or show an interior. Do not publish without permission. Remove any unsuitable file from the images folder; do not add or edit files. Then return to PowerShell and choose whether to import the rest. Sources are recorded in sources.csv.</p><p>Current missing-cover count before this batch: ''' + str(missing_count) + '''. Only these few have candidates; the rest remain incomplete.</p><div class="grid">''' + ''.join(cards) + '</div></main>'
    (folder / 'review.html').write_text(page, encoding='utf-8')


def backup(root):
    dump = Path(r'C:\xampp\mysql\bin\mysqldump.exe')
    media = root / 'media'
    if not dump.is_file() or not media.is_dir():
        raise ValueError('XAMPP mysqldump or project media directory missing')
    folder = Path.home() / ('EK_backup_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    folder.mkdir(exist_ok=False)
    sql = folder / 'exploreanywhere.sql'
    result = subprocess.run([str(dump), '--host=127.0.0.1', '--port=3306', '--user=root', '--single-transaction', '--routines', '--triggers', '--result-file=' + str(sql), 'exploreanywhere'], check=False)
    if result.returncode != 0 or not sql.is_file() or sql.stat().st_size == 0:
        raise ValueError('database backup failed; nothing imported')
    shutil.copytree(media, folder / 'media')
    print('Backup saved to:', folder, flush=True)
    return folder


def main():
    root = Path.cwd()
    if not (root / 'manage.py').is_file():
        raise SystemExit('Open PowerShell in the project folder containing manage.py.')
    importer = root / 'photo_import' / 'import_photos'
    if not importer.is_file() or sha(importer.read_bytes()) != IMPORTER_HASH:
        raise SystemExit('Importer missing or differs from the tested version. No changes made.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    import django
    django.setup()
    from django.conf import settings
    from apps.places.models import Place
    db = settings.DATABASES['default']
    if (db['ENGINE'] != 'django.db.backends.mysql' or db['NAME'] != 'exploreanywhere' or str(db.get('HOST', '')).lower() not in ('localhost', '127.0.0.1', '::1')):
        raise SystemExit('Stopped: expected local MySQL exploreanywhere database.')
    places = {p.pk: p for p in Place.objects.filter(pk__in=[x[0] for x in CANDIDATES])}
    # Covers may be stored either as uploaded files or external URLs.
    missing_count = sum(not p.cover_image and not p.cover_image_url for p in Place.objects.filter(city_id=2, is_active=True, is_verified=True))
    folder = root / 'photo_import' / ('bulk_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    images = folder / 'images'
    images.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(importer, folder / 'import_photos')
    rows = []
    for pk, name, url, source in CANDIDATES:
        problem = eligibility(places.get(pk), name)
        status, size, digest = '', '', ''
        if problem:
            status = 'SKIPPED: ' + problem
        else:
            try:
                data, (width, height) = download_jpeg(url)
                (images / f'{pk}.jpg').write_bytes(data)
                size, digest, status = f'{width} x {height}', sha(data), 'STAGED: identity and rights require review'
            except Exception as exc:
                status = 'FAILED: ' + str(exc)[:300]
        print(f'{pk} {name}: {status} {size}', flush=True)
        rows.append({'id': pk, 'place': name, 'status': status, 'size': size, 'source_page': source, 'image_url': url, 'rights': 'Unknown; private local testing only', 'sha256': digest})
    write_report(folder, rows, missing_count)
    print('\nCurrent missing-cover count before this batch:', missing_count)
    print('Only the listed research leads have candidates. Many places remain without photos.')
    print('Review folder:', folder)
    if not any(row['sha256'] for row in rows):
        raise SystemExit('No images staged. No database changes made.')
    print('Opening review.html. Check the images. Delete unsuitable photos from the images folder.\nDo NOT add or edit files. Close Django server; leave XAMPP MySQL running.')
    try:
        webbrowser.open((folder / 'review.html').as_uri())
    except Exception:
        print('Open review.html manually in the folder printed above.')
    answer = input('\nType IMPORT LOCAL to confirm the remaining images match and are for private testing only (anything else cancels): ').strip()
    if answer != 'IMPORT LOCAL':
        raise SystemExit('Cancelled. No database changes made.')
    staged = {f'{row["id"]}.jpg': row for row in rows if row['sha256']}
    selected = list(images.iterdir())
    if not selected:
        raise SystemExit('No images selected. No database changes made.')
    for path in selected:
        if path.is_symlink() or not path.is_file() or path.name not in staged or sha(path.read_bytes()) != staged[path.name]['sha256']:
            raise SystemExit('Files were added or changed after review. Stopped without importing.')
    names = {int(row['id']): row['place'] for row in rows if row['sha256'] and (images / f'{row["id"]}.jpg').exists()}
    current = {p.pk: p for p in Place.objects.filter(pk__in=names)}
    for pk, name in names.items():
        problem = eligibility(current.get(pk), name)
        if problem:
            raise SystemExit(f'ID {pk}: {problem}; stopped without importing.')
    if sha((folder / 'import_photos').read_bytes()) != IMPORTER_HASH:
        raise SystemExit('Importer changed after review. Stopped without importing.')
    backup(root)
    if sha((folder / 'import_photos').read_bytes()) != IMPORTER_HASH:
        raise SystemExit('Importer changed during backup. Stopped without importing.')
    for args in ([], ['--apply']):
        result = subprocess.run([sys.executable, str(folder / 'import_photos'), *args], cwd=root, check=False)
        if result.returncode:
            raise SystemExit('Importer stopped. Check its output above.')
    print('Keep the review folder and sources.csv as the provenance record. Do not publish these images without permission.')


if __name__ == '__main__':
    main()
