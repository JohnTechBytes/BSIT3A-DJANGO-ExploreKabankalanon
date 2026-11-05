"""Public, read-only City Information module.

The records shown here are published by staff in the administrative panel
(Admin > City information). This page only displays what the city
administration actually published for Kabankalan; it never invents content and
it never offers editing controls to visitors.
"""
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render

from apps.cities.locking import LOCKED_CITY_PK, locked_city
from apps.cities.models import City

from apps.places.models import Place

from .directory import DIRECTORY_FILTERS, DIRECTORY_SECTIONS
from .models import CityInformation


def city_information(request):
    """List the published City Information entries for Kabankalan."""
    city = locked_city() or City.objects.filter(pk=LOCKED_CITY_PK).first()
    if city is None:
        entries = CityInformation.objects.none()
    else:
        entries = CityInformation.objects.filter(city=city, is_published=True)

    # Type filter (one of the published categories).
    selected_type = (request.GET.get("type") or "").strip()
    valid_types = {value for value, _ in CityInformation.InfoType.choices}
    if selected_type not in valid_types:
        selected_type = ""

    # Free text filter over the published title and description.
    search_query = (request.GET.get("q") or "").strip()[:100]
    if search_query:
        entries = entries.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    if selected_type:
        entries = entries.filter(info_type=selected_type)

    published = list(entries.order_by("info_type", "order", "pk"))

    grouped = []
    for info_type, label in CityInformation.InfoType.choices:
        items = [entry for entry in published if entry.info_type == info_type]
        if items:
            grouped.append({"type": info_type, "label": label, "items": items})

    # The type chips always show the total number of published entries, even
    # while a search or another type is active.
    if city is None:
        type_counts = {}
    else:
        type_counts = {
            row["info_type"]: row["total"]
            for row in CityInformation.objects.filter(city=city, is_published=True)
            .values("info_type")
            .annotate(total=Count("id"))
        }
    type_links = [
        {
            "type": info_type,
            "label": label,
            "count": type_counts.get(info_type, 0),
            "active": info_type == selected_type,
        }
        for info_type, label in CityInformation.InfoType.choices
    ]

    # The City Information directory reuses the original Place rows; it does
    # not copy, move, retag, or publish records. Old ?type= links continue to
    # address staff-authored city guides.
    valid_sections = {value for value, _ in DIRECTORY_SECTIONS}
    section = (request.GET.get("directory") or "").strip()
    if section not in valid_sections:
        section = "guides" if selected_type else "all"
    show_guides = section in ("all", "guides")
    show_places = section != "guides"
    directory_links = []
    for value, label in DIRECTORY_SECTIONS:
        params = {}
        if value != "all":
            params["directory"] = value
        if search_query:
            params["q"] = search_query
        url = "?" + urlencode(params) if params else request.path
        directory_links.append({"value": value, "label": label, "url": url, "active": value == section})

    if city is None:
        directory_places = Place.objects.none()
    else:
        directory_places = Place.objects.filter(city=city, is_active=True, is_verified=True)
    if search_query:
        directory_places = directory_places.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
            | Q(address__icontains=search_query) | Q(category__name__icontains=search_query)
        )
    if section in DIRECTORY_FILTERS:
        directory_places = directory_places.filter(DIRECTORY_FILTERS[section])
    directory_places = directory_places.select_related("category").prefetch_related("hobbies").order_by("title", "pk")
    page_number = request.GET.get("page", "1")
    if not page_number.isascii() or not page_number.isdecimal() or len(page_number) > 9:
        page_number = "1"
    place_page = Paginator(directory_places, 24).get_page(page_number) if show_places else None

    def page_link(number):
        params = {"page": number}
        if section != "all":
            params["directory"] = section
        if search_query:
            params["q"] = search_query
        return "?" + urlencode(params)

    previous_page_url = page_link(place_page.previous_page_number()) if place_page and place_page.has_previous() else ""
    next_page_url = page_link(place_page.next_page_number()) if place_page and place_page.has_next() else ""

    return render(
        request,
        "info/city_information.html",
        {
            "directory_links": directory_links,
            "selected_directory": section,
            "directory_label": dict(DIRECTORY_SECTIONS)[section],
            "show_guides": show_guides,
            "show_places": show_places,
            "place_page": place_page,
            "previous_page_url": previous_page_url,
            "next_page_url": next_page_url,
            "selected_city": city,
            "grouped_entries": grouped,
            "entry_count": len(published),
            "total_count": sum(type_counts.values()),
            "type_links": type_links,
            "selected_type": selected_type,
            "search_query": search_query,
        },
    )
