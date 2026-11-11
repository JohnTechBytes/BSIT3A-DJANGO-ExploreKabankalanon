"""Permission-aware, read-only ExploreAnywhere admin overview metrics."""
from django import template
from django.db.models import Q

register = template.Library()


@register.simple_tag(takes_context=True)
def ea_admin_summary(context):
    result = {
        "published": None,
        "missing_photos": None,
        "users": None,
    }
    request = context.get("request")
    if not request or not request.user.is_active or not request.user.is_staff:
        return result

    if request.user.has_perm("places.view_place") or request.user.has_perm("places.change_place"):
        from apps.places.models import Place
        places = Place.objects.filter(city_id=2)
        result["published"] = places.filter(is_verified=True, is_active=True).count()
        result["missing_photos"] = places.filter(
            (Q(cover_image__isnull=True) | Q(cover_image=""))
            & (Q(cover_image_url__isnull=True) | Q(cover_image_url=""))
        ).count()

    # The active user model is apps.users.User, so the matching permissions
    # live under the "users" app label (not "auth").
    if request.user.has_perm("users.view_user") or request.user.has_perm("users.change_user"):
        from django.contrib.auth import get_user_model
        result["users"] = get_user_model().objects.count()

    return result
