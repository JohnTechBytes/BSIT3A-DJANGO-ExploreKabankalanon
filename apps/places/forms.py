# ExploreAnywhere Phase 4E.3 - Kabankalan destination editing checks.
# This admin-only form does not change database models or migrations.
from django import forms
import re
from .models import Place

OSM_SLUG = re.compile(r"^osm-(node|way|relation)-(\d+)$")


class KabankalanPlaceAdminForm(forms.ModelForm):
    coordinates_confirmed = forms.BooleanField(
        required=False,
        label="I checked these coordinates against a reliable map/source",
        help_text=(
            "Required when changing coordinates OR first verifying/publishing an "
            "OSM-imported business. Do not rely only on a crowdsourced map pin."
        ),
    )
    osm_review_confirmed = forms.BooleanField(
        required=False,
        label="I independently verified this imported business and its location",
        help_text="Required when marking an OSM-imported business verified or active.",
    )
    osm_review_notes = forms.CharField(
        required=False, max_length=500,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Evidence, source and date (do not use OSM alone)"}),
        label="Independent verification evidence and date",
    )

    class Meta:
        model = Place
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()

        # A city-locked admin must not accept posted city IDs for other places.
        city = cleaned.get("city")
        if city is not None and city.pk != 2:
            self.add_error("city", "This manager only publishes Kabankalan City destinations.")
        if self.instance.pk and self.instance.city_id != 2:
            raise forms.ValidationError("This destination does not belong to Kabankalan City.")

        # A staged OpenStreetMap listing is not verified just because OSM has
        # a name and coordinate. Native admin must enforce a human review for
        # every transition to verified or published status.
        is_osm = self.instance.pk and OSM_SLUG.fullmatch(self.instance.slug or "")
        if not self.instance.pk and OSM_SLUG.fullmatch(cleaned.get("slug") or ""):
            self.add_error("slug", "Stage OSM source IDs via the import command, not Add Place.")
        if is_osm:
            verified = bool(cleaned.get("is_verified"))
            active = bool(cleaned.get("is_active"))
            if active and not verified:
                self.add_error("is_verified", "Imported businesses cannot become active until independently verified.")
            reviewing_now = (
                (verified and not self.instance.is_verified) or
                (active and not self.instance.is_active)
            )
            if reviewing_now:
                if not cleaned.get("osm_review_confirmed"):
                    self.add_error("osm_review_confirmed", "Confirm independent business and location verification.")
                if len((cleaned.get("osm_review_notes") or "").strip()) < 15:
                    self.add_error("osm_review_notes", "Record meaningful independent evidence, source and date (at least 15 characters).")
                if cleaned.get("category") is None:
                    self.add_error("category", "Choose the verified business category before approval.")
                if cleaned.get("latitude") is None or cleaned.get("longitude") is None:
                    self.add_error("latitude", "Nearby businesses need independently verified coordinates.")
                elif not cleaned.get("coordinates_confirmed"):
                    self.add_error("coordinates_confirmed", "Confirm independent map/location checking before publishing an OSM business.")

        latitude = cleaned.get("latitude")
        longitude = cleaned.get("longitude")
        if (latitude is None) != (longitude is None):
            message = "Enter both latitude and longitude, or leave both blank."
            self.add_error("latitude" if latitude is None else "longitude", message)
        else:
            if latitude is not None and not (-90 <= latitude <= 90):
                self.add_error("latitude", "Latitude must be between -90 and 90.")
            if longitude is not None and not (-180 <= longitude <= 180):
                self.add_error("longitude", "Longitude must be between -180 and 180.")
            if (
                latitude is not None
                and longitude is not None
                and ("latitude" in self.changed_data or "longitude" in self.changed_data)
                and not cleaned.get("coordinates_confirmed")
            ):
                self.add_error(
                    "coordinates_confirmed",
                    "Confirm that you independently checked the location before saving new coordinates.",
                )

        has_photo = bool(cleaned.get("cover_image") or cleaned.get("cover_image_url"))
        changed_photo = "cover_image" in self.changed_data or "cover_image_url" in self.changed_data
        # Legacy images can still have missing credits: don't block unrelated
        # edits, but ensure newly changed cover photos carry basic attribution.
        if has_photo and changed_photo:
            if not (cleaned.get("photo_credit") or "").strip():
                self.add_error("photo_credit", "Add the photographer/owner attribution for this cover photo.")
            if cleaned.get("cover_image_url") and not (cleaned.get("photo_source_url") or "").strip():
                self.add_error("photo_source_url", "External cover photos need a traceable source URL.")

        return cleaned
