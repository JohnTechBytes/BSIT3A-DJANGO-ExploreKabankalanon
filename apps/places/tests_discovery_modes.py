"""Distinguish browse and nearby without changing the existing results cap."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.places.models import Place


class DiscoveryModeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        cls.user = get_user_model().objects.create_user(username='modes', password='test')
        cls.category = Category.objects.create(name='Coffee Shops', slug='coffee-shops-cafes')
        cls.cafe = Place.objects.create(city=cls.city, title='Cafe Sample', category=cls.category,
                                        is_active=True, is_verified=True)
        hobby = Hobby.objects.create(name='Coffee and Cafe Hopping', slug='coffee-cafe-hopping')
        cls.hobby_place = Place.objects.create(city=cls.city, title='Tagged Sample', is_active=True, is_verified=True)
        cls.hobby_place.hobbies.add(hobby)
        cls.landmark = Place.objects.create(city=cls.city, title='CPSU Museum', is_active=True, is_verified=True,
                                           latitude=Decimal('9.980000'), longitude=Decimal('122.820000'))
        Place.objects.create(city=cls.city, title='Unpublished Cafe', category=cls.category,
                             is_active=False, is_verified=False)

    def setUp(self):
        self.client.force_login(self.user)
        self.url = reverse('places:attraction_carousel')

    def test_service_search_stays_in_browse_and_keeps_nearby_service_matches(self):
        browse = self.client.get(self.url, {'q': 'coffee shop'})
        nearby = self.client.get(self.url, {'mode': 'nearby', 'q': 'coffee shop'})
        self.assertEqual(browse.status_code, 200)
        self.assertTemplateUsed(browse, 'places/attraction_carousel.html')
        self.assertTemplateUsed(nearby, 'places/nearby_places.html')
        self.assertEqual({p.pk for p in browse.context['attractions']}, {self.cafe.pk, self.hobby_place.pk})
        self.assertEqual({p.pk for p in nearby.context['results']}, {self.cafe.pk, self.hobby_place.pk})
        for fragment in ('id="ea-voice-search"', 'id="ea-carousel"', 'id="ea-map-button"'):
            self.assertContains(browse, fragment)

    def test_non_service_search_keeps_exact_name_precedence(self):
        Place.objects.create(city=self.city, title='Museum', is_active=True, is_verified=True)
        response = self.client.get(self.url, {'q': 'Museum'})
        self.assertEqual({p.title for p in response.context['attractions']}, {'Museum'})

    def test_nearby_requires_origin_and_defaults_to_five_km(self):
        response = self.client.get(self.url, {'mode': 'nearby'})
        self.assertContains(response, 'id="ea6-search-panel" class="ea6-box ea6-search-box" hidden')
        self.assertContains(response, 'id="ea6-results-section" hidden')
        self.assertContains(response, 'value="5" selected')
        self.assertContains(response, 'Browse all places instead')
        self.assertContains(response, 'Location permission denied. Choose a landmark instead.')
        self.assertContains(response, 'No GPS data is sent to Django')

    def test_landmark_remains_selected_during_nearby_search_even_no_results(self):
        response = self.client.get(self.url, {'mode': 'nearby', 'origin': self.landmark.pk, 'q': 'missingastronomical'})
        self.assertEqual(response.context['selected_origin'].pk, self.landmark.pk)
        self.assertContains(response, f'name="origin" value="{self.landmark.pk}"')
        self.assertContains(response, 'data-origin-lat="9.980000"')
        self.assertContains(response, 'No matching places found yet')
        self.assertContains(response, 'const reference = document.getElementById("ea6-results-section")')

    def test_existing_250_result_cap_and_notice_are_unchanged(self):
        Place.objects.bulk_create([
            Place(city=self.city, title=f'Example {n:03}', is_active=True, is_verified=True)
            for n in range(251)
        ])
        response = self.client.get(self.url, {'mode': 'nearby'})
        self.assertEqual(len(response.context['results']), 250)
        self.assertTrue(response.context['limit_reached'])
        self.assertContains(response, 'Distance sorting applies to these displayed results')
