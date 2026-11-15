"""Public, read-only City Information guides for Kabankalan.

Staff can still manage all City Information records in the administrative
panel. This page displays only published attraction and event/festival guides;
it does not delete, alter, or unpublish records.
"""
from django.db.models import Count, Q
from django.shortcuts import render

from apps.cities.locking import LOCKED_CITY_PK, locked_city
from apps.cities.models import City

from .models import CityInformation


PUBLIC_TYPES = (CityInformation.InfoType.ATTRACTION, CityInformation.InfoType.EVENT)


def city_information(request):
    """Show published attraction and event guides, optionally searched by text."""
    city = locked_city() or City.objects.filter(pk=LOCKED_CITY_PK).first()
    entries = CityInformation.objects.filter(
        city=city, is_published=True, info_type__in=PUBLIC_TYPES,
    ) if city else CityInformation.objects.none()

    # Old links to the two retained types still work. Other former type and
    # directory parameters are ignored rather than showing the removed content.
    selected_type = (request.GET.get("type") or "").strip()
    if selected_type not in PUBLIC_TYPES:
        selected_type = ""
    search_query = (request.GET.get("q") or "").strip()[:100]

    counts = {
        row["info_type"]: row["total"]
        for row in entries.values("info_type").annotate(total=Count("id"))
    }
    if search_query:
        entries = entries.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    if selected_type:
        entries = entries.filter(info_type=selected_type)

    published = list(entries.order_by("info_type", "order", "pk"))
    public_choices = [(value, label) for value, label in CityInformation.InfoType.choices if value in PUBLIC_TYPES]
    grouped = []
    for info_type, label in public_choices:
        items = [entry for entry in published if entry.info_type == info_type]
        if items:
            grouped.append({"type": info_type, "label": label, "items": items})

    return render(request, "info/city_information.html", {
        "selected_city": city,
        "grouped_entries": grouped,
        "entry_count": len(published),
        "total_count": sum(counts.values()),
        "type_links": [
            {"type": value, "label": label, "count": counts.get(value, 0), "active": value == selected_type}
            for value, label in public_choices
        ],
        "selected_type": selected_type,
        "search_query": search_query,
    })
