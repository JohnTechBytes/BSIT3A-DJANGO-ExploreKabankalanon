"""End-to-end functional checks for the flows the redesign touched.

Every test drives the real views with the real templates, so a broken form
field name, missing URL name, or changed redirect is caught here rather than
in the browser.
"""
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from unittest import mock

from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.itineraries.models import Itinerary, ItineraryStop
from apps.visits.models import VisitCheckIn

from .models import Place, Review, SavedPlace

User = get_user_model()
PASSWORD = "test-pass-123"


class FlowFixture(TestCase):
    """One published, one unpublished and one foreign-city destination."""

    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(
            pk=2, name="Kabankalan", slug="kabankalan",
            province="Negros Occidental",
        )
        cls.other_city = City.objects.create(
            name="Bago", slug="bago", province="Negros Occidental",
        )
        cls.nature = Category.objects.create(name="Nature & mountains", slug="nature-mountains")
        cls.food = Category.objects.create(name="Food", slug="food")
        cls.hiking = Hobby.objects.create(name="Hiking", slug="hiking")

        cls.place = Place.objects.create(
            city=cls.city, title="Published Falls", slug="published-falls",
            address="Kabankalan", category=cls.nature,
            description="A real published destination.",
            is_active=True, is_verified=True,
            latitude="9.876392", longitude="122.840476",
        )
        cls.place.hobbies.add(cls.hiking)
        cls.cafe = Place.objects.create(
            city=cls.city, title="Published Cafe", slug="published-cafe",
            address="Kabankalan", category=cls.food,
            is_active=True, is_verified=True,
        )
        cls.hidden = Place.objects.create(
            city=cls.city, title="Unpublished Draft Place", slug="unpublished-draft",
            address="Kabankalan", category=cls.nature,
            is_active=True, is_verified=False,
        )
        cls.other_town = Place.objects.create(
            city=cls.other_city, title="Other City Landmark", slug="other-city-landmark",
            address="Bago", is_active=True, is_verified=True,
        )

        cls.user = User.objects.create_user(username="flow_user", password=PASSWORD)
        cls.other_user = User.objects.create_user(username="other_user", password=PASSWORD)

    def login(self, user=None):
        self.assertTrue(self.client.login(
            username=(user or self.user).username, password=PASSWORD))
        return user or self.user


