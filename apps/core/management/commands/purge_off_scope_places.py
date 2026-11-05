"""Unpublish (or delete) the place rows that fall outside the system scope.

The catalogue of ExploreKabankalan holds places a visitor can choose for a
hobby or a local errand. Educational institutions are the canonical record
that does not belong: they carry no hobby, the recommendation score can never
rank them, and a bulk import of them only dilutes the places that work.

The command is a **dry run by default** - it prints what it would do and
changes nothing. Two explicit switches are needed to act:

``--apply``
    Unpublish the off-pillar rows (``is_active=False`` and
    ``is_verified=False``). They leave the public catalogue and stay in the
    database, so the change can be undone from the staff dashboard.

``--delete``
    Delete the off-pillar rows outright. Reviews, itineraries and saved
    places that point at them are removed with them, so this is not
    reversible.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.scope import (
    SCOPE_CITY_PK,
    SYSTEM_PURPOSE,
    institution_kind,
)


class Command(BaseCommand):
    help = "Finds and (optionally) unpublishes place rows outside the system scope."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually unpublish the off-pillar records (dry run without it).",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the off-pillar records instead of unpublishing them.",
        )
        parser.add_argument(
            "--include-pending",
            action="store_true",
            help=(
                "Also cover records that are verified but not active yet "
                "(the review queue)."
            ),
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="How many records to list (0 lists all of them).",
        )

    def handle(self, *args, **options):
        from apps.places.models import Place

        queryset = Place.objects.filter(city_id=SCOPE_CITY_PK)
        if not options["include_pending"]:
            queryset = queryset.filter(is_active=True)

        offenders = [
            place for place in queryset.order_by("title")
            if institution_kind(place.title)
        ]

        self.stdout.write(self.style.MIGRATE_HEADING("Off-pillar places"))
        self.stdout.write(f"  Purpose: {SYSTEM_PURPOSE}")
        self.stdout.write(f"  Records outside the scope: {len(offenders)}")

        limit = options["limit"]
        shown = offenders[:limit] if limit else offenders
        for place in shown:
            self.stdout.write(
                self.style.WARNING(
                    "    - %s (%s)" % (place.title, institution_kind(place.title))
                )
            )
        if limit and len(offenders) > limit:
            self.stdout.write("    ... and %d more" % (len(offenders) - limit))

        if not offenders:
            self.stdout.write(self.style.SUCCESS("  Nothing to do."))
            return

        if not options["apply"]:
            self.stdout.write("")
            self.stdout.write(
                "Dry run: nothing was changed. Re-run with --apply to "
                "unpublish these records"
                + (" (--delete to remove them)." if options["delete"] else ".")
            )
            return

        with transaction.atomic():
            if options["delete"]:
                ids = [place.pk for place in offenders]
                deleted, _ = Place.objects.filter(pk__in=ids).delete()
                self.stdout.write(
                    self.style.SUCCESS("  Deleted %d row(s)." % deleted)
                )
            else:
                updated = Place.objects.filter(
                    pk__in=[place.pk for place in offenders]
                ).update(is_active=False, is_verified=False)
                self.stdout.write(
                    self.style.SUCCESS(
                        "  Unpublished %d record(s). They stay in the database "
                        "and can be restored from the staff dashboard." % updated
                    )
                )
