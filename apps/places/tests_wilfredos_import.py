"""Campsite importer tests: temporary SQLite and media, no real records."""
import hashlib
import importlib.util
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase, override_settings
from PIL import Image
from apps.cities.models import City
from apps.core.models import Category
from apps.places.models import Place

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('wilfredos_import', ROOT / 'tools/place_import/import_wilfredos.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class WilfredosImportTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.media = Path(self.temp.name) / 'media'
        self.settings = override_settings(MEDIA_ROOT=str(self.media))
        self.settings.enable()
        self.addCleanup(self.settings.disable)
        image = BytesIO()
        Image.new('RGB', (2, 2), 'green').save(image, format='PNG')
        self.image = image.getvalue()
        patcher1 = patch.object(updater, 'IMAGE_SIZE', len(self.image))
        patcher2 = patch.object(updater, 'IMAGE_HASH', hashlib.sha256(self.image).hexdigest())
        patcher1.start(); patcher2.start()
        self.addCleanup(patcher1.stop); self.addCleanup(patcher2.stop)
        self.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        self.category = Category.objects.create(name='Nature', slug='nature')
        self.other = Place.objects.create(city=self.city, title='Existing Mag-aso Falls', address='Existing address', is_verified=True, is_active=True)
        self.media.mkdir()
        (self.media / 'existing.png').write_bytes(b'existing media')

    def test_inserts_one_place_and_photo_then_refuses_duplicate(self):
        pk = updater.create_place(self.city.pk, self.category.pk, self.image)
        p = Place.objects.get(pk=pk)
        self.assertEqual(p.title, "Wilfredo's Campsite")
        self.assertEqual(p.latitude, Decimal('9.900833'))
        self.assertEqual(p.longitude, Decimal('122.894188'))
        self.assertEqual(p.category, self.category)
        self.assertTrue(p.is_active and p.is_verified)
        self.assertEqual(Path(p.cover_image.path).read_bytes(), self.image)
        self.assertIn('not independently verified', p.description)
        self.assertIn('PHP 400', p.description)
        self.assertEqual(p.photo_credit, 'Photo provided by the photographer')
        with self.assertRaisesRegex(ValueError, 'matching or nearby'):
            updater.create_place(self.city.pk, self.category.pk, self.image)
        self.assertEqual(Place.objects.count(), 2)
        self.other.refresh_from_db()
        self.assertEqual(self.other.address, 'Existing address')
        self.assertEqual((self.media / 'existing.png').read_bytes(), b'existing media')
        self.assertEqual(len(list((self.media / 'places/covers').glob('*.png'))), 1)

    def test_nearby_record_or_unpublished_name_stops_without_files(self):
        other = Place.objects.create(city=self.city, title='Nearby', address='x', latitude=Decimal('9.900900'), longitude=Decimal('122.894200'), is_active=False, is_verified=False)
        with self.assertRaisesRegex(ValueError, 'matching or nearby'):
            updater.create_place(self.city.pk, None, self.image)
        other.latitude = None; other.longitude = None; other.title = 'WILFREDO Campsite'; other.save()
        with self.assertRaisesRegex(ValueError, 'matching or nearby'):
            updater.create_place(self.city.pk, None, self.image)
        self.assertFalse((self.media / 'places').exists())

    def test_save_failure_removes_new_photo_only(self):
        with patch.object(Place, 'save', side_effect=RuntimeError('simulated save failure')):
            with self.assertRaisesRegex(RuntimeError, 'simulated'):
                updater.create_place(self.city.pk, self.category.pk, self.image)
        self.assertEqual(Place.objects.count(), 1)
        self.assertEqual(list((self.media / 'places/covers').glob('*.png')), [])
        self.assertEqual((self.media / 'existing.png').read_bytes(), b'existing media')

    def test_bad_photo_or_city_does_not_write(self):
        with self.assertRaisesRegex(ValueError, 'Photo verification failed'):
            updater.create_place(self.city.pk, None, b'not the supplied image')
        self.city.province = 'Other Province'; self.city.save(update_fields=['province'])
        with self.assertRaisesRegex(ValueError, 'not confirmed'):
            updater.create_place(self.city.pk, None, self.image)
        self.assertEqual(Place.objects.count(), 1)
        self.assertFalse((self.media / 'places').exists())

    def test_exact_local_photo_required(self):
        path = Path(self.temp.name) / 'provided.png'
        path.write_bytes(self.image)
        self.assertEqual(updater.read_photo(path), self.image)
        path.write_bytes(self.image[:-1] + b'X')
        with self.assertRaisesRegex(ValueError, 'does not match'):
            updater.read_photo(path)
