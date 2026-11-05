"""Show how a question is answered by the published Kabankalan catalogue.

``python manage.py check_search "where to buy a phone case"``

The command prints, for every query:

* the normalised words,
* the intent group and the product it recognised,
* the note the public page shows,
* the published places that answer the question,
* a warning when the answer comes from a category instead of from a listing
  that names the product.

It is a read-only audit of the search behaviour; the same rules run in the
carousel and in the nearby page.
"""
from django.core.management.base import BaseCommand

from apps.places.search_intents import with_article

from apps.places.search_intents import (
    CATEGORY_GROUPS,
    describe_search,
    exact_title_filter,
    group_filter,
    normalize_words,
    product_group,
    resolve_buying_group,
    shopping_product,
    wants_to_buy,
    maybe_buying,
)

DEFAULT_QUERIES = (
    "where to buy a phone case",
    "where can I buy groceries",
    "where to get a haircut",
    "Mag-aso Falls",
)


class Command(BaseCommand):
    help = "Shows how a search question is answered by the published catalogue."

    def add_arguments(self, parser):
        parser.add_argument(
            "queries",
            nargs="*",
            help="One or more questions to check (defaults to a few examples).",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="How many matching places to list per query (default: 10).",
        )

    def handle(self, *args, **options):
        from apps.places.models import Place

        queries = options["queries"] or list(DEFAULT_QUERIES)
        limit = max(0, options["limit"])

        published = Place.objects.filter(
            city_id=2, is_active=True, is_verified=True,
        ).select_related("category").order_by("title", "pk")

        for query in queries:
            self.stdout.write(self.style.MIGRATE_HEADING("Search: %s" % query))

            words = normalize_words(query)
            self.stdout.write("  Words: %s" % (words or "(empty)"))

            product = shopping_product(query)
            buying = wants_to_buy(query) or maybe_buying(query)
            group = resolve_buying_group(query) if buying else ""
            self.stdout.write("  Intent group: %s" % (group or "(none)"))
            self.stdout.write("  Product: %s" % (product or "(none)"))

            note = describe_search(group, product) if buying else ""
            self.stdout.write("  Page note: %s" % (note or "(no note)"))

            exact = exact_title_filter(query, published)
            if exact is not None:
                matches = published.filter(exact)
                self.stdout.write(
                    self.style.SUCCESS(
                        "  Answered by the named place: %d match(es)" % matches.count()
                    )
                )
            elif buying and group:
                predicate = group_filter(group)
                matches = (
                    published.filter(predicate).distinct()
                    if predicate else published.none()
                )
                self.stdout.write(
                    "  Matching published places (%d):" % matches.count()
                )
                for place in list(matches)[:limit]:
                    self.stdout.write(
                        "    - %s (%s)"
                        % (place.title, place.category.name if place.category else "no category")
                    )
                if matches.count() > limit:
                    self.stdout.write("    ... and %d more" % (matches.count() - limit))
                self.stdout.write(
                    self.style.WARNING(
                        "  Warning: no listing names %s directly - the answer "
                        "comes from the category (%s)."
                        % (with_article(product or "the product"), group)
                    )
                )
            else:
                from apps.places.search_intents import build_attraction_filter

                predicate = build_attraction_filter(query)
                matches = (
                    published.filter(predicate).distinct()
                    if predicate else published.none()
                )
                self.stdout.write(
                    "  Matching published places (%d):" % matches.count()
                )
                for place in list(matches)[:limit]:
                    self.stdout.write("    - %s" % place.title)

            self.stdout.write("")

        self.stdout.write(
            "Buying categories: %s"
            % ", ".join(
                "%s (%s)" % (name, ", ".join(spec["slugs"]))
                for name, spec in sorted(CATEGORY_GROUPS.items())
            )
        )
