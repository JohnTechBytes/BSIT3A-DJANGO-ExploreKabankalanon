"""Presentation helpers for clearly labelled, local category illustrations."""
from django import template
from django.templatetags.static import static

from apps.places.sample_images import sample_image_for

register = template.Library()


@register.simple_tag
def sample_photo(place):
    """Return a local category sample, or no image for an unknown category."""
    path = sample_image_for(place)
    return static(path) if path else ""
