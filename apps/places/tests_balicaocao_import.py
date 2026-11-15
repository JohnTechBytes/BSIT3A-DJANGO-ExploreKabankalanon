"""One-place importer tests run only against Django's temporary test database."""
import importlib.util
from decimal import Decimal
from pathlib import Path

from django.test import TestCase
from apps.cities.models import City
from apps.core.models import Category
from apps.places.models import Place

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('balicaocao_import', ROOT / 'tools/place_import/import_balicaocao.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class BalicaocaoImportTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        self.category = Category.objects.create(name='Nature', slug='nature')
        self.other = Place.objects.create(city=self.city, title='Existing place', address='Existing address', is_verified=True, is_active=True)

    def test_adds_only_one_place_then_refuses_duplicate(self):
        pk = updater.create_place(self.city.pk, self.category.pk)
        place = Place.objects.get(pk=pk)
        self.assertEqual(place.title, 'Balicaocao Eco-Park')
        self.assertEqual(place.latitude, Decimal('9.956680'))
        self.assertEqual(place.longitude, Decimal('122.858250'))
        self.assertEqual(place.category, self.category)
        self.assertTrue(place.is_active and place.is_verified)
        self.assertFalse(place.cover_image)
        self.assertFalse(place.cover_image_url)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            updater.create_place(self.city.pk, self.category.pk)
        self.assertEqual(Place.objects.count(), 2)
        self.other.refresh_from_db()
        self.assertEqual(self.other.address, 'Existing address')

    def test_unpublished_name_variant_stops_import(self):
        Place.objects.create(city=self.city, title='Balicao-cao Mountain Resort', address='x', is_active=False, is_verified=False)
        matches = updater.find_candidates(self.city)
        self.assertEqual(len(matches), 1)
        with self.assertRaisesRegex(ValueError, 'already exists'):
            updater.create_place(self.city.pk)
        self.assertEqual(Place.objects.count(), 2)

    def test_nearby_differently_named_record_stops_import(self):
        Place.objects.create(city=self.city, title='Different Name', address='x', latitude=Decimal('9.956900'), longitude=Decimal('122.858500'), is_active=False, is_verified=False)
        with self.assertRaisesRegex(ValueError, 'nearby'):
            updater.create_place(self.city.pk)
        self.assertEqual(Place.objects.count(), 2)

    def test_unrecognized_city_and_bad_category_do_not_write(self):
        self.city.province = 'Other Province'
        self.city.save(update_fields=['province'])
        with self.assertRaisesRegex(ValueError, 'not confirmed'):
            updater.create_place(self.city.pk)
        self.city.province = 'Negros Occidental'
        self.city.save(update_fields=['province'])
        with self.assertRaises(Category.DoesNotExist):
            updater.create_place(self.city.pk, -1)
        self.assertEqual(Place.objects.count(), 1)
