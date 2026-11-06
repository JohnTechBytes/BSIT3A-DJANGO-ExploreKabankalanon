"""Read-only export of the information visible on public place pages."""
import csv
from datetime import time
from pathlib import Path
from tempfile import TemporaryDirectory

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from apps.cities.models import City
from apps.core.models import Category
from apps.places.models import OpeningHours, Place
from tools.hobby_audit.report_visitor_details import address_status, export_report


class VisitorDetailsReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        other = City.objects.create(name='Other', slug='other')
        category = Category.objects.create(name='Cafes', slug='cafes')
        cls.place = Place.objects.create(city=city, title='=Cafe', slug='osm-node-12',
                                         category=category, address='Address not independently verified',
                                         phone='+63 123', email='hidden@example.com',
                                         is_active=True, is_verified=True)
        OpeningHours.objects.create(place=cls.place, weekday=0, open_time=time(8), close_time=time(17))
        OpeningHours.objects.create(place=cls.place, weekday=1, is_closed=True)
        Place.objects.create(city=city, title='Hidden', is_active=True, is_verified=False)
        Place.objects.create(city=city, title='Inactive', is_active=False, is_verified=True)
        Place.objects.create(city=other, title='Other City', is_active=True, is_verified=True)

    def test_export_public_scope_and_avoids_writes(self):
        places = (Place.objects.filter(city_id=2, is_active=True, is_verified=True)
                  .select_related('category').prefetch_related('opening_hours')
                  .only('id', 'city_id', 'title', 'slug', 'category__name', 'address',
                        'barangay', 'phone', 'email', 'website', 'latitude', 'longitude')
                  .order_by('title', 'pk'))
        with TemporaryDirectory() as tmp, CaptureQueriesContext(connection) as queries:
            path = Path(tmp) / 'visitor_information.csv'
            count = export_report(path, places)
            with path.open(encoding='utf-8-sig', newline='') as f:
                rows = list(csv.DictReader(f))
        self.assertEqual(count, 1)
        self.assertEqual(rows[0]['place'], "'=Cafe")
        self.assertEqual(rows[0]['contact_displayed'], "'+63 123")
        self.assertNotIn('hidden@example.com', str(rows))
        self.assertEqual(rows[0]['address_status'], 'Missing or placeholder; research needed')
        self.assertIn('Monday: 08:00-17:00', rows[0]['opening_hours'])
        self.assertIn('Tuesday: Closed', rows[0]['opening_hours'])
        self.assertTrue(all(q['sql'].lstrip().upper().startswith('SELECT') for q in queries))

    def test_empty_export_and_address_status_are_honest(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'empty.csv'
            self.assertEqual(export_report(path, []), 0)
            self.assertTrue(path.read_text(encoding='utf-8-sig').startswith('place_id,'))
        self.assertIn('Missing', address_status(''))
        self.assertEqual(address_status('12 Main Street'), 'Recorded; accuracy not verified')
