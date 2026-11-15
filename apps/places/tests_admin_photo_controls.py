"""Admin photo controls: do not delete stored rights on unrelated edits."""
from types import SimpleNamespace
from unittest.mock import Mock

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.admin import CityInformationAdmin
from apps.info.models import CityInformation
from apps.places.models import Place


class PhotoControlAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        cls.staff = get_user_model().objects.create_superuser(username='photo_admin', password='test')
        cls.place = Place.objects.create(
            city=cls.city, title='Example place', slug='example-place', address='Kabankalan',
            cover_image_url='https://example.com/old.jpg', photo_credit='Original credit',
            photo_source_url='https://example.com/old-source', photo_license='CC BY 4.0',
            photo_license_url='https://example.com/license', is_active=True, is_verified=True,
        )
        cls.osm_place = Place.objects.create(
            city=cls.city, title='Mapped place', slug='osm-node-12345', address='Kabankalan',
            is_active=False, is_verified=False,
        )
        cls.guide = CityInformation.objects.create(city=cls.city, title='Guide', info_type='attraction',
                                                  description='Example guide', photo_credit='Guide credit',
                                                  is_published=True)

    def setUp(self):
        self.client.force_login(self.staff)
        self.request = RequestFactory().get('/')
        self.request.user = self.staff
        self.place_admin = admin.site._registry[Place]

    def test_admin_add_normal_and_osm_forms_hide_license_controls(self):
        for url in (reverse('admin:places_place_add'),
                    reverse('admin:places_place_change', args=[self.place.pk]),
                    reverse('admin:places_place_change', args=[self.osm_place.pk])):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'name="photo_license"')
                self.assertNotContains(response, 'name="photo_license_url"')
                self.assertContains(response, 'name="photo_credit"')
                self.assertContains(response, 'name="photo_source_url"')

    def save_place(self, **changes):
        place = Place.objects.get(pk=self.place.pk)
        form_class = self.place_admin.get_form(self.request, place)
        data = model_to_dict(place)
        data.update(changes)
        form = form_class(data=data, instance=place)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        obj = form.save(commit=False)
        self.place_admin.save_model(self.request, obj, form, True)
        return Place.objects.get(pk=self.place.pk)

    def test_unrelated_edit_keeps_license_and_public_attribution(self):
        saved = self.save_place(description='Updated description')
        self.assertEqual(saved.photo_license, 'CC BY 4.0')
        self.assertEqual(saved.photo_license_url, 'https://example.com/license')
        self.assertEqual(saved.photo_credit, 'Original credit')
        response = self.client.get(reverse('places:place_detail', args=[saved.pk]))
        self.assertContains(response, 'CC BY 4.0')
        self.assertContains(response, 'Original credit')

    def test_photo_replacement_clears_old_license_but_not_entered_credit(self):
        saved = self.save_place(cover_image_url='https://example.com/new.jpg',
                                photo_credit='New credit', photo_source_url='https://example.com/new-source')
        self.assertEqual(saved.cover_image_url, 'https://example.com/new.jpg')
        self.assertEqual(saved.photo_license, '')
        self.assertEqual(saved.photo_license_url, '')
        self.assertEqual(saved.photo_credit, 'New credit')
        self.assertEqual(saved.photo_source_url, 'https://example.com/new-source')

    def test_removing_cover_clears_old_license(self):
        saved = self.save_place(cover_image_url='')
        self.assertEqual(saved.photo_license, '')
        self.assertEqual(saved.photo_license_url, '')

    def test_posted_hidden_license_fields_cannot_override_existing_values(self):
        saved = self.save_place(description='Updated', photo_license='forged',
                                photo_license_url='https://example.com/forged')
        self.assertEqual(saved.photo_license, 'CC BY 4.0')
        self.assertEqual(saved.photo_license_url, 'https://example.com/license')

    def test_uploaded_cover_keeps_license_when_only_secondary_url_changes(self):
        self.place.cover_image = 'places/covers/original.jpg'
        self.place.save(update_fields=['cover_image'])
        saved = self.save_place(cover_image_url='https://example.com/secondary.jpg')
        self.assertEqual(saved.photo_license, 'CC BY 4.0')

    def test_city_guide_form_retains_credit_and_excludes_optional_license_fields(self):
        response = self.client.get(reverse('admin:info_cityinformation_change', args=[self.guide.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="photo_credit"')
        self.assertNotContains(response, 'name="photo_license"')
        self.assertNotContains(response, 'name="photo_license_url"')
        city_admin = admin.site._registry[CityInformation]
        self.assertEqual(city_admin.get_exclude(self.request), ('photo_license', 'photo_license_url'))
        self.assertContains(response, 'name="photo_source_url"')

    def test_city_info_edits_preserve_license_and_replacement_clears_it(self):
        self.guide.thumbnail_url = 'https://example.com/old.jpg'
        self.guide.photo_license = 'CC BY 4.0'
        self.guide.photo_license_url = 'https://example.com/license'
        self.guide.photo_source_url = 'https://example.com/source'
        self.guide.save()
        city_admin = admin.site._registry[CityInformation]
        for image, title, expected_license in (
            ('https://example.com/old.jpg', 'Updated guide', 'CC BY 4.0'),
            ('https://example.com/new.jpg', 'Updated again', ''),
        ):
            guide = CityInformation.objects.get(pk=self.guide.pk)
            form_class = city_admin.get_form(self.request, guide)
            data = model_to_dict(guide)
            data.update(thumbnail_url=image, title=title, photo_license='forged',
                        photo_license_url='https://example.com/forged')
            form = form_class(data=data, instance=guide)
            self.assertTrue(form.is_valid(), form.errors.as_json())
            obj = form.save(commit=False)
            city_admin.save_model(self.request, obj, form, True)
            guide.refresh_from_db()
            self.assertEqual(guide.photo_license, expected_license)
            self.assertEqual(guide.photo_license_url, 'https://example.com/license' if expected_license else '')
            self.assertEqual(guide.photo_source_url, 'https://example.com/source')
            self.assertEqual(guide.photo_credit, 'Guide credit')
            self.assertContains(self.client.get(reverse('info:city_information')), 'Guide credit')

    def test_optional_mapped_city_license_fields_preserve_or_clear(self):
        site_admin = CityInformationAdmin(CityInformation, admin.site)
        field_names = ['title', 'photo_license', 'photo_license_url']
        site_admin.model = SimpleNamespace(_meta=SimpleNamespace(concrete_fields=[SimpleNamespace(name=n) for n in field_names]))
        self.assertEqual(site_admin.get_exclude(self.request), ('photo_license', 'photo_license_url'))
        obj = SimpleNamespace(photo_license='Old license', photo_license_url='https://example.com/license', save=Mock())
        site_admin.save_model(self.request, obj, SimpleNamespace(changed_data=['title']), True)
        self.assertEqual(obj.photo_license, 'Old license')
        self.assertEqual(obj.photo_license_url, 'https://example.com/license')
        site_admin.save_model(self.request, obj, SimpleNamespace(changed_data=['thumbnail_url']), True)
        self.assertEqual(obj.photo_license, '')
        self.assertEqual(obj.photo_license_url, '')
