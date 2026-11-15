"""Sourced city profile is separate from published guide records."""
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation


class CityProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        CityInformation.objects.create(city=city, title='An attraction', info_type='attraction',
                                       description='A published attraction', is_published=True)
        CityInformation.objects.create(city=city, title='An event', info_type='event',
                                       description='A published event', is_published=True)
        CityInformation.objects.create(city=city, title='Private food guide', info_type='food',
                                       description='Hidden category', is_published=True)

    def test_summary_and_credits_are_visible_without_duplicate_nav_or_data_changes(self):
        before = list(CityInformation.objects.order_by('pk').values())
        response = self.client.get(reverse('info:city_information'))
        self.assertContains(response, 'About Kabankalan')
        for topic in ('City overview and government', 'Attractions and celebrations', 'History and cityhood',
                      'Geography', 'Climate', 'Barangays', 'Population and demographics', 'Languages',
                      'Economy', 'Transportation and infrastructure', 'Notable people'):
            self.assertContains(response, '<summary>' + topic + '</summary>', html=True)
        for text in ('210,893', '2024 census', '2014 report', 'marked as lacking sources',
                     'Wikipedia contributors', 'CC BY-SA 4.0', 'Lightningscale', 'CC BY 4.0', 'Chaelo86'):
            self.assertContains(response, text)
        for url in ('https://creativecommons.org/licenses/by/4.0/',
                    'https://creativecommons.org/licenses/by-sa/4.0/',
                    'https://psa.gov.ph/classification/psgc/barangays/1804515000',
                    'https://commons.wikimedia.org/wiki/File:New_Kabankalan_Cathedral.jpg',
                    'https://commons.wikimedia.org/wiki/File:Barangays_of_Kabankalan,_Negros_Occidental.png'):
            self.assertContains(response, url)
        self.assertContains(response, 'An attraction')
        self.assertContains(response, 'An event')
        self.assertNotContains(response, 'Private food guide')
        self.assertNotContains(response, 'class="eainfo-site-nav"')
        self.assertNotContains(response, 'aria-label="City guide types"')
        self.assertEqual(before, list(CityInformation.objects.order_by('pk').values()))

    def test_search_and_category_links_only_search_guides(self):
        for query in ({'q': 'event'}, {'type': 'event'}):
            with self.subTest(query=query):
                response = self.client.get(reverse('info:city_information'), query)
                self.assertContains(response, 'An event')
                self.assertNotContains(response, 'id="ek-city-profile-heading"')
                self.assertNotContains(response, 'An attraction')