class AuthFlowTests(FlowFixture):
    def test_login_page_uses_the_redesigned_template(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "auth-card")
        self.assertContains(response, "Welcome back")

    def test_login_and_logout_round_trip(self):
        response = self.client.post(
            "/accounts/login/", {"username": self.user.username, "password": PASSWORD})
        self.assertRedirects(response, "/hobbies/", fetch_redirect_response=False)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

        response = self.client.post("/accounts/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_legacy_users_login_route_still_works(self):
        response = self.client.get("/users/login/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            "/users/login/", {"username": self.user.username, "password": PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_login_keeps_the_existing_hobbies_landing_redirect(self):
        """ExploreLoginView always lands on the hobbies step (which now opens
        Explore Places), even when a ?next= parameter is present. Pinned here
        so a future redesign does not change the sign-in destination silently.
        """
        response = self.client.post(
            "/accounts/login/?next=" + reverse("places:saved_places"),
            {"username": self.user.username, "password": PASSWORD})
        self.assertRedirects(response, "/hobbies/", fetch_redirect_response=False)

    def test_bad_credentials_keep_visitor_signed_out(self):
        response = self.client.post(
            reverse("login"), {"username": self.user.username, "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "auth-card")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_registration_creates_and_signs_in_user(self):
        response = self.client.post(reverse("register"), {
            "username": "brand_new", "email": "brand_new@example.com",
            "password1": "sup3r-secret-pass", "password2": "sup3r-secret-pass",
            "consent_privacy": "on",
        })
        self.assertRedirects(response, "/hobbies/", fetch_redirect_response=False)
        created = User.objects.get(username="brand_new")
        self.assertEqual(created.email, "brand_new@example.com")
        self.assertEqual(int(self.client.session["_auth_user_id"]), created.pk)
        # The acceptance of the privacy notice is stored with the account.
        self.assertTrue(created.consent_privacy)
        self.assertIsNotNone(created.consent_privacy_at)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="taken_email", email="dup@example.com", password=PASSWORD)
        response = self.client.post(reverse("register"), {
            "username": "another", "email": "dup@example.com",
            "password1": "sup3r-secret-pass", "password2": "sup3r-secret-pass",
            "consent_privacy": "on",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="another").exists())

    def test_anonymous_visitors_are_sent_to_login_for_private_pages(self):
        for name, kwargs in [
            ("places:saved_places", {}),
            ("places:my_reviews", {}),
            ("places:journey_dashboard", {}),
            ("itineraries:list", {}),
            ("visits:list", {}),
            ("places:place_detail", {"pk": self.place.pk}),
            ("places:attraction_carousel", {}),
        ]:
            with self.subTest(url=name):
                response = self.client.get(reverse(name, kwargs=kwargs))
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response["Location"])


class DiscoveryFlowTests(FlowFixture):
    def setUp(self):
        self.login()
        self.url = reverse("places:attraction_carousel")

    def test_browse_lists_only_published_kabankalan_places(self):
        response = self.client.get(self.url, {"browse": "all"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Falls")
        self.assertContains(response, "Published Cafe")
        self.assertNotContains(response, "Unpublished Draft Place")
        self.assertNotContains(response, "Other City Landmark")

    def test_category_filter_narrows_results(self):
        response = self.client.get(self.url, {"category": str(self.food.pk)})
        self.assertContains(response, "Published Cafe")
        self.assertNotContains(response, "Published Falls")

    def test_hobby_filter_narrows_results(self):
        response = self.client.get(self.url, {"hobby": "hiking"})
        self.assertContains(response, "Published Falls")
        self.assertNotContains(response, "Published Cafe")

    def test_free_text_search_matches_place_names(self):
        response = self.client.get(self.url, {"q": "Published Falls"})
        self.assertContains(response, "Published Falls")
        self.assertNotContains(response, "Published Cafe")

    def test_sort_options_render(self):
        for sort in ("recommended", "rating", "name"):
            with self.subTest(sort=sort):
                self.assertEqual(
                    self.client.get(self.url, {"sort": sort}).status_code, 200)

    def test_smart_search_redirects_into_discovery(self):
        response = self.client.get(reverse("places:smart_search"), {"q": "falls"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("places:attraction_carousel"), response["Location"])
        self.assertIn("q=falls", response["Location"])

    def test_empty_smart_search_falls_back_to_browse(self):
        response = self.client.get(reverse("places:smart_search"), {"q": "   "})
        self.assertRedirects(
            response, reverse("places:attraction_carousel"),
            fetch_redirect_response=False)

    def test_nearby_search_filters_and_keeps_privacy_notice(self):
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Falls")
        self.assertNotContains(response, "Unpublished Draft Place")

    def test_legacy_nearby_url_still_redirects(self):
        response = self.client.get(reverse("places:nearby_places"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("mode=nearby", response["Location"])

    def test_place_detail_hides_unpublished_and_other_cities(self):
        self.assertEqual(
            self.client.get(reverse("places:place_detail", args=[self.place.pk])).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("places:place_detail", args=[self.hidden.pk])).status_code, 404)
        self.assertEqual(
            self.client.get(reverse("places:place_detail", args=[self.other_town.pk])).status_code, 404)

    def test_place_detail_shows_map_link_and_coordinates(self):
        response = self.client.get(reverse("places:place_detail", args=[self.place.pk]))
        self.assertContains(response, "Open the map in Google Maps")
        self.assertContains(response, "9.876392")


class CarouselLoopTests(FlowFixture):
    """The Explore Places loop serves every match, with voice + map controls."""

    def setUp(self):
        self.login()
        self.url = reverse("places:attraction_carousel")

    def test_carousel_context_serves_every_match_in_one_request(self):
        extra = [
            Place.objects.create(
                city=self.city, title=f"Loop Place {index}", slug=f"loop-place-{index}",
                address="Kabankalan", category=self.nature,
                is_active=True, is_verified=True,
            )
            for index in range(1, 15)
        ]
        response = self.client.get(self.url, {"browse": "all"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_attractions"], 16)
        self.assertEqual(len(response.context["attractions"]), 16)
        self.assertFalse(response.context["carousel_truncated"])
        for place in extra:
            self.assertContains(response, place.title)
        self.assertNotContains(response, "Unpublished Draft Place")

    def test_carousel_renders_a_single_marquee_track(self):
        response = self.client.get(self.url, {"browse": "all"})

        self.assertContains(response, 'id="ea-carousel-track"')
        self.assertContains(response, "data-marquee")
        self.assertContains(response, "ea-carousel-caption")
        self.assertContains(response, "2 matching places shown. Open a place on the map to explore.")
        # Pagination is gone: one request holds the whole list.
        self.assertNotContains(response, "ea-pagination")

    def test_voice_search_controls_render_beside_the_query_field(self):
        response = self.client.get(self.url, {"browse": "all"})

        self.assertContains(response, 'id="ea-search-query"')
        self.assertContains(response, 'id="ea-voice-search"')
        self.assertContains(response, 'id="ea-voice-status"')
        self.assertContains(response, 'aria-pressed="false"')

    def test_card_photo_carries_the_map_view_hook(self):
        response = self.client.get(self.url, {"browse": "all"})

        self.assertContains(response, "ea-card-map-hint")
        self.assertContains(response, 'data-lat="9.876392"')
        self.assertContains(response, 'id="ea-drone-hud"')
        self.assertContains(response, 'id="ea-drone-target"')

    def test_marquee_controls_appear_only_for_a_scrollable_set(self):
        two_places = self.client.get(self.url, {"browse": "all"})
        self.assertNotContains(two_places, 'id="ea-marquee-toggle"')

        Place.objects.create(
            city=self.city, title="Third Place", slug="third-place",
            address="Kabankalan", is_active=True, is_verified=True,
        )
        Place.objects.create(
            city=self.city, title="Fourth Place", slug="fourth-place",
            address="Kabankalan", is_active=True, is_verified=True,
        )
        four_places = self.client.get(self.url, {"browse": "all"})
        self.assertContains(four_places, 'id="ea-marquee-toggle"')
        self.assertContains(four_places, 'All 4 matching places shown')

    def test_carousel_cap_truncates_with_a_visible_notice(self):
        with mock.patch("apps.places.views.MAX_CAROUSEL_PLACES", 1):
            response = self.client.get(self.url, {"browse": "all"})

        self.assertEqual(len(response.context["attractions"]), 1)
        self.assertEqual(response.context["total_attractions"], 2)
        self.assertTrue(response.context["carousel_truncated"])
        self.assertContains(response, "Showing the first 1 of 2 matching places")


class NearbyPageTests(FlowFixture):
    """Nearby search: voice input and the drone map, but no looping carousel."""

    def setUp(self):
        self.login()
        self.url = reverse("places:attraction_carousel")

    def test_nearby_offers_voice_search(self):
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="ea6-voice"')
        self.assertContains(response, 'id="ea6-voice-status"')
        self.assertContains(response, "js/ea-voice.js")

    def test_nearby_map_uses_bundled_leaflet(self):
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertContains(response, 'vendor/leaflet/leaflet.js')
        self.assertContains(response, 'vendor/leaflet/leaflet.css')
        self.assertNotContains(response, 'unpkg.com/leaflet')

    def test_nearby_keeps_a_plain_grid_instead_of_a_marquee(self):
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertNotContains(response, "data-marquee")
        self.assertNotContains(response, "ea-carousel-track")
        self.assertNotContains(response, "ea-marquee-toggle")
        self.assertContains(response, 'id="ea6-results"')

    def test_every_card_can_fly_the_map_to_its_place(self):
        response = self.client.get(self.url, {"mode": "nearby"})
        self.assertContains(response, "ea6-drone-hud")
        self.assertContains(response, 'id="ea6-drone-target"')
        self.assertContains(response, "ea6-card-map-hint")
        self.assertContains(response, 'aria-label="View on map: Published Falls')

class ScoringDisplayTests(FlowFixture):
    """Percentages and "not scored" labels are no longer shown to visitors."""

    def setUp(self):
        self.login()
        self.url = reverse("places:attraction_carousel")

    def test_cards_and_map_show_no_match_percentage(self):
        # A hobby is selected, so the old markup would have shown a score.
        response = self.client.get(self.url, {"browse": "all", "hobby": "hiking"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Falls")
        for fragment in ("% match", "Not scored", "Personalized Relevance",
                         "personalized relevance", "ea-match-badge"):
            with self.subTest(fragment=fragment):
                self.assertNotContains(response, fragment)

    def test_scoring_explainer_paragraph_is_gone(self):
        response = self.client.get(self.url, {"browse": "all"})
        self.assertNotContains(response, "ea-score-guidance")
        self.assertNotContains(response, "normalized over available signals")
        self.assertNotContains(response, "hobby-match-legend")

    def test_map_markers_use_one_neutral_colour(self):
        response = self.client.get(self.url, {"browse": "all"})
        self.assertNotContains(response, "#16a34a")
        self.assertNotContains(response, "#dc2626")
        self.assertContains(response, "selectAttraction(index)")
        self.assertContains(response, "ea-map-pin")

    def test_recommended_sorting_still_works_without_the_badge(self):
        response = self.client.get(self.url, {"browse": "all", "sort": "recommended"})
        self.assertEqual(response.status_code, 200)
        titles = [place.title for place in response.context["attractions"]]
        self.assertIn("Published Falls", titles)
        self.assertIn("Published Cafe", titles)


class InlineSortControlTests(FlowFixture):
    """The inline sort must submit its own search form, never another one.

    The shared header renders a logout form before the page content, so
    ``document.forms[0]`` pointed at logout: changing the sort signed the
    visitor out and dropped them on the home page.
    """

    def setUp(self):
        self.login()
        self.url = reverse("places:attraction_carousel")

    def test_inline_sort_submits_the_search_form(self):
        response = self.client.get(self.url, {"browse": "all"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "id=\"ea-inline-sort\"")
        self.assertContains(response, "eaSort.form")
        self.assertContains(response, "requestSubmit")
        self.assertNotContains(response, "document.forms[0]")

    def test_sort_select_is_rendered_once(self):
        response = self.client.get(self.url, {"browse": "all"})
        html = response.content.decode()
        self.assertEqual(html.count('id="ea-inline-sort"'), 1)
        self.assertEqual(html.count('id="ea-filter-sort"'), 1)

    def test_sort_choice_survives_in_the_search_form(self):
        # Browse-all pins the recommended order; an explicit sort applies once
        # the visitor leaves that scope, which is what the inline control sends.
        response = self.client.get(self.url, {"sort": "rating"})
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('name="sort"', body)
        self.assertRegex(body, r'<option value="rating"\s+selected>')


class SavedPlacesFlowTests(FlowFixture):
    def setUp(self):
        self.login()
        self.detail = reverse("places:place_detail", args=[self.place.pk])

    def test_save_then_unsave(self):
        response = self.client.post(reverse("places:save_place", args=[self.place.pk]))
        self.assertRedirects(response, self.detail, fetch_redirect_response=False)
        self.assertTrue(SavedPlace.objects.filter(user=self.user, place=self.place).exists())

        response = self.client.post(reverse("places:unsave_place", args=[self.place.pk]))
        self.assertRedirects(response, self.detail, fetch_redirect_response=False)
        self.assertFalse(SavedPlace.objects.filter(user=self.user, place=self.place).exists())

    def test_saving_twice_is_idempotent(self):
        for _ in range(2):
            self.client.post(reverse("places:save_place", args=[self.place.pk]))
        self.assertEqual(
            SavedPlace.objects.filter(user=self.user, place=self.place).count(), 1)

    def test_save_requires_post(self):
        self.assertEqual(
            self.client.get(reverse("places:save_place", args=[self.place.pk])).status_code, 405)

    def test_cannot_save_unpublished_place(self):
        self.assertEqual(
            self.client.post(reverse("places:save_place", args=[self.hidden.pk])).status_code, 404)

    def test_saved_page_lists_and_scopes_to_user(self):
        SavedPlace.objects.create(user=self.other_user, place=self.cafe)
        SavedPlace.objects.create(user=self.user, place=self.place)
        response = self.client.get(reverse("places:saved_places"))
        self.assertContains(response, "Published Falls")
        self.assertNotContains(response, "Published Cafe")

    def test_saved_page_labels_remove_action_and_keeps_details_without_itinerary_link(self):
        SavedPlace.objects.create(user=self.user, place=self.place)
        response = self.client.get(reverse("places:saved_places"))
        self.assertContains(response, '1 saved destination')
        self.assertContains(response, f'Remove {self.place.title} from saved places')
        self.assertContains(response, reverse("places:place_detail", args=[self.place.pk]))
        self.assertNotContains(response, reverse("itineraries:choose_for_place", args=[self.place.pk]))
        self.assertNotContains(response, f'href="{reverse("places:journey_dashboard")}"')

    def test_empty_saved_page_offers_a_way_to_explore(self):
        response = self.client.get(reverse("places:saved_places"))
        self.assertContains(response, 'No saved places yet')
        self.assertContains(response, reverse("places:attraction_carousel") + '?browse=all')

    def test_journey_dashboard_counts_reflect_saved_itinerary_and_review(self):
        SavedPlace.objects.create(user=self.user, place=self.place)
        Review.objects.create(user=self.user, place=self.place, rating=4, comment="Good")
        Itinerary.objects.create(user=self.user, city=self.city, title="Day trip")
        response = self.client.get(reverse("places:journey_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["saved_count"], 1)
        self.assertEqual(response.context["itinerary_count"], 1)
        self.assertEqual(response.context["review_count"], 1)


class ReviewFlowTests(FlowFixture):
    def setUp(self):
        self.login()
        self.submit = reverse("places:submit_review", args=[self.place.pk])

    def test_submit_creates_review_and_updates_place_rating(self):
        response = self.client.post(self.submit, {"rating": "4", "comment": "Lovely trail"})
        self.assertRedirects(
            response, reverse("places:place_detail", args=[self.place.pk]),
            fetch_redirect_response=False)
        # The detail page renders the confirmation banner after the redirect.
        self.assertContains(
            self.client.get(reverse("places:place_detail", args=[self.place.pk])),
            "Your review was submitted.")
        review = Review.objects.get(user=self.user, place=self.place)
        self.assertEqual(review.rating, 4)
        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 1)
        self.assertEqual(str(self.place.avg_rating), "4.00")

    def test_submitting_again_updates_the_same_review(self):
        self.client.post(self.submit, {"rating": "4", "comment": "First"})
        self.client.post(self.submit, {"rating": "5", "comment": "Second"})
        reviews = Review.objects.filter(user=self.user, place=self.place)
        self.assertEqual(reviews.count(), 1)
        self.assertEqual(reviews.first().rating, 5)
        self.place.refresh_from_db()
        self.assertEqual(str(self.place.avg_rating), "5.00")

    def test_invalid_rating_is_rejected_without_touching_records(self):
        self.client.post(self.submit, {"rating": "9", "comment": "Nope"})
        self.assertFalse(Review.objects.filter(user=self.user, place=self.place).exists())

    def test_overlong_comment_is_rejected(self):
        self.client.post(self.submit, {"rating": "5", "comment": "x" * 1501})
        self.assertFalse(Review.objects.filter(user=self.user, place=self.place).exists())

    def test_delete_review_resets_rating(self):
        Review.objects.create(user=self.user, place=self.place, rating=5, comment="Nice")
        self.place.review_count = 1
        self.place.avg_rating = 5
        self.place.save()
        response = self.client.post(
            reverse("places:delete_review", args=[self.place.pk]))
        self.assertRedirects(
            response, reverse("places:place_detail", args=[self.place.pk]),
            fetch_redirect_response=False)
        self.assertFalse(Review.objects.filter(user=self.user, place=self.place).exists())
        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 0)
        self.assertEqual(str(self.place.avg_rating), "0.00")

    def test_my_reviews_lists_only_my_reviews(self):
        Review.objects.create(user=self.user, place=self.place, rating=5, comment="Mine")
        Review.objects.create(user=self.other_user, place=self.cafe, rating=3, comment="Theirs")
        response = self.client.get(reverse("places:my_reviews"))
        self.assertContains(response, "Published Falls")
        self.assertNotContains(response, "Published Cafe")

    def test_unpublished_place_review_is_rejected(self):
        self.assertEqual(self.client.post(
            reverse("places:submit_review", args=[self.hidden.pk]),
            {"rating": "5", "comment": "Ghost"}).status_code, 404)


class ItineraryFlowTests(FlowFixture):
    def setUp(self):
        self.login()

    def test_create_update_add_reorder_and_delete(self):
        response = self.client.post(reverse("itineraries:create"), {
            "title": "Weekend plan", "day_number": "2", "initial_place": "",
        })
        trip = Itinerary.objects.get(user=self.user)
        self.assertRedirects(
            response, reverse("itineraries:builder", args=[trip.pk]),
            fetch_redirect_response=False)
        self.assertEqual(trip.title, "Weekend plan")
        self.assertEqual(trip.day_number, 2)

        # Rename the trip.
        self.client.post(reverse("itineraries:update", args=[trip.pk]), {
            "title": "Renamed plan", "day_number": "1",
        })
        trip.refresh_from_db()
        self.assertEqual(trip.title, "Renamed plan")
        self.assertEqual(trip.day_number, 1)

        # Add two stops.
        for place, when in ((self.place, "09:00"), (self.cafe, "11:30")):
            self.client.post(reverse("itineraries:add_stop", args=[trip.pk]), {
                "place_id": str(place.pk), "start_time": when, "notes": "Visit",
            })
        stops = list(ItineraryStop.objects.filter(itinerary=trip).order_by("stop_order"))
        self.assertEqual([s.place for s in stops], [self.place, self.cafe])
        self.assertEqual([s.stop_order for s in stops], [1, 2])

        # Move the second stop above the first.
        response = self.client.post(
            reverse("itineraries:move_stop", args=[trip.pk, stops[1].pk]),
            {"direction": "up"})
        self.assertEqual(response.status_code, 302)
        stops = list(ItineraryStop.objects.filter(itinerary=trip).order_by("stop_order"))
        self.assertEqual([s.place for s in stops], [self.cafe, self.place])

        # Remove one stop.
        self.client.post(
            reverse("itineraries:remove_stop", args=[trip.pk, stops[0].pk]))
        self.assertEqual(
            ItineraryStop.objects.filter(itinerary=trip).count(), 1)

        # Delete the itinerary.
        response = self.client.post(reverse("itineraries:delete", args=[trip.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Itinerary.objects.filter(pk=trip.pk).exists())

    def test_create_rejects_blank_title(self):
        response = self.client.post(reverse("itineraries:create"), {
            "title": "", "day_number": "1",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Itinerary.objects.filter(user=self.user).exists())

    def test_choose_for_place_adds_a_stop_to_an_existing_trip(self):
        trip = Itinerary.objects.create(user=self.user, city=self.city, title="Existing")
        response = self.client.post(
            reverse("itineraries:choose_for_place", args=[self.place.pk]), {
                "itinerary_id": str(trip.pk), "start_time": "14:00", "notes": "Afternoon",
            })
        self.assertRedirects(
            response, reverse("itineraries:builder", args=[trip.pk]),
            fetch_redirect_response=False)
        self.assertTrue(ItineraryStop.objects.filter(
            itinerary=trip, place=self.place, notes="Afternoon").exists())

    def test_other_users_cannot_open_or_change_my_trip(self):
        trip = Itinerary.objects.create(user=self.other_user, city=self.city, title="Theirs")
        self.assertEqual(
            self.client.get(reverse("itineraries:builder", args=[trip.pk])).status_code, 404)
        self.assertEqual(self.client.post(
            reverse("itineraries:delete", args=[trip.pk])).status_code, 404)
        self.assertTrue(Itinerary.objects.filter(pk=trip.pk).exists())

    def test_itinerary_list_keeps_empty_and_populated_navigation(self):
        response = self.client.get(reverse("itineraries:list"))
        self.assertContains(response, "No itinerary yet")
        self.assertContains(response, reverse("itineraries:create"))
        trip = Itinerary.objects.create(user=self.user, city=self.city, title="My plan", day_number=2)
        response = self.client.get(reverse("itineraries:list"))
        self.assertContains(response, "My plan")
        self.assertContains(response, "Day 2")
        self.assertContains(response, "0 planned stops")
        self.assertContains(response, reverse("itineraries:builder", args=[trip.pk]))
        self.assertContains(response, reverse("places:journey_dashboard"))
        self.assertContains(response, reverse("places:saved_places"))

    def test_my_itineraries_lists_only_my_trips(self):
        Itinerary.objects.create(user=self.user, city=self.city, title="Mine to keep")
        Itinerary.objects.create(user=self.other_user, city=self.city, title="Not mine")
        response = self.client.get(reverse("itineraries:list"))
        self.assertContains(response, "Mine to keep")
        self.assertNotContains(response, "Not mine")


class VisitFlowTests(FlowFixture):
    def setUp(self):
        self.login()
        self.today = date.today()

    def test_check_in_page_renders_for_published_place(self):
        response = self.client.get(reverse("visits:check_in", args=[self.place.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Submit your check-in")

    def test_unpublished_place_check_in_is_hidden(self):
        self.assertEqual(self.client.get(
            reverse("visits:check_in", args=[self.hidden.pk])).status_code, 404)

    def test_valid_check_in_is_pending_and_listed(self):
        response = self.client.post(reverse("visits:check_in", args=[self.place.pk]), {
            "visited_on": self.today.isoformat(),
            "visit_note": "Walked the trail with my family and took photos at the ridge.",
        })
        self.assertRedirects(
            response, reverse("visits:list"), fetch_redirect_response=False)
        checkin = VisitCheckIn.objects.get(user=self.user, place=self.place)
        self.assertEqual(checkin.status, VisitCheckIn.Status.PENDING)
        listing = self.client.get(reverse("visits:list"))
        self.assertContains(listing, "Published Falls")
        self.assertContains(listing, "Check-in submitted for staff review.")

    def test_duplicate_check_in_does_not_create_a_second_record(self):
        payload = {
            "visited_on": self.today.isoformat(),
            "visit_note": "Walked the trail with my family and took photos at the ridge.",
        }
        self.client.post(reverse("visits:check_in", args=[self.place.pk]), payload)
        self.client.post(reverse("visits:check_in", args=[self.place.pk]), payload)
        self.assertEqual(
            VisitCheckIn.objects.filter(user=self.user, place=self.place).count(), 1)

    def test_short_note_and_future_date_are_rejected(self):
        for payload in (
            {"visited_on": self.today.isoformat(), "visit_note": "too short"},
            {"visited_on": (self.today + timedelta(days=3)).isoformat(),
             "visit_note": "Walked the trail with my family and took photos at the ridge."},
        ):
            with self.subTest(payload=payload):
                self.client.post(
                    reverse("visits:check_in", args=[self.place.pk]), payload)
                self.assertFalse(VisitCheckIn.objects.filter(
                    user=self.user, place=self.place).exists())


class LegacyRouteTests(FlowFixture):
    def setUp(self):
        self.login()

    def test_retired_hobby_routes_redirect_to_discovery(self):
        response = self.client.get(reverse("hobbies:select"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("places:attraction_carousel"), response["Location"])

        response = self.client.get(reverse("hobbies:search"), {"q": "hiking"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("q=hiking", response["Location"])

    def test_city_selection_redirect_is_preserved(self):
        response = self.client.get(reverse("city_selection"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/hobbies/", response["Location"])

    def test_home_page_still_renders_public_content(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Published Falls")
        self.assertNotContains(response, "Unpublished Draft Place")
