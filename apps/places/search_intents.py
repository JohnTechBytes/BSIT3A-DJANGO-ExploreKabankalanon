"""Question-aware search for the Explore Kabankalan catalogue.

The catalogue holds **real places**, so a search has to answer two different
kinds of question honestly:

``"Mag-aso Falls"`` / ``"Kabankalan Plaza"``
    The visitor names a place. The answer is that place - and only that
    place. A query that carries a full place name used to fall back to a
    broad "all titles contain these words" match and could return dozens of
    unrelated records, so the exact title is matched first.

``"where to buy a phone case"``
    The visitor names a **product**, not a place. No listing in Kabankalan
    is called "Phone Case", so a text search finds nothing. The honest answer
    is the *category* that sells such things - the shops and malls - and the
    page says so: the match came from the category, not from a listing name.

Everything in this module is a curated rule over the existing taxonomy. No
external service and no generated data is involved.
"""
import re
import unicodedata

from django.db.models import Q

from .nearby_intent import normalize_words

# ---------------------------------------------------------------------------
# Word lists
# ---------------------------------------------------------------------------

#: Question words and filler that never carry meaning on their own.
STOP_WORDS = {
    "i", "want", "to", "go", "a", "an", "the",
    "in", "at", "of", "for", "me", "find",
    "show", "places", "place", "visit", "near",
    "some", "where", "can", "you", "please",
    "would", "like", "explore",
}

#: City/province words are location qualifiers, not attraction keywords.
LOCATION_WORDS = {
    "kabankalan", "city", "negros", "occidental", "philippines",
}

#: Extra filler used by the attraction filter on top of :data:`STOP_WORDS`.
FILLER_WORDS = {
    "attraction", "attractions", "destination", "destinations",
    "thing", "things", "do", "around", "within", "nearby",
    "spot", "spots", "tourist", "site", "sites", "best", "top",
    "looking", "from", "my", "and", "hopping", "activity", "activities",
}

#: Broad searches such as "nature", "museum" and "waterfalls".
SEARCH_INTENTS = {
    "beach": {
        "triggers": ["beach", "beaches", "swimming", "seaside"],
        "terms": ["beach", "coast", "seaside", "shore", "bay"],
    },
    "waterfall": {
        "triggers": ["waterfall", "waterfalls", "falls"],
        "terms": ["waterfall", "falls", "cascade"],
    },
    "nature": {
        "triggers": ["nature", "forest", "mountain", "hiking"],
        "terms": [
            "forest", "mountain", "trail", "hiking",
            "nature", "park", "hill", "peak",
        ],
    },
    "history": {
        "triggers": ["history", "historical", "heritage", "museum"],
        "terms": [
            "museum", "heritage", "historical",
            "monument", "memorial", "shrine",
        ],
    },
    "food": {
        "triggers": ["food", "eat", "restaurant", "cafe", "coffee"],
        "terms": [
            "restaurant", "cafe", "coffee",
            "eatery", "food", "dining",
        ],
    },
}

#: Words that describe a *kind* of place rather than one particular place.
GENERIC_WORDS = {
    word
    for intent in SEARCH_INTENTS.values()
    for word in intent["triggers"] + intent["terms"]
} | {
    "mount", "mountain", "mountains", "hill", "hills", "peak", "peaks",
    "plaza", "museum", "park", "parks", "trail", "trails", "river",
    "food", "photography", "gaming", "art", "culture", "shopping",
    "billiards", "basketball", "music", "swimming",
}

#: Hobby words that may accompany a place name ("Mag-aso Falls hiking").
IGNORED_MODIFIERS = {
    "nature", "hiking", "photography", "swimming", "beach",
    "beaches", "food", "eat", "cafe", "coffee", "shopping",
    "gaming", "music", "art", "culture",
}

# ---------------------------------------------------------------------------
# Buying intent
# ---------------------------------------------------------------------------

#: Phrases that clearly ask for a product to be bought.
STRONG_BUYING_PHRASES = (
    "where to buy", "where can i buy", "where do i buy",
    "where shall i buy", "i want to buy", "i need to buy",
    "i would like to buy", "to buy", "buy", "buying", "purchase",
    "who sells", "where to get", "where can i get", "where do i get",
)

