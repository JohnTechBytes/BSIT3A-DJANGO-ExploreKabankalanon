"""Django system checks that keep the catalogue inside the system scope.

The rules live in :mod:`apps.core.scope`; this module only wires them into
Django's check framework so that ``python manage.py check --database default``
fails loudly when the published catalogue drifts away from the two pillars of
the system.

The check is deliberately **database scoped** (``Tags.database``): it reads the
live catalogue, so it must not run while the schema is still being created
(``migrate``) or on every ``runserver`` reload. Django's check framework only
executes database-tagged checks when a database is selected explicitly, so
every other command stays untouched.
"""
from django.core.checks import Error, Tags, Warning, register
from django.db import DatabaseError, connections

from apps.core.scope import (
    SCOPE_CITY_PK,
    civic_kind,
    institution_kind,
    place_violations,
)

#: How many individual records are listed before the rest is summarised.
MAX_LISTED = 20


def _published_places(alias):
    """Return the published places of ``alias`` with their hobbies loaded.

    "Published" is the same definition the public pages use: the place is in
    Kabankalan, active and verified.
    """
    from apps.places.models import Place

    return list(
        Place.objects.using(alias)
        .filter(city_id=SCOPE_CITY_PK, is_active=True, is_verified=True)
        .prefetch_related("hobbies")
        .only("id", "title", "description", "category_id")
    )


def _check_database(alias):
    """Return the scope issues found in the published catalogue of ``alias``."""
    try:
        places = _published_places(alias)
    except DatabaseError:
        # The table is not there yet (fresh database, mid-migrate). Nothing to
        # report, and never break the command that triggered the check.
        return []

    issues = []
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

    for place, reasons in off_pillar[:MAX_LISTED]:
        issues.append(
            Error(
                "'%s' is outside the scope of ExploreKabankalan: %s. It "
                "belongs in City Information as a single curated fact, not "
                "as a place row."
                % (place.title, "; ".join(reasons)),
                hint=(
                    "Run 'python manage.py purge_off_scope_places' to review "
                    "the off-pillar records and unpublish them."
                ),
                id="core.E001",
            )
        )
    if len(off_pillar) > MAX_LISTED:
        issues.append(
            Error(
                "%d more published places are outside the scope of "
                "ExploreKabankalan." % (len(off_pillar) - MAX_LISTED),
                hint=(
                    "Run 'python manage.py purge_off_scope_places' to review "
                    "the off-pillar records and unpublish them."
                ),
                id="core.E001",
            )
        )

    if civic:
        issues.append(
            Warning(
                "%d published place(s) look like civic offices (%s). They are "
                "reported for review only - remove them if they are not "
                "landmarks a visitor would choose."
                % (
                    len(civic),
                    ", ".join(sorted({civic_kind(place.title) for place, _ in civic})),
                ),
                id="core.W001",
            )
        )

    for reason, count in sorted(incomplete.items()):
        issues.append(
            Warning(
                "%d published place(s) have %s." % (count, reason),
                id="core.W002",
            )
        )

    return issues


@register(Tags.database)
def check_content_scope(app_configs=None, databases=None, **kwargs):
    """Report published places that do not belong to the Places pillar.

    Returns an empty list when no database is selected or when the database
    is not reachable, so the check can never break ``migrate`` or ``test``.
    """
    if not databases:
        return []

    issues = []
    for alias in databases:
        if alias not in connections:
            continue
        issues.extend(_check_database(alias))
    return issues
