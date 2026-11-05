"""Regression tests for the existing recommendation rules, not evaluation results."""
from types import SimpleNamespace

from django.test import SimpleTestCase

from .recommendations import rank_kabankalan_places


def place(title, hobbies=(), rating=0, reviews=0, latitude=None):
    # Only the attributes consumed by the ranking rule are needed here.
    return SimpleNamespace(
        title=title,
        hobbies=SimpleNamespace(all=lambda: [SimpleNamespace(slug=slug) for slug in hobbies]),
        avg_rating=rating,
        review_count=reviews,
        latitude=latitude,
    )


class RecommendationRuleTests(SimpleTestCase):
    def test_hobby_fit_and_rating_are_normalized_over_available_weights(self):
        full_unrated = place('Unrated', ('hiking',))
        full_rated = place('Rated', ('hiking',), rating=4, reviews=1)
        unrelated = place('Other', (), rating=5, reviews=1)
        ranked = rank_kabankalan_places([unrelated, full_rated, full_unrated], ['hiking'])
        self.assertEqual([p.title for p in ranked], ['Unrated', 'Rated', 'Other'])
        self.assertEqual([p.match_percent for p in ranked], [100, 95, 25])

    def test_without_a_hobby_ratings_contribute_but_unrated_places_have_zero(self):
        rated = place('Rated', rating=5, reviews=2)
        unrated = place('Unrated')
        ranked = rank_kabankalan_places([unrated, rated], [])
        self.assertEqual([p.title for p in ranked], ['Rated', 'Unrated'])
        self.assertEqual([p.match_percent for p in ranked], [25, 0])

    def test_ties_use_matching_hobby_count_then_title_not_coordinates(self):
        # Both have a zero score for no selected hobbies, so the title decides.
        zulu = place('Zulu', latitude=9.9)
        alpha = place('Alpha', latitude=10.0)
        self.assertEqual([p.title for p in rank_kabankalan_places([zulu, alpha], [])],
                         ['Alpha', 'Zulu'])
        # Eight matches with a 2-star rating and seven matches without a
        # rating both score 70; the greater number of matches breaks the tie.
        selected = [str(i) for i in range(10)]
        more = place('Zulu', selected[:8], rating=2, reviews=1)
        fewer = place('Alpha', selected[:7])
        ranked = rank_kabankalan_places([fewer, more], selected)
        self.assertEqual([p.match_percent for p in ranked], [70, 70])
        self.assertEqual([p.title for p in ranked], ['Zulu', 'Alpha'])