#: Softer seller wording - still a question about a product, not a place.
SOFT_BUYING_PHRASES = (
    "sell", "sells", "selling", "sold", "supplier", "suppliers",
    "vendor", "vendors", "shop that has", "store that has",
    "market that has",
)

#: The buying categories of the existing taxonomy. The slugs and the name
#: fragments are matched, because a category can be renamed by staff.
CATEGORY_GROUPS = {
    "shopping": {
        "label": "shops and malls",
        "slugs": ("malls-shopping-centers", "other-local-businesses"),
        "names": ("malls", "shopping centers", "other local businesses"),
        "answer": "the shops and malls of Kabankalan may be places to look for {product}",
        "answer_plural": "the shops and malls of Kabankalan may be places to look for {product}",
    },
    "food": {
        "label": "restaurants and cafes",
        "slugs": ("restaurants-eateries", "coffee-shops-cafes"),
        "names": ("restaurants", "eateries", "coffee shops", "cafes"),
        "answer": "the restaurants and cafes of Kabankalan may be places to look for {product}",
        "answer_plural": "the restaurants and cafes of Kabankalan may be places to look for {product}",
    },
    "grooming": {
        "label": "barbershops and salons",
        "slugs": ("barber-hair-salon",),
        "names": ("barber", "hair salon"),
        "answer": "the barbershops and salons of Kabankalan may offer {product}",
        "answer_plural": "the barbershops and salons of Kabankalan may offer {product}",
    },
}

#: Product words that belong to a specific buying category.
PRODUCT_GROUPS = {
    "grooming": (
        "haircut", "hair cut", "hair", "barber", "barbershop", "salon",
        "shave", "hairdo", "braid",
    ),
    "food": (
        "food", "meal", "lunch", "dinner", "breakfast", "snack", "drink",
        "drinks", "beverage", "coffee", "restaurant", "eatery", "pastry",
    ),
}

#: Flat product -> group lookup, used by :func:`product_group`.
PRODUCT_TO_GROUP = {
    keyword: group
    for group, keywords in PRODUCT_GROUPS.items()
    for keyword in keywords
}

#: Words that name a buying category inside the question itself.
INTENT_GROUP_WORDS = {
    "grooming": ("barber", "barbershop", "salon", "haircut", "hair"),
    "food": (
        "restaurant", "eatery", "food", "eat", "dining", "cafe",
        "coffee", "snack", "meal",
    ),
    "shopping": (
        "mall", "malls", "shop", "shops", "store", "stores", "market",
        "supermarket", "groceries", "grocery",
    ),
}

#: Words that are dropped when the product itself is extracted.
PRODUCT_STOP_WORDS = {
    "i", "want", "need", "would", "like", "please", "can", "could", "you",
    "we", "do", "does", "is", "are", "there", "any", "some", "me", "my",
    "a", "an", "the", "of", "in", "at", "for", "on", "to", "get", "know",
    "tell", "where", "who", "what", "which", "and", "or", "it", "be",
}


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def tokenize(search_text):
    """Return the lower-case word tokens of ``search_text``."""
    normalized = unicodedata.normalize(
        "NFKD", str(search_text or "")[:300]
    ).encode("ascii", "ignore").decode("ascii").lower()
    return re.findall(r"[a-z0-9]+", normalized)


def search_keywords(search_text):
    """Return the meaningful keywords of a query (no location or filler words)."""
    filler_words = STOP_WORDS | FILLER_WORDS
    return list(dict.fromkeys(
        word for word in tokenize(search_text)
        if word not in LOCATION_WORDS
        and word not in filler_words
        and len(word) >= 2
    ))


def _contains_phrase(text, phrase):
    """True when ``phrase`` appears in ``text`` as a whole word sequence."""
    return f" {phrase} " in f" {text} "


def _remove_phrase(words, phrase):
    """Remove the first occurrence of ``phrase`` from a list of words."""
    needle = phrase.split()
    for index in range(len(words) - len(needle) + 1):
        if words[index:index + len(needle)] == needle:
            return words[:index] + words[index + len(needle):]
    return words


# ---------------------------------------------------------------------------
# Buying intent
# ---------------------------------------------------------------------------

def wants_to_buy(query):
    """True when the query asks for a product to be bought."""
    text = normalize_words(query)
    if not text:
        return False
    return any(
        _contains_phrase(text, phrase)
        for phrase in STRONG_BUYING_PHRASES
    )


