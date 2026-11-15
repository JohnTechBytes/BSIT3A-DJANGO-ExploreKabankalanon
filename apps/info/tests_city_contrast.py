"""City Information controls remain labelled and searches keep their scope."""
from django.test import TestCase
from django.urls import reverse

from apps.cities.models import City
from apps.info.models import CityInformation


def contrast(foreground, background):
    def luminance(hex_color):
        values = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in values]
        return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))
    left, right = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (left + .05) / (right + .05)


class CityInformationContrastTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = City.objects.create(pk=2, name='Kabankalan', slug='kabankalan', province='Negros Occidental')
        CityInformation.objects.create(city=city, title='Sample guide', info_type='attraction', is_published=True)

    def test_labels_and_search_scope_are_preserved(self):
        url = reverse('info:city_information')
        response = self.client.get(url, {'section': 'official', 'kind': 'post', 'q': 'resolution'})
        self.assertContains(response, '<label for="city-info-search">Search official sitemap links</label>')
        self.assertContains(response, '<label for="official-kind">Record type</label>')
        self.assertContains(response, 'name="section" value="official"')
        self.assertContains(response, 'value="post" selected')
        self.assertContains(response, 'name="q" value="resolution"')
        self.assertGreater(response.context['official_page'].paginator.count, 0)
        response = self.client.get(url, {'section': 'attraction', 'q': 'Sample'})
        self.assertContains(response, '<label for="city-info-search">Search published city guides</label>')
        self.assertContains(response, 'Sample guide')
        self.assertNotContains(response, 'id="official-kind"')

    def test_accessible_colours_and_responsive_control_rules(self):
        # Ratios for the scoped link, nav and metadata colours against their surfaces.
        for text, background in (('#a5edcb', '#121b29'), ('#a5edcb', '#0b1019'),
                                 ('#f0ece2', '#121b29'), ('#10251f', '#9be8c6'),
                                 ('#d2dedb', '#121b29'), ('#e7edea', '#0b1019')):
            with self.subTest(text=text, background=background):
                self.assertGreaterEqual(contrast(text, background), 4.5)
        response = self.client.get(reverse('info:city_information'), {'section': 'official'})
        self.assertContains(response, 'class="ek-city-search-field"')
        self.assertContains(response, 'class="ek-city-type-field"')
        self.assertContains(response, 'flex:0 0 auto !important; box-sizing:border-box; width:100%')
        self.assertContains(response, 'input[type="hidden"] { display:none !important; }')
        self.assertContains(response, 'flex:1 1 100%;')
        self.assertContains(response, ':focus-visible { outline:3px solid #9be8c6;')
