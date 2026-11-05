"""Offline tests for the read-only cafe review staging helper."""
import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from tools.photo_import import review_cafe_photos as review


def place(name, **overrides):
    values = dict(title=name, city_id=2, is_active=True, is_verified=True,
                  cover_image=None, cover_image_url='', photo_credit='',
                  photo_source_url='', photo_license='', photo_license_url='')
    values.update(overrides)
    return SimpleNamespace(**values)


class CafeReviewTests(unittest.TestCase):
    def test_eligibility_skips_mismatches_existing_covers_and_attribution(self):
        self.assertIn('not found', review.eligibility(None, 'Cafe'))
        self.assertIn('differs', review.eligibility(place('Other'), 'Cafe'))
        self.assertIn('differs', review.eligibility(place('Cafe', is_verified=False), 'Cafe'))
        self.assertIn('external cover', review.eligibility(place('Cafe', cover_image_url='https://example.com/a'), 'Cafe'))
        self.assertIn('attribution', review.eligibility(place('Cafe', photo_credit='Someone'), 'Cafe'))
        image = SimpleNamespace(name='places/covers/a.jpg', storage=SimpleNamespace(exists=lambda path: False))
        self.assertIn('file missing', review.eligibility(place('Cafe', cover_image=image), 'Cafe'))
        self.assertEqual(review.eligibility(place('Cafe'), 'Cafe'), '')

    def test_staging_never_writes_existing_or_unavailable_images_and_reports_failures(self):
        places = {pk: place(name) for pk, name, *_ in review.CAFES}
        places[7624].cover_image_url = 'https://example.com/existing.jpg'
        calls = []
        def download(url):
            calls.append(url)
            if 'Regals' in url:
                raise ValueError('network unavailable')
            return b'test image', (12, 34)
        with TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            folder = Path(tmp)
            rows = review.stage(folder, places, downloader=download)
            by_id = {r['id']: r for r in rows}
            self.assertEqual(len(rows), 9)
            self.assertIn('existing external', by_id[7624]['status'])
            self.assertIn('NO IMAGE LEAD', by_id[7622]['status'])
            self.assertIn('DOWNLOAD FAILED', by_id[7630]['status'])
            self.assertIn('STAGED', by_id[7623]['status'])
            self.assertFalse((folder / 'images' / '7624.jpg').exists())
            self.assertTrue((folder / 'images' / '7623.jpg').exists())
            self.assertTrue((folder / 'sources.csv').exists())
            self.assertTrue((folder / 'review.html').exists())
            self.assertEqual(len(calls), 5)  # six leads, one skipped existing cover

    def test_formula_cells_are_escaped(self):
        for value in ('=x', ' +x', '-x', '@x'):
            self.assertTrue(review.spreadsheet_safe(value).startswith("'"))
        self.assertEqual(review.spreadsheet_safe('Cafe'), 'Cafe')


if __name__ == '__main__':
    unittest.main()
