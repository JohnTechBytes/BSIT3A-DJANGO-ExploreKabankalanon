"""Missing photos use honest illustrations without altering place records."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.places.models import Place, SavedPlace


class IllustrativePhotoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        cls.user = get_user_model().objects.create_user(username='visitor', password='test')
        cls.place = Place.objects.create(city=cls.city, title='Unclassified Local Business',
                                         is_active=True, is_verified=True, address='Kabankalan')
        SavedPlace.objects.create(user=cls.user, place=cls.place)

    def setUp(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['selected_city_id'] = self.city.pk
        session.save()

    def test_missing_cover_uses_labeled_generic_image_across_public_views(self):
        paths = [
            (reverse('home'), {}),
            (reverse('places:attraction_carousel'), {'browse': 'all'}),
            (reverse('places:attraction_carousel'), {'mode': 'nearby'}),
            (reverse('places:place_detail', args=[self.place.pk]), {}),
            (reverse('places:saved_places'), {}),
            (reverse('places:city_discover'), {}),
            (reverse('info:city_information'), {}),
        ]
        for url, params in paths:
            with self.subTest(url=url, params=params):
                response = self.client.get(url, params, follow=True)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, ' src="/static/img/samples/generic.jpg"')
                self.assertContains(response, 'Not an actual photo')
                self.assertContains(response, 'not an actual photo of Unclassified Local Business')
        self.place.refresh_from_db()
        self.assertFalse(self.place.cover_image)
        self.assertFalse(self.place.cover_image_url)

    def test_recorded_cover_remains_primary_and_gets_fallback_attribute(self):
        self.place.cover_image = 'places/covers/missing-local-file.jpg'
        self.place.save(update_fields=['cover_image'])
        for params in ({'browse': 'all'}, {'mode': 'nearby'}):
            with self.subTest(params=params):
                response = self.client.get(reverse('places:attraction_carousel'), params)
                self.assertContains(response, '/media/places/covers/missing-local-file.jpg')
                self.assertContains(response, 'data-sample-src="/static/img/samples/generic.jpg"')
                self.assertNotContains(response, ' src="/static/img/samples/generic.jpg"')
        self.place.refresh_from_db()
        self.assertEqual(self.place.cover_image.name, 'places/covers/missing-local-file.jpg')
