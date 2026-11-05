"""Audit the published catalogue against the scope of the system.

``python manage.py check_content_scope`` prints what the system is *for* and
then reports every published record that drifts away from the two pillars:

* educational institutions matching the narrow title rules, excluded by the
  agreed directory scope;
* civic offices - reported for review only, they can be genuine landmarks;
* incomplete records - missing category, hobby tags to review or description.
  A missing hobby tag does not make a place irrelevant.

The command never writes to the database. Use
``python manage.py purge_off_scope_places`` to act on the off-pillar rows.
"""
from django.core.management.base import BaseCommand

from apps.core.scope import (
    PILLARS,
    SCOPE_CITY_PK,
    SYSTEM_PURPOSE,
    civic_kind,
    institution_kind,
    place_violations,
)


class Command(BaseCommand):
    help = "Audits the published catalogue against the scope of ExploreKabankalan."

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit with status 1 when off-pillar records are published.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=20,
            help="How many individual records to list (default: 20).",
        )

    def handle(self, *args, **options):
        from apps.info.models import CityInformation
        from apps.places.models import Place

        limit = max(0, options["limit"])

        self.stdout.write(self.style.MIGRATE_HEADING("ExploreKabankalan content scope"))
        self.stdout.write(f"  Purpose: {SYSTEM_PURPOSE}")
        for pillar in PILLARS:
            self.stdout.write(f"  - {pillar}")

        places = list(
            Place.objects.filter(
                city_id=SCOPE_CITY_PK, is_active=True, is_verified=True,
            ).prefetch_related("hobbies")
        )

        off_pillar = []
        civic = []
        incomplete = {}
        for place in places:
            reasons = place_violations(place)
            if not reasons:
                continue
            if institution_kind(place.title):
                off_pillar.append((place, reasons))
                continue
            if civic_kind(place.title):
                civic.append((place, reasons))
                continue
            for reason in reasons:
                incomplete[reason] = incomplete.get(reason, 0) + 1

        self.stdout.write("")
        self.stdout.write(f"Published places: {len(places)}")

        self.stdout.write(
            self.style.SUCCESS("  In scope: %d" % (len(places) - len(off_pillar) - len(civic)))
        )

        if off_pillar:
            self.stdout.write(
                self.style.ERROR(
                    "  Off-pillar (educational institutions): %d" % len(off_pillar)
                )
            )
            for place, reasons in off_pillar[:limit]:
                self.stdout.write(
                    self.style.ERROR("    - %s: %s" % (place.title, "; ".join(reasons)))
                )
            if len(off_pillar) > limit:
                self.stdout.write(
                    self.style.ERROR("    ... and %d more" % (len(off_pillar) - limit))
                )
        else:
            self.stdout.write(self.style.SUCCESS("  Off-pillar (educational institutions): 0"))

        if civic:
            self.stdout.write(
                self.style.WARNING(
                    "  Civic offices (report only): %d" % len(civic)
                )
            )
            for place, _ in civic[:limit]:
                self.stdout.write(self.style.WARNING("    - %s" % place.title))
            if len(civic) > limit:
                self.stdout.write(
                    self.style.WARNING("    ... and %d more" % (len(civic) - limit))
                )
        else:
            self.stdout.write(self.style.WARNING("  Civic offices (report only): 0"))

        if incomplete:
            self.stdout.write(self.style.WARNING("  Incomplete records:"))
            for reason, count in sorted(incomplete.items()):
                self.stdout.write(self.style.WARNING("    - %d place(s): %s" % (count, reason)))
        else:
            self.stdout.write(self.style.SUCCESS("  Incomplete records: 0"))

        published_entries = CityInformation.objects.filter(
            city_id=SCOPE_CITY_PK, is_published=True,
        ).count()
        total_entries = CityInformation.objects.filter(city_id=SCOPE_CITY_PK).count()
        self.stdout.write("")
        self.stdout.write(
            "City Information: %d published of %d entries"
            % (published_entries, total_entries)
        )

        if off_pillar:
            self.stdout.write("")
            self.stdout.write(
                self.style.ERROR(
                    "%d published place(s) are outside the scope of the system. "
                    "Review them with 'python manage.py purge_off_scope_places'."
                    % len(off_pillar)
                )
            )
            if options["strict"]:
                raise SystemExit(1)
