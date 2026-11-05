"""Tests for the City Information publish workflow.

Only published entries are public, staff publish and unpublish them from the
administrative panel, and the starter content ships published so that a new
installation has a working public page.
"""
from django.apps import apps as global_apps
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation


class _Apps:
    """Minimal stand-in for the migration ``apps`` registry."""

    def get_model(self, app_label, model_name):
        return global_apps.get_model(app_label, model_name)


class CityInformationPublishTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental",
        )
        cls.staff = get_user_model().objects.create_user(
            username="staff", password="test-pass", is_staff=True, is_superuser=True,
        )
        cls.published = CityInformation.objects.create(
            city=cls.city, title="City Government Center", info_type="attraction",
            description="The administrative seat of Kabankalan City.", order=1,
            is_published=True,
        )
        cls.draft = CityInformation.objects.create(
            city=cls.city, title="Getting to Kabankalan", info_type="transport",
            description="Buses and jeepneys connect Kabankalan with Bacolod City.",
            order=1, is_published=False,
        )

    def test_only_published_entries_are_public(self):
        response = self.client.get(reverse("info:city_information"))

        self.assertContains(response, "City Government Center")
        self.assertNotContains(response, "Getting to Kabankalan")
        self.assertEqual(response.context["entry_count"], 1)

    def test_the_type_counts_only_count_published_entries(self):
        response = self.client.get(reverse("info:city_information"))

        counts = {link["type"]: link["count"] for link in response.context["type_links"]}
        self.assertEqual(counts["attraction"], 1)
        self.assertEqual(counts["transport"], 0)

    def test_the_staff_can_publish_an_entry(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("admin:info_cityinformation_changelist"),
            {
                "action": "publish_selected",
                "_selected_action": [str(self.draft.pk)],
                "index": "0",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.draft.refresh_from_db()
        self.assertTrue(self.draft.is_published)
        self.assertContains(response, "published")

    def test_the_staff_can_unpublish_an_entry(self):
        self.client.force_login(self.staff)
        self.client.post(
            reverse("admin:info_cityinformation_changelist"),
            {
                "action": "unpublish_selected",
                "_selected_action": [str(self.published.pk)],
                "index": "0",
            },
            follow=True,
        )

        self.published.refresh_from_db()
        self.assertFalse(self.published.is_published)

    def test_the_publish_flag_is_part_of_the_admin_form(self):
        self.client.force_login(self.staff)
        response = self.client.get(
            reverse("admin:info_cityinformation_add"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "id_is_published")
        self.assertContains(response, "id_photo_credit")

    def test_a_photo_credit_is_shown_next_to_the_entry(self):
        self.published.photo_credit = "Photo: Juan Dela Cruz / Wikimedia Commons (CC BY-SA 4.0)"
        self.published.save(update_fields=["photo_credit"])

        response = self.client.get(reverse("info:city_information"))
        self.assertContains(response, "eainfo-credit")
        self.assertContains(response, "Wikimedia Commons")


class SeedCityInformationPublishTests(TestCase):
    def setUp(self):
        City.objects.create(
            id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental",
        )

    def test_the_starter_entries_are_published(self):
        call_command("seed_city_information", verbosity=0)

        self.assertEqual(CityInformation.objects.count(), 7)
        self.assertFalse(CityInformation.objects.filter(title="Central Philippine University").exists())
        cathedral = CityInformation.objects.get(title="New Kabankalan Cathedral")
        self.assertIn("Talubangi", cathedral.description)
        self.assertEqual(
            CityInformation.objects.filter(is_published=True).count(), 7,
        )


class CityInformationMigrationTests(TestCase):
    """The publish flag must not empty the public page of an existing install."""

    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental",
        )

    def test_the_data_migration_publishes_the_existing_entries(self):
        import importlib

        migration = importlib.import_module(
            "apps.info.migrations.0004_cityinformation_photo_credit",
        )

        CityInformation.objects.create(
            city=self.city, title="City Government Center", info_type="attraction",
            description="The administrative seat of Kabankalan City.",
        )
        self.assertFalse(
            CityInformation.objects.filter(is_published=True).exists(),
        )

        migration.publish_existing_entries(_Apps(), None)

        self.assertEqual(
            CityInformation.objects.filter(is_published=True).count(), 1,
        )
