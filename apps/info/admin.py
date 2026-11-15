
from django.contrib import admin
from django.contrib import messages

from .models import (
    CityInformation,
    RecommendationRating,
    QueryLog,
)


@admin.register(CityInformation)
class CityInformationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "city",
        "info_type",
        "is_published",
        "order",
        "created_at",
    )
    list_filter = ("city", "info_type", "is_published")
    search_fields = ("title", "description", "city__name")
    ordering = ("city", "info_type", "order")
    actions = ("publish_selected", "unpublish_selected")

    def get_exclude(self, request, obj=None):
        # Some local versions have dedicated license model fields; do not show
        # them in the form, and do not delete their saved values on normal edits.
        excluded = list(super().get_exclude(request, obj) or ())
        fields = {field.name for field in self.model._meta.concrete_fields}
        for name in ("photo_license", "photo_license_url"):
            if name in fields and name not in excluded:
                excluded.append(name)
        return tuple(excluded)

    def save_model(self, request, obj, form, change):
        # Only a replacement makes the previous image's license inapplicable.
        if change and "thumbnail_url" in form.changed_data:
            fields = {field.name for field in self.model._meta.concrete_fields}
            for name in ("photo_license", "photo_license_url"):
                if name in fields:
                    setattr(obj, name, "")
        super().save_model(request, obj, form, change)

    @admin.action(description="Publish the selected City Information entries")
    def publish_selected(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(
            request,
            f"{count} City Information entr{'y' if count == 1 else 'ies'} published.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Unpublish the selected City Information entries")
    def unpublish_selected(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(
            request,
            f"{count} City Information entr{'y' if count == 1 else 'ies'} unpublished.",
            level=messages.SUCCESS,
        )


@admin.register(RecommendationRating)
class RecommendationRatingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "place",
        "user",
        "rating",
        "created_at",
    )
    list_filter = ("rating", "created_at")
    search_fields = ("place__name", "query_text")


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "matched_count",
        "created_at",
    )
    search_fields = ("raw_query",)
    readonly_fields = ("created_at",)
