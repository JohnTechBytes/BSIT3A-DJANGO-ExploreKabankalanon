"""Search aliases work with the real fresh-install hobby taxonomy too."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from apps.cities.models import City
from apps.core.management.commands.seed_kabankalan import HOBBIES
from apps.core.models import Hobby
from apps.places.hobby_search import hobby_for_query
from apps.places.models import Place


class SeededHobbySearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(id=2, name='Kabankalan', slug='kabankalan')
        cls.user = get_user_model().objects.create_user(username='visitor', password='test')
        # Mirror the seed command's taxonomy without running its place-writing logic.
        cls.hobbies = {
            slugify(entry['name']): Hobby.objects.create(
                slug=slugify(entry['name']), name=entry['name']
            )
            for entry in HOBBIES
        }

    def test_seeded_aliases_and_exact_names(self):
        queries = {
            'hiking': 'hiking-eco-tourism',
            'go hiking': 'hiking-eco-tourism',
            'coffee hopping': 'coffee-cafe-hopping',
            'café hopping': 'coffee-cafe-hopping',
            'food trips': 'dining-foodie',
            'music': 'karaoke-nightlife',
            'art and culture': 'culture-heritage',
            'taking photos': 'photography',
            'play billiards': 'billiards',
            'Hiking & Eco-Tourism': 'hiking-eco-tourism',
            'places for coffee hopping in Kabankalan City': 'coffee-cafe-hopping',
        }
        for query, slug in queries.items():
            with self.subTest(query=query):
                self.assertEqual(hobby_for_query(query), slug)
        self.assertIsNone(hobby_for_query('unknown activity'))
        self.assertIsNone(hobby_for_query('Sunset Point hiking'))

    def test_ambiguous_aliases_are_not_guessed_but_exact_names_win(self):
        Hobby.objects.create(slug='hiking', name='Hiking')
        self.assertIsNone(hobby_for_query('go hiking'))
        self.assertEqual(hobby_for_query('hiking'), 'hiking')
        self.assertEqual(hobby_for_query('Hiking & Eco-Tourism'), 'hiking-eco-tourism')

    def test_seeded_hobbies_filter_tagged_public_places_in_browse_and_nearby(self):
        self.client.force_login(self.user)
        for index, (query, slug) in enumerate((
            ('go hiking', 'hiking-eco-tourism'),
            ('coffee hopping', 'coffee-cafe-hopping'),
            ('food trips', 'dining-foodie'),
            ('music', 'karaoke-nightlife'),
            ('art and culture', 'culture-heritage'),
        )):
            tagged = Place.objects.create(city=self.city, title=f'Tagged place {index}',
                                          is_active=True, is_verified=True)
            tagged.hobbies.add(self.hobbies[slug])
            hidden = Place.objects.create(city=self.city, title=f'Hidden place {index}',
                                          is_active=False, is_verified=True)
            hidden.hobbies.add(self.hobbies[slug])
            for params in ({'q': query}, {'mode': 'nearby', 'q': query}):
                with self.subTest(query=query, params=params):
                    response = self.client.get(reverse('places:attraction_carousel'), params, follow=True)
                    self.assertEqual(response.status_code, 200)
                    places = response.context.get('results', response.context.get('attractions', []))
                    self.assertEqual([p.pk for p in places], [tagged.pk])
                    self.assertContains(response, 'Matched by assigned hobby tags')
                    self.assertContains(response, 'Untagged places may also be relevant')
            self.assertFalse(hidden.is_active)
