"""Conservative free-text matching against existing, staff-assigned hobbies.

Only an entire interest phrase (possibly with a simple request prefix or city
suffix) is interpreted as a hobby. Named places and unrecognised free text keep
the normal search path. No hobby tags or places are created by search.
"""
import re

from apps.core.models import Hobby
from .nearby_intent import normalize_words

# Aliases describe the user's interest, not an assertion that a place supports
# that activity. A match still requires an existing Hobby relation on the place.
HOBBY_ALIASES = {
    "billiards": ("billiard", "billiards", "bilyar", "play billiards", "play pool"),
    "basketball": ("basketball", "play basketball", "basketball courts"),
    "cafe": ("cafe", "cafes", "cafe hopping", "coffee hopping"),
    "hiking": ("hiking", "hike", "hikes", "go hiking", "trekking"),
    "photography": ("photography", "photograph", "taking photos", "take photos", "taking pictures"),
    "gaming": ("gaming", "video games", "playing video games"),
    "food": ("food trip", "food trips", "food hopping", "food tasting"),
    "music": ("music", "live music", "listen to music"),
    "culture": ("art and culture", "art culture", "cultural activities"),
    "nature": ("beach and nature", "beach nature", "nature trips", "nature walks"),
    "shopping": ("shopping", "go shopping", "shopping trip"),
    "others": ("others",),
}

# The fresh-install seed uses longer slugs than some older installations. Map
# those slugs to the same phrase sets without changing any stored hobby tags.
# If both variants exist, the normal ambiguity check below still avoids guessing.
SEEDED_HOBBY_ALIASES = {
    "hiking-eco-tourism": "hiking",
    "coffee-cafe-hopping": "cafe",
    "dining-foodie": "food",
    "karaoke-nightlife": "music",
    "culture-heritage": "culture",
}

_PREFIXES = (
    r"(?:show|find|recommend|suggest)(?: me)? (?:places|spots|destinations|activities) (?:for|to|with)",
    r"(?:places|spots|destinations|activities) (?:for|to|with)",
    r"(?:i (?:like|love|enjoy|want to|would like to)|im interested in|i am interested in|my (?:hobby|interest) is)",
)
_CITY_SUFFIX = re.compile(r"\s+(?:in|around|near) kabankalan(?: city)?$")


def hobby_for_query(query):
    """Return one existing hobby slug for a clear interest phrase, or None.

    Exact database name/slug takes precedence over curated aliases. If an
    alias is ambiguous between multiple existing hobbies, it is not guessed.
    """
    phrase = normalize_words(query)
    if not phrase:
        return None
    phrase = _CITY_SUFFIX.sub("", phrase)
    for prefix in _PREFIXES:
        reduced = re.sub(rf"^(?:{prefix})\s+", "", phrase, count=1)
        if reduced != phrase:
            phrase = reduced
            break
    if not phrase:
        return None

    hobbies = list(Hobby.objects.values_list("slug", "name"))
    direct = [slug for slug, name in hobbies if phrase in (normalize_words(slug), normalize_words(name))]
    if len(direct) == 1:
        return direct[0]
    if direct:
        return None
    matches = [
        slug for slug, _ in hobbies
        if phrase in HOBBY_ALIASES.get(SEEDED_HOBBY_ALIASES.get(slug, slug), ())
    ]
    return matches[0] if len(matches) == 1 else None
