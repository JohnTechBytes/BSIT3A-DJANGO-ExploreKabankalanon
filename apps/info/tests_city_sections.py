"""City Information sections and search remain separate and read-only."""
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

    def test_each_section_shows_only_its_own_content(self):
        before = list(CityInformation.objects.order_by('pk').values())
        url = reverse('info:city_information')
        for section, present, absent in (
            ('attraction', 'Example attraction', ('Example event', 'id="ek-city-profile-heading"')),
            ('event', 'Example event', ('Example attraction', 'id="ek-city-profile-heading"')),
            ('about', 'id="ek-city-profile-heading"', ('Example attraction', 'Example event')),
        ):
            with self.subTest(section=section):
                response = self.client.get(url, {'section': section})
                self.assertContains(response, 'aria-label="Main navigation"', count=1)
                self.assertContains(response, 'aria-label="City Information sections"', count=1)
                self.assertContains(response, '?section=' + section + '" aria-current="page"')
                self.assertContains(response, present)
                for text in absent:
                    self.assertNotContains(response, text)
                self.assertNotContains(response, 'Unpublished event')
                self.assertNotContains(response, 'class="eainfo-site-nav"')
        self.assertEqual(before, list(CityInformation.objects.order_by('pk').values()))

    def test_default_is_attractions_and_empty_event_view_is_clear(self):
        url = reverse('info:city_information')
        response = self.client.get(url)
        self.assertContains(response, 'Example attraction')
        self.assertNotContains(response, 'Example event')
        self.event.delete()
        response = self.client.get(url, {'section': 'event'})
        self.assertContains(response, 'No published Event / Festival guides yet')
        self.assertNotContains(response, 'Example attraction')
        self.assertNotContains(response, 'Unpublished event')

    def test_search_stays_in_guide_section_and_about_search_is_explicit(self):
        url = reverse('info:city_information')
        response = self.client.get(url, {'section': 'event', 'q': 'Example'})
        self.assertContains(response, 'Example event')
        self.assertNotContains(response, 'Example attraction')
        self.assertContains(response, 'name="section" value="event"')
        self.assertContains(response, '?section=attraction&amp;q=Example')
        self.assertContains(response, '?section=about"')
        response = self.client.get(url, {'section': 'about', 'q': 'event'})
        self.assertContains(response, 'id="ek-city-profile-heading"')
        self.assertNotContains(response, 'Example event')
        self.assertContains(response, 'name="section" value="all"')
        self.assertContains(response, 'Search looks through published attraction and event guides')
        response = self.client.get(url, {'q': 'Example'})
        self.assertContains(response, 'Example attraction')
        self.assertContains(response, 'Example event')

    def test_legacy_type_link_still_works(self):
        response = self.client.get(reverse('info:city_information'), {'type': 'event'})
        self.assertContains(response, 'Example event')
        self.assertNotContains(response, 'Example attraction')
        self.assertEqual(response.context['selected_section'], 'event')
