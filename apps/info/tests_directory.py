from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.info.models import CityInformation
from apps.places.models import Place


class CityGuideVisibilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental")
        for kind in ("attraction", "event", "food", "stay", "transport"):
            CityInformation.objects.create(city=cls.city, title="Guide " + kind, info_type=kind,
                                           description="Guide description", is_published=True)
        cls.place = Place.objects.create(city=cls.city, title="Directory example", is_active=True, is_verified=True)
        cls.url = reverse("info:city_information")

    def test_only_attraction_and_event_guides_are_shown(self):
        before_guides = list(CityInformation.objects.order_by("pk").values())
        before_places = list(Place.objects.order_by("pk").values())
        response = self.client.get(self.url, {"section": "all"})
        for title in ("Guide attraction", "Guide event"):
            self.assertContains(response, title)
        for title in ("Guide food", "Guide stay", "Guide transport", "Directory example"):
            self.assertNotContains(response, title)
        self.assertNotContains(response, 'id="city-places-heading"')
        self.assertNotContains(response, 'aria-label="City guide types"')
        self.assertNotContains(response, 'aria-label="Explore city information by category"')
        self.assertEqual(response.context["total_count"], 2)
        self.assertEqual(before_guides, list(CityInformation.objects.order_by("pk").values()))
        self.assertEqual(before_places, list(Place.objects.order_by("pk").values()))

    def test_removed_type_and_directory_bookmarks_show_retained_guides(self):
        for params in ({"type": "food"}, {"type": "stay"}, {"type": "transport"},
                       {"directory": "malls"}, {"directory": "waterfalls"}):
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertContains(response, "Guide attraction")
                self.assertNotContains(response, "Guide event")
                event_response = self.client.get(self.url, {"section": "event"})
                self.assertContains(event_response, "Guide event")
                self.assertNotContains(response, "Guide food")
                self.assertNotContains(response, "Directory example")

    def test_empty_when_only_other_guide_types_are_published(self):
        CityInformation.objects.filter(info_type__in=["attraction", "event"]).update(is_published=False)
        response = self.client.get(self.url)
        self.assertContains(response, "No published Attraction guides yet")
        self.assertEqual(response.context["total_count"], 0)
        self.assertTrue(CityInformation.objects.filter(title="Guide food", is_published=True).exists())

    def test_places_remain_in_explore_places(self):
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.create_user(username="directoryvisitor", password="test")
        self.client.force_login(user)
        response = self.client.get(reverse("places:attraction_carousel"), {"browse": "all"})
        self.assertContains(response, "Directory example")


class HobbyAssignmentAdminFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth import get_user_model
        cls.user = get_user_model().objects.create_superuser(username='admin', password='test-only')
        city = City.objects.create(id=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        cls.tagged = Place.objects.create(city=city, title='Tagged shop', address='Kabankalan', is_active=True, is_verified=True)
        cls.untagged = Place.objects.create(city=city, title='Untagged place', address='Kabankalan', is_active=True, is_verified=True)
        cls.tagged.hobbies.add(Hobby.objects.create(name='Shopping', slug='shopping'))
        cls.tagged.hobbies.add(Hobby.objects.create(name='Photography', slug='photography'))

    def test_admin_filter_lists_untagged_without_changing_records(self):
        self.client.force_login(self.user)
        url = reverse('admin:places_place_changelist')
        response = self.client.get(url, {'hobby_assignment': 'missing'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Untagged place')
        self.assertNotContains(response, 'Tagged shop')
        self.assertContains(response, 'No hobbies assigned (review)')
        response = self.client.get(url, {'hobby_assignment': 'assigned'})
        self.assertContains(response, 'Tagged shop')
        self.assertNotContains(response, 'Untagged place')
        self.assertEqual(response.context['cl'].result_count, 1)  # multiple tags do not duplicate results
        self.assertEqual(self.tagged.hobbies.count(), 2)
        self.assertEqual(self.untagged.hobbies.count(), 0)
