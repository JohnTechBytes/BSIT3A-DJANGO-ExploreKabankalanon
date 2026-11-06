"""Choose explicitly illustrative artwork for places without a real photo.

These are shared illustrations, not photos or claims about listed places.
Unknown categories receive a generic, AI-generated scene rather than a
place-specific claim.
"""
import re
import unicodedata


# Specific features are checked before broad categories (for example, a
# waterfall in a nature category should not receive the mountain illustration).
_SAMPLE_PATTERNS = (
    (r"\b(coffee(?:\s*shops?)?|coffeehouse|cafes?|cafeteria|kape)\b", "coffee"),
    (r"\b(billiards?|billards?|bilyar|pool\s+(?:halls?|tables?))\b", "billiards"),
    (r"\b(barber(?:s|\s*shops?)?|salons?|hairdressers?|haircuts?)\b", "barber"),
    (r"\b(malls?|shopping\s+cent(?:er|re)s?|department\s+stores?)\b", "shopping"),
    (r"\b(waterfalls?|falls|rivers?|springs?)\b", "nature"),
    (r"\b(mount(?:ains?)?|hills?|peaks?|hiking|trails?)\b", "mountain"),
    (r"\b(nature|forests?|outdoors?)\b", "nature"),
    (r"\b(restaurants?|food|inasal|grills?|barbecue|bbq|eatery|eateries|dining)\b", "food"),
    (r"\b(museums?|heritage|culture|cultural|historical)\b", "museum"),
    (r"\b(plazas?|parks?|landmarks?|monuments?)\b", "city"),
)


def sample_image_for(place):
    """Return a shared category sample, or a generic scene for unknown places."""
    category = place.category.name if place.category else ""
    text = f"{place.title} {category}".casefold()
    # A café should match both accented and unaccented spellings.
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    for pattern, image in _SAMPLE_PATTERNS:
        if re.search(pattern, text):
            return f"img/samples/{image}.jpg"
    return "img/samples/generic.jpg"
