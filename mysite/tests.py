from copy import copy

from django.template.context import Context, RequestContext
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from apps.cities.models import City
from apps.core.models import Category
from apps.places.models import Place
from .views import home


class HomepageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city = City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        cls.other_city = City.objects.create(name="Other City", slug="other-city")
        cls.category = Category.objects.create(name="Nature", slug="nature")
        cls.place = Place.objects.create(
            city=cls.city, title="Existing local place", address="Kabankalan",
            category=cls.category, is_verified=True, is_active=True,
            description="Existing description", avg_rating=4.5, review_count=3,
        )
        Place.objects.create(city=cls.city, title="Unverified place", address="Local")
        Place.objects.create(city=cls.city, title="Inactive place", address="Local",
                             is_verified=True, is_active=False)
        Place.objects.create(city=cls.other_city, title="Outside city", address="Other",
                             is_verified=True)

    def render_home(self, query=None):
        request = RequestFactory().get("/", query or {})
        request.user = AnonymousUser()
        return home(request)

    def test_existing_published_content_only(self):
        response = self.render_home()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Existing local place")
        self.assertContains(response, "Existing description")
        self.assertContains(response, "css/explore.css")
        self.assertContains(response, "js/motion.js")
        self.assertContains(response, "4.5")
        self.assertNotContains(response, "Unverified place")
        self.assertNotContains(response, "Inactive place")
        self.assertNotContains(response, "Outside city")

    def test_landing_loads_opt_in_design_token_foundation(self):
        from django.contrib.staticfiles import finders
        from pathlib import Path

        response = self.render_home()
        self.assertContains(response, 'css/explore.css')
        css = Path(finders.find('css/explore.css')).read_text()
        self.assertIn('--ek-primary: #1e7a5c', css)
        self.assertIn('--ek-bg: #f8f6f1', css)
        self.assertIn('.ek-theme {', css)
        self.assertContains(response, 'class="landing-page ek-theme"')
        for asset in ('plus-jakarta-sans-variable.ttf', 'inter-variable.ttf',
                      'PLUS-JAKARTA-SANS-OFL.txt', 'INTER-OFL.txt'):
            self.assertIsNotNone(finders.find('fonts/' + asset))

    def test_city_hall_background_is_local_and_featured_cathedral_remains(self):
        from django.contrib.staticfiles import finders
        from pathlib import Path

        background = finders.find('img/places/kabankalan-city-hall-background.jpg')
        stylesheet = finders.find('css/explore.css')
        self.assertIsNotNone(background)
        self.assertIn('kabankalan-city-hall-background.jpg', Path(stylesheet).read_text())
        response = self.render_home()
        self.assertContains(response, 'img/places/new-kabankalan-cathedral.jpg')
        self.assertContains(response, 'Lightningscale / Wikimedia Commons')

    def test_landing_retains_shared_guide_and_respects_reduced_motion(self):
        from django.contrib.staticfiles import finders
        from pathlib import Path

        response = self.render_home()
        self.assertContains(response, 'Discover<br><em>Kabankalan.</em>')
        self.assertContains(response, 'content="#111b2a"')
        stylesheet = Path(finders.find('css/explore.css')).read_text()
        self.assertIn('--ek-bg: #f8f6f1', stylesheet)
        self.assertIn('--ek-primary: #1e7a5c', stylesheet)
        self.assertIn('backdrop-filter: blur(8px)', stylesheet)
        self.assertIn('prefers-reduced-motion: reduce', stylesheet)
        self.assertIn('landing-reveal.is-reveal-pending', stylesheet)
        self.assertContains(response, 'aria-label="Ways to explore Kabankalan"')
        self.assertContains(response, 'aria-label="Your places links"')
        self.assertContains(response, '<strong>1</strong> published place')

    def test_homepage_pilot_is_scoped_and_preserves_core_interactions(self):
        response = self.render_home()
        self.assertContains(response, 'css/homepage-pilot.css?v=5')
        self.assertContains(response, 'class="hero-actions"')
        html = response.content.decode()
        self.assertLess(html.index('id="discover"'), html.index('id="hobbies"'))
        self.assertLess(html.index('id="hobbies"'), html.index('id="how-it-works"'))
        self.assertContains(response, f'href="{reverse("places:attraction_carousel")}?mode=nearby"')
        self.assertContains(response, 'id="home-search"')
        self.assertContains(response, 'type="submit"')
        self.assertContains(response, 'id="home-places"')
        self.assertContains(response, 'data-carousel-toggle')
        self.assertContains(response, 'id="landing-map-places"')
        self.assertContains(response, 'Photo not yet available')
        self.assertContains(response, 'Wikimedia Commons')
        from pathlib import Path
        from django.contrib.staticfiles import finders
        pilot_css = Path(finders.find('css/homepage-pilot.css')).read_text(encoding='utf-8')
        self.assertIn('prefers-reduced-motion: no-preference', pilot_css)
        self.assertIn('perspective(1200px)', pilot_css)

    def test_landing_search_and_main_links_use_existing_routes(self):
        response = self.render_home()
        self.assertContains(response, f'action="{reverse("places:smart_search")}"')
        self.assertContains(response, 'name="q"')
        self.assertContains(response, f'href="{reverse("info:city_information")}"')
        self.assertContains(response, f'href="{reverse("places:attraction_carousel")}?mode=nearby"')
        self.assertContains(response, f'href="{reverse("places:attraction_carousel")}?browse=all"')
        self.assertNotContains(response, f'href="{reverse("itineraries:list")}"')
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, f'href="{reverse("register")}"')

    def test_landing_quick_explore_links_use_existing_routes(self):
        response = self.render_home()
        self.assertContains(response, 'aria-label="Ways to explore Kabankalan"')
        self.assertContains(response, f'href="{reverse("places:attraction_carousel")}?browse=all"><span>Explore places</span>')
        self.assertContains(response, f'href="{reverse("places:attraction_carousel")}?mode=nearby"><span>Find nearby</span>')
        self.assertContains(response, f'href="{reverse("info:city_information")}"><span>City information</span>')

    def test_landing_carousel_contains_all_published_places(self):
        for number in range(12):
            Place.objects.create(city=self.city, title=f"Published {number:02}", address="Local",
                                 is_verified=True, is_active=True)
        response = self.render_home()
        for number in range(12):
            self.assertContains(response, f"Published {number:02}")
        self.assertContains(response, 'data-carousel-toggle')
        self.assertContains(response, 'landing-carousel.js')
        self.assertNotContains(response, "Unverified place")

    def test_landing_map_uses_only_published_real_coordinates(self):
        self.place.latitude = 9.9889
        self.place.longitude = 122.8142
        self.place.save()
        Place.objects.create(city=self.city, title="Not public", address="Local",
                             latitude=9.98, longitude=122.8, is_active=False, is_verified=True)
        response = self.render_home()
        self.assertContains(response, 'id="landing-map-places"')
        self.assertContains(response, 'Existing local place')
        self.assertNotContains(response, 'Not public')
        self.assertContains(response, 'js/landing-map.js')

    def test_landing_osm_tiles_send_only_origin_as_referrer(self):
        from django.contrib.staticfiles import finders
        from pathlib import Path

        script = Path(finders.find('js/landing-map.js')).read_text(encoding='utf-8')
        self.assertIn("https://tile.openstreetmap.org/{z}/{x}/{y}.png", script)
        self.assertIn("referrerPolicy: 'origin'", script)
        self.assertContains(self.render_home(), 'js/landing-map.js?v=20261109-3')

    def test_landing_map_is_bounded_and_safely_serialized(self):
        self.place.title = '</script><script>alert(1)</script>'
        self.place.latitude = 9.9889
        self.place.longitude = 122.8142
        self.place.save()
        Place.objects.bulk_create([
            Place(city=self.city, title=f'Public {number:02}', address='Local',
                  latitude=9.98, longitude=122.8, is_active=True, is_verified=True)
            for number in range(30)
        ])
        import json

        response = self.render_home()
        payload = response.content.decode().split('<script id="landing-map-places" type="application/json">', 1)[1].split('</script>', 1)[0]
        self.assertEqual(len(json.loads(payload)), 24)
        self.assertContains(response, r'\u003C/script\u003E')
        self.assertNotContains(response, '</script><script>alert(1)</script>')

    def test_landing_place_links_still_point_to_the_record(self):
        response = self.render_home()
        self.assertContains(response, f'href="{reverse("places:place_detail", args=[self.place.pk])}"')
        self.assertContains(response, 'Illustrative category sample')

    def test_category_filter(self):
        self.assertContains(self.render_home({"category": "nature"}), "Existing local place")
        response = self.render_home({"category": "missing"})
        self.assertNotContains(response, "Existing local place")
        self.assertContains(response, "No places in this category yet.")
        self.assertContains(response, "Nature")

    def test_empty_database_does_not_invent_destinations(self):
        Place.objects.all().delete()
        response = self.render_home()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find your kind of local adventure.")
        self.assertContains(response, "img/places/new-kabankalan-cathedral.jpg")
        self.assertContains(response, "New Kabankalan Cathedral")

    def test_cathedral_hero_is_credited_and_not_linked_to_an_unrelated_place(self):
        for query in ({}, {"category": "missing"}):
            with self.subTest(query=query):
                response = self.render_home(query)
                self.assertContains(response, "img/places/new-kabankalan-cathedral.jpg")
                self.assertContains(response, "New Kabankalan Cathedral")
                self.assertContains(response, 'href="/info/?q=New%20Kabankalan%20Cathedral"')
                self.assertContains(response, "Lightningscale / Wikimedia Commons")
                self.assertContains(response, "https://creativecommons.org/licenses/by/4.0/")
                self.assertNotContains(response, 'class="sample-badge hero-sample"')

    def test_content_is_escaped(self):
        self.place.title = '<script>alert("test")</script>'
        self.place.save()
        response = self.render_home()
        self.assertNotContains(response, '<script>alert("test")</script>')
        self.assertContains(response, "&lt;script&gt;")

    def test_published_osm_records_are_prioritized_and_attributed(self):
        osm = Place.objects.create(
            city=self.city, title="Published OSM discovery", slug="osm-node-12345",
            address="Kabankalan", is_verified=True, is_active=True,
        )
        response = self.render_home()
        self.assertContains(response, osm.title)
        self.assertContains(response, "https://www.openstreetmap.org/node/12345")
        self.assertContains(response, "OpenStreetMap contributors")
        self.assertLess(response.content.index(osm.title.encode()),
                        response.content.index(self.place.title.encode()))

    def test_unpublished_osm_record_is_not_exposed(self):
        Place.objects.create(city=self.city, title="Private OSM record",
                             slug="osm-way-123", address="Local", is_verified=False)
        self.assertNotContains(self.render_home(), "Private OSM record")
        self.assertNotContains(self.render_home(), "openstreetmap.org/way/123")

    def test_invalid_osm_slug_never_becomes_source_link(self):
        self.place.slug = 'osm-node-123/invalid'
        self.place.save()
        self.assertNotContains(self.render_home(), 'openstreetmap.org/node/123')

    def test_photographed_osm_record_is_featured_first(self):
        Place.objects.create(city=self.city, title="OSM without photo", slug="osm-node-1",
                             address="Local", is_verified=True, avg_rating=5)
        photo = Place.objects.create(
            city=self.city, title="OSM with photo", slug="osm-way-2", address="Local",
            is_verified=True, cover_image_url="https://example.com/place.jpg",
        )
        response = self.render_home()
        self.assertContains(response, photo.cover_image_url)
        self.assertLess(response.content.index(b'OSM with photo'),
                        response.content.index(b'OSM without photo'))

    def test_missing_nature_photo_uses_labeled_sample(self):
        response = self.render_home()
        self.assertContains(response, 'img/samples/nature.jpg')
        self.assertContains(response, 'Illustrative category sample')
        self.assertContains(response, 'not an actual photo of Existing local place')

    def test_real_photo_always_takes_priority_over_sample(self):
        self.place.cover_image_url = 'https://example.com/real-photo.jpg'
        self.place.save()
        response = self.render_home()
        self.assertContains(response, self.place.cover_image_url)
        self.assertNotContains(response, ' src="/static/img/samples/nature.jpg"')
        self.assertContains(response, 'data-sample-src="/static/img/samples/nature.jpg"')
        self.assertNotContains(response, 'Illustrative category sample')

    def test_samples_match_category_or_use_a_generic_illustration(self):
        from .views import sample_image_for
        self.place.category = None
        for title, expected in [
            ('Local Waterfalls', 'nature'), ('Local Inasal Grill', 'food'),
            ('City Plaza', 'city'), ('Billiards Hall', 'billiards'), ('Book Shop', 'generic'),
        ]:
            self.place.title = title
            self.assertEqual(sample_image_for(self.place),
                             f'img/samples/{expected}.jpg' if expected else '')


