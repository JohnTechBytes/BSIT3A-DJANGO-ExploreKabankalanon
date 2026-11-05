# ExploreAnywhere Phase 4E.3 - Kabankalan City Destination Manager.
# Existing Place data, models, migrations and visitor routes are not modified.
from django.contrib import admin, messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
import re
from difflib import SequenceMatcher
from math import asin, cos, radians, sin, sqrt

from apps.cities.models import City
from .forms import KabankalanPlaceAdminForm
from .models import OpeningHours, Place, PlacePhoto

KABANKALAN_CITY_ID = 2
# Wikimedia lookups are volunteer-run; keep each action run small.
MAX_PHOTO_LOOKUPS = 40
OSM_SLUG = re.compile(r"^osm-(node|way|relation)-(\d+)$")


def _business_name_key(title):
    """Normalize case, punctuation and ampersands for reviewer-only warnings."""
    return " ".join(re.findall(r"[a-z0-9]+", (title or "").casefold().replace("&", " and ")))


def _pin_distance_meters(first, second):
    """Great-circle distance between two *mapped*, not necessarily verified, pins."""
    if any(value is None for value in (
        first.latitude, first.longitude, second.latitude, second.longitude
    )):
        return None
    lat_a, lon_a = radians(float(first.latitude)), radians(float(first.longitude))
    lat_b, lon_b = radians(float(second.latitude)), radians(float(second.longitude))
    delta_lat, delta_lon = lat_b - lat_a, lon_b - lon_a
    h = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
    return 12742000 * asin(min(1.0, sqrt(max(0.0, h))))


def _duplicate_review_hints(page_places):
    """Add non-destructive possible-match flags; never change publication state.

    Exact normalized names are candidates even without pins. Similar names
    require pins within 150 m; two unrelated shops sharing a building are NOT
    flagged based on coordinates alone. Limits keep comparisons cheap in admin.
    """
    # Only the Kabankalan subset is needed, not the 7,000+ nationwide places.
    existing = list(Place.objects.filter(city_id=KABANKALAN_CITY_ID).only(
        "id", "title", "latitude", "longitude"
    ))
    keyed = [(candidate, _business_name_key(candidate.title)) for candidate in existing]
    for place in page_places:
        name = _business_name_key(place.title)
        matches = []
        if len(name) >= 4:
            for other, other_name in keyed:
                if other.pk == place.pk or len(other_name) < 4:
                    continue
                if name == other_name:
                    reason = "Same normalized name (may be another branch)"
                elif SequenceMatcher(None, name, other_name).ratio() >= 0.84:
                    distance = _pin_distance_meters(place, other)
                    if distance is None or distance > 150:
                        continue
                    reason = "Similar name; mapped pins within 150 m"
                else:
                    continue
                matches.append({"name": other.title, "reason": reason})
                if len(matches) == 3:
                    break
        place.osm_possible_matches = matches


def _photo_url(obj):
    if obj.cover_image:
        try:
            return obj.cover_image.url
        except ValueError:
            return ""
    return obj.cover_image_url or ""


def _content_gaps(obj):
    issues = []
    if not (obj.description or "").strip():
        issues.append("Description")
    if not _photo_url(obj):
        issues.append("Genuine cover photo")
    elif not (obj.photo_credit or "").strip() or not (obj.photo_license or "").strip():
        issues.append("Photo attribution/license")
    if obj.latitude is None or obj.longitude is None:
        issues.append("Verified coordinates")
    if not obj.hobbies.exists():
        issues.append("Hobby associations")
    return issues


class PlacePhotoInline(admin.StackedInline):
    model = PlacePhoto
    extra = 0
    fields = ("image", "image_url", "caption", "order", "photo_preview")
    readonly_fields = ("photo_preview",)
    verbose_name_plural = (
        "Destination gallery photos (include source, credit and license "
        "in caption: this gallery model has no dedicated rights fields)"
    )

    @admin.display(description="Gallery preview")
    def photo_preview(self, obj):
        if not obj.pk:
            return "A preview appears after saving the photo."
        try:
            url = obj.image.url if obj.image else obj.image_url
        except ValueError:
            url = ""
        if not url:
            return "No photo supplied."
        return format_html(
            '<img src="{}" alt="Gallery photo preview" '
            'style="max-width:240px;max-height:130px;object-fit:cover;border-radius:8px;">',
            url,
        )


