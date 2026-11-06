"""Presentation helpers for clearly labelled, local category illustrations."""
from django import template
from django.templatetags.static import static

from apps.places.sample_images import sample_image_for

register = template.Library()


@register.simple_tag
def sample_photo(place):
    """Return a shared local category or generic illustration."""
    path = sample_image_for(place)
    return static(path) if path else ""
