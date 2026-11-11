"""Tests for retained hobby preferences and search history."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from datetime import date


from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.info.models import QueryLog, RecommendationRating
from .models import Place, Review, SavedPlace


class JourneyPreferenceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental",
        )
        cls.category = Category.objects.create(name="Nature", slug="nature")
        cls.hiking = Hobby.objects.create(name="Hiking", slug="hiking")
        cls.coffee = Hobby.objects.create(name="Coffee", slug="coffee")
        cls.place = Place.objects.create(
            city=cls.city, title="Mag Aso Falls", slug="mag-aso-falls",
            category=cls.category, address="Kabankalan", is_active=True, is_verified=True,
            description="A waterfall attraction in the city.",
        )
        cls.place.hobbies.add(cls.hiking)
        cls.user = get_user_model().objects.create_user(
            username="journey_user", password="test-pass"
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.url = reverse("places:attraction_carousel")

    def test_choosing_a_hobby_remembers_it_in_the_session(self):
        self.client.get(self.url, {"hobby": "hiking"})
        self.assertEqual(self.client.session["selected_hobbies"], ["hiking"])

    def test_the_remembered_hobby_is_used_for_the_ranking(self):
        response = self.client.get(self.url, {"hobby": "hiking"})
        self.assertEqual(response.context["selected_hobbies"], ["hiking"])

    def test_browsing_every_place_keeps_the_hobby_preference(self):
        self.client.get(self.url, {"hobby": "hiking"})
        self.client.get(self.url, {"browse": "all"})
        self.assertEqual(self.client.session["selected_hobbies"], ["hiking"])

    def test_clearing_the_hobby_removes_the_preference(self):
        self.client.get(self.url, {"hobby": "hiking"})
        self.client.get(self.url, {"hobby": ""})
        self.assertNotIn("selected_hobbies", self.client.session)

    def test_an_unknown_hobby_is_ignored(self):
        self.client.get(self.url, {"hobby": "not-a-hobby"})
        self.assertNotIn("selected_hobbies", self.client.session)

    def test_a_submitted_search_is_logged_with_its_match_count(self):
        self.client.get(self.url, {"q": "falls"})
        log = QueryLog.objects.get()
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.raw_query, "falls")
        self.assertEqual(log.matched_count, 1)
        self.assertEqual(log.parsed_json["category"], "")

    def test_loading_the_page_without_a_query_does_not_log_anything(self):
        self.client.get(self.url, {"browse": "all"})
        self.assertEqual(QueryLog.objects.count(), 0)

    def test_a_service_search_is_logged_by_the_nearby_view(self):
        self.client.get(self.url, {"q": "coffee shop", "mode": "nearby"})
        self.assertEqual(QueryLog.objects.count(), 1)
        self.assertEqual(QueryLog.objects.get().raw_query, "coffee shop")
