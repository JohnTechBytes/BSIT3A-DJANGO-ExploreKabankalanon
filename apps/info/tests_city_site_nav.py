"""City Information uses the shared navigation without a duplicate row."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation


class CitySiteNavigationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        CityInformation.objects.create(
            city=city, title='Test event', info_type='event', description='Event description',
            thumbnail_url='https://example.com/test.jpg', photo_credit='Example photographer', is_published=True,
        )
        cls.user = get_user_model().objects.create_user(username='example', password='test')

    def test_site_links_and_existing_image_card_for_anonymous_visitors(self):
        response = self.client.get(reverse('info:city_information'), {'section': 'event'})
        self.assertContains(response, 'aria-label="Main navigation"', count=1)
        self.assertNotContains(response, 'aria-label="City Information site links"')
        self.assertNotContains(response, 'class="eainfo-site-nav"')
        self.assertContains(response, 'href="' + reverse('places:attraction_carousel') + '?browse=all"')
        self.assertContains(response, 'href="' + reverse('places:attraction_carousel') + '?mode=nearby"')
        self.assertNotContains(response, 'aria-label="City guide types"')
        self.assertContains(response, 'src="https://example.com/test.jpg"')
        self.assertContains(response, 'Example photographer')
        self.assertContains(response, 'Event description')

    def test_signed_in_links_and_search_remain_available(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('info:city_information'), {'q': 'Test'})
        self.assertContains(response, reverse('places:saved_places'))
        self.assertContains(response, reverse('places:my_reviews'))
        self.assertContains(response, 'value="Test"')
        self.assertContains(response, 'Test event')
