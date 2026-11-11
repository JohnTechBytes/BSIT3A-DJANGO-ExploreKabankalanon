"""Regression tests for the discovery query behaviour.

The Explore Places carousel used to materialise every published place (and all
of its hobby rows) twice: once to build the category/hobby filter options and
once to fill the carousel. These tests pin the optimised behaviour so a future
refactor cannot silently reintroduce the duplicated scan.
"""
import datetime

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from apps.cities.models import City
from apps.core.models import Category, Hobby
from .models import OpeningHours, Place, SavedPlace


class CarouselQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        cls.visitor = get_user_model().objects.create_user(
            username="perf_visitor", password="test-pass"
        )
        cls.nature = Category.objects.create(name="Nature", slug="nature")
        cls.food = Category.objects.create(name="Food", slug="food")
        cls.unused = Category.objects.create(name="Unused", slug="unused")
        cls.hiking = Hobby.objects.create(name="Hiking", slug="hiking")
        cls.eating = Hobby.objects.create(name="Eating", slug="eating")
        cls.unused_hobby = Hobby.objects.create(name="Unused hobby", slug="unused-hobby")

    def setUp(self):
        self.client.force_login(self.visitor)
        self.url = reverse("places:attraction_carousel")

    def _publish(self, index, category, hobby):
        place = Place.objects.create(
            city=self.city, title=f"Destination {index:02d}", slug=f"dest-{index:02d}",
            category=category, address="Kabankalan", is_active=True, is_verified=True,
        )
        place.hobbies.add(hobby)
        return place

    def test_filter_options_only_list_categories_used_by_published_places(self):
        self._publish(1, self.nature, self.hiking)
        self._publish(2, self.food, self.eating)
        # A place that is not published must not offer its category or hobby.
        Place.objects.create(
            city=self.city, title="Hidden", slug="hidden", category=self.unused,
            address="Kabankalan", is_active=False, is_verified=True,
        ).hobbies.add(self.unused_hobby)

        response = self.client.get(self.url, {"browse": "all"})

        category_values = {item["value"] for item in response.context["category_options"]}
        category_labels = {item["label"] for item in response.context["category_options"]}
        hobby_values = {item["value"] for item in response.context["hobby_options"]}
        hobby_labels = {item["label"] for item in response.context["hobby_options"]}

        self.assertEqual(category_labels, {"Nature", "Food"})
        self.assertEqual(hobby_labels, {"Hiking", "Eating"})
        self.assertEqual(category_values, {str(self.nature.pk), str(self.food.pk)})
        self.assertEqual(hobby_values, {"hiking", "eating"})

    def test_published_total_only_counts_published_places(self):
        self._publish(1, self.nature, self.hiking)
        Place.objects.create(
            city=self.city, title="Hidden", slug="hidden-2", address="Kabankalan",
            is_active=True, is_verified=False,
        )

        response = self.client.get(self.url, {"browse": "all"})

        self.assertEqual(response.context["published_total"], 1)

    def test_query_count_does_not_grow_with_the_number_of_published_places(self):
        self._publish(1, self.nature, self.hiking)
        # Warm up so the session write is not part of the measured queries.
        self.client.get(self.url, {"browse": "all"})
        with CaptureQueriesContext(connection) as small:
            self.client.get(self.url, {"browse": "all"})
        small_count = len(small.captured_queries)

        for index in range(2, 26):
            self._publish(index, self.nature, self.hiking)
        with CaptureQueriesContext(connection) as large:
            self.client.get(self.url, {"browse": "all"})
        large_count = len(large.captured_queries)

        # The published set is loaded once, not once per filter option.
        self.assertEqual(large_count, small_count)

    def test_nearby_suggestion_list_does_not_add_a_second_full_scan(self):
        for index in range(1, 13):
            self._publish(index, self.nature, self.hiking)
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(self.url, {"mode": "nearby"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["approved_suggestions"])
        # The suggestion list is built from the already loaded published set.
        self.assertLessEqual(len(context.captured_queries), 12)