class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours
    extra = 0
    fields = ("weekday", "open_time", "close_time", "is_closed")


class HobbyAssignmentFilter(admin.SimpleListFilter):
    """Help staff review missing tags without claiming those places are irrelevant."""
    title = "Hobby tags"
    parameter_name = "hobby_assignment"

    def lookups(self, request, model_admin):
        return (("missing", "No hobbies assigned (review)"), ("assigned", "Has hobby tags"))

    def queryset(self, request, queryset):
        if self.value() == "missing":
            return queryset.filter(hobbies__isnull=True)
        if self.value() == "assigned":
            return queryset.filter(hobbies__isnull=False).distinct()
        return queryset


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    form = KabankalanPlaceAdminForm
    inlines = (PlacePhotoInline, OpeningHoursInline)
    filter_horizontal = ("hobbies",)

    # Phase 5D.2: a compact, readable table; hobbies are displayed beneath the title.
    change_list_template = "admin/places/place/change_list.html"
    change_form_template = "admin/places/place/change_form.html"
    list_display = (
        "destination_label", "category", "publication", "content_status",
        "has_image", "has_map_pin", "review_count",
    )
    list_display_links = ("destination_label",)
    list_filter = ("is_verified", "is_active", "category", HobbyAssignmentFilter)
    search_fields = (
        "title", "slug", "description", "address", "barangay",
        "category__name", "hobbies__name",
    )
    list_select_related = ("city", "category")
    list_per_page = 25
    readonly_fields = (
        "cover_preview", "content_checklist", "avg_rating",
        "review_count", "created_at", "updated_at",
    )
    fieldsets = (
        ("Kabankalan Destination Information", {
            "fields": ("title", "slug", "city", "category", "hobbies", "description"),
            "description": "Use verified destination details. Match hobbies to actual activities.",
        }),
        ("Address & Verified Map Location", {
            "fields": (
                "address", "barangay", "latitude", "longitude", "coordinates_confirmed",
            ),
            "description": "Missing coordinates are allowed. Verify new coordinates from a reliable source before saving.",
        }),
        ("Genuine Cover Photo & Rights", {
            "fields": (
                "cover_image", "cover_image_url", "cover_preview", "photo_credit",
                "photo_source_url", "photo_license", "photo_license_url",
            ),
            "description": "Use actual destination photography with permission. Never label sample or unrelated images as the destination.",
        }),
        ("Content Completeness", {
            "fields": ("content_checklist",),
            "description": "Warnings do not invent missing records or stop edits to legacy entries.",
        }),
        ("Contact Information", {
            "fields": ("phone", "website", "email"),
            "classes": ("collapse",),
        }),
        ("Publication Controls", {
            "fields": ("is_verified", "is_active"),
        }),
        ("Administrative Details", {
            "fields": (
                "owner", "avg_rating", "review_count", "created_at", "updated_at",
            ),
            "classes": ("collapse",),
        }),
    )
    actions = ("approve_selected", "unpublish_selected",
               "preview_commons_photos", "attach_commons_photos")

    def get_urls(self):
        # Before Django's object routes: a permission-protected GET-only queue.
        custom = [
            path(
                "osm-review/",
                self.admin_site.admin_view(self.osm_review_view),
                name="places_place_osm_review",
            ),
        ]
        return custom + super().get_urls()

    def osm_review_view(self, request):
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied
        if request.method != "GET":
            raise PermissionDenied

        all_osm = Place.objects.filter(
            city_id=KABANKALAN_CITY_ID, slug__startswith="osm-"
        )
        status_counts = {
            "total": all_osm.count(),
            "pending": all_osm.filter(is_verified=False, is_active=False).count(),
            "ready": all_osm.filter(is_verified=True, is_active=False).count(),
            "published": all_osm.filter(is_verified=True, is_active=True).count(),
        }
        status = request.GET.get("status", "pending")
        if status not in ("pending", "ready", "published", "all"):
            status = "pending"
        results = all_osm
        if status == "pending":
            results = results.filter(is_verified=False, is_active=False)
        elif status == "ready":
            results = results.filter(is_verified=True, is_active=False)
        elif status == "published":
            results = results.filter(is_verified=True, is_active=True)

        query = (request.GET.get("q") or "").strip()[:120]
        if query:
            results = results.filter(
                Q(title__icontains=query) | Q(slug__icontains=query)
                | Q(address__icontains=query) | Q(category__name__icontains=query)
            )
        category = (request.GET.get("category") or "").strip()
        if category.isdecimal() and len(category) <= 10:
            results = results.filter(category_id=int(category))
        else:
            category = ""

        map_status = (request.GET.get("map") or "all").strip()
        if map_status == "missing":
            results = results.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
        elif map_status == "mapped":
            results = results.filter(latitude__isnull=False, longitude__isnull=False)
        else:
            map_status = "all"

        categories = list(
            all_osm.exclude(category__isnull=True)
            .values("category_id", "category__name")
            .distinct().order_by("category__name")
        )
        for item in categories:
            item["selected"] = str(item["category_id"]) == category
        page = Paginator(
            results.select_related("category").order_by("-created_at", "pk"), 25
        ).get_page(request.GET.get("page"))
        _duplicate_review_hints(page.object_list)
        for place in page.object_list:
            matched = OSM_SLUG.fullmatch(place.slug or "")
            place.osm_review_url = (
                f"https://www.openstreetmap.org/{matched.group(1)}/{matched.group(2)}"
                if matched else ""
            )
            place.osm_admin_status = (
                "Published" if place.is_verified and place.is_active else
                "Verified / unpublished" if place.is_verified else
                "Active / unverified" if place.is_active else "Needs verification"
            )
            place.osm_review_change_url = reverse(
                "admin:places_place_change", args=[place.pk]
            )
        context = {
            **self.admin_site.each_context(request),
            "title": "Business verification queue",
            "opts": self.model._meta,
            "status_counts": status_counts,
            "status": status,
            "query": query,
            "category": category,
            "categories": categories,
            "map_status": map_status,
            "page_obj": page,
            "can_change": self.has_change_permission(request),
        }
        request.current_app = self.admin_site.name
        return TemplateResponse(request, "admin/places/place/osm_review.html", context)

    def get_fieldsets(self, request, obj=None):
        # Keep the original Destination Manager exactly as it is.  Imported
        # OSM businesses use a simpler, task-focused arrangement of the SAME
        # fields.  Validation remains in KabankalanPlaceAdminForm.clean().
        fields = tuple(super().get_fieldsets(request, obj))
        if obj is None or not OSM_SLUG.fullmatch(obj.slug or ""):
            return fields

        return (
            ("1 · Business identity and location", {
                "fields": (
                    "title", "slug", "city", "category", "address", "barangay",
                    "latitude", "longitude", "coordinates_confirmed",
                ),
                "description": (
                    "Confirm the business exists, is currently operating and is "
                    "physically within Kabankalan. The imported OSM coordinates "
                    "are leads, NOT independent proof of location."
                ),
            }),
            ("2 · Independent review and publication", {
                "fields": (
                    "osm_source_link", "osm_review_confirmed", "osm_review_notes",
                    "is_verified", "is_active",
                ),
                "description": (
                    "Check an independent source or visit, record evidence and the "
                    "verification date, then change the status only when the facts "
                    "are confirmed. OSM alone is insufficient. Form validation "
                    "prevents unverified publication; evidence is logged in Admin History."
                ),
            }),
            ("3 · Public listing details", {
                "fields": ("description", "hobbies"),
                "description": (
                    "Write only confirmed information and select hobbies that "
                    "really fit this establishment. Missing details may be left blank."
                ),
            }),
            ("Content readiness", {
                "fields": ("content_checklist",),
                "description": "Review missing description, photo, hobby and map details.",
            }),
            ("Contact information · optional", {
                "fields": ("phone", "website", "email"),
                "classes": ("collapse",),
            }),
            ("Genuine cover photo and rights · optional", {
                "fields": (
                    "cover_image", "cover_image_url", "cover_preview", "photo_credit",
                    "photo_source_url", "photo_license", "photo_license_url",
                ),
                "classes": ("collapse",),
                "description": (
                    "Use authentic photographs only with permission and proper "
                    "attribution. Do not copy OSM map images into cover photos."
                ),
            }),
            ("Administrative details · optional", {
                "fields": (
                    "owner", "avg_rating", "review_count", "created_at", "updated_at",
                ),
                "classes": ("collapse",),
            }),
        )

    @admin.display(description="OpenStreetMap source")
    def osm_source_link(self, obj):
        matched = OSM_SLUG.fullmatch((obj.slug or "") if obj else "")
        if not matched:
            return "No OSM source reference"
        source = f"https://www.openstreetmap.org/{matched.group(1)}/{matched.group(2)}"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">'
            'View mapped source record (not independent verification) ↗</a>', source,
        )

    def log_change(self, request, obj, message):
        # Store reviewer-supplied evidence in native Django Admin History.
        # No additional database model or migration required.
        note = getattr(request, "_ea_osm_review_note", "")
        if note and OSM_SLUG.fullmatch(obj.slug or ""):
            if isinstance(message, list):
                message = list(message) + [
                    {"changed": {"fields": ["OSM verification evidence: " + note]}}
                ]
            else:
                message = str(message) + " OSM verification evidence: " + note
        return super().log_change(request, obj, message)

    def changelist_view(self, request, extra_context=None):
        # HTML select controls submit empty values for "All". Django's native
        # list filters expect absent parameters, not empty exact-lookups.
        # Strip only these empty filter inputs before passing to native admin.
        filter_keys = ("category__id__exact", "is_verified__exact", "is_active__exact")
        if any(key in request.GET and not request.GET.get(key) for key in filter_keys):
            cleaned_query = request.GET.copy()
            for key in filter_keys:
                if key in cleaned_query and not cleaned_query.get(key):
                    cleaned_query.pop(key)
            request.GET = cleaned_query
        # The native admin filter back end remains in control. Only the visual
        # controls are compacted; every category is sourced from Kabankalan rows.
        selected_category = request.GET.get("category__id__exact", "")
        rows = (
            self.get_queryset(request)
            .exclude(category__isnull=True)
            .values("category_id", "category__name")
            .distinct()
            .order_by("category__name")
        )
        categories = [
            {
                "id": str(row["category_id"]),
                "name": row["category__name"],
                "selected": str(row["category_id"]) == selected_category,
            }
            for row in rows
        ]
        selected = {
            "query": request.GET.get("q", ""),
            "category": selected_category,
            "verified": request.GET.get("is_verified__exact", ""),
            "active": request.GET.get("is_active__exact", ""),
            "hobby_assignment": request.GET.get("hobby_assignment", ""),
            "categories": categories,
        }
        extra_context = dict(extra_context or {})
        extra_context["ea_filters"] = selected
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description="Destination", ordering="title")
    def destination_label(self, obj):
        hobbies = ", ".join(h.name for h in obj.hobbies.all())
        return format_html(
            '<span style="display:block;font-weight:750;color:#143b67">{}</span>'
            '<small style="display:block;color:#66819c;margin-top:3px">{}</small>',
            obj.title, hobbies or "No hobbies assigned",
        )

    def get_queryset(self, request):
        # Older nationwide rows remain in the database, but are not managed
        # from the Kabankalan-only Place admin.
        queryset = (
            super().get_queryset(request)
            .filter(city_id=KABANKALAN_CITY_ID)
            .prefetch_related("hobbies")
        )
        # Hide only *unverified OSM imports* from the normal destination list.
        # Review/edit URLs still see them, and independently verified OSM
        # businesses return to the destination list when verified.
        if getattr(getattr(request, "resolver_match", None), "url_name", "") == "places_place_changelist":
            queryset = queryset.exclude(slug__startswith="osm-", is_verified=False)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "city":
            kwargs["queryset"] = City.objects.filter(pk=KABANKALAN_CITY_ID)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["city"] = KABANKALAN_CITY_ID
        return initial

    def get_readonly_fields(self, request, obj=None):
        fields = tuple(super().get_readonly_fields(request, obj))
        if obj is not None and OSM_SLUG.fullmatch(obj.slug or ""):
            fields += ("slug", "osm_source_link")
        return fields + (("city",) if obj is not None else ())

    def save_model(self, request, obj, form, change):
        obj.city_id = KABANKALAN_CITY_ID
        if obj.pk and OSM_SLUG.fullmatch(obj.slug or ""):
            if (form.cleaned_data.get("osm_review_notes")
                    and ("is_verified" in form.changed_data or "is_active" in form.changed_data)
                    and form.cleaned_data.get("osm_review_confirmed")):
                request._ea_osm_review_note = form.cleaned_data["osm_review_notes"].strip()
        super().save_model(request, obj, form, change)

    def has_view_permission(self, request, obj=None):
        if obj is not None and obj.city_id != KABANKALAN_CITY_ID:
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.city_id != KABANKALAN_CITY_ID:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.city_id != KABANKALAN_CITY_ID:
            return False
        return super().has_delete_permission(request, obj)

    @admin.display(description="Publication")
    def publication(self, obj):
        if obj.is_active and obj.is_verified:
            return format_html('<span style="color:#11753d;font-weight:700">Published</span>')
        if obj.is_active:
            return "Active · Not verified"
        return "Not published"

    @admin.display(description="Content completeness")
    def content_status(self, obj):
        gaps = _content_gaps(obj)
        if not gaps:
            return format_html('<span style="color:#11753d;font-weight:700">Ready</span>')
        return format_html(
            '<span title="{}" style="color:#9b5500;font-weight:600">{} missing</span>',
            ", ".join(gaps), len(gaps),
        )

    @admin.display(description="Cover photo")
    def has_image(self, obj):
        # Cover presence only; photo permissions are checked separately.
        if _photo_url(obj):
            return format_html('<span class="ea-dest-state ea-dest-good">{}</span>', 'Cover set')
        return format_html('<span class="ea-dest-state ea-dest-warn">{}</span>', 'No photo')

    @admin.display(description="Map")
    def has_map_pin(self, obj):
        if obj.latitude is not None and obj.longitude is not None:
            return format_html('<span class="ea-dest-state ea-dest-good">{}</span>', 'Has pin')
        return format_html('<span class="ea-dest-state ea-dest-warn">{}</span>', 'No pin')

    @admin.display(description="Hobbies")
    def hobby_labels(self, obj):
        values = [h.name for h in obj.hobbies.all()]
        return ", ".join(values) if values else "Not assigned"

    @admin.display(description="Cover image preview")
    def cover_preview(self, obj):
        if not obj or not obj.pk:
            return "Upload a genuine image or enter a verified cover image URL."
        url = _photo_url(obj)
        if not url:
            return "No genuine cover photo has been recorded."
        return format_html(
            '<img src="{}" alt="Destination cover preview" '
            'style="width:300px;max-width:100%;max-height:180px;object-fit:cover;border-radius:10px;">',
            url,
        )

    @admin.display(description="Missing information")
    def content_checklist(self, obj):
        if not obj or not obj.pk:
            return "Save the destination to check photo, description, map, and hobby coverage."
        issues = _content_gaps(obj)
        if not issues:
            return format_html('<strong style="color:#11753d">All content checks passed.</strong>')
        items = format_html_join("", "<li>{}</li>", ((item,) for item in issues))
        return format_html(
            '<div style="color:#9b5500"><strong>Still needed:</strong><ul>{}</ul></div>',
            items,
        )

    # ------------------------------------------------------------------
    # Licensed photo lookup (Wikimedia Commons)
    # ------------------------------------------------------------------
    def _commons_helpers(self):
        from apps.places.management.commands.phase6o_search_commons import (
            commons_search, searches_for,
        )
        return commons_search, searches_for

    def _photo_targets(self, queryset):
        published = queryset.filter(city_id=KABANKALAN_CITY_ID, is_verified=True, is_active=True)
        return list(published.order_by("title")[:MAX_PHOTO_LOOKUPS])

    @admin.action(description="Check Wikimedia Commons for a licensed photo (no changes)")
    def preview_commons_photos(self, request, queryset):
        from . import photo_enrichment

        if not photo_enrichment.user_agent():
            self.message_user(
                request,
                "Set WIKIMEDIA_USER_AGENT (app name + contact email) before asking Wikimedia. "
                "Nothing was changed.",
                messages.ERROR,
            )
            return

        commons_search, searches_for = self._commons_helpers()
        targets = self._photo_targets(queryset)
        matched, unmatched = [], []
        for place in targets:
            candidate, reason = photo_enrichment.find_photo(
                place, search=commons_search, queries_for=searches_for)
            if candidate:
                matched.append(f"{place.title} → {candidate.get('file_title', '')}")
            else:
                unmatched.append(f"{place.title} ({reason})")

        if matched:
            self.message_user(
                request,
                f"{len(matched)} of {len(targets)} destination(s) have a licensed, name-matched photo. "
                "Run “Attach Wikimedia Commons photos” to use them. Preview only, nothing was saved.",
                messages.SUCCESS,
            )
            self.message_user(request, " · ".join(matched[:10]) + (" …" if len(matched) > 10 else ""),
                              messages.INFO)
        if unmatched:
            self.message_user(
                request,
                f"{len(unmatched)} destination(s) had no confident match: "
                + " · ".join(unmatched[:8]) + (" …" if len(unmatched) > 8 else ""),
                messages.WARNING,
            )

    @admin.action(description="Attach Wikimedia Commons photos (licensed name matches only)")
    def attach_commons_photos(self, request, queryset):
        from . import photo_enrichment

        if not photo_enrichment.user_agent():
            self.message_user(
                request,
                "Set WIKIMEDIA_USER_AGENT (app name + contact email) before asking Wikimedia. "
                "Nothing was changed.",
                messages.ERROR,
            )
            return

        commons_search, searches_for = self._commons_helpers()
        targets = self._photo_targets(queryset)
        attached, skipped, unmatched = 0, 0, []
        for place in targets:
            if place.cover_image or place.cover_image_url:
                skipped += 1
                continue
            candidate, reason = photo_enrichment.find_photo(
                place, search=commons_search, queries_for=searches_for)
            if not candidate:
                unmatched.append(f"{place.title} ({reason})")
                continue
            photo_enrichment.apply_photo(place, candidate)
            attached += 1

        if attached:
            self.message_user(
                request,
                f"Attached {attached} licensed photo(s) with credit and licence. "
                "Review each record before publishing.",
                messages.SUCCESS,
            )
        if skipped:
            self.message_user(request, f"{skipped} destination(s) already had a photo and were left alone.",
                              messages.INFO)
        if unmatched:
            self.message_user(
                request,
                f"{len(unmatched)} destination(s) had no confident match: "
                + " · ".join(unmatched[:8]) + (" …" if len(unmatched) > 8 else ""),
                messages.WARNING,
            )

    @admin.action(description="Approve and publish selected Kabankalan destinations")
    def approve_selected(self, request, queryset):
        # Bulk approval is NOT an acceptable verification path for OSM
        # imports. They must be reviewed one at a time with evidence notes.
        selected = queryset.filter(city_id=KABANKALAN_CITY_ID)
        excluded = selected.filter(slug__startswith="osm-").count()
        count = selected.exclude(slug__startswith="osm-").update(
            is_verified=True, is_active=True,
        )
        if excluded:
            self.message_user(
                request,
                f"{excluded} imported OSM record(s) skipped: open the Business "
                "verification queue and review each record individually.",
                level=messages.WARNING,
            )
        self.message_user(
            request, f"{count} existing Kabankalan destinations approved and published. "
            "Check content-completeness warnings before sharing a destination.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Unpublish selected Kabankalan destinations")
    def unpublish_selected(self, request, queryset):
        count = queryset.filter(city_id=KABANKALAN_CITY_ID).update(is_active=False)
        self.message_user(
            request, f"{count} Kabankalan destinations unpublished.",
            level=messages.SUCCESS,
        )
