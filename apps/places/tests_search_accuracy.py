"""Accuracy tests for the question search.

Two promises are tested here:

* a question that names a place returns **that place**, not every record
  that happens to contain one of its words;
* a question that asks for a product is answered by the **category** that
  sells such things, and the page says so honestly - the catalogue only
  holds real places, so no listing is invented for "a phone case".
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category, Hobby
from .models import Place
from .search_intents import (
    describe_search,
    group_filter,
    intent_group,
    product_group,
    resolve_buying_group,
    shopping_product,
    wants_to_buy,
)


class SearchAccuracyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        cls.visitor = get_user_model().objects.create_user(
            username="searcher", password="test-pass",
        )

        cls.mall = Category.objects.create(
            name="Malls / Shopping Centers", slug="malls-shopping-centers",
        )
        cls.business = Category.objects.create(
            name="Other Local Businesses", slug="other-local-businesses",
        )
        cls.restaurant = Category.objects.create(
            name="Restaurants / Eateries", slug="restaurants-eateries",
        )
        cls.cafe = Category.objects.create(
            name="Coffee Shops / Cafes", slug="coffee-shops-cafes",
        )
        cls.barber = Category.objects.create(
            name="Barber / Hair Salon", slug="barber-hair-salon",
        )
        cls.public_art = Category.objects.create(
            name="Public Art", slug="public-art",
        )
        cls.peak = Category.objects.create(
            name="Mountain & Peak", slug="mountain-peak",
        )

        cls.shopping_hobby = Hobby.objects.create(name="Shopping", slug="shopping")
        cls.food_hobby = Hobby.objects.create(name="Food Trip", slug="food")
        cls.cafe_hobby = Hobby.objects.create(name="Café Hopping", slug="cafe")
        cls.nature_hobby = Hobby.objects.create(name="Beach & Nature", slug="nature")
        cls.photo_hobby = Hobby.objects.create(name="Photography", slug="photography")

        def place(title, slug, category, hobby, description):
            record = Place.objects.create(
                city=cls.city, title=title, slug=slug, category=category,
                address="Kabankalan", is_verified=True, is_active=True,
                description=description,
                latitude=9.98, longitude=122.82,
            )
            record.hobbies.add(hobby)
            return record

        # Real Kabankalan names, used to prove that a named place resolves to
        # exactly one record instead of to every similar title.
        cls.plaza = place(
            "Kabankalan Plaza", "kabankalan-plaza", cls.public_art,
            cls.photo_hobby, "The main public plaza of Kabankalan City.",
        )
        place(
            "Aguinaldo Public Plaza", "aguinaldo-public-plaza", cls.public_art,
            cls.photo_hobby, "A public plaza in Kabankalan City.",
        )
        place(
            "Altavas Town Plaza", "altavas-town-plaza", cls.public_art,
            cls.photo_hobby, "A public plaza in Kabankalan City.",
        )
        cls.falls = place(
            "Mag-Aso Falls", "mag-aso-falls", cls.peak,
            cls.nature_hobby, "A waterfall attraction inside the city limits.",
        )
        place(
            "Long Point Hill", "long-point-hill", cls.peak,
            cls.nature_hobby, "A hill overlooking the Kabankalan plain.",
        )

        # The business side of the catalogue.
        cls.shop = place(
            "City Mall", "city-mall", cls.mall,
            cls.shopping_hobby, "A shopping center in Kabankalan City.",
        )
        cls.store = place(
            "Corner Store", "corner-store", cls.business,
            cls.shopping_hobby, "A sari-sari store in Kabankalan City.",
        )
        cls.diner = place(
            "Local Diner", "local-diner", cls.restaurant,
            cls.food_hobby, "A restaurant in Kabankalan City.",
        )
        cls.cafe_place = place(
            "Local Café", "local-cafe", cls.cafe,
            cls.cafe_hobby, "A coffee shop in Kabankalan City.",
        )
        cls.barbershop = place(
            "Local Barbershop", "local-barbershop", cls.barber,
            cls.shopping_hobby, "A barbershop in Kabankalan City.",
        )

        # Not published: a buying question must never surface it.
        place(
            "Inactive Mall", "inactive-mall", cls.mall,
            cls.shopping_hobby, "A shopping center that is not published.",
        ).is_active = False
        Place.objects.filter(slug="inactive-mall").update(is_active=False)

        cls.published = Place.objects.filter(
            city=cls.city, is_active=True, is_verified=True,
        )

    def setUp(self):
        self.client.force_login(self.visitor)
        self.url = reverse("places:attraction_carousel")

    # -- buying intent ----------------------------------------------------

    def test_buying_question_returns_the_business_category(self):
        response = self.client.get(self.url, {"q": "where to buy a phone case"})

        titles = [place.title for place in response.context["attractions"]]
        self.assertEqual(sorted(titles), ["City Mall", "Corner Store"])
        self.assertNotIn("Mag-Aso Falls", titles)

    def test_buying_question_works_for_any_product(self):
        for product in ("a phone case", "an umbrella", "school supplies", "groceries"):
            with self.subTest(product=product):
                response = self.client.get(self.url, {"q": "where to buy %s" % product})
                titles = [place.title for place in response.context["attractions"]]
                self.assertEqual(sorted(titles), ["City Mall", "Corner Store"])

    def test_buying_question_for_a_haircut_returns_the_barbershop(self):
        # "haircut" is a known service, so the carousel hands the question to
        # the nearby page, which answers it with the barbershop.
        response = self.client.get(self.url, {"q": "where to get a haircut"}, follow=True)

        titles = [place.title for place in response.context["results"]]
        self.assertEqual(titles, ["Local Barbershop"])

    def test_buying_question_explains_that_the_match_came_from_the_category(self):
        response = self.client.get(self.url, {"q": "where to buy a phone case"})

        note = response.context["search_note"]
        self.assertIn("Matched by category", note)
        self.assertIn("shops and malls of Kabankalan", note)
        self.assertIn("availability is not confirmed", note)
        self.assertNotIn("are where a phone case is sold", note)
        self.assertContains(response, "ea-search-note")

    def test_plain_search_has_no_category_note(self):
        response = self.client.get(self.url, {"q": "Mag-Aso Falls"})

        self.assertEqual(response.context["search_note"], "")
        self.assertNotContains(response, "Matched by category")

    def test_buying_question_is_detected_and_grouped(self):
        self.assertTrue(wants_to_buy("where to buy a phone case"))
        self.assertFalse(wants_to_buy("Mag-Aso Falls"))
        self.assertEqual(shopping_product("where to buy a phone case"), "phone case")
        self.assertEqual(product_group("haircut"), "grooming")
        self.assertEqual(product_group("phone case"), "")
        self.assertEqual(intent_group("where to buy at the mall"), "shopping")

    def test_any_product_falls_back_to_the_shops_and_malls(self):
        self.assertEqual(resolve_buying_group("where to buy a phone case"), "shopping")
        self.assertEqual(resolve_buying_group("where to buy an umbrella"), "shopping")
        self.assertEqual(resolve_buying_group("where to buy groceries"), "shopping")
        self.assertEqual(resolve_buying_group("where to get a haircut"), "grooming")

    def test_category_group_filter_matches_slugs_and_names(self):
        predicate = group_filter("shopping")
        titles = set(
            self.published.filter(predicate).values_list("title", flat=True)
        )
        self.assertEqual(titles, {"City Mall", "Corner Store"})

    def test_describe_search_is_honest_about_the_source(self):
        note = describe_search("shopping", "phone case")
        self.assertTrue(note.startswith("Matched by category:"))

    # -- named places -----------------------------------------------------

    def test_named_place_returns_only_that_place(self):
        response = self.client.get(self.url, {"q": "Kabankalan Plaza"})

        titles = [place.title for place in response.context["attractions"]]
        self.assertEqual(titles, ["Kabankalan Plaza"])

    def test_named_place_is_found_with_a_different_spelling(self):
        response = self.client.get(self.url, {"q": "Mag Aso Falls"})

        titles = [place.title for place in response.context["attractions"]]
        self.assertEqual(titles, ["Mag-Aso Falls"])

    def test_broad_keyword_search_still_returns_every_matching_place(self):
        response = self.client.get(self.url, {"q": "falls"})

        titles = [place.title for place in response.context["attractions"]]
        self.assertIn("Mag-Aso Falls", titles)
        self.assertNotIn("City Mall", titles)

    # -- the nearby page --------------------------------------------------

    def test_nearby_page_answers_a_buying_question_too(self):
        response = self.client.get(self.url, {"mode": "nearby", "q": "where to buy a phone case"})

        titles = [place.title for place in response.context["results"]]
        self.assertEqual(sorted(titles), ["City Mall", "Corner Store"])
        self.assertIn("Matched by category", response.context["search_note"])

    def test_natural_language_complete_names_are_prioritized_in_both_modes(self):
        sol = Place.objects.create(
            city=self.city, title="Sol's Garden Café", slug="sols-garden-cafe",
            category=self.cafe, is_active=True, is_verified=True,
        )
        for query, expected in (
            ("Where is Mag Aso Falls in Kabankalan?", self.falls),
            ("Saan ang Mag-Aso Falls?", self.falls),
            ("How do I get to Sols Garden Cafe?", sol),
            ("Show me Local Diner", self.diner),
        ):
            for mode in ("explore", "nearby"):
                with self.subTest(query=query, mode=mode):
                    params = {"q": query}
                    if mode == "nearby":
                        params["mode"] = "nearby"
                    response = self.client.get(self.url, params, follow=True)
                    results = response.context.get("results", response.context.get("attractions"))
                    self.assertEqual([p.pk for p in results], [expected.pk])
                    self.assertEqual(response.context["search_note"], "")

    def test_generic_query_does_not_get_confused_with_a_generic_title(self):
        Place.objects.create(city=self.city, title="Coffee", slug="generic-coffee",
                             category=self.cafe, is_active=True, is_verified=True)
        response = self.client.get(self.url, {"mode": "nearby", "q": "where can i find coffee"})
        self.assertIn(self.cafe_place.pk, [p.pk for p in response.context["results"]])
        self.assertGreaterEqual(len(response.context["results"]), 2)

    def test_filipino_buying_is_category_only_and_unconfirmed(self):
        for params in ({"q": "saan makabili ng phone case"},
                       {"mode": "nearby", "q": "saan makabili ng phone case"}):
            with self.subTest(params=params):
                response = self.client.get(self.url, params, follow=True)
                results = response.context.get("results", response.context.get("attractions"))
                self.assertEqual({p.pk for p in results}, {self.shop.pk, self.store.pk})
                self.assertIn("availability is not confirmed", response.context["search_note"])

    def test_simple_food_and_coffee_questions_find_services(self):
        for query, expected in (("where can i eat", self.diner),
                                ("saan kakain", self.diner),
                                ("saan may kape", self.cafe_place)):
            response = self.client.get(self.url, {"mode": "nearby", "q": query})
            self.assertIn(expected.pk, [p.pk for p in response.context["results"]])

    def test_named_question_does_not_expose_unpublished_or_other_city(self):
        other = City.objects.create(name="Other City", slug="other-city")
        for title, city, active in (("Hidden Secret", self.city, False),
                                    ("Other Secret", other, True)):
            Place.objects.create(city=city, title=title, slug=title.lower().replace(' ', '-'),
                                 category=self.cafe, is_active=active, is_verified=True)
            for params in ({"q": "where is " + title},
                           {"mode": "nearby", "q": "where is " + title}):
                response = self.client.get(self.url, params, follow=True)
                results = response.context.get("results", response.context.get("attractions"))
                self.assertNotIn(title, [p.title for p in results])
