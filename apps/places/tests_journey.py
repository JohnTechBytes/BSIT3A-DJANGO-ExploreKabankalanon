"""Tests for the interests, search history and relevance feedback in My Journey."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from datetime import date

from apps.itineraries.models import Itinerary
from apps.visits.models import VisitCheckIn

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


class JourneyDashboardPanelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental",
        )
        cls.hiking = Hobby.objects.create(name="Hiking", slug="hiking")
        cls.place = Place.objects.create(
            city=cls.city, title="Mag Aso Falls", slug="mag-aso-falls",
            address="Kabankalan", is_active=True, is_verified=True,
        )
        cls.user = get_user_model().objects.create_user(
            username="panel_user", password="test-pass"
        )
        cls.other = get_user_model().objects.create_user(
            username="other_user", password="test-pass"
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_dashboard_retains_populated_activity_and_links(self):
        SavedPlace.objects.create(user=self.user, place=self.place)
        Itinerary.objects.create(user=self.user, city=self.city, title="Test plan")
        Review.objects.create(user=self.user, place=self.place, rating=4, comment="Test review")
        VisitCheckIn.objects.create(user=self.user, place=self.place, visited_on=date(2026, 1, 1),
                                    visit_note="Test visit", status=VisitCheckIn.Status.APPROVED)
        response = self.client.get(reverse("places:journey_dashboard"))
        self.assertContains(response, "My Journey")
        self.assertContains(response, "Mag Aso Falls")
        self.assertContains(response, "Test plan")
        self.assertContains(response, "4 / 5 stars")
        self.assertContains(response, "Staff approved")
        self.assertEqual(response.context["saved_count"], 1)
        self.assertEqual(response.context["itinerary_count"], 1)
        self.assertEqual(response.context["review_count"], 1)
        self.assertEqual(response.context["approved_visit_count"], 1)
        for name in ("places:saved_places", "itineraries:list", "places:my_reviews", "visits:list"):
            self.assertContains(response, f'href="{reverse(name)}"')

    def test_panel_shows_the_interests_and_the_search_history(self):
        session = self.client.session
        session["selected_hobbies"] = ["hiking"]
        session.save()
        QueryLog.objects.create(user=self.user, raw_query="falls", matched_count=3)
        QueryLog.objects.create(user=self.other, raw_query="private", matched_count=1)

        response = self.client.get(reverse("places:journey_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interests &amp; Recent Searches")
        self.assertContains(response, "Hiking")
        self.assertContains(response, "falls")
        # Another account's history is never shown.
        self.assertNotContains(response, "private")
        self.assertEqual(len(response.context["recent_searches"]), 1)

    def test_panel_shows_the_relevance_feedback(self):
        RecommendationRating.objects.create(
            user=self.user, place=self.place, query_text="falls", rating="relevant",
        )
        response = self.client.get(reverse("places:journey_dashboard"))
        self.assertContains(response, "Your relevance feedback")
        self.assertContains(response, "Mag Aso Falls")
        self.assertContains(response, "Relevant")

    def test_panel_is_honest_when_there_is_nothing_yet(self):
        response = self.client.get(reverse("places:journey_dashboard"))
        self.assertContains(response, "No interests selected yet")
        self.assertContains(response, "No searches yet")
        self.assertContains(response, "No ratings yet")
