from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Hobby
from apps.places.hobby_search import hobby_for_query
from apps.places.models import Place
from apps.places.search_intents import question_matches


class HobbyQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(id=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        cls.user = get_user_model().objects.create_user(username='visitor', password='test')
        names = {
            'billiards': 'Billiards', 'basketball': 'Basketball', 'cafe': 'Café Hopping',
            'hiking': 'Hiking', 'photography': 'Photography', 'gaming': 'Gaming',
            'food': 'Food Trip', 'music': 'Music', 'culture': 'Art & Culture',
            'nature': 'Beach & Nature', 'shopping': 'Shopping', 'others': 'Others',
            'birdwatching': 'Bird Watching',
        }
        cls.hobbies = {slug: Hobby.objects.create(slug=slug, name=name) for slug, name in names.items()}
        cls.match = Place.objects.create(city=cls.city, title='Sunset Point', address='Kabankalan',
                                         is_active=True, is_verified=True)
        cls.match.hobbies.add(cls.hobbies['photography'])
        cls.untagged = Place.objects.create(city=cls.city, title='Untagged park', address='Kabankalan',
                                            is_active=True, is_verified=True)
        cls.hidden = Place.objects.create(city=cls.city, title='Hidden photo place', address='Kabankalan',
                                           is_active=False, is_verified=True)
        cls.hidden.hobbies.add(cls.hobbies['photography'])
        cls.other = City.objects.create(name='Other City', slug='other-city')
        other_place = Place.objects.create(city=cls.other, title='Other photo place', address='Other',
                                           is_active=True, is_verified=True)
        other_place.hobbies.add(cls.hobbies['photography'])

    def test_all_builtin_hobbies_and_curated_phrases(self):
        queries = {
            'play billiards': 'billiards', 'basketball': 'basketball', 'café hopping': 'cafe',
            'go hiking': 'hiking', 'taking photos': 'photography', 'video games': 'gaming',
            'food trips': 'food', 'live music': 'music', 'art and culture': 'culture',
            'beach and nature': 'nature', 'shopping': 'shopping', 'others': 'others',
            'bird watching': 'birdwatching',
        }
        for query, slug in queries.items():
            with self.subTest(query=query):
                self.assertEqual(hobby_for_query(query), slug)

    def test_request_prefix_and_city_suffix(self):
        self.assertEqual(hobby_for_query('I enjoy taking photos in Kabankalan'), 'photography')
        self.assertEqual(hobby_for_query('I want to go hiking'), 'hiking')
        self.assertEqual(hobby_for_query('places for bird watching around Kabankalan'), 'birdwatching')

    def test_unknown_or_named_place_query_is_not_guessed(self):
        self.assertIsNone(hobby_for_query('Sunset Point photography'))
        self.assertIsNone(hobby_for_query('skydiving'))
        self.assertIsNone(hobby_for_query(''))

    def test_interest_query_returns_only_tagged_public_city_places_with_disclosure(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('places:attraction_carousel'), {'q': 'I enjoy taking photos'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([p.pk for p in response.context['attractions']], [self.match.pk])
        self.assertContains(response, 'Matched by assigned hobby tags')
        self.assertContains(response, 'Untagged places may also be relevant')
        self.assertFalse(self.untagged.hobbies.exists())

    def test_exact_place_named_as_hobby_wins(self):
        named = Place.objects.create(city=self.city, title='Photography', address='Kabankalan',
                                     is_active=True, is_verified=True)
        self.client.force_login(self.user)
        response = self.client.get(reverse('places:attraction_carousel'), {'q': 'Photography'})
        self.assertEqual([p.pk for p in response.context['attractions']], [named.pk])
        self.assertEqual(response.context['search_note'], '')

    def test_empty_tagged_set_is_empty_not_all_places(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('places:attraction_carousel'), {'q': 'bird watching'})
        self.assertEqual(list(response.context['attractions']), [])
        self.assertContains(response, 'Untagged places may also be relevant')

    def test_nearby_uses_same_hobby_matching(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('places:attraction_carousel'), {'mode': 'nearby', 'q': 'photography'})
        self.assertEqual([p.pk for p in response.context['results']], [self.match.pk])
        self.assertContains(response, 'Matched by assigned hobby tags')

    def test_hobby_phrases_survive_service_intent_routing(self):
        from apps.core.models import Category
        cafe_category = Category.objects.create(name='Coffee Shops', slug='coffee-shops-cafes')
        cafe = Place.objects.create(city=self.city, title='Tagged hangout', category=cafe_category,
                                    address='Kabankalan', is_active=True, is_verified=True)
        cafe.hobbies.add(self.hobbies['cafe'])
        Place.objects.create(city=self.city, title='Untagged cafe', category=cafe_category,
                             address='Kabankalan', is_active=True, is_verified=True)
        billiard = Place.objects.create(city=self.city, title='Tagged billiards venue', address='Kabankalan',
                                         is_active=True, is_verified=True)
        billiard.hobbies.add(self.hobbies['billiards'])
        self.client.force_login(self.user)
        for query, expected in [('café hopping', cafe), ('play billiards', billiard)]:
            for params in ({'q': query}, {'mode': 'nearby', 'q': query}):
                with self.subTest(query=query, params=params):
                    response = self.client.get(reverse('places:attraction_carousel'), params, follow=True)
                    self.assertEqual([p.pk for p in response.context['results']], [expected.pk])
                    self.assertContains(response, 'Matched by assigned hobby tags')
                    self.assertContains(response, 'Untagged places may also be relevant')
        # Selecting the coffee service explicitly continues to use category matches.
        response = self.client.get(reverse('places:attraction_carousel'),
                                   {'mode': 'nearby', 'service': 'coffee', 'q': 'café hopping'})
        self.assertEqual(set(p.pk for p in response.context['results']),
                         set(Place.objects.filter(category=cafe_category).values_list('pk', flat=True)))
        self.assertNotContains(response, 'Matched by assigned hobby tags')

    def test_buying_coffee_is_not_mistaken_for_hobby_or_service(self):
        from apps.core.models import Category
        cafe_category = Category.objects.create(name='Coffee Shops / Cafes', slug='coffee-shops-cafes')
        cafe = Place.objects.create(city=self.city, title='Local cafe', category=cafe_category,
                                    address='Kabankalan', is_active=True, is_verified=True)
        self.client.force_login(self.user)
        response = self.client.get(reverse('places:attraction_carousel'),
                                   {'q': 'where to buy coffee'}, follow=True)
        self.assertEqual([p.pk for p in response.context['results']], [cafe.pk])
        self.assertContains(response, 'availability is not confirmed')
        self.assertNotContains(response, 'Matched by assigned hobby tags')