class AdminContextCopyTests(TestCase):
    """Regression guard for the "/admin/places/place/" AttributeError.

    Django < 5.1 copies a context with ``copy(super())``, which returns the
    ``super`` object on Python 3.13+ and then fails on ``duplicate.dicts``.
    Every inclusion tag copies the context, so the Destinations changelist was
    the first page to break.
    """

    @classmethod
    def setUpTestData(cls):
        City.objects.create(pk=2, name="Kabankalan", slug="kabankalan")
        category = Category.objects.create(name="Nature", slug="nature")
        Place.objects.create(
            city=City.objects.get(pk=2), title="Amyan Hill", address="Kabankalan",
            category=category, is_verified=True, is_active=True,
        )
        from django.contrib.auth import get_user_model

        cls.staff = get_user_model().objects.create_superuser(
            username="admin_probe", email="admin@example.test", password="probe-pass-123",
        )

    def test_copying_a_context_keeps_its_dictionaries(self):
        context = Context({"a": 1})
        clone = copy(context)
        self.assertIsInstance(clone, Context)
        self.assertEqual(clone.dicts, context.dicts)
        self.assertIsNot(clone.dicts, context.dicts)
        self.assertEqual(clone["a"], 1)

    def test_copying_a_request_context_stays_a_request_context(self):
        request = RequestFactory().get("/admin/places/place/")
        context = RequestContext(request, {"a": 1})
        clone = copy(context)
        self.assertIsInstance(clone, RequestContext)
        self.assertEqual(clone["a"], 1)

    def test_the_installed_django_no_longer_has_the_bug(self):
        from . import compat

        self.assertFalse(
            compat._context_copy_is_broken(),
            "copying a template context is broken again: upgrade Django "
            "(see mysite/compat.py).",
        )

    def test_admin_pages_render_for_a_staff_account(self):
        self.assertTrue(self.client.login(username="admin_probe", password="probe-pass-123"))
        for url in ("/admin/", "/admin/places/place/", "/admin/places/place/1/change/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_destinations_changelist_lists_published_places(self):
        self.client.login(username="admin_probe", password="probe-pass-123")
        response = self.client.get("/admin/places/place/")
        self.assertContains(response, "Destination management")
        self.assertContains(response, "Amyan Hill")


class ErrorPageTests(SimpleTestCase):
    """The custom 404/500 handlers must render the dark error screens."""

    def test_error_page_views_use_the_shared_design(self):
        from .views import error_404, error_500

        not_found = error_404(RequestFactory().get("/missing/"))
        self.assertEqual(not_found.status_code, 404)
        self.assertIn(b"ERROR 404", not_found.content)
        self.assertIn(b"css/error.css", not_found.content)

        server_error = error_500(RequestFactory().get("/boom/"))
        self.assertEqual(server_error.status_code, 500)
        self.assertIn(b"ERROR 500", server_error.content)
        self.assertIn(b"ExploreKabankalan", server_error.content)

    def test_custom_handlers_are_wired(self):
        from mysite import urls

        self.assertEqual(urls.handler404, "mysite.views.error_404")
        self.assertEqual(urls.handler500, "mysite.views.error_500")
