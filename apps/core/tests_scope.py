"""Tests for the content scope rules and the commands that enforce them."""
from io import StringIO

from django.core.checks import Tags
from django.core.checks.registry import registry
from django.core.management import call_command
from django.test import TestCase

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.core.scope import (
    civic_kind,
    institution_kind,
    is_place_in_scope,
    place_violations,
)
from apps.places.models import Place


class ScopeRuleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        cls.category = Category.objects.create(
            name="Mountain & Peak", slug="mountain-peak",
        )
        cls.hobby = Hobby.objects.create(name="Hiking", slug="hiking")

    def test_educational_institutions_are_recognised(self):
        self.assertEqual(
            institution_kind("Kabankalan National High School"), "high school",
        )
        self.assertEqual(institution_kind("St. Mary's Elementary School"), "elementary school")
        self.assertEqual(institution_kind("Central Philippine University"), "university")
        self.assertEqual(institution_kind("Kabankalan Technical Institute"), "technical institute")
        self.assertEqual(institution_kind("Mag-Aso Falls"), "")

    def test_civic_offices_are_recognised_but_not_treated_as_schools(self):
        self.assertEqual(civic_kind("Kabankalan City Hall"), "city hall")
        self.assertEqual(civic_kind("Kabankalan Public Library"), "public library")
        self.assertEqual(civic_kind("Mag-Aso Falls"), "")

    def test_place_violations_report_the_missing_parts(self):
        place = Place.objects.create(
            city=self.city, title="Mag-Aso Falls", slug="mag-aso-falls",
            is_verified=True, is_active=True,
        )

        reasons = place_violations(place)
        self.assertIn("no category: the place is not filed in the taxonomy", reasons)
        self.assertIn(
            "no hobby tags: review whether a relevant activity applies; "
            "the place remains visible in general browsing",
            reasons,
        )
        self.assertIn("no description", reasons)
        self.assertTrue(is_place_in_scope(place))

    def test_a_complete_place_is_in_scope(self):
        place = Place.objects.create(
            city=self.city, title="Long Point Hill", slug="long-point-hill",
            category=self.category, is_verified=True, is_active=True,
            description="A hill overlooking the Kabankalan plain.",
        )
        place.hobbies.add(self.hobby)

        self.assertEqual(place_violations(place), [])
        self.assertTrue(is_place_in_scope(place))

    def test_a_school_is_out_of_scope_even_with_a_category_and_hobby(self):
        place = Place.objects.create(
            city=self.city, title="Kabankalan National High School",
            slug="kabankalan-national-high-school", category=self.category,
            is_verified=True, is_active=True,
            description="A public secondary school in Kabankalan City.",
        )
        place.hobbies.add(self.hobby)

        reasons = place_violations(place)
        self.assertEqual(len(reasons), 1)
        self.assertIn("educational institution (high school)", reasons[0])
        self.assertFalse(is_place_in_scope(place))


class ScopeCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        cls.category = Category.objects.create(
            name="Public Art", slug="public-art",
        )
        cls.hobby = Hobby.objects.create(name="Photography", slug="photography")

        cls.good = Place.objects.create(
            city=cls.city, title="Kabankalan Plaza", slug="kabankalan-plaza",
            category=cls.category, is_verified=True, is_active=True,
            description="The main public plaza of Kabankalan City.",
        )
        cls.good.hobbies.add(cls.hobby)

        cls.school = Place.objects.create(
            city=cls.city, title="Kabankalan National High School",
            slug="kabankalan-national-high-school", is_verified=True, is_active=True,
            description="A public secondary school in Kabankalan City.",
        )

    def test_check_content_scope_reports_the_off_pillar_records(self):
        out = StringIO()
        call_command("check_content_scope", stdout=out)

        report = out.getvalue()
        self.assertIn("ExploreKabankalan is a shared directory", report)
        self.assertIn("Off-pillar (educational institutions): 1", report)
        self.assertIn("Kabankalan National High School", report)

    def test_check_content_scope_can_fail_the_run(self):
        with self.assertRaises(SystemExit):
            call_command("check_content_scope", "--strict", stdout=StringIO())

    def test_purge_is_a_dry_run_until_apply_is_given(self):
        out = StringIO()
        call_command("purge_off_scope_places", stdout=out)

        self.assertIn("Dry run", out.getvalue())
        self.school.refresh_from_db()
        self.assertTrue(self.school.is_active)

    def test_purge_unpublishes_the_off_pillar_records(self):
        out = StringIO()
        call_command("purge_off_scope_places", "--apply", stdout=out)

        self.school.refresh_from_db()
        self.good.refresh_from_db()
        self.assertFalse(self.school.is_active)
        self.assertFalse(self.school.is_verified)
        self.assertTrue(self.good.is_active)


class ScopeSystemCheckTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        Place.objects.create(
            city=cls.city, title="Kabankalan National High School",
            slug="kabankalan-national-high-school", is_verified=True, is_active=True,
            description="A public secondary school in Kabankalan City.",
        )

    def test_the_check_is_silent_without_a_database(self):
        from apps.core.checks import check_content_scope

        self.assertEqual(check_content_scope(databases=None), [])
        self.assertEqual(check_content_scope(databases=[]), [])

    def test_the_check_reports_the_off_pillar_records(self):
        issues = registry.run_checks(
            tags=[Tags.database], include_deployment_checks=False, databases=["default"],
        )

        messages = [issue.msg for issue in issues if issue.id == "core.E001"]
        self.assertTrue(
            any("Kabankalan National High School" in message for message in messages),
            messages,
        )