def maybe_buying(query):
    """True when the query asks about a seller rather than about a place."""
    text = normalize_words(query)
    if not text:
        return False
    return any(
        _contains_phrase(text, phrase)
        for phrase in SOFT_BUYING_PHRASES
    )


def shopping_product(query):
    """Return the product of a buying question, e.g. ``"a phone case"``."""
    words = normalize_words(query).split()
    for phrase in sorted(
        STRONG_BUYING_PHRASES + SOFT_BUYING_PHRASES,
        key=lambda item: -len(item.split()),
    ):
        words = _remove_phrase(words, phrase)
    words = [word for word in words if word not in PRODUCT_STOP_WORDS]
    return " ".join(words)


def product_group(product):
    """Return the buying group a product belongs to, or ``""``."""
    text = normalize_words(product)
    if not text:
        return ""
    words = text.split()
    for group, keywords in PRODUCT_GROUPS.items():
        for keyword in keywords:
            if " " in keyword:
                if keyword in text:
                    return group
            elif keyword in words:
                return group
    return ""


def intent_group(query):
    """Return the buying group named by the query itself, or ``""``."""
    text = normalize_words(query)
    if not text:
        return ""
    words = text.split()
    for group, keywords in INTENT_GROUP_WORDS.items():
        for keyword in keywords:
            if " " in keyword:
                if keyword in text:
                    return group
            elif keyword in words:
                return group
    return ""


def group_filter(group):
    """Return the queryset filter for a buying group, or ``None``."""
    spec = CATEGORY_GROUPS.get(group)
    if not spec:
        return None
    predicate = Q(category__slug__in=list(spec["slugs"]))
    for fragment in spec["names"]:
        predicate |= Q(category__name__icontains=fragment)
    return predicate


def resolve_buying_group(query):
    """Return the buying group that answers ``query``.

    A product that does not belong to a specific category ("a phone case",
    "an umbrella") is answered by the shops and malls of the city.
    """
    product = shopping_product(query)
    return product_group(product) or intent_group(query) or "shopping"


def _is_plural(product):
    words = product.split()
    if not words:
        return False
    last = words[-1]
    return last.endswith("s") and not last.endswith("ss")


def with_article(product):
    """Return the product with a leading article when it is singular."""
    if not product or _is_plural(product):
        return product
    return ("an " if product[0] in "aeiou" else "a ") + product


def describe_search(group, product):
    """Return the honest note that explains where the answer comes from."""
    spec = CATEGORY_GROUPS.get(group)
    if not spec:
        return ""
    phrase = with_article(product or "it")
    answer = spec["answer_plural"] if _is_plural(product or "") else spec["answer"]
    sentence = answer.format(product=phrase)
    return (
        "Matched by category: %s. No listing names %s directly; availability is not confirmed."
        % (sentence, phrase)
    )


# ---------------------------------------------------------------------------
# Named places
# ---------------------------------------------------------------------------

def exact_title_filter(query, queryset):
    """Return a filter for the place whose title is the query, or ``None``.

    The comparison is done on the normalised title, so ``"Mag Aso Falls"``
    still finds ``"Mag-Aso Falls"``. Only one place can carry a given
    title, so the answer to a named-place question is that place alone.
    """
    text = (query or "").strip()
    if not text:
        return None

    ids = [
        place.pk for place in queryset.filter(title__iexact=text)[:5]
    ]
    if ids:
        return Q(pk__in=ids)

    normalized = normalize_words(text)
    if not normalized:
        return None

    # Narrow the comparison with the first word that is not the city name,
    # so the scan runs over a handful of titles instead of the whole table.
    token = next(
        (word for word in normalized.split() if word not in LOCATION_WORDS),
        None,
    )
    if not token:
        return None

    ids = [
        pk for pk, title in queryset.filter(title__icontains=token)
        .values_list("pk", "title")[:500]
        if normalize_words(title) == normalized
    ][:5]
    if not ids:
        return None
    return Q(pk__in=ids)


