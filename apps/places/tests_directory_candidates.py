import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, SimpleTestCase

from apps.cities.models import City
from apps.places.models import Place
from apps.places.management.commands.review_kabankalan_directory import (
    fetch_candidates, make_rows, safe_cell, overpass_request,
)


def mapped(kind, ident, name, **tags):
    return {'type': kind, 'id': ident, 'lat': 9.98, 'lon': 122.81,
            'tags': {'name': name, **tags}}


def candidate(item, *groups):
    return {'item': item, 'categories': set(groups)}


class CandidateHelpersTests(SimpleTestCase):
    @patch('apps.places.management.commands.review_kabankalan_directory.time.sleep')
    @patch('apps.places.management.commands.review_kabankalan_directory.overpass_request')
    def test_queries_each_group_and_deduplicates_osm_ids(self, request, sleep):
        shared = mapped('node', 1, 'Cafe Shop', shop='coffee')
        request.side_effect = [
            [{'type': 'area', 'id': 3600000042}],
            [mapped('way', 2, 'A Mall', shop='mall')],
            [mapped('node', 3, 'A Falls', natural='waterfall')],
            [shared], [shared],
        ]
        result = fetch_candidates(42, 'https://overpass-api.de/api/interpreter')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[('node', 1)]['categories'], {'food_cafes', 'shops_services'})
        self.assertEqual(request.call_count, 5)
        for call in request.call_args_list[1:]:
            self.assertIn('relation(42);map_to_area->.kab;', call.args[0])
            self.assertIn('nwr(area.kab)', call.args[0])

    @patch('apps.places.management.commands.review_kabankalan_directory.overpass_request')
    def test_missing_boundary_area_stops(self, request):
        request.return_value = []
        with self.assertRaises(CommandError):
            fetch_candidates(42, 'https://overpass-api.de/api/interpreter')
        self.assertEqual(request.call_count, 1)

    @patch('apps.places.management.commands.review_kabankalan_directory.urlopen')
    def test_partial_response_with_elements_is_rejected(self, urlopen):
        from io import BytesIO
        response = BytesIO(b'{"remark":"runtime error: timed out", "elements":[{"id":1}]}')
        urlopen.return_value.__enter__.return_value = response
        with self.assertRaisesMessage(CommandError, 'incomplete or invalid'):
            overpass_request('test query', 'https://overpass-api.de/api/interpreter')

    def test_flag_duplicates_and_school_names_without_hiding_shop_leads(self):
        combined = {
            ('node', 1): candidate(mapped('node', 1, 'One Shop', shop='convenience'), 'shops_services'),
            ('way', 2): candidate(mapped('way', 2, 'Other Shop', shop='convenience'), 'shops_services'),
            ('node', 3): candidate(mapped('node', 3, 'One Shop', shop='convenience'), 'shops_services'),
            ('node', 4): candidate(mapped('node', 4, 'School Supplies Store', shop='stationery'), 'shops_services'),
            ('node', 5): candidate(mapped('node', 5, 'A School', amenity='school', shop='stationery'), 'shops_services'),
        }
        existing = [{'id': 10, 'slug': 'osm-way-2', 'title': 'Other Shop'},
                    {'id': 11, 'slug': 'manual', 'title': 'One Shop'},
                    {'id': 12, 'slug': 'other', 'title': 'Other Shop'}]
        rows, excluded = make_rows(combined, existing)
        indexed = {(row['osm_type'], row['osm_id']): row for row in rows}
        self.assertEqual(excluded, 1)
        self.assertEqual(indexed[('way', 2)]['review_status'], 'existing_osm_id')
        self.assertEqual(indexed[('way', 2)]['possible_existing_ids'], '10, 12')
        self.assertIn('Same name exists', indexed[('way', 2)]['review_notes'])
        self.assertEqual(indexed[('node', 1)]['review_status'], 'possible_duplicate_name')
        self.assertIn('same name appears', indexed[('node', 1)]['review_notes'])
        self.assertEqual(indexed[('node', 4)]['review_status'], 'school_scope_review')
        self.assertEqual(indexed[('node', 1)]['possible_existing_ids'], '11')

    def test_spreadsheet_formula_text_is_neutralized(self):
        for value in ('=HYPERLINK("bad")', '+test', '-2+3', '@formula', '\t=1'):
            self.assertTrue(safe_cell(value).startswith("'"))
        self.assertEqual(safe_cell('Good Shop'), 'Good Shop')


class CandidateCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name='Kabankalan', province='Negros Occidental', slug='kabankalan')
        Place.objects.create(city=cls.city, title='Existing Shop', slug='manual', address='Kabankalan',
                             is_active=True, is_verified=True)

    @patch('apps.places.management.commands.review_kabankalan_directory.fetch_candidates')
    @patch('apps.places.management.commands.review_kabankalan_directory.discover_boundary_nominatim')
    def test_report_only_never_modifies_places(self, boundary, fetch):
        boundary.return_value = (42, 'Kabankalan', 'test')
        fetch.return_value = {
            ('node', 1): candidate(mapped('node', 1, 'Existing Shop', shop='clothes'), 'shops_services'),
            ('node', 2): candidate(mapped('node', 2, 'Another Falls', natural='waterfall'), 'waterfalls'),
        }
        before = list(Place.objects.values_list('id', 'title', 'is_verified', 'is_active'))
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'review.csv'
            call_command('review_kabankalan_directory', output=str(path), verbosity=0)
            with path.open(encoding='utf-8-sig', newline='') as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 2)
            existing = next(row for row in rows if row['name'] == 'Existing Shop')
            self.assertEqual(existing['review_status'], 'possible_duplicate_name')
            self.assertTrue(existing['possible_existing_ids'])
            self.assertTrue(existing['fetched_at_utc'])
            self.assertEqual(existing['boundary_relation_id'], '42')
            self.assertIn('OpenStreetMap contributors', existing['source_attribution'])
            self.assertIn('clothes', existing['osm_tags'])
            self.assertEqual(before, list(Place.objects.values_list('id', 'title', 'is_verified', 'is_active')))
            with self.assertRaises(CommandError):
                call_command('review_kabankalan_directory', output=str(path), verbosity=0)
            self.assertEqual(fetch.call_count, 1)

    @patch('apps.places.management.commands.review_kabankalan_directory.fetch_candidates')
    @patch('apps.places.management.commands.review_kabankalan_directory.discover_boundary_nominatim')
    def test_failed_fetch_does_not_write_a_partial_report(self, boundary, fetch):
        boundary.return_value = (42, 'Kabankalan', 'test')
        fetch.side_effect = CommandError('Partial response')
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / 'review.csv'
            with self.assertRaises(CommandError):
                call_command('review_kabankalan_directory', output=str(path), verbosity=0)
            self.assertFalse(path.exists())
