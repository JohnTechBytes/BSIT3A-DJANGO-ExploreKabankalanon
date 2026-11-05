"""Tests for the local seeding command.

``seed_kabankalan`` is the first command a new installation runs, so it has
to create the city the whole site is locked to, the interest taxonomy and the
published OpenStreetMap places that ship with the repository.
"""
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.places.models import Place


class SeedKabankalanTests(TestCase):
    def test_seed_creates_the_city_the_taxonomy_and_the_published_places(self):
        call_command("seed_kabankalan", verbosity=0)

        city = City.objects.get(pk=2)
        self.assertEqual(city.name, "Kabankalan")
        self.assertTrue(Hobby.objects.filter(slug="hiking-eco-tourism").exists())
        self.assertTrue(Category.objects.exists())

        places = Place.objects.filter(
            city=city, is_active=True, is_verified=True
        )
        # The six real Kabankalan attractions in the shipped OSM extract.
        self.assertEqual(places.count(), 6)
        names = set(places.values_list("title", flat=True))
        self.assertIn("Mag Aso Falls", names)
        self.assertIn("Amyan Hill", names)
        self.assertIn("CPSU Museum", names)

        for place in places:
            with self.subTest(place=place.title):
                self.assertIsNotNone(place.latitude)
                self.assertIsNotNone(place.longitude)
                self.assertTrue(place.hobbies.exists())
                self.assertTrue(place.category_id)

    def test_seed_can_be_run_twice_without_duplicating_anything(self):
        output = StringIO()
        call_command("seed_kabankalan", verbosity=0, stdout=output)
        warning = output.getvalue()
        self.assertIn("replaces hobby tags on matching existing places", warning)
        self.assertIn("Unmapped categories receive a default Photography tag", warning)
        self.assertIn("This warning does not stop the command", warning)
        call_command("seed_kabankalan", verbosity=0)

        self.assertEqual(Place.objects.filter(city_id=2).count(), 6)
        self.assertEqual(City.objects.filter(pk=2).count(), 1)
        self.assertEqual(
            Hobby.objects.filter(slug="hiking-eco-tourism").count(), 1
        )
