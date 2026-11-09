"""Tests for the accounts app: URL hygiene, the legacy alias and staff admin."""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City

User = get_user_model()


class AccountUrlTests(TestCase):
    """The branded account routes must own the canonical URL names."""

    def setUp(self):
        # The city-locking middleware requires the Kabankalan city row (id 2).
        City.objects.get_or_create(id=2, defaults={"name": "Kabankalan"})

    def test_login_name_resolves_to_the_branded_accounts_route(self):
        self.assertEqual(reverse("login"), "/accounts/login/")

    def test_register_and_logout_names_resolve_to_the_accounts_routes(self):
        self.assertEqual(reverse("register"), "/accounts/register/")
        self.assertEqual(reverse("logout"), "/accounts/logout/")

    def test_auth_forms_keep_csrf_and_progressive_password_controls(self):
        for name, count in (("login", 1), ("register", 2)):
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, 'name="csrfmiddlewaretoken"')
                self.assertContains(response, 'data-password-toggle', count=count)
                self.assertContains(response, 'aria-pressed="false" hidden', count=count)
                self.assertContains(response, 'css/explore.css')

    def test_invalid_registration_preserves_fields_and_reports_errors(self):
        response = self.client.post(reverse("register"), {
            "username": "invalid_account", "email": "bad-address",
            "password1": "short", "password2": "different",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="invalid_account"')
        self.assertContains(response, 'Please review the highlighted fields below.')
        self.assertContains(response, 'field-error-email')
        self.assertContains(response, 'field-error-consent_privacy')
        self.assertNotContains(response, 'value="short"')
        self.assertFalse(User.objects.filter(username="invalid_account").exists())

    def test_auth_posts_still_require_csrf(self):
        csrf_client = self.client_class(enforce_csrf_checks=True)
        for name in ("login", "register"):
            with self.subTest(name=name):
                self.assertEqual(csrf_client.post(reverse(name), {}).status_code, 403)
                csrf_client.get(reverse(name))
                token = csrf_client.cookies["csrftoken"].value
                self.assertEqual(csrf_client.post(reverse(name), {"csrfmiddlewaretoken": token}).status_code, 200)

    def test_legacy_users_login_route_still_serves_the_branded_page(self):
        response = self.client.get("/users/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "auth-card")

    def test_legacy_users_login_route_still_signs_a_user_in(self):
        User.objects.create_user(username="legacy_user", password="legacy-pass-2026")
        response = self.client.post(
            "/users/login/", {"username": "legacy_user", "password": "legacy-pass-2026"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)


class PrivacyNoticeTests(TestCase):
    """The privacy notice and the consent on sign-up (P3)."""

    @classmethod
    def setUpTestData(cls):
        City.objects.get_or_create(id=2, defaults={"name": "Kabankalan"})

    def test_notice_is_public_and_states_what_is_never_stored(self):
        response = self.client.get(reverse("core:privacy_notice"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "privacy/notice.html")
        self.assertContains(response, "Privacy Notice")
        self.assertContains(response, "Your live GPS position")
        self.assertContains(response, "not sent to this application’s server")
        self.assertContains(response, "OSRM routing service")
        self.assertContains(response, "Who can see it")

    def test_notice_is_linked_from_the_footer(self):
        response = self.client.get(reverse("core:privacy_notice"))
        self.assertContains(response, reverse("core:privacy_notice"))

    def test_registration_requires_the_consent(self):
        response = self.client.post(reverse("register"), {
            "username": "no_consent", "email": "no_consent@example.com",
            "password1": "sup3r-secret-pass", "password2": "sup3r-secret-pass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="no_consent").exists())
        self.assertContains(response, "Privacy Notice")

    def test_registration_stores_the_acceptance_with_a_date(self):
        response = self.client.post(reverse("register"), {
            "username": "with_consent", "email": "with_consent@example.com",
            "password1": "sup3r-secret-pass", "password2": "sup3r-secret-pass",
            "consent_privacy": "on",
        })
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(username="with_consent")
        self.assertTrue(created.consent_privacy)
        self.assertIsNotNone(created.consent_privacy_at)


class UserAdminTests(TestCase):
    """The custom user model has to be reachable from the staff dashboard."""

    def setUp(self):
        # The city-locking middleware requires the Kabankalan city row (id 2).
        City.objects.get_or_create(id=2, defaults={"name": "Kabankalan"})
        self.admin_user = User.objects.create_superuser(
            username="staff_admin", email="staff@example.com", password="staff-pass-2026"
        )
        self.client.force_login(self.admin_user)

    def test_custom_user_model_is_registered_in_the_admin(self):
        self.assertIn(User, admin.site._registry)
        self.assertEqual(admin.site._registry[User].__class__.__name__, "ExploreUserAdmin")

    def test_admin_index_hides_the_authentication_group_editor(self):
        # Accounts are managed through the project's own Users section, so the
        # default "Authentication and Authorization" block is not listed.
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Authentication and Authorization")
        # ... but the native group editor is still reachable for a superuser.
        self.assertEqual(self.client.get("/admin/auth/group/").status_code, 200)

    def test_admin_index_shows_the_manage_users_shortcut(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage users")
        self.assertContains(response, "/admin/users/user/")

    def test_user_changelist_and_add_form_render(self):
        response = self.client.get("/admin/users/user/")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/admin/users/user/add/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kabankalan role")

    def test_admin_can_create_an_account_with_a_role(self):
        response = self.client.post(
            "/admin/users/user/add/",
            {
                "username": "created_by_staff",
                "email": "created@example.com",
                "password1": "created-pass-2026",
                "password2": "created-pass-2026",
                "role": "city_admin",
                "managed_city": "",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(username="created_by_staff")
        self.assertEqual(created.role, User.Role.CITY_ADMIN)
