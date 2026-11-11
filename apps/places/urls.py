from django.urls import path
from . import views, journey_views, review_views, nearby, relevance_views
from .photo_preview import admin_photo_preview
from .city_discovery import city_discover

app_name = "places"

urlpatterns = [
    path("", views.attraction_carousel, name="attraction_carousel"),
    path("nearby/", nearby.nearby_places, name="nearby_places"),
    path("smart-search/", nearby.smart_search, name="smart_search"),
    path("admin-photo-preview/", admin_photo_preview, name="admin_photo_preview"),
    path("discover/", city_discover, name="city_discover"),
    path("<int:pk>/", views.place_detail, name="place_detail"),
    # ExploreAnywhere phase3 save-and-journey v1
    # ExploreAnywhere phase3e reviews v1
    path("my-reviews/", review_views.my_reviews, name="my_reviews"),
    path("<int:pk>/review/", review_views.submit_review, name="submit_review"),
    path("<int:pk>/review/delete/", review_views.delete_review, name="delete_review"),
    path("<int:pk>/relevance/", relevance_views.rate_relevance, name="rate_relevance"),
    path("saved/", journey_views.saved_places, name="saved_places"),
    path("<int:pk>/save/", journey_views.save_place, name="save_place"),
    path("<int:pk>/unsave/", journey_views.unsave_place, name="unsave_place"),
]
