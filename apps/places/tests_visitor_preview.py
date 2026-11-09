"""The laptop visitor preview must not mutate any database records."""
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from apps.cities.models import City
from apps.core.models import Category
from apps.places.models import Place
from tools.visitor_updates.preview_visitor_changes import PROPOSALS, build_rows, write_report


class VisitorChangePreviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        cls.category = Category.objects.create(name='Cafe', slug='cafe')
        cls.place = Place.objects.create(city=city, title='Test Place', slug='osm-node-12',
                                         address='Address not independently verified',
                                         barangay='', phone='+63 1', email='real@example.com',
                                         category=cls.category, is_active=True, is_verified=True)

    def test_preview_reads_only_and_identifies_existing_fields(self):
        base = {'id': self.place.pk, 'title': 'Test Place', 'slug': 'osm-node-12',
                'notes': 'Source https://example.test/', 'document': 'review.md'}
        items = [dict(base, field='address', proposed='Street'),
                 dict(base, field='phone', proposed='+63 2'),
                 dict(base, field='email', proposed='real@example.com'),
                 dict(base, field='category', proposed='Coffee')]
        with CaptureQueriesContext(connection) as queries:
            places = {p.pk: p for p in Place.objects.filter(pk=self.place.pk).select_related('category')}
            rows = build_rows(places, items)
        self.assertTrue(all(q['sql'].lstrip().upper().startswith('SELECT') for q in queries))
        self.assertIn('PLACEHOLDER', rows[0]['comparison'])
        self.assertIn('EXISTING VALUE', rows[1]['comparison'])
        self.assertIn('ALREADY MATCHES', rows[2]['comparison'])
        self.assertIn('CATEGORY REVIEW ONLY', rows[3]['comparison'])
        self.place.refresh_from_db()
        self.assertEqual(self.place.address, 'Address not independently verified')
        self.assertEqual(self.place.phone, '+63 1')

    def test_identity_scope_and_formula_safety(self):
        item = {'id': self.place.pk, 'title': 'Test Place', 'slug': 'wrong',
                'field': 'phone', 'proposed': '=malicious()', 'notes': '+unsafe',
                'document': 'review.md'}
        rows = build_rows({self.place.pk: self.place}, [item])
        self.assertEqual(rows[0]['comparison'], 'NOT A CANDIDATE')
        self.assertEqual(rows[0]['existing_value'], '')
        item['slug'] = self.place.slug
        self.place.is_active = False
        self.assertEqual(build_rows({self.place.pk: self.place}, [item])[0]['comparison'], 'NOT A CANDIDATE')
        with TemporaryDirectory() as temp:
            report = Path(temp) / 'preview.csv'
            write_report(report, rows)
            with report.open(encoding='utf-8-sig', newline='') as stream:
                saved = list(csv.DictReader(stream))[0]
            self.assertEqual(saved['proposed_value'], "'=malicious()")
            self.assertEqual(saved['sources_and_caveats'], "'+unsafe")

    def test_manifest_has_unique_fields_and_public_research_links(self):
        self.assertEqual(len(PROPOSALS), 102)
        self.assertEqual(len({(p['id'], p['field']) for p in PROPOSALS}), len(PROPOSALS))
        self.assertEqual(len({p['id'] for p in PROPOSALS}), 58)
        self.assertTrue(all(p['slug'].startswith('osm-') for p in PROPOSALS))
        self.assertTrue(all('https://' in p['notes'] or 'http://' in p['notes'] for p in PROPOSALS))
