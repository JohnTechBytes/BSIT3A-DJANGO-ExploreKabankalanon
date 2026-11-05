from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.info.models import CityInformation
from apps.places.models import Place


class SharedCityDirectoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(id=2, name="Kabankalan", slug="kabankalan", province="Negros Occidental")
        cls.other = City.objects.create(name="Other City", slug="other-city")
        cls.mall_category = Category.objects.create(name="Malls / Shopping Centers", slug="malls-shopping-centers")
        cls.food_category = Category.objects.create(name="Restaurants / Eateries", slug="restaurants-eateries")
        cls.shop_category = Category.objects.create(name="Other Local Businesses", slug="other-local-businesses")
        cls.nature_category = Category.objects.create(name="Mountain & Peak", slug="mountain-peak")
        cls.hobby = Hobby.objects.create(name="Shopping", slug="shopping")
        def place(title, category=None, **kwargs):
            return Place.objects.create(title=title, city=kwargs.pop("city", cls.city), category=category,
                                        address="Kabankalan", is_active=kwargs.pop("is_active", True),
                                        is_verified=kwargs.pop("is_verified", True), **kwargs)
        cls.mall = place("Example Mall", cls.mall_category)
        cls.mall.hobbies.add(cls.hobby)
        cls.falls = place("Example Falls")  # unclassified: a conservative name match
        cls.hill = place("Example Hill", cls.nature_category)
        cls.food = place("Example Kitchen", cls.food_category)
        cls.shop = place("Example Shop", cls.shop_category)
        cls.unknown = place("Unknown category")
        cls.unverified = place("Unpublished place", is_verified=False)
        cls.inactive = place("Inactive place", is_active=False)
        cls.other_place = place("Other city place", city=cls.other)
        cls.guide = CityInformation.objects.create(city=cls.city, title="Travel note", info_type="transport",
                                                   description="Published city guide", is_published=True)
        cls.draft = CityInformation.objects.create(city=cls.city, title="Private draft", info_type="transport",
                                                   description="Not public", is_published=False)
        cls.url = reverse("info:city_information")

    def test_all_shows_guides_and_shared_places_without_exposing_hidden_content(self):
        response = self.client.get(self.url)
        for content in ("Travel note", "Example Mall", "Example Falls", "Unknown category"):
            self.assertContains(response, content)
        for content in ("Private draft", "Unpublished place", "Inactive place", "Other city place"):
            self.assertNotContains(response, content)
        self.assertContains(response, reverse("places:place_detail", args=[self.mall.pk]))
        self.assertContains(response, "No hobby tags assigned")
        self.assertContains(response, "Hobbies: Shopping")
        self.assertContains(response, "missing hobby tag does not mean a place is irrelevant")

    def test_directory_groups_and_overlapping_attractions(self):
        tests = {
            "malls": ("Example Mall", "Example Kitchen"),
            "waterfalls": ("Example Falls", "Example Mall"),
            "attractions": ("Example Falls", "Example Mall"),
            "food": ("Example Kitchen", "Example Shop"),
            "services": ("Example Shop", "Example Kitchen"),
        }
        for section, (present, absent) in tests.items():
            with self.subTest(section=section):
                response = self.client.get(self.url, {"directory": section})
                self.assertContains(response, present)
                self.assertNotContains(response, absent)
                self.assertNotContains(response, "Travel note")
                self.assertContains(response, 'aria-current="page"')

    def test_legacy_type_link_and_guide_filter_are_preserved(self):
        response = self.client.get(self.url, {"type": "transport"})
        self.assertEqual(response.context["selected_directory"], "guides")
        self.assertContains(response, "Travel note")
        self.assertNotContains(response, "Example Mall")
        self.assertContains(response, 'name="type" value="transport"')

    def test_search_filters_places_and_keeps_category(self):
        response = self.client.get(self.url, {"directory": "malls", "q": "Example"})
        self.assertContains(response, "Example Mall")
        self.assertNotContains(response, "Example Kitchen")
        self.assertContains(response, 'name="directory" value="malls"')
        self.assertContains(response, 'directory=waterfalls&amp;q=Example')
        response = self.client.get(self.url, {"directory": "malls", "q": "nonexistent"})
        self.assertContains(response, "No matching places")

    def test_unknown_directory_and_invalid_page_fall_back_safely(self):
        response = self.client.get(self.url, {"directory": "not-real", "page": "oops"})
        self.assertEqual(response.context["selected_directory"], "all")
        self.assertEqual(response.context["place_page"].number, 1)

    def test_pagination_keeps_search_and_section(self):
        Place.objects.bulk_create([
            Place(city=self.city, category=self.mall_category, title=f"Example extra {i:02}",
                  address="Kabankalan", is_active=True, is_verified=True)
            for i in range(25)
        ])
        response = self.client.get(self.url, {"directory": "malls", "q": "Example"})
        self.assertEqual(response.context["place_page"].paginator.count, 26)
        self.assertContains(response, 'page=2&amp;directory=malls&amp;q=Example')
        response = self.client.get(self.url, {"directory": "malls", "q": "Example", "page": "2"})
        self.assertEqual(response.context["place_page"].number, 2)
        self.assertEqual(len(response.context["place_page"].object_list), 2)

    def test_render_is_read_only_and_photo_attribution_is_displayed(self):
        self.mall.cover_image_url = 'https://example.com/mall.jpg'
        self.mall.photo_credit = 'Test photographer'
        self.mall.photo_license = 'CC BY 4.0'
        self.mall.photo_license_url = 'https://creativecommons.org/licenses/by/4.0/'
        self.mall.photo_source_url = 'https://example.com/source'
        self.mall.save()
        before = list(Place.objects.order_by('pk').values_list('pk', 'is_active', 'is_verified', 'category_id'))
        response = self.client.get(self.url, {"directory": "malls"})
        self.assertContains(response, "Test photographer")
        self.assertContains(response, 'https://example.com/source')
        self.assertContains(response, 'https://creativecommons.org/licenses/by/4.0/')
        self.assertEqual(before, list(Place.objects.order_by('pk').values_list('pk', 'is_active', 'is_verified', 'category_id')))
        self.assertEqual(list(self.mall.hobbies.values_list('pk', flat=True)), [self.hobby.pk])


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
