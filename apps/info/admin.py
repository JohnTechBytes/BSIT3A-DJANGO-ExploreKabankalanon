
from django.contrib import admin
from django.contrib import messages

from .models import (
    CityInformation,
    SusResponse,
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


@admin.register(SusResponse)
class SusResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "score", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("score", "created_at")


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
