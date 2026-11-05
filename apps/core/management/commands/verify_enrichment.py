"""Report how complete the published Kabankalan catalogue is.

``python manage.py verify_enrichment`` prints, for the published places of
Kabankalan:

* how many carry a description and at least one hobby,
* how many carry a real, sourced photograph and how many an illustrative
  sample (the sample is always labelled as such on the page),
* how many published places are still incomplete,
* the state of the City Information entries.

The command only reads. It never invents content and never changes a record.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count

from apps.core.scope import SCOPE_CITY_PK, institution_kind
from apps.places.sample_images import sample_image_for


class Command(BaseCommand):
    help = "Reports how complete the published Kabankalan catalogue is."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="How many incomplete records to list (default: 20).",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit with status 1 when a published place is incomplete.",
        )

    def handle(self, *args, **options):
        from apps.info.models import CityInformation
        from apps.places.models import Place

        limit = max(0, options["limit"])

        published = Place.objects.filter(
            city_id=SCOPE_CITY_PK, is_active=True, is_verified=True,
        )
        places = list(
            published.select_related("category").prefetch_related("hobbies")
        )

        total = len(places)
        with_description = sum(
            1 for place in places if (place.description or "").strip()
        )
        with_hobby = sum(1 for place in places if place.hobbies.exists())
        with_photo = sum(
            1 for place in places if place.cover_image or place.cover_image_url
        )
        with_sample = sum(
            1 for place in places
            if not (place.cover_image or place.cover_image_url)
            and sample_image_for(place)
        )

        self.stdout.write(self.style.MIGRATE_HEADING("Content enrichment report"))
        self.stdout.write(f"  City: Kabankalan (id {SCOPE_CITY_PK})")
        self.stdout.write(f"  Published places (active and verified): {total}")
        self.stdout.write(f"  With a description: {with_description}")
        self.stdout.write(f"  With at least one hobby: {with_hobby}")
        self.stdout.write(f"  With a real, sourced photograph: {with_photo}")
        self.stdout.write(f"  With an illustrative sample image: {with_sample}")
        self.stdout.write("  Without any image: %d" % (total - with_photo - with_sample))

        duplicates = (
            published.values("title")
            .annotate(total=Count("id"))
            .filter(total__gt=1)
        )
        duplicate_titles = [row["title"] for row in duplicates]
        self.stdout.write(
            "  Duplicate titles among the published places: %d"
            % len(duplicate_titles)
        )
        for title in duplicate_titles[:limit]:
            self.stdout.write(self.style.WARNING("    - %s" % title))

        incomplete = []
        off_pillar = []
        for place in places:
            problems = []
            if not (place.description or "").strip():
                problems.append("no description")
            if not place.hobbies.exists():
                problems.append("no hobby")
            if place.category_id is None:
                problems.append("no category")
            if institution_kind(place.title):
                off_pillar.append(place.title)
            if problems:
                incomplete.append((place.title, problems))

        self.stdout.write(f"  Published but incomplete: {len(incomplete)}")
        for title, problems in incomplete[:limit]:
            self.stdout.write(
                self.style.WARNING("    - %s: %s" % (title, ", ".join(problems)))
            )
        if len(incomplete) > limit:
            self.stdout.write(
                self.style.WARNING("    ... and %d more" % (len(incomplete) - limit))
            )

        if off_pillar:
            self.stdout.write(
                self.style.ERROR(
                    "  Published places outside the scope of the system: %d"
                    % len(off_pillar)
                )
            )
            for title in off_pillar[:limit]:
                self.stdout.write(self.style.ERROR("    - %s" % title))

        entries = CityInformation.objects.filter(city_id=SCOPE_CITY_PK)
        self.stdout.write("")
        self.stdout.write(
            "  City Information: %d entries, %d published, %d with a photo credit"
            % (
                entries.count(),
                entries.filter(is_published=True).count(),
                entries.exclude(photo_credit="").count(),
            )
        )

        if options["strict"] and (incomplete or off_pillar):
            raise SystemExit(1)
