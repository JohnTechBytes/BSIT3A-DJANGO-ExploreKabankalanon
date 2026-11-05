
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.cities.models import City
from apps.core.models import Category, Hobby
from .models import Place, SavedPlace, Review
from .sample_images import sample_image_for

# The search rules live in apps.places.search_intents so that the carousel,
# the nearby page and the search audit command all use the same vocabulary.
# They are re-exported here because other modules import them from views.
from .search_intents import (
    SEARCH_INTENTS,
    STOP_WORDS,
    build_attraction_filter,
    question_matches,
)


# Guard rail only: the carousel is designed to show every published place.
MAX_CAROUSEL_PLACES = 500


@login_required
def attraction_carousel(request):
   
    # ExploreAnywhere: Kabankalan City Edition
    city_id = 2

    # Keep existing session-dependent templates compatible.
    request.session["city_id"] = city_id
    request.session["selected_city_id"] = city_id
    request.session["selected_city_name"] = "Kabankalan"
    request.session["selected_province"] = "Negros Occidental"

    if not city_id:
        return redirect("city_selection")

    city = City.objects.filter(pk=city_id).first()

    if city is None:
        return redirect("city_selection")

    # Phase 6F: one Discover Kabankalan URL with Browse / Nearby / Map modes.
    # Nearby reuses the existing verified-only queryset and browser-only GPS.
    # The previous /places/nearby/ URL is retained as a compatibility redirect.
    if (request.GET.get("mode") == "nearby" or
            any(key in request.GET for key in ("service", "place", "origin"))):
        from .nearby import nearby_places
        return nearby_places(request, unified=True)

    # The visitor must finish Hobby Selection first.
    # exploreanywhere-phase4f-direct-place-browse-v1
    # Browse published Kabankalan places without requiring a hobby session.

    # exploreanywhere-phase5a-discovery-controls-v1
    # Browse all resets the previous search; hobby personalization is preserved.
    browse_all = request.GET.get("browse") == "all"
    if browse_all:
        request.session.pop("attraction_search_query", None)
        search_query = ""
    elif "q" in request.GET:
        # Inline search shares the existing hobby-search session convention.
        search_query = (request.GET.get("q") or "").strip()[:200]
        if search_query:
            request.session["attraction_search_query"] = search_query
        else:
            request.session.pop("attraction_search_query", None)
    else:
        search_query = (
            request.session.get("attraction_search_query") or ""
        ).strip()[:200]

    # Phase 6A: natural-language service requests open nearby results directly.
    # Avoid changing hobby search sessions or normal attraction queries.
    if "q" in request.GET and search_query:
        from urllib.parse import urlencode as ea6_urlencode
        from django.urls import reverse as ea6_reverse
        from .nearby_intent import detect_service_intent
        if detect_service_intent(search_query):
            return redirect(
                ea6_reverse("places:attraction_carousel") + "?" +
                ea6_urlencode({"mode": "nearby", "q": search_query})
            )

    # Only offer category/hobby filters used by published Kabankalan places.
    # Performance: the option lists are built with small aggregate queries
    # instead of loading every published place (and all of its hobby rows) a
    # second time. The complete set is still loaded once, for the carousel.
    published_scope = Place.objects.filter(
        city=city, is_active=True, is_verified=True,
    )
    published_total = published_scope.count()
    available_categories = {
        str(category_id): name
        for category_id, name in Category.objects
            .filter(places__in=published_scope)
            .values_list("id", "name")
            .distinct()
    }
    available_hobbies = {
        slug: name
        for slug, name in Hobby.objects
            .filter(places__in=published_scope)
            .exclude(slug="")
            .values_list("slug", "name")
            .distinct()
    }
    published_places = published_scope.select_related("city", "category")

    category_options = sorted(
        ({"value": key, "label": value} for key, value in available_categories.items()),
        key=lambda item: item["label"].casefold(),
    )
    hobby_options = sorted(
        ({"value": key, "label": value} for key, value in available_hobbies.items()),
        key=lambda item: item["label"].casefold(),
    )

    selected_category = "" if browse_all else (request.GET.get("category") or "").strip()
    selected_hobby = "" if browse_all else (request.GET.get("hobby") or "").strip()
    selected_sort = "recommended" if browse_all else (request.GET.get("sort") or "recommended")
    if selected_category not in available_categories:
        selected_category = ""
    if selected_hobby not in available_hobbies:
        selected_hobby = ""
    if selected_sort not in {"recommended", "rating", "name"}:
        selected_sort = "recommended"

    # The hobby choice is a preference, not a one-off filter: it is stored in
    # the session so the recommendation score keeps using it on later pages
    # (and so My Journey can show the visitor's interests). Browsing every
    # place keeps the preference; an explicit empty hobby parameter clears it.
    if "hobby" in request.GET and not browse_all:
        if selected_hobby:
            request.session["selected_hobbies"] = [selected_hobby]
        else:
            request.session.pop("selected_hobbies", None)

    attractions = published_places
    if selected_category:
        attractions = attractions.filter(category_id=int(selected_category))
    if selected_hobby:
        attractions = attractions.filter(hobbies__slug=selected_hobby).distinct()

    # Apply the user's NLP search request.
    # A question is answered by the record it names ("Mag-aso Falls" returns
    # that place) or by the category that holds the answer ("where to buy a
    # phone case" returns the shops and malls). question_matches() returns
    # the honest note that tells the visitor where the answer came from.
    search_note = ""
    if search_query:
        search_filter, search_note = question_matches(search_query, published_places)
        if search_filter is None:
            search_filter = build_attraction_filter(search_query)

        if search_filter is not None:
            attractions = attractions.filter(search_filter)

    from .recommendations import rank_kabankalan_places

    # exploreanywhere-phase6i-inline-hobby-relevance
    # Use the Explore Places hobby dropdown without requiring a separate step.
    # If no filter is chosen, retain any previously saved preferences.
    scoring_hobbies = (
        [selected_hobby] if selected_hobby
        else request.session.get("selected_hobbies", [])
    )
    attractions = rank_kabankalan_places(
        attractions.prefetch_related("hobbies"),
        scoring_hobbies,
    )

    # Sorting affects display only; preserve existing recommendation scores.
    if selected_sort == "name":
        attractions.sort(key=lambda place: (place.title or "").casefold())
    elif selected_sort == "rating":
        attractions.sort(key=lambda place: (
            -float(place.avg_rating or 0),
            -int(place.review_count or 0),
            (place.title or "").casefold(),
        ))

    # The looping carousel shows every matching destination, so no pagination
    # page is sliced here. A high cap only guards against pathological datasets.
    total_matches = len(attractions)
    carousel_places = attractions[:MAX_CAROUSEL_PLACES]
    # Real photos remain authoritative; illustrative samples fill genuine gaps.
    for place in carousel_places:
        place.sample_image = sample_image_for(place) if not (place.cover_image or place.cover_image_url) else ""

    # Every submitted search is written to the query log so the visitor can
    # see their own search history in My Journey.
    if "q" in request.GET and search_query:
        from apps.info.models import QueryLog

        QueryLog.objects.create(
            user=request.user if request.user.is_authenticated else None,
            raw_query=search_query,
            parsed_json={
                "category": selected_category,
                "hobby": selected_hobby,
                "sort": selected_sort,
            },
            matched_count=total_matches,
        )

    # exploreanywhere-phase5a2-discovery-clarity-v1
    # Remove-one controls retain the other active filters and clear q from the
    # existing search session when the Search chip is removed.
    from urllib.parse import urlencode

    active_state = {
        "q": search_query,
        "category": selected_category,
        "hobby": selected_hobby,
        "sort": selected_sort,
    }
    active_filter_chips = []
    labels = (
        ("q", "Search", search_query),
        ("category", "Category", available_categories.get(selected_category, "")),
        ("hobby", "Hobby", available_hobbies.get(selected_hobby, "")),
        (
            "sort", "Sort",
            {"name": "Name A–Z", "rating": "Highest rated"}.get(selected_sort, ""),
        ),
    )
    for field, label, value in labels:
        if not value:
            continue
        remaining_state = dict(active_state)
        remaining_state[field] = "recommended" if field == "sort" else ""
        active_filter_chips.append({
            "label": f"{label}: {value}",
            "remove_url": "?" + urlencode(remaining_state),
        })

    return render(
        request,
        "places/attraction_carousel.html",
        {
            "selected_city": city,
            "attractions": carousel_places,
            "total_attractions": total_matches,
            "carousel_truncated": total_matches > len(carousel_places),
            "selected_hobbies": scoring_hobbies,
            "search_query": search_query,
            "search_note": search_note,
            "published_total": published_total,
            "category_options": category_options,
            "hobby_options": hobby_options,
            "selected_category": selected_category,
            "selected_hobby": selected_hobby,
            "selected_sort": selected_sort,
            "active_filter_chips": active_filter_chips,
            "active_discovery_mode": (
                "map" if request.GET.get("display") == "map" else "browse"
            ),
        },
    )

