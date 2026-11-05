from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category
from .models import Place
from .sample_images import sample_image_for


class SampleImageTests(SimpleTestCase):
    def test_samples_follow_actual_place_metadata(self):
        cases = [
            ("Café Hopping", None, "coffee"),
            ("Local Billiards Hall", None, "billiards"),
            ("Barber Shop", None, "barber"),
            ("Shopping Mall", None, "shopping"),
            ("Mag Aso Falls", "Nature & mountains", "nature"),
            ("Amyan Hill", "Nature", "mountain"),
            ("CPSU Museum", "Culture", "museum"),
            ("City Plaza", None, "city"),
            ("Local Inasal Grill", None, "food"),
            ("A Local Bookstore", None, ""),
        ]
        for title, category_name, expected in cases:
            with self.subTest(title=title):
                category = Category(name=category_name) if category_name else None
                place = Place(title=title, category=category)
                expected_path = f"img/samples/{expected}.jpg" if expected else ""
                self.assertEqual(sample_image_for(place), expected_path)


class NearbyRedesignTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        cls.other_city = City.objects.create(name="Other City", slug="other-city")
        cls.visitor = get_user_model().objects.create_user(username="visitor", password="test-pass")
        cls.coffee = Category.objects.create(name="Coffee shops / cafés", slug="coffee-shops-cafes")
        cls.nature = Category.objects.create(name="Nature", slug="nature")
        cls.cafe = Place.objects.create(
            city=cls.city, title="Local Café", slug="local-cafe", category=cls.coffee,
            address="Kabankalan", is_verified=True, is_active=True,
            latitude=9.98, longitude=122.82, description="A real local listing.",
        )
        cls.museum = Place.objects.create(
            city=cls.city, title="CPSU Museum", slug="osm-node-123", address="Kabankalan",
            is_verified=True, is_active=True, latitude=9.99, longitude=122.81,
        )
        Place.objects.create(city=cls.city, title="Unverified Café", category=cls.coffee,
                             address="Kabankalan", is_verified=False, is_active=True)
        Place.objects.create(city=cls.city, title="Inactive Café", category=cls.coffee,
                             address="Kabankalan", is_verified=True, is_active=False)
        Place.objects.create(city=cls.other_city, title="Other City Café", category=cls.coffee,
                             address="Other City", is_verified=True, is_active=True)

    def setUp(self):
        self.client.force_login(self.visitor)
        self.url = reverse("places:attraction_carousel")

    def test_nearby_page_uses_new_theme_and_keeps_existing_controls(self):
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "places/nearby_places.html")
        for content in [
            'class="nearby-page ek-theme ek-discovery-theme"', 'css/nearby.css', 'css/editorial.css', 'css/explore.css', 'class="ek-brand-name"',
            'Find places near you.', 'Find your next stop',
            'id="ea6-search-form"', 'id="ea6-use-gps"', 'id="ea6-origin"',
            'id="ea6h-distance"', 'id="ea6g-toggle"', 'id="ea6g-map-shell"',
            'id="ea6-results"', 'View details', 'Directions', 'Show on map',
        ]:
            self.assertContains(response, content)
        self.assertContains(response, "Local Café")
        self.assertContains(response, "CPSU Museum")
        for private in ("Unverified Café", "Inactive Café", "Other City Café"):
            self.assertNotContains(response, private)

    def test_publication_does_not_claim_independent_verification(self):
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertContains(response, "Publication does not guarantee independent verification")
        self.assertContains(response, "Published listing")
        self.assertNotContains(response, "Staff verified listing")

    def test_detail_actions_remain_available_without_duplicate_navigation(self):
        response = self.client.get(reverse("places:place_detail", args=[self.cafe.pk]))
        self.assertContains(response, reverse("places:save_place", args=[self.cafe.pk]))
        self.assertContains(response, reverse("places:submit_review", args=[self.cafe.pk]))
        self.assertContains(response, reverse("places:saved_places"))
        self.assertNotContains(response, reverse("itineraries:choose_for_place", args=[self.cafe.pk]))
        self.assertNotContains(response, reverse("visits:check_in", args=[self.cafe.pk]))
        self.assertNotContains(response, f'href="{reverse("places:journey_dashboard")}"')

    def test_missing_photos_have_clear_messages_and_real_photos_are_not_labelled_missing(self):
        for url, params in [
            (self.url, {"mode": "nearby", "place": self.cafe.pk}),
            (reverse("places:place_detail", args=[self.cafe.pk]), {}),
            (self.url, {"browse": "all"}),
        ]:
            response = self.client.get(url, params)
            self.assertContains(response, "Photo not yet available · Illustrative category sample")
            self.assertContains(response, "data-place-cover")
            self.assertContains(response, "place-photo-fallback.js")

        self.cafe.cover_image_url = "https://example.com/real-cafe.jpg"
        self.cafe.save()
        response = self.client.get(reverse("places:place_detail", args=[self.cafe.pk]))
        self.assertContains(response, 'data-place-cover src="https://example.com/real-cafe.jpg"')
        self.assertNotContains(response, "Photo not yet available · Illustrative category sample")

    def test_nearby_unmapped_photo_does_not_claim_to_open_a_map(self):
        Place.objects.create(city=self.city, title="Unmapped Bookstore", address="Kabankalan",
                             is_verified=True, is_active=True)
        response = self.client.get(self.url, {"mode": "nearby", "q": "Unmapped Bookstore"})
        self.assertContains(response, "Unmapped Bookstore")
        self.assertNotContains(response, 'aria-label="View on map: Unmapped Bookstore')
        self.assertNotContains(response, 'aria-label="Show on map: Unmapped Bookstore')

    def test_service_search_retains_matching_and_selected_filter(self):
        response = self.client.get(self.url, {"mode": "nearby", "service": "coffee"})
        self.assertEqual([place.title for place in response.context["results"]], ["Local Café"])
        self.assertContains(response, 'name="service"')
        self.assertContains(response, 'aria-current="true"')
        self.assertContains(response, 'img/samples/coffee.jpg')
        self.assertContains(response, 'Illustrative category sample')
        self.assertContains(response, 'not an actual photo of Local Café')
        # Other published places remain available as landmark/autocomplete options,
        # but must not appear as cards in this filtered result set.
        self.assertNotContains(response, 'data-title="CPSU Museum"')

    def test_real_photos_and_attribution_take_precedence(self):
        self.cafe.cover_image_url = "https://example.com/real-cafe.jpg"
        self.cafe.photo_credit = "Original photographer"
        self.cafe.photo_source_url = "https://example.com/source"
        self.cafe.save()
        response = self.client.get(self.url, {"mode": "nearby", "place": self.cafe.pk})
        self.assertContains(response, self.cafe.cover_image_url)
        self.assertContains(response, "Original photographer")
        self.assertContains(response, self.cafe.photo_source_url)
        self.assertNotContains(response, "Illustrative category sample")
        self.assertNotContains(response, "img/samples/coffee.jpg")

    def test_unknown_category_uses_neutral_placeholder(self):
        place = Place.objects.create(city=self.city, title="Local Bookstore", address="Local",
                                     is_verified=True, is_active=True)
        response = self.client.get(self.url, {"mode": "nearby", "place": place.pk})
        self.assertContains(response, "PHOTO NOT YET AVAILABLE")
        self.assertNotContains(response, "Illustrative category sample")
        self.assertContains(response, "Precise map coordinates unavailable")
        self.assertNotContains(response, "Show on map ↗")

    def test_selected_landmark_preserves_search_and_location_reference(self):
        response = self.client.get(self.url, {
            "mode": "nearby", "service": "coffee", "origin": self.museum.pk,
        })
        self.assertEqual(response.context["selected_origin"], self.museum)
        self.assertContains(response, f'data-origin-name="{self.museum.title}"')
        self.assertContains(response, 'name="service" value="coffee"')
        self.assertContains(response, 'name="origin" required')
        self.assertContains(response, "not your live GPS position")

    def test_empty_search_stays_honest_and_usable(self):
        response = self.client.get(self.url, {"mode": "nearby", "q": "No such place at all"})
        self.assertContains(response, "No matching places found yet")
        self.assertContains(response, "Our directory may be incomplete")
        self.assertContains(response, "Clear search and filters")
        self.assertContains(response, "Browse all published places")
        self.assertNotContains(response, 'class="ea6-card"')

    def test_browse_page_keeps_its_existing_theme(self):
        response = self.client.get(self.url, {"browse": "all"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "places/attraction_carousel.html")
        self.assertContains(response, "ExploreAnywhere")
        self.assertNotContains(response, 'class="nearby-page"')
        self.assertNotContains(response, "css/nearby.css")
        self.assertContains(response, "css/browse-guide.css")
        self.assertContains(response, "THE LOCAL GUIDE")
        # The marker icon stays a fixed pixel size while Leaflet animates zoom.
        self.assertContains(response, 'className: "ea-map-pin"')
        self.assertContains(response, 'iconSize: [20, 20]')
        self.assertContains(response, 'const marker = L.marker(')

    def test_unauthenticated_discovery_still_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertRedirects(response, "/accounts/login/?next=/places/%3Fmode%3Dnearby", fetch_redirect_response=False)

    def test_browse_only_offers_map_for_places_with_coordinates(self):
        Place.objects.create(
            city=self.city, title="Unmapped Bookstore", slug="unmapped-bookstore",
            address="Kabankalan", is_verified=True, is_active=True,
        )
        unmapped = self.client.get(self.url, {"q": "Unmapped Bookstore"})
        self.assertContains(unmapped, "Unmapped Bookstore")
        self.assertNotContains(unmapped, 'class="ea-card-map-hint"')
        mapped = self.client.get(self.url, {"q": "CPSU Museum"})
        self.assertContains(mapped, 'class="ea-card-map-hint"')
        self.assertContains(mapped, 'vendor/leaflet/leaflet.js')
        self.assertContains(mapped, 'vendor/leaflet/leaflet.css')
        self.assertNotContains(mapped, 'unpkg.com/leaflet@1.9.4')
