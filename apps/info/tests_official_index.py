"""Official sitemap inventory is a separate, read-only, searchable snapshot."""
from urllib.parse import urlsplit

from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation
from apps.info.official_index import search_entries, sitemap_entries


class OfficialIndexTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        CityInformation.objects.create(city=city, title='Staff attraction', info_type='attraction', is_published=True)
        CityInformation.objects.create(city=city, title='Private event', info_type='event', is_published=False)

    def test_index_contains_each_uploaded_entry_and_only_official_https_urls(self):
        entries = sitemap_entries()
        self.assertEqual(len(entries), 1297)
        self.assertEqual(sum(e['kind'] == 'page' for e in entries), 122)
        self.assertEqual(sum(e['kind'] == 'post' for e in entries), 1166)
        self.assertEqual(sum(e['kind'] == 'category' for e in entries), 9)
        self.assertEqual(sum(e['url'].endswith('/executive-order-no-07-2023/') for e in entries), 2)
        self.assertTrue(all(urlsplit(e['url']).netloc == 'kabankalancity.gov.ph' and e['url'].startswith('https://') for e in entries))
        self.assertTrue(search_entries('SINULOG', ''))
        self.assertTrue(search_entries('CITIZENS-CHARTER', ''))

    def test_official_view_is_isolated_and_read_only(self):
        before = list(CityInformation.objects.order_by('pk').values())
        response = self.client.get(reverse('info:city_information'), {'section': 'official'})
        self.assertContains(response, 'Official City Information')
        self.assertContains(response, '?section=official" aria-current="page"')
        self.assertContains(response, '1297 matching sitemap entries')
        self.assertContains(response, 'Labels below are generated from URL paths')
        self.assertContains(response, 'not copies of the records')
        self.assertContains(response, 'Page 1 of 52')
        self.assertContains(response, 'href="https://kabankalancity.gov.ph/"')
        self.assertNotContains(response, 'Staff attraction')
        self.assertNotContains(response, 'Private event')
        self.assertNotContains(response, 'id="ek-city-profile-heading"')
        self.assertNotContains(response, 'id="city-guides-heading"')
        self.assertEqual(before, list(CityInformation.objects.order_by('pk').values()))

    def test_search_filter_pagination_and_clear(self):
        url = reverse('info:city_information')
        response = self.client.get(url, {'section': 'official', 'kind': 'post', 'q': 'resolution'})
        self.assertGreater(response.context['official_page'].paginator.count, 25)
        self.assertTrue(all(e['kind'] == 'post' and 'resolution' in e['search'] for e in response.context['official_page']))
        self.assertContains(response, 'value="post" selected')
        self.assertContains(response, 'name="section" value="official"')
        next_link = response.context['next_official_url']
        self.assertIn('q=resolution', next_link)
        self.assertIn('kind=post', next_link)
        second = self.client.get(url + next_link)
        self.assertEqual(second.context['official_page'].number, 2)
        self.assertTrue(second.context['previous_official_url'])
        response = self.client.get(url, {'section': 'official', 'q': 'no such sitemap entry xyz'})
        self.assertContains(response, 'No sitemap entries match')
        self.assertContains(response, 'Clear search and type')
        response = self.client.get(url, {'section': 'official', 'page': '9999999999999999', 'kind': 'invalid'})
        self.assertEqual(response.context['official_page'].number, 1)
        self.assertEqual(response.context['official_kind'], '')

    def test_guide_search_and_section_navigation_do_not_mix_official_search(self):
        url = reverse('info:city_information')
        response = self.client.get(url, {'section': 'attraction', 'q': 'Staff'})
        self.assertContains(response, 'Staff attraction')
        self.assertNotContains(response, 'id="ek-official-heading"')
        response = self.client.get(url, {'section': 'official', 'q': 'Staff'})
        self.assertContains(response, 'href="?section=attraction"')
        self.assertNotContains(response, 'Staff attraction')
