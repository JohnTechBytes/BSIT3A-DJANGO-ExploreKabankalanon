"""In-page City Information navigation preserves search and guide content."""
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation


class CitySectionNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        cls.attraction = CityInformation.objects.create(city=cls.city, title='Example attraction',
            info_type='attraction', description='Attraction text', is_published=True)
        cls.event = CityInformation.objects.create(city=cls.city, title='Example event',
            info_type='event', description='Event text', is_published=True)
        CityInformation.objects.create(city=cls.city, title='Unpublished event',
            info_type='event', description='Not public', is_published=False)

    def test_navigation_targets_existing_sections_without_duplicating_site_nav(self):
        before = list(CityInformation.objects.order_by('pk').values())
        response = self.client.get(reverse('info:city_information'))
        self.assertContains(response, 'aria-label="Main navigation"', count=1)
        self.assertContains(response, 'aria-label="City Information sections"', count=1)
        for target in ('eainfo-group-attraction', 'eainfo-group-event', 'ek-city-profile-heading'):
            self.assertContains(response, 'href="#' + target + '"', count=1)
            self.assertContains(response, 'id="' + target + '"', count=1)
        self.assertContains(response, 'Example attraction')
        self.assertContains(response, 'Example event')
        self.assertNotContains(response, 'Unpublished event')
        self.assertNotContains(response, 'class="eainfo-site-nav"')
        self.assertEqual(before, list(CityInformation.objects.order_by('pk').values()))

    def test_empty_sections_still_have_working_anchor_targets(self):
        self.attraction.delete()
        self.event.delete()
        response = self.client.get(reverse('info:city_information'))
        self.assertContains(response, 'id="eainfo-group-event"', count=1)
        self.assertContains(response, 'id="eainfo-group-attraction"', count=1)
        self.assertContains(response, 'No published event / festival guides yet.')
        self.assertContains(response, 'No published attraction guides yet.')
        self.assertNotContains(response, 'Unpublished event')

    def test_filtered_links_return_to_unfiltered_page(self):
        for query in ({'q': 'event'}, {'type': 'event'}):
            with self.subTest(query=query):
                response = self.client.get(reverse('info:city_information'), query)
                self.assertContains(response, 'Example event')
                self.assertNotContains(response, 'Example attraction')
                self.assertContains(response, 'Section links return to all city information.')
                for target in ('eainfo-group-attraction', 'eainfo-group-event', 'ek-city-profile-heading'):
                    self.assertContains(response, 'href="' + reverse('info:city_information') + '#' + target + '"')
                self.assertNotContains(response, 'id="ek-city-profile-heading"')
