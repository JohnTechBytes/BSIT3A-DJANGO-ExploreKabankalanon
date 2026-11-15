"""Festival import safety tests, using only Django's disposable test database."""
import importlib.util
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation
from apps.places.models import Place

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('festival_import', ROOT / 'tools/city_info_import/import_festivals.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class FestivalImportTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        self.existing = CityInformation.objects.create(city=self.city, title='Existing guide', info_type='food',
                                                        description='Existing text', is_published=True)
        self.place = Place.objects.create(city=self.city, title='Existing place', is_active=True, is_verified=True)

    def test_adds_two_published_events_once_and_displays_them(self):
        before = list(CityInformation.objects.values().order_by('pk'))
        place_before = list(Place.objects.values().order_by('pk'))
        ids = updater.add_guides(self.city.pk)
        self.assertEqual(len(ids), 2)
        entries = list(CityInformation.objects.filter(pk__in=ids).order_by('order'))
        self.assertEqual([e.title for e in entries], ['Sinulog sa Kabankalan', 'Udyakan sa Kabankalan'])
        self.assertTrue(all(e.info_type == 'event' and e.is_published for e in entries))
        self.assertTrue(all(not e.thumbnail_url and not e.photo_credit for e in entries))
        self.assertEqual(list(CityInformation.objects.filter(pk=self.existing.pk).values()), before)
        self.assertEqual(list(Place.objects.values().order_by('pk')), place_before)
        response = self.client.get(reverse('info:city_information'), {'section': 'event'})
        self.assertContains(response, 'Sinulog sa Kabankalan')
        self.assertContains(response, 'Udyakan sa Kabankalan')
        self.assertContains(response, 'Event / Festival')
        with self.assertRaisesRegex(ValueError, 'possible existing'):
            updater.add_guides(self.city.pk)
        self.assertEqual(CityInformation.objects.count(), 3)

    def test_published_or_unpublished_duplicate_or_description_blocks_both(self):
        for title, description, published in (
            ('The Sinulog festival', 'An event', True),
            ('Udyakan', 'A cultural celebration', False),
            ('Local celebration', 'About the Udyakan event', False),
        ):
            candidate = CityInformation.objects.create(city=self.city, title=title, info_type='attraction',
                                                        description=description, is_published=published)
            with self.assertRaisesRegex(ValueError, 'possible existing'):
                updater.add_guides(self.city.pk)
            self.assertEqual(CityInformation.objects.count(), 2)
            candidate.delete()

    def test_storage_guard_requires_innodb_and_no_insert_trigger(self):
        from unittest.mock import MagicMock
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.side_effect = [
            [('explore_cities', 'InnoDB'), ('explore_city_information', 'InnoDB')], []
        ]
        updater.check_storage(connection)
        cursor.fetchall.side_effect = [[('explore_cities', 'InnoDB'), ('explore_city_information', 'MyISAM')]]
        with self.assertRaisesRegex(ValueError, 'not InnoDB'):
            updater.check_storage(connection)
        cursor.fetchall.side_effect = [
            [('explore_cities', 'InnoDB'), ('explore_city_information', 'InnoDB')], [('custom_trigger',)]
        ]
        with self.assertRaisesRegex(ValueError, 'INSERT trigger'):
            updater.check_storage(connection)

    def test_main_rejects_sqlite_before_asking_for_confirmation(self):
        with patch('builtins.input') as prompt:
            with self.assertRaisesRegex(ValueError, 'Expected local MySQL/MariaDB'):
                updater.main()
            prompt.assert_not_called()
        self.assertEqual(CityInformation.objects.count(), 1)

    def test_other_city_match_does_not_block(self):
        other = City.objects.create(name='Different City', slug='different-city')
        CityInformation.objects.create(city=other, title='Sinulog elsewhere', info_type='event',
                                       description='A different city', is_published=True)
        self.assertEqual(len(updater.add_guides(self.city.pk)), 2)

    def test_wrong_city_and_second_insert_failure_leave_no_partial_results(self):
        self.city.province = 'Other Province'
        self.city.save(update_fields=['province'])
        with self.assertRaisesRegex(ValueError, 'not Kabankalan'):
            updater.add_guides(self.city.pk)
        self.city.province = 'Negros Occidental'
        self.city.save(update_fields=['province'])
        save = CityInformation.save
        calls = 0
        def fail_second(instance, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError('simulated second insert failure')
            return save(instance, *args, **kwargs)
        with patch.object(CityInformation, 'save', fail_second):
            with self.assertRaisesRegex(RuntimeError, 'simulated second insert failure'):
                updater.add_guides(self.city.pk)
        self.assertEqual(list(CityInformation.objects.values_list('title', flat=True)), ['Existing guide'])
