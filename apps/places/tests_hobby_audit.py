import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.places.models import Place
from tools.hobby_audit.report_published_hobbies import export_report


class HobbyAuditTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        cls.other_city = City.objects.create(name='Other', slug='other')
        cls.category = Category.objects.create(name='Cafés', slug='cafes')
        cls.tag = Hobby.objects.create(name='Café hopping', slug='cafe')
        cls.tagged = Place.objects.create(city=cls.city, title='Cafe A', address='Main St', category=cls.category, is_active=True, is_verified=True)
        cls.tagged.hobbies.add(cls.tag)
        cls.untagged = Place.objects.create(city=cls.city, title='=Danger', address='Other St', category=cls.category, is_active=True, is_verified=True)
        Place.objects.create(city=cls.city, title='Draft', address='', is_active=True, is_verified=False)
        Place.objects.create(city=cls.other_city, title='Other city', address='', is_active=True, is_verified=True)

    def test_export_scopes_public_places_and_does_not_write_to_database(self):
        places = (Place.objects.filter(city_id=2, is_active=True, is_verified=True)
                  .select_related('category').prefetch_related('hobbies').order_by('title', 'pk'))
        with TemporaryDirectory() as tmp, CaptureQueriesContext(connection) as queries:
            folder = Path(tmp)
            total, missing = export_report(folder, places)
            with (folder / 'places_and_hobbies.csv').open(encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f))
            with (folder / 'category_summary.csv').open(encoding='utf-8-sig', newline='') as f:
                categories = list(csv.DictReader(f))
            with (folder / 'hobby_summary.csv').open(encoding='utf-8-sig', newline='') as f:
                hobbies = list(csv.DictReader(f))
        self.assertEqual((total, missing), (2, 1))
        self.assertEqual({int(row['place_id']) for row in rows}, {self.tagged.pk, self.untagged.pk})
        self.assertEqual(next(row for row in rows if row['place_id'] == str(self.tagged.pk))['hobbies'], 'Café hopping')
        self.assertEqual(next(row for row in rows if row['place_id'] == str(self.untagged.pk))['place'], "'=Danger")
        self.assertEqual(categories[0]['without_hobby_tags'], '1')
        self.assertEqual(hobbies[0]['places_with_tag'], '1')
        self.assertTrue(all(q['sql'].lstrip().upper().startswith('SELECT') for q in queries))

    def test_empty_export_has_headers(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual(export_report(folder, []), (0, 0))
            self.assertTrue((folder / 'places_and_hobbies.csv').read_text(encoding='utf-8-sig').startswith('place_id,'))
