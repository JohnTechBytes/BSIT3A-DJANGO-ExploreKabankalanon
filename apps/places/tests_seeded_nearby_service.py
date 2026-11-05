"""Nearby service matching accepts both existing coffee hobby slug variants."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from apps.cities.models import City
from apps.core.management.commands.seed_kabankalan import HOBBIES
from apps.core.models import Category, Hobby
from apps.places.models import Place


class SeededNearbyServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        other_city = City.objects.create(name='Other City', slug='other-city')
        cls.user = get_user_model().objects.create_user(username='visitor', password='test')
        seeded_name = next(entry['name'] for entry in HOBBIES if entry['name'] == 'Coffee & Cafe Hopping')
        seeded = Hobby.objects.create(name=seeded_name, slug=slugify(seeded_name))
        short = Hobby.objects.create(name='Café Hopping', slug='cafe')
        cafe_category = Category.objects.create(name='Coffee Shops', slug='coffee-shops-cafes')
        cls.seeded_place = Place.objects.create(city=cls.city, title='Seed tagged venue',
                                               is_active=True, is_verified=True)
        cls.seeded_place.hobbies.add(seeded)
        cls.short_place = Place.objects.create(city=cls.city, title='Short tagged venue',
                                              is_active=True, is_verified=True)
        cls.short_place.hobbies.add(short)
        cls.category_place = Place.objects.create(city=cls.city, title='Category venue', category=cafe_category,
                                                 is_active=True, is_verified=True)
        Place.objects.create(city=cls.city, title='Untagged venue', is_active=True, is_verified=True)
        for city, active, verified in ((cls.city, False, True), (cls.city, True, False),
                                       (other_city, True, True)):
            hidden = Place.objects.create(city=city, title='Hidden tagged venue',
                                          is_active=active, is_verified=verified)
            hidden.hobbies.add(seeded)

    def test_coffee_service_uses_both_tag_variants_and_categories(self):
        self.client.force_login(self.user)
        url = reverse('places:attraction_carousel')
        for params in ({'mode': 'nearby', 'service': 'coffee'},
                       {'mode': 'nearby', 'q': 'coffee shop'}):
            with self.subTest(params=params):
                response = self.client.get(url, params, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertEqual({place.pk for place in response.context['results']},
                                 {self.seeded_place.pk, self.short_place.pk, self.category_place.pk})
                self.assertContains(response, 'Matches use listing names, categories, or assigned hobby tags.')
                self.assertContains(response, 'Confirm current services before visiting.')
