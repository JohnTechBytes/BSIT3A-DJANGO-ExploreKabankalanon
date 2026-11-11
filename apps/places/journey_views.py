"""Saved-place actions.

All public place collections are restricted to verified, active Kabankalan places.
Saving and unsaving use POST + CSRF, with data scoped to the current user.
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Place, SavedPlace
from .sample_images import sample_image_for

KABANKALAN_CITY_ID = 2


def _public_places():
    return Place.objects.filter(
        city_id=KABANKALAN_CITY_ID,
        is_verified=True,
        is_active=True,
    )


@login_required
@require_POST
def save_place(request, pk):
    place = get_object_or_404(_public_places(), pk=pk)
    SavedPlace.objects.get_or_create(user=request.user, place=place)
    return redirect("places:place_detail", pk=place.pk)


@login_required
@require_POST
def unsave_place(request, pk):
    # Allow removing a saved Kabankalan place even if it was unpublished later.
    place = get_object_or_404(Place, pk=pk, city_id=KABANKALAN_CITY_ID)
    SavedPlace.objects.filter(user=request.user, place=place).delete()
    return redirect("places:place_detail", pk=pk) if (
        place.is_active and place.is_verified
    ) else redirect("places:saved_places")


@login_required
def saved_places(request):
    entries = (SavedPlace.objects
        .filter(user=request.user, place__city_id=KABANKALAN_CITY_ID,
                place__is_active=True, place__is_verified=True)
        .select_related("place", "place__category", "place__city")
        .order_by("-created_at"))
    entries = list(entries)
    for entry in entries:
        place = entry.place
        place.sample_image = (sample_image_for(place)
                              if not (place.cover_image or place.cover_image_url) else "")
    return render(request, "places/saved_places.html", {
        "entries": entries,
    })
