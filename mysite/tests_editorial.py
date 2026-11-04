"""The remaining redesigned screens retain their forms and admin controls."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category
from apps.itineraries.models import Itinerary
from apps.places.models import Place


class EditorialScreenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        cls.user = get_user_model().objects.create_superuser(
            username="editorial_staff", password="test-password-123", email="staff@example.test"
        )
        cls.place = Place.objects.create(
            city=city, title="Published destination", slug="published-destination",
            is_active=True, is_verified=True,
        )
        cls.trip = Itinerary.objects.create(user=cls.user, city=city, title="Trip", day_number=1)

    def test_account_forms_load_the_editorial_styles(self):
        for name in ("login", "register"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, "css/explore.css")
                self.assertContains(response, "js/motion.js")
                self.assertContains(response, 'class="auth-page ek-theme"')
                self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_public_screens_retain_their_editorial_scope(self):
        self.client.force_login(self.user)
        routes = [
            reverse("itineraries:create"), reverse("itineraries:builder", args=[self.trip.pk]),
            reverse("itineraries:choose_for_place", args=[self.place.pk]),
            reverse("places:my_reviews"), reverse("visits:list"),
            reverse("visits:check_in", args=[self.place.pk]),
            reverse("evaluation:sus_survey"), reverse("evaluation:sus_thanks"),
            reverse("core:privacy_notice"),
        ]
        for url in routes:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'site-dark refresh-page')
                self.assertContains(response, 'css/public-refresh.css')
                self.assertContains(response, 'css/system-guide.css')
                self.assertContains(response, 'css/design-craft.css')
                self.assertContains(response, 'css/public-night.css')
                self.assertContains(response, 'js/public-reveal.js')
                self.assertContains(response, 'js/public-motion.js')
        self.assertContains(self.client.get(reverse("itineraries:create")), 'name="title"')
        self.assertContains(self.client.get(reverse("itineraries:builder", args=[self.trip.pk])), 'name="place_id"')
        self.assertContains(self.client.get(reverse("visits:check_in", args=[self.place.pk])), 'name="visit_note"')
        self.assertContains(self.client.get(reverse("evaluation:sus_survey")), 'name="q10"')

    def test_city_discovery_keeps_its_listing_and_pagination(self):
        Place.objects.create(city=self.place.city, title="Unpublished candidate",
                             slug="unpublished-candidate", is_active=False, is_verified=False)
        response = self.client.get(reverse("places:city_discover"))
        self.assertContains(response, 'browse-page discovery-page')
        self.assertContains(response, self.place.title)
        self.assertNotContains(response, 'Unpublished candidate')
        self.assertContains(response, 'Page 1 of 1')
        self.assertContains(response, 'Photo not yet available')
        self.assertNotContains(response, 'images.unsplash.com')

    def test_city_discovery_uses_labelled_local_category_samples(self):
        category = Category.objects.create(name="Museum", slug="museum")
        Place.objects.create(city=self.place.city, title="Local Museum", category=category,
                             is_active=True, is_verified=True)
        response = self.client.get(reverse("places:city_discover"))
        self.assertContains(response, '/static/img/samples/museum.jpg')
        self.assertContains(response, 'Illustrative category sample · Not actual destination')
        self.assertNotContains(response, 'images.unsplash.com')

    def test_staff_admin_keeps_forms_filters_and_actions(self):
        self.client.force_login(self.user)
        for name in ("admin:index", "admin:places_place_changelist", "admin:places_place_osm_review"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, "css/admin-editorial.css")
                self.assertContains(response, "css/admin-guide.css")
                self.assertContains(response, "css/design-craft.css")
        response = self.client.get(reverse("admin:places_place_changelist"))
        self.assertContains(response, 'id="ea-dest-filter-form"')
        self.assertContains(response, 'name="action"')
        response = self.client.get(reverse("admin:places_place_change", args=[self.place.pk]))
        self.assertContains(response, 'name="_save"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_staff_dashboard_displays_real_summary_and_management_links(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, 'ea-admin-home')
        self.assertContains(response, 'Staff dashboard')
        self.assertContains(response, 'Published places')
        self.assertContains(response, reverse("admin:places_place_changelist"))
        self.assertContains(response, reverse("admin:places_place_osm_review"))
        self.assertContains(response, reverse("admin:users_user_changelist"))
        self.assertContains(response, 'All permitted admin modules')

    def test_staff_dashboard_hides_unpermitted_metrics_and_shortcuts(self):
        limited = get_user_model().objects.create_user(
            username="limited_staff", password="test-password-123", is_staff=True
        )
        limited.user_permissions.add(Permission.objects.get(
            content_type__app_label="places", codename="view_place"
        ))
        self.client.force_login(limited)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, 'Published places')
        self.assertContains(response, reverse("admin:places_place_changelist"))
        self.assertContains(response, reverse("admin:places_place_osm_review"))
        self.assertNotContains(response, 'Pending visits')
        self.assertNotContains(response, 'User accounts')
        self.assertNotContains(response, reverse("admin:users_user_changelist"))
        self.assertNotContains(response, reverse("admin:visits_visitcheckin_changelist"))

    def test_admin_navigation_retains_account_actions_and_csrf_logout(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, 'id="ea-account-menu"')
        self.assertContains(response, reverse("admin:password_change"))
        self.assertContains(response, reverse("admin:logout"))
        self.assertContains(response, 'aria-controls="ea-admin-sidebar"')
        self.assertContains(response, 'aria-expanded="false"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        csrf_client.get(reverse("admin:index"))
        self.assertEqual(csrf_client.post(reverse("admin:logout")).status_code, 403)
        token = csrf_client.cookies["csrftoken"].value
        self.assertEqual(csrf_client.post(reverse("admin:logout"), {"csrfmiddlewaretoken": token}).status_code, 302)
        self.assertNotIn("_auth_user_id", csrf_client.session)

    def test_sidebar_sections_load_shared_workspace_styles_and_native_controls(self):
        self.client.force_login(self.user)
        for name in ("admin:places_place_changelist", "admin:places_place_osm_review",
                     "admin:info_cityinformation_changelist", "admin:visits_visitcheckin_changelist",
                     "admin:users_user_changelist"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, "css/admin-workspace.css")
                self.assertContains(response, 'id="ea-admin-sidebar"')
        for name in ("admin:info_cityinformation_changelist", "admin:visits_visitcheckin_changelist",
                     "admin:users_user_changelist"):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, 'name="q"')
        # Django shows bulk actions only when there are rows to act on.
        self.assertContains(self.client.get(reverse("admin:users_user_changelist")), 'name="action"')
        response = self.client.get(reverse("admin:places_place_change", args=[self.place.pk]))
        self.assertContains(response, "css/admin-workspace.css")
        self.assertContains(response, 'name="_save"')
