import re

from django.db.models import Case, Count, IntegerField, Q, Value, When
from django.shortcuts import render
from django.urls import reverse

from apps.cities.locking import LOCKED_CITY_PK
from apps.core.models import Category
from apps.places.models import Place
from apps.places.sample_images import sample_image_for


def home(request):
    """Feature published local records, prioritizing the existing OSM imports."""
    published = Place.objects.filter(
        city_id=LOCKED_CITY_PK, is_active=True, is_verified=True,
    )
    categories = Category.objects.filter(places__in=published).distinct().order_by("name")
    selected_category = request.GET.get("category", "")
    places = published
    if selected_category:
        places = places.filter(category__slug=selected_category)
    places = places.annotate(
        osm_priority=Case(
            When(slug__startswith="osm-", then=Value(1)),
            default=Value(0), output_field=IntegerField(),
        ),
        photo_priority=Case(
            When(
                (Q(cover_image__isnull=False) & ~Q(cover_image=""))
                | (Q(cover_image_url__isnull=False) & ~Q(cover_image_url="")),
                then=Value(1),
            ),
            default=Value(0), output_field=IntegerField(),
        ),
    ).select_related("category").prefetch_related("hobbies").order_by(
        "-osm_priority", "-photo_priority", "-avg_rating", "-review_count", "title", "pk",
    )
    featured_places = list(places)
    for place in featured_places:
        place.sample_image = sample_image_for(place) if not (place.cover_image or place.cover_image_url) else ""
        # The importer's osm-type-id slug is the existing provenance identifier.
        match = re.fullmatch(r"osm-(node|way|relation)-(\d+)", place.slug)
        place.osm_source_url = (
            f"https://www.openstreetmap.org/{match[1]}/{match[2]}" if match else ""
        )
    # The landing map is a small preview of actual records, not a second
    # ranking or invented locations. The full list remains in the carousel.
    map_places = []
    for place in featured_places:
        if (place.latitude is not None and place.longitude is not None
                and -90 <= place.latitude <= 90 and -180 <= place.longitude <= 180):
            map_places.append({
                "title": place.title, "latitude": float(place.latitude),
                "longitude": float(place.longitude),
                "url": reverse("places:place_detail", args=[place.pk]),
            })
            if len(map_places) == 24:
                break
    # One aggregate query for both counters instead of two separate counts.
    totals = published.aggregate(
        published=Count("id"),
        osm=Count("id", filter=Q(slug__startswith="osm-")),
    )
    return render(request, "home.html", {
        "featured_places": featured_places,
        "map_places": map_places,
        "categories": categories,
        "selected_category": selected_category,
        "published_count": totals["published"],
        "osm_count": totals["osm"],
    })


def error_404(request, exception=None):
    """Dark editorial 404 page; used when DEBUG is off."""
    return render(request, "errors/404.html", status=404)


def error_500(request):
    """Dark editorial 500 page; used when DEBUG is off."""
    return render(request, "errors/500.html", status=500)
