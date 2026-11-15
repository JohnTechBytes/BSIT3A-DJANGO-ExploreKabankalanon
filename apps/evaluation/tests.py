"""Retired SUS survey: public access is removed; existing data is preserved."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import SusResponse


class RetiredSusTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        City.objects.get_or_create(id=2, defaults={'name': 'Kabankalan'})
        cls.user = get_user_model().objects.create_superuser(
            username='reviewer', password='test-pass', email='reviewer@example.test'
        )
        cls.response = SusResponse.objects.create(user=cls.user, **{f'q{i}': 3 for i in range(1, 11)})

    def test_old_survey_routes_do_not_accept_get_or_post_and_preserve_records(self):
        self.client.force_login(self.user)
        for url in ('/evaluation/sus/', '/evaluation/sus/thanks/'):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)
                self.assertEqual(self.client.post(url, {f'q{i}': '3' for i in range(1, 11)}).status_code, 404)
        self.assertEqual(SusResponse.objects.count(), 1)
        self.assertTrue(SusResponse.objects.filter(pk=self.response.pk, user=self.user).exists())

    def test_no_public_survey_links_and_review_links_remain(self):
        self.client.force_login(self.user)
        for url in (reverse('home'), reverse('info:city_information'), reverse('places:my_reviews')):
            with self.subTest(url=url):
                result = self.client.get(url)
                self.assertNotContains(result, '/evaluation/sus/')
                self.assertNotContains(result, 'Usability Survey')
                self.assertContains(result, reverse('places:my_reviews'))

    def test_admin_survey_interface_is_retired_not_the_model_or_data(self):
        self.assertNotIn(SusResponse, admin.site._registry)
        self.assertEqual(SusResponse.objects.count(), 1)

    def test_privacy_notice_discloses_past_responses(self):
        result = self.client.get(reverse('core:privacy_notice'))
        self.assertContains(result, 'survey answers submitted before the survey was retired')
