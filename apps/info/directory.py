"""Read-only groupings of the existing Kabankalan place catalogue.

These navigation groups are search aids, not verified classifications or
hobby assignments. They use existing category slugs and conservative title
matches; an ungrouped place remains available under All places.
"""
from django.db.models import Q

DIRECTORY_SECTIONS = (
    ("all", "All"),
    ("malls", "Malls"),
    ("attractions", "Attractions"),
    ("waterfalls", "Waterfalls"),
    ("food", "Food & cafés"),
    ("services", "Shops & services"),
    ("guides", "City guides"),
)

ATTRACTION_CATEGORIES = (
    "archaeological-site", "art-gallery", "beach", "cave", "garden",
    "historic-castle", "historic-fort", "historic-ruins", "hot-spring",
    "memorial", "monument", "mountain-peak", "museum", "nature-reserve",
    "park", "public-art", "scenic-viewpoint", "shrine", "spring",
    "theme-park", "zoo", "waterfall", "waterfalls",
)
WATERFALLS = Q(category__slug__in=("waterfall", "waterfalls")) | Q(
    title__iregex=r"(^|[^a-z])(falls|waterfalls?)($|[^a-z])"
)
ATTRACTIONS = Q(category__slug__in=ATTRACTION_CATEGORIES) | WATERFALLS | Q(
    title__iregex=r"(^|[^a-z])(plazas?|parks?|museums?|hills?|mountains?|mount|peaks?)($|[^a-z])"
)
DIRECTORY_FILTERS = {
    "malls": Q(category__slug="malls-shopping-centers"),
    "attractions": ATTRACTIONS,
    "waterfalls": WATERFALLS,
    "food": Q(category__slug__in=("restaurants-eateries", "coffee-shops-cafes")),
    "services": Q(category__slug__in=("other-local-businesses", "barber-hair-salon")),
}
