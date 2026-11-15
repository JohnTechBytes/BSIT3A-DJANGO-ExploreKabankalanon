"""Topic filters use URL keywords, not invented classifications or DB changes."""
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation
from apps.info.official_index import TOPICS, search_entries, sitemap_entries, topics_for_path


class OfficialTopicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        CityInformation.objects.create(city=city, title='Existing guide', info_type='attraction', is_published=True)
        CityInformation.objects.create(city=city, title='Private guide', info_type='event', is_published=False)

    def test_keyword_matching_is_multiple_and_word_boundaries_are_safe(self):
        self.assertIn('tourism', topics_for_path('/tourism/cultural-heritage/'))
        self.assertIn('services', topics_for_path('/citizens-charter/city-tourism-office/'))
        self.assertIn('tourism', topics_for_path('/citizens-charter/city-tourism-office/'))
        self.assertIn('barangays', topics_for_path('/barangay/barangay-oringao/'))
        self.assertIn('documents', topics_for_path('/sp-resolution-no-2024-378/'))
        self.assertIn('procurement', topics_for_path('/category/bid-opportunities/'))
        self.assertNotIn('procurement', topics_for_path('/forbidden/'))
        self.assertEqual(topics_for_path('/unrecognisable-1234/'), ('other',))
        self.assertEqual(topics_for_path('/BIDDING_DOCUMENTS/'), ('procurement',))
        self.assertEqual(len(sitemap_entries()), 1297)
        self.assertTrue(all(e['topics'] for e in sitemap_entries()))
        for topic in TOPICS:
            self.assertTrue(search_entries('', '', topic), topic)

    def test_topic_and_type_and_search_work_together_across_pages(self):
        url = reverse('info:city_information')
        params = {'section': 'official', 'topic': 'documents', 'kind': 'post', 'q': 'resolution'}
        response = self.client.get(url, params)
        page = response.context['official_page']
        self.assertGreater(page.paginator.count, 25)
        self.assertTrue(all(e['kind'] == 'post' and 'documents' in e['topics'] and 'resolution' in e['search'] for e in page))
        self.assertContains(response, 'name="topic"')
        self.assertContains(response, 'value="documents" selected')
        self.assertContains(response, 'value="post" selected')
        self.assertContains(response, 'name="q" value="resolution"')
        self.assertContains(response, 'Topics are estimated from words in each URL')
        next_url = response.context['next_official_url']
        for param in ('section=official', 'topic=documents', 'kind=post', 'q=resolution'):
            self.assertIn(param, next_url)
        second = self.client.get(url + next_url)
        self.assertEqual(second.context['official_page'].number, 2)
        self.assertEqual(second.context['official_topic'], 'documents')
        self.assertIn('topic=documents', second.context['previous_official_url'])
        self.assertContains(second, 'Clear all filters')

    def test_invalid_and_empty_filters_and_old_urls(self):
        url = reverse('info:city_information')
        all_page = self.client.get(url, {'section': 'official'})
        self.assertEqual(all_page.context['official_page'].paginator.count, 1297)
        response = self.client.get(url, {'section': 'official', 'topic': 'bogus'})
        self.assertEqual(response.context['official_topic'], '')
        self.assertEqual(response.context['official_page'].paginator.count, 1297)
        response = self.client.get(url, {'section': 'official', 'topic': 'tourism', 'q': 'xyz-no-result'})
        self.assertContains(response, 'No sitemap entries match')
        self.assertContains(response, 'Clear all filters')
        self.assertContains(response, 'href="?section=official"')
        old_link = self.client.get(url, {'section': 'official', 'kind': 'category', 'q': 'news'})
        self.assertContains(old_link, 'category / news and updates')

    def test_filters_keep_records_read_only_and_guides_separate(self):
        before = list(CityInformation.objects.order_by('pk').values())
        url = reverse('info:city_information')
        for topic in TOPICS:
            with self.subTest(topic=topic):
                response = self.client.get(url, {'section': 'official', 'topic': topic})
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'Existing guide')
                self.assertNotContains(response, 'Private guide')
                self.assertTrue(all(topic in e['topics'] for e in response.context['official_page']))
        self.assertEqual(before, list(CityInformation.objects.order_by('pk').values()))
        guide = self.client.get(url, {'section': 'attraction', 'topic': 'documents'})
        self.assertContains(guide, 'Existing guide')
        self.assertNotContains(guide, 'name="topic"')
