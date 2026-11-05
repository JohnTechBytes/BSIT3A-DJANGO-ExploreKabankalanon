"""Curated ExploreAnywhere search aliases for verified Kabankalan businesses.

These are intent/category matches, not external place records, geocoding or AI.
"""
import re
import unicodedata

SERVICE_CATEGORIES = (
    ("billiards", "Billiards / pool halls"),
    ("coffee", "Coffee shops / cafés"),
    ("barber", "Barbershops / salons"),
    ("restaurant", "Restaurants / eateries"),
    ("mall", "Malls / shopping centers"),
)

# Keep aliases specific: e.g. "mall" must not match "small".
ALIASES = {
    "billiards": (
        "billiards", "billiard", "billard", "billards", "bilyar",
        "pool hall", "pool halls", "pool table", "play pool", "play billiards",
    ),
    "coffee": (
        "coffee shop", "coffeeshop", "coffeshop", "coffee shops",
        "coffee", "cafe", "cafes", "cafeteria", "coffeehouse",
    ),
    "barber": (
        "barbershop", "barber shop", "barber", "barbers", "barber shops",
        "haircut", "hair cut", "hair salon", "salon", "hairdresser",
    ),
    "restaurant": (
        "restaurant", "restaurants", "resto", "eatery", "eateries",
        "food court", "diner", "where to eat", "dining", "fast food",
    ),
    "mall": (
        "shopping mall", "mall", "malls", "shopping center",
        "shopping centre", "department store",
    ),
}

# The seed taxonomy uses a longer slug for coffee/café hopping. Keep both
# variants so the service filter treats the same staff-assigned tag consistently.
HOBBY_ALIASES = {"billiards": ("billiards",), "coffee": ("cafe", "coffee-cafe-hopping")}


def normalize_words(value):
    normalized = unicodedata.normalize("NFKD", str(value or "")[:200])
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").casefold()
    return " ".join(re.findall(r"[a-z0-9]+", ascii_text))


def phrase_present(text, phrase):
    haystack = f" {normalize_words(text)} "
    needle = f" {normalize_words(phrase)} "
    return bool(needle.strip()) and needle in haystack


def detect_service_intent(query):
    """Return a supported category or None, preserving other existing searches."""
    q = normalize_words(query)
    if not q:
        return None
    for key, _ in SERVICE_CATEGORIES:
        if any(phrase_present(q, alias) for alias in ALIASES[key]):
            return key
    return None


def matches_service(place, service):
    """Match supported category via real record metadata, never invent a POI."""
    if service not in ALIASES:
        return False
    category = getattr(place, "category", None)
    fields = [getattr(place, "title", "")]
    if category is not None:
        fields.extend((getattr(category, "name", ""), getattr(category, "slug", "")))
    if any(phrase_present(field, alias) for field in fields for alias in ALIASES[service]):
        return True
    allowed_hobbies = set(HOBBY_ALIASES.get(service, ()))
    if allowed_hobbies:
        return bool(allowed_hobbies.intersection(
            hobby.slug for hobby in place.hobbies.all()
        ))
    return False
