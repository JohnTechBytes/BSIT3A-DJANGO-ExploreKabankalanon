"""Public design-system wiring and task layout regression tests."""
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.core.models import Category
from apps.places.models import Place


class PublicSystemTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan')
        category = Category.objects.create(name='Food', slug='food')
        cls.place = Place.objects.create(city=city, category=category, title='Existing place',
                                         is_active=True, is_verified=True)
        cls.user = get_user_model().objects.create_user(username='design_test', password='test-pass-123')

    def test_public_pages_load_shared_stylesheet_and_existing_controls(self):
        self.client.force_login(self.user)
        for url in (reverse('places:attraction_carousel'), reverse('info:city_information'),
                    reverse('places:place_detail', args=[self.place.pk]),
                    reverse('places:saved_places'), reverse('places:my_reviews'),
                    reverse('core:privacy_notice'), reverse('evaluation:sus_survey')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'css/public-system.css?v=1')
        nearby = self.client.get(reverse('places:attraction_carousel'), {'mode': 'nearby'})
        self.assertContains(nearby, 'id="ea6-query"')
        self.assertContains(nearby, 'id="ea6-use-gps"')
        self.assertContains(nearby, 'css/public-system.css?v=1')

    def test_search_precedes_summary_without_losing_map_or_carousel(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('places:attraction_carousel'), {'browse': 'all'})
        html = response.content.decode()
        self.assertLess(html.index('class="ea-discovery-tools"'), html.index('class="ea-summary"'))
        for control in ('id="ea-search-query"', 'id="ea-filter-category"', 'id="ea-filter-hobby"',
                        'id="ea-list-button"', 'id="ea-map-button"', 'id="ea-carousel"'):
            self.assertIn(control, html)

    def test_auth_and_error_templates_load_the_shared_system(self):
        self.assertContains(self.client.get(reverse('login')), 'css/public-system.css?v=1')
        self.assertContains(self.client.get(reverse('register')), 'css/public-system.css?v=1')
        for template in ('errors/404.html', 'errors/500.html'):
            self.assertIn('css/public-system.css?v=1', render_to_string(template))
        css = Path(finders.find('css/public-system.css')).read_text(encoding='utf-8')
        self.assertIn(':focus-visible', css)
        self.assertIn('prefers-reduced-motion: reduce', css)

    def test_cinematic_experience_is_wired_to_public_pages(self):
        self.client.force_login(self.user)
        for url in (reverse('home'), reverse('places:attraction_carousel'),
                    reverse('info:city_information'), reverse('places:place_detail', args=[self.place.pk]),
                    reverse('places:saved_places'), reverse('places:my_reviews'),
                    reverse('core:privacy_notice'), reverse('evaluation:sus_survey')):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), 'css/public-experience.css?v=1')
        self.client.logout()
        for url in (reverse('login'), reverse('register')):
            self.assertContains(self.client.get(url), 'css/public-experience.css?v=1')
        self.client.force_login(self.user)
        for template in ('errors/404.html', 'errors/500.html'):
            self.assertIn('css/public-experience.css?v=1', render_to_string(template))
        response = self.client.get(reverse('places:attraction_carousel'))
        self.assertContains(response, 'mode=nearby')
        self.assertContains(response, '--xp-carousel-transform')
        css = Path(finders.find('css/public-experience.css')).read_text(encoding='utf-8')
        self.assertIn('100cqw', css)
        self.assertIn('var(--xp-carousel-transform, none)', css)

    def test_homepage_photo_credit_and_sample_are_not_confused(self):
        self.place.cover_image_url = 'https://example.com/photo.jpg'
        self.place.photo_credit = 'Photographer Example'
        self.place.photo_source_url = 'https://example.com/source'
        self.place.photo_license = 'CC BY 4.0'
        self.place.save()
        html = self.client.get(reverse('home')).content.decode()
        self.assertIn('Photographer Example', html)
        self.assertIn('https://example.com/source', html)
        self.assertIn('place-photo-fallback.js', html)
        fallback = Path(finders.find('js/public-experience-photo.js')).read_text(encoding='utf-8')
        self.assertIn('.card-credit', fallback)
        self.assertIn('credit.hidden = true', fallback)

    def test_palette_is_loaded_for_public_and_recovery_pages(self):
        self.client.force_login(self.user)
        for url in (reverse('home'), reverse('places:attraction_carousel'),
                    reverse('info:city_information'), reverse('places:place_detail', args=[self.place.pk]),
                    reverse('places:saved_places'), reverse('core:privacy_notice')):
            with self.subTest(url=url):
                self.assertContains(self.client.get(url), 'css/public-palette.css?v=1')
        self.client.logout()
        for url in (reverse('login'), reverse('register')):
            self.assertContains(self.client.get(url), 'css/public-palette.css?v=1')
        for template in ('errors/404.html', 'errors/500.html'):
            self.assertIn('css/public-palette.css?v=1', render_to_string(template))

    def test_field_guide_wiring_and_mobile_saved_link(self):
        self.client.force_login(self.user)
        urls = (reverse('places:attraction_carousel'), reverse('places:city_discover'),
                reverse('info:city_information'), reverse('places:place_detail', args=[self.place.pk]),
                reverse('places:saved_places'), reverse('places:my_reviews'),
                reverse('places:journey_dashboard'), reverse('itineraries:list'),
                reverse('itineraries:create'), reverse('itineraries:choose_for_place', args=[self.place.pk]),
                reverse('visits:list'), reverse('visits:check_in', args=[self.place.pk]),
                reverse('core:privacy_notice'), reverse('evaluation:sus_survey'))
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'css/public-field-guide.css?v=1')
                self.assertContains(response, 'class="field-mobile-saved"')
        self.client.logout()
        for url in (reverse('login'), reverse('register')):
            self.assertContains(self.client.get(url), 'css/public-field-guide.css?v=1')
        for template in ('errors/404.html', 'errors/500.html'):
            self.assertIn('css/public-field-guide.css?v=1', render_to_string(template))
        css = Path(finders.find('css/public-field-guide.css')).read_text(encoding='utf-8')
        self.assertIn(':focus-visible', css)
        self.assertIn('prefers-reduced-motion:reduce', css)

    def test_privacy_notice_distinguishes_distance_from_osrm_routes(self):
        response = self.client.get(reverse('core:privacy_notice'))
        self.assertContains(response, 'For distance estimates')
        self.assertContains(response, 'OSRM demo service receives')
        self.assertContains(response, 'origin and destination coordinates')
        self.assertContains(response, 'no availability guarantee')

    def test_nearby_search_location_and_results_have_clear_order_and_controls(self):
        self.client.force_login(self.user)
        html = self.client.get(reverse('places:attraction_carousel'), {'mode': 'nearby'}).content.decode()
        self.assertLess(html.index('id="ea6-search-title"'), html.index('id="ea6-nearby-title"'))
        self.assertLess(html.index('id="ea6-nearby-title"'), html.index('id="ea6-results-title"'))
        for item in ('id="ea6-query"', 'id="ea6-service"', 'id="ea6-voice-status"',
                     'id="ea6-use-gps"', 'id="ea6h-distance"', 'id="ea6g-toggle"',
                     'id="ea6g-map-shell"', 'aria-current="page">Nearby</a>'):
            self.assertIn(item, html)
        self.assertIn('No starting point selected. Results are alphabetical', html)
        self.assertIn('if (listbox && !listbox.hidden) event.preventDefault()', html)

    def test_driving_route_guides_keep_existing_map_controls(self):
        self.client.force_login(self.user)
        browse = self.client.get(reverse('places:attraction_carousel'), {'browse': 'all'}).content.decode()
        nearby = self.client.get(reverse('places:attraction_carousel'), {'mode': 'nearby'}).content.decode()
        for html in (browse, nearby):
            self.assertIn('js/map-guide.js', html)
            self.assertIn('driving route', html)
            self.assertIn('Fit results', html)
            self.assertIn('OSRM demo', html)
        for fragment in ('id="ea-map-locate"', 'id="ea-map-fit"', 'id="ea-map-retry-route"', 'selectAttraction(index)'):
            self.assertIn(fragment, browse)
        for fragment in ('id="ea6-use-gps"', 'id="ea6g-close"', 'id="ea6g-retry-route"', 'selectCard(card)'):
            self.assertIn(fragment, nearby)
        self.assertIn('container.hidden = true', nearby)
        self.assertIn('Back to results', nearby)