def named_place_filter(search_text):
    """Return a filter that matches a named place, or ``None``.

    A query only names a place when it carries a word that does not belong
    to the generic vocabulary (``"Mag"``, ``"Amyan"``, ``"Aguinaldo"``).
    Generic queries such as ``"coffee shop"`` are left to the ordinary
    category search.
    """
    keywords = search_keywords(search_text)
    if not keywords:
        return None
    if not [word for word in keywords if word not in GENERIC_WORDS]:
        return None
    name_words = [word for word in keywords if word not in IGNORED_MODIFIERS]
    if not name_words:
        return None
    predicate = Q()
    for word in name_words:
        predicate &= Q(title__icontains=word)
    return predicate


# ---------------------------------------------------------------------------
# The filter used by the carousel and the nearby page
# ---------------------------------------------------------------------------

def build_attraction_filter(search_text):
    """Match named Kabankalan places precisely; expand only broad category searches.

    The caller already limits records to verified, published Kabankalan places.
    Query-based filtering is separate from hobby/rating recommendation ranking.
    """
    words = tokenize(search_text)
    if not words:
        return None

    keywords = search_keywords(search_text)

    # "places in Kabankalan" is a browse-all request, not a failed search.
    if not keywords:
        return None

    matched_intents = [
        name for name, intent in SEARCH_INTENTS.items()
        if any(word in intent["triggers"] for word in keywords)
    ]

    # A distinctive name token (Amyan, CPSU, Mag, Aso, Nai-guin, etc.) means
    # the visitor is looking for a particular place, not all places of a type.
    # Require every name token to appear in the title, preventing broad OR
    # matches from yielding nearly all places for "CPSU Museum".
    named = named_place_filter(search_text)
    if named is not None:
        return named

    # "Kabankalan Plaza" or "plaza in Kabankalan" should only find
    # the actual place title, not unrelated places mentioning Kabankalan.
    if "kabankalan" in words and not matched_intents:
        title_filter = Q()
        for word in keywords:
            title_filter &= Q(title__icontains=word)
        return title_filter

    # Broad searches such as "nature", "museum" and "waterfalls" can use
    # known types and matching text. Do not demand the correct category slug
    # alone, because some verified records still have a generic category.
    if matched_intents:
        category_slugs = {
            "beach": ("beach",),
            "waterfall": ("waterfall",),
            "history": (
                "museum", "memorial", "monument", "historic-ruins",
                "historic-fort", "archaeological-site",
            ),
        }
        terms = set()
        slugs = set()
        for name in matched_intents:
            terms.update(SEARCH_INTENTS[name]["terms"])
            slugs.update(category_slugs.get(name, ()))

        broad_filter = Q()
        if slugs:
            broad_filter |= Q(category__slug__in=sorted(slugs))
        for term in sorted(terms):
            broad_filter |= Q(title__icontains=term)
            broad_filter |= Q(description__icontains=term)
            broad_filter |= Q(address__icontains=term)
            broad_filter |= Q(category__name__icontains=term)
        return broad_filter

    # Plain terms such as "plaza" require a match to the supplied terms.
    # AND across words prevents location text from matching every destination.
    text_filter = Q()
    for word in keywords:
        text_filter &= (
            Q(title__icontains=word)
            | Q(description__icontains=word)
            | Q(address__icontains=word)
            | Q(barangay__icontains=word)
            | Q(category__name__icontains=word)
        )
    return text_filter


def question_matches(query, queryset=None):
    """Return ``(filter, note)`` for a question-shaped query.

    * a query that names a place exactly returns that single place;
    * a buying question returns the business category that answers it and
      an honest note that says the match came from the category;
    * a clear hobby phrase uses existing assigned tags, with a disclosure;
    * anything else returns ``(None, "")`` so the caller can fall back to
      the ordinary attraction filter.
    """
    text = normalize_words(query)
    if not text:
        return None, ""

    if queryset is not None:
        exact = exact_title_filter(query, queryset)
        if exact is not None:
            return exact, ""

    if wants_to_buy(text) or maybe_buying(text):
        product = shopping_product(text)
        group = resolve_buying_group(query)
        predicate = group_filter(group)
        if predicate is not None:
            return predicate, describe_search(group, product)

    # A clear interest phrase uses existing staff-assigned hobby tags, not
    # guesses based on a business category or generated place descriptions.
    # Exact place names and buying intent above retain priority.
    from .hobby_search import hobby_for_query

    hobby_slug = hobby_for_query(query)
    if hobby_slug:
        return Q(hobbies__slug=hobby_slug), (
            "Matched by assigned hobby tags. Untagged places may also be relevant."
        )

    return None, ""
