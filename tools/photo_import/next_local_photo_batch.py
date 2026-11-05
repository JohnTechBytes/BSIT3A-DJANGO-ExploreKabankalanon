#!/usr/bin/env python3
"""Run the tested local-only batch tool with the next research leads."""
import hashlib
from pathlib import Path

BASE_HASH = 'aace23984f1aa81247870638a1dcf30b61fa0e5046fb8992bf6a65614e29b346'
CANDIDATES = [
    (7623, 'Coffee & Talk', 'https://img02.restaurantguru.com/c5ac-Restaurant-Coffee-and-Talk-interior.jpg', 'https://restaurantguru.com/Coffee-and-Talk-Kabankalan'),
    (7624, 'Cofioca', 'https://img02.restaurantguru.com/caca-Restaurant-Cofioca-Kabankalan-exterior.jpg', 'https://restaurantguru.com/Cofioca-Kabankalan-Kabankalan'),
    (7625, 'daily brew', 'https://img02.restaurantguru.com/c0f7-Daily-Brew-Coffee-House-Kabankalan-interior.jpg', 'https://restaurantguru.com/Daily-Brew-Kabankalan'),
    (7654, 'BPI', 'https://lh3.googleusercontent.com/grass-cs/AABkmLfrjtC9lFlwJ5IyAlkjJOvXI60v0smjXdFUIZ-SEfftXZeSvYsg1mz_WULkEpqsQqZib19MiB1jTkVAlSHHUILDg5sTqJ3hq4Ybe_DO3BcZIx6yCUv_9_sbTSRrFR252fBjcx8=s1600-w100', 'https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/bpi-negros-kabankalan-branch?to=place.ChIJ9-eGOSgRrDMRAb4rVF1ANlQ'),
    (7687, 'Holy Mother of Mercy Hospital', 'https://lh3.googleusercontent.com/grass-cs/AABkmLexwv30dncga2pz8549Q4HpN-AspsEuYOrKYfO265RJSyutmAwOmtn9605OgpSQcgHFhd8yMxwWdMRR7uNMKPMn79DzPxM1BUTbt94Nz69yPrU-cx_fpTJdFtP2T7MCYcqtRplAtw=s1600-w100', 'https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/holy-mother-of-mercy-hospital?to=place.ChIJsRJTjzoRrDMRGP9JkBANVgI'),
    (7688, 'Honda 3S Shop', 'https://lh3.googleusercontent.com/grass-cs/AABkmLez8FAQWOTCGbZzezN6KDGvH5-IrSmgQ7neWiztFrIYq8Wr6pc1_J1ZfI2fV2iqzOo7FxSb37Wx_wvB18WgSfqzlyL1EG-oaRwWsSIXEvvDFV0MsYUJ0C3LPBMJaCoBi_QqTwODCYRKZmk=s1600-w100', 'https://www.waze.com/live-map/directions/ph/western-visayas/kabankalan-city/du-ek-sam,-inc.-(honda-3s-shop)?to=place.ChIJuXEYfSkRrDMRNLv7DGvCOtY'),
    (7779, 'De La Gente Pizza', 'https://img02.restaurantguru.com/ce01-Pizzeria-Mama-Marias-Pizza-picture.jpg', 'https://restaurantguru.com/De-La-Gente-Pizzaformerly-MAMMA-MARIAS-PIZZA-Kabankalan'),
]


def main():
    base = Path.cwd() / 'photo_import' / 'review_and_import_local_batch.py'
    if not base.is_file():
        raise SystemExit('Previous batch tool is missing; no photos imported.')
    data = base.read_bytes()
    if hashlib.sha256(data).hexdigest() != BASE_HASH:
        raise SystemExit('Previous batch tool differs from the tested version; no photos imported.')
    namespace = {'__name__': 'verified_local_batch', '__file__': str(base)}
    exec(compile(data, str(base), 'exec'), namespace)
    namespace['CANDIDATES'] = CANDIDATES
    original_report = namespace['write_report']

    def report_with_privacy_note(folder, rows, count):
        original_report(folder, rows, count)
        page = folder / 'review.html'
        content = page.read_text(encoding='utf-8')
        notice = '<p><strong>Privacy:</strong> Do not import photos showing identifiable patients or personal medical information.</p>'
        page.write_text(content.replace('<div class="grid">', notice + '<div class="grid">', 1), encoding='utf-8')

    namespace['write_report'] = report_with_privacy_note
    namespace['main']()


if __name__ == '__main__':
    main()
