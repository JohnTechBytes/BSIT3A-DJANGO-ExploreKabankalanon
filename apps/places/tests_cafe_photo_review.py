"""The café photo review can inspect catalogue data without changing it."""
import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from apps.cities.models import City
from apps.places.models import Place
from tools.photo_import import review_cafe_photos as review


class CafePhotoReviewTests(TestCase):
    def test_review_reads_existing_places_without_writing_them(self):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        for pk, name, *_ in review.CAFES:
            Place.objects.create(pk=pk, city=city, title=name, is_active=True, is_verified=True)
        Place.objects.filter(pk=7631).update(cover_image='places/covers/existing.jpg')
        with TemporaryDirectory() as temp, override_settings(MEDIA_ROOT=temp), contextlib.redirect_stdout(io.StringIO()):
            with CaptureQueriesContext(connection) as queries:
                places = {p.pk: p for p in Place.objects.filter(pk__in=[x[0] for x in review.CAFES])}
                rows = review.stage(Path(temp), places, downloader=lambda url: (b'fake', (30, 40)))
            self.assertTrue(all(q['sql'].lstrip().upper().startswith('SELECT') for q in queries.captured_queries))
            by_id = {row['id']: row for row in rows}
            self.assertIn('file missing from this project media', by_id[7631]['status'])
            self.assertFalse((Path(temp) / 'images' / '7631.jpg').exists())
            self.assertEqual(Place.objects.get(pk=7631).cover_image.name, 'places/covers/existing.jpg')
            self.assertFalse(Place.objects.get(pk=7623).cover_image)

    def test_download_validation_requires_jpeg(self):
        from PIL import Image
        image_bytes = io.BytesIO()
        Image.new('RGB', (3, 2), 'red').save(image_bytes, format='JPEG')
        class Response:
            def __init__(self, data):
                self.data = data
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, limit):
                return self.data[:limit]
        with patch.object(review.urllib.request, 'urlopen', return_value=Response(image_bytes.getvalue())):
            data, size = review.download_jpeg('https://example.com/image.jpg')
            self.assertEqual(size, (3, 2))
            self.assertEqual(data, image_bytes.getvalue())
        with patch.object(review.urllib.request, 'urlopen', return_value=Response(b'not an image')):
            with self.assertRaises(Exception):
                review.download_jpeg('https://example.com/image.jpg')
