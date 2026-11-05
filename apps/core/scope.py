"""Review rules for the shared Kabankalan directory.

Schools are outside the agreed catalogue scope. Other real places can serve a
hobby, a practical errand, or both. Missing hobby tags are a review item, not
proof that a place is irrelevant or outside the city directory. Publication
status alone is not independent verification.
"""
import re

#: The one city this system covers.
SCOPE_CITY_PK = 2

#: The system's purpose, in one sentence. Used by the audit commands so the
#: operator always sees what the catalogue is *for* while judging records.
SYSTEM_PURPOSE = (
    "ExploreKabankalan is a shared directory of real Kabankalan places for "
    "hobbies and local needs, plus staff-published City Information notes."
)

#: The two pillars of public content.
PILLARS = (
    "Places: a real destination a visitor chooses for a hobby or a local errand.",
    "City Information: an editorial fact about the city, published by staff.",
)

#: The agreed place-directory scope excludes educational institutions. This
#: title matcher is intentionally narrow and is not a complete school audit.
INSTITUTION_PATTERNS = (
    (re.compile(r"\belementary\s+school\b", re.IGNORECASE), "elementary school"),
    (re.compile(r"\bhigh\s*school\b", re.IGNORECASE), "high school"),
    (re.compile(r"\bcollege\b", re.IGNORECASE), "college"),
    (re.compile(r"\bacademy\b", re.IGNORECASE), "academy"),
    (re.compile(r"\buniversity\b", re.IGNORECASE), "university"),
    (re.compile(r"\bseminary\b", re.IGNORECASE), "seminary"),
    (re.compile(r"\bvocational\s+school\b", re.IGNORECASE), "vocational school"),
    (re.compile(r"\btechnical\s+institute\b", re.IGNORECASE), "technical institute"),
)

#: Civic and institutional offices are reported for review but are **not**
#: removed automatically: some of them (a city hall, a public library) are
#: genuine landmarks a visitor photographs.
CIVIC_PATTERNS = (
    (re.compile(r"\bcity\s+hall\b", re.IGNORECASE), "city hall"),
    (re.compile(r"\bmunicipal\s+hall\b", re.IGNORECASE), "municipal hall"),
    (re.compile(r"\bpublic\s+library\b", re.IGNORECASE), "public library"),
    (re.compile(r"\bhealth\s+centre?\b", re.IGNORECASE), "health centre"),
    (re.compile(r"\bpolice\s+station\b", re.IGNORECASE), "police station"),
)


def institution_kind(title):
    """Return the kind of educational institution in ``title``, or ``""``."""
    for pattern, label in INSTITUTION_PATTERNS:
        if pattern.search(title or ""):
            return label
    return ""


def civic_kind(title):
    """Return the kind of civic office in ``title``, or ``""``."""
    for pattern, label in CIVIC_PATTERNS:
        if pattern.search(title or ""):
            return label
    return ""


def hobby_slugs(place):
    """Return the hobby slugs linked to ``place``.

    Accepts a Django model instance (the usual case) or any object that
    exposes a ``hobbies`` collection, so the rule can be unit tested without
    touching the database.
    """
    hobbies = getattr(place, "hobbies", None)
    if hobbies is None:
        return []
    if hasattr(hobbies, "all"):
        hobbies = hobbies.all()
    slugs = []
    for hobby in hobbies:
        slug = getattr(hobby, "slug", None)
        if slug:
            slugs.append(slug)
    return slugs


def place_violations(place):
    """Return the scope problems of a place, as a list of readable reasons.

    The reasons are ordered from "this record is the wrong shape for the
    system" to "this record is merely incomplete".
    """
    reasons = []

    kind = institution_kind(getattr(place, "title", ""))
    if kind:
        reasons.append(
            "educational institution (%s): excluded from the place directory "
            "under the agreed scope" % kind
        )

    if getattr(place, "category_id", None) is None:
        reasons.append("no category: the place is not filed in the taxonomy")

    if not hobby_slugs(place):
        reasons.append(
            "no hobby tags: review whether a relevant activity applies; "
            "the place remains visible in general browsing"
        )

    if not (getattr(place, "description", "") or "").strip():
        reasons.append("no description")

    return reasons


def is_place_in_scope(place):
    """Scope and completeness are distinct; missing metadata needs review."""
    return not bool(institution_kind(getattr(place, "title", "")))