@login_required
def place_detail(request, pk):
    
    city = City.objects.get(
        pk=2,
        name__iexact="Kabankalan",
        province__iexact="Negros Occidental",
    )


    # phase4f: place details accessible without hobby-selection session
    # Saved Places, reviews and visit history must open details directly.

    from django.shortcuts import get_object_or_404

    place = get_object_or_404(
        Place.objects.select_related(
            "city", "category"
        ).prefetch_related(
            "photos", "opening_hours", "hobbies"
        ),
        pk=pk,
        city=city,
        is_active=True,
        is_verified=True,
    )

    photos = [
        photo for photo in place.photos.all()
        if photo.image or photo.image_url
    ]

    nearby_places = (
        Place.objects.filter(
            city=city,
            is_active=True,
            is_verified=True,
        )
        .exclude(pk=place.pk)
        .select_related("category")
        .order_by("-avg_rating", "title")[:4]
    )

    place.sample_image = sample_image_for(place) if not (place.cover_image or place.cover_image_url) else ""

    # The active search is what makes a relevance rating meaningful, so the
    # page can offer the rating control and show the visitor's own answer.
    from apps.info.models import RecommendationRating

    active_search_query = (
        request.session.get("attraction_search_query") or ""
    ).strip()[:255]
    my_relevance_rating = None
    if request.user.is_authenticated:
        my_relevance_rating = (
            RecommendationRating.objects.filter(
                user=request.user, place=place, query_text=active_search_query,
            ).order_by("-created_at", "-pk").first()
        )

    return render(
        request,
        "places/place_detail.html",
        {
            "place": place,
            "photos": photos,
            "nearby_places": nearby_places,
            "opening_hours": place.opening_hours.all(),
            "selected_city": city,
            "is_saved": SavedPlace.objects.filter(user=request.user, place=place).exists(),
            # ExploreAnywhere phase3e reviews v1
            "my_review": Review.objects.filter(user=request.user, place=place).order_by("pk").first(),
            "public_reviews": Review.objects.filter(place=place).select_related("user").order_by("-created_at")[:8],
            "review_rating_options": (5, 4, 3, 2, 1),
            # Relevance feedback for the active search (P1)
            "active_search_query": active_search_query,
            "my_relevance_rating": my_relevance_rating,
            "relevance_rating_choices": RecommendationRating.RatingChoices.choices,
        },
    )


from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from .models import Place



def city_discover(request):
    city_id = 2

    places = (
        Place.objects
        .filter(city_id=city_id)
        .select_related("city", "category")
        .order_by("-is_verified", "-is_active", "title")
    )


    paginator = Paginator(places, 24)
    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "places/city_discover.html",
        {
            "page_obj": page_obj,
            "city_name": request.session.get(
                "selected_city_name", "Selected City"
            ),
            "total_places": paginator.count,
        },
    )

# ExploreAnywhere phase3 save-and-journey v1
