"""Tests for the public City Information module.

The legacy ``Info`` CRUD tests live in ``apps/info/tests.py`` and stay skipped:
they describe a model that no longer exists. These tests cover the module that
replaced them.
"""
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation


class CityInformationPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental",
        )
        cls.attraction = CityInformation.objects.create(
            city=cls.city, title="City Government Center", info_type="attraction",
            description="The administrative seat of Kabankalan City.", order=1,
            is_published=True,
        )
        cls.food = CityInformation.objects.create(
            city=cls.city, title="Local dining", info_type="food",
            description="Restaurants and inasal stalls across the city.", order=1,
            is_published=True,
        )
        cls.draft = CityInformation.objects.create(
            city=cls.city, title="Draft transport note", info_type="transport",
            description="Still being written.", order=2, is_published=False,
        )
        cls.other_city_entry = CityInformation.objects.create(
            city=City.objects.create(name="Other City", slug="other-city"),
            title="Other city notice", info_type="attraction", description="Hidden.",
            is_published=True,
        )

    def test_page_is_public_and_lists_the_published_entries(self):
        response = self.client.get(reverse("info:city_information"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "info/city_information.html")
        self.assertContains(response, "City Information")
        self.assertContains(response, "City Government Center")
        self.assertContains(response, "Local dining")
        # Records of another city are never shown.
        self.assertNotContains(response, "Other city notice")
        # Unpublished entries stay in the staff dashboard.
        self.assertNotContains(response, "Draft transport note")

    def test_entries_are_grouped_by_their_published_type(self):
        response = self.client.get(reverse("info:city_information"))
        groups = {group["type"]: group for group in response.context["grouped_entries"]}
        self.assertIn("attraction", groups)
        self.assertIn("food", groups)
        self.assertEqual(
            [entry.title for entry in groups["attraction"]["items"]],
            ["City Government Center"],
        )

    def test_type_filter_narrows_the_list(self):
        response = self.client.get(reverse("info:city_information"), {"type": "food"})
        self.assertEqual(response.context["selected_type"], "food")
        self.assertContains(response, "Local dining")
        self.assertNotContains(response, "City Government Center")

    def test_unknown_type_is_ignored(self):
        response = self.client.get(reverse("info:city_information"), {"type": "unknown"})
        self.assertEqual(response.context["selected_type"], "")
        self.assertContains(response, "City Government Center")

    def test_search_filters_the_entries(self):
        response = self.client.get(reverse("info:city_information"), {"q": "dining"})
        self.assertContains(response, "Local dining")
        self.assertNotContains(response, "City Government Center")

    def test_combined_filter_keeps_category_and_offers_clear_on_no_match(self):
        response = self.client.get(reverse("info:city_information"), {"type": "food", "q": "missing"})
        self.assertEqual(response.context["entry_count"], 0)
        self.assertContains(response, "No matching city information")
        self.assertContains(response, 'name="type" value="food"')
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, "Clear filters")
        self.assertNotContains(response, "Draft transport note")

    def test_counts_are_shown_for_every_type(self):
        response = self.client.get(reverse("info:city_information"))
        counts = {link["type"]: link["count"] for link in response.context["type_links"]}
        self.assertEqual(counts["attraction"], 1)
        self.assertEqual(counts["food"], 1)
        self.assertEqual(counts["event"], 0)

    def test_empty_state_when_nothing_is_published(self):
        CityInformation.objects.all().delete()
        response = self.client.get(reverse("info:city_information"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No published city information yet")
        self.assertEqual(response.context["entry_count"], 0)


class SeedCityInformationCommandTests(TestCase):
    def setUp(self):
        City.objects.create(
            id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental",
        )

    def test_command_creates_the_starter_entries_once(self):
        call_command("seed_city_information", verbosity=0)
        self.assertEqual(CityInformation.objects.count(), 7)
        self.assertTrue(
            CityInformation.objects.filter(info_type="attraction").exists()
        )

        # A second run must not duplicate the content.
        call_command("seed_city_information", verbosity=0)
        self.assertEqual(CityInformation.objects.count(), 7)

    def test_force_replaces_the_entries(self):
        call_command("seed_city_information", verbosity=0)
        CityInformation.objects.filter(title="City Government Center").delete()
        call_command("seed_city_information", "--force", verbosity=0)
        self.assertEqual(CityInformation.objects.count(), 7)
        self.assertTrue(
            CityInformation.objects.filter(title="City Government Center").exists()
        )
