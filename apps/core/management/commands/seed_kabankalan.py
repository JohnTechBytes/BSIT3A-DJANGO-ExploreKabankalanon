"""Seed the Kabankalan dataset for a fresh local installation.

The places are the **real** OpenStreetMap attractions of Kabankalan City that
ship with this repository
(``data/osm/validation/attractions_full_adm3_validated.csv``), so a new
installation shows verifiable records instead of invented sample names.

What the command creates:

1. the Kabankalan city row (pk 2 — the id the whole site is locked to),
2. the interest taxonomy (hobbies) and the place categories,
3. the published, verified Kabankalan attractions from the OSM extract.

Running it twice does not duplicate these records, but it is not read-only:
it replaces hobby associations on matching existing places, and assigns the
Photography hobby for categories without a mapped interest. Use only with an
isolated fresh database or after explicit approval and a verified backup.

Usage::

    python manage.py seed_kabankalan
"""
import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.cities.models import City
from apps.core.models import Category, Hobby
from apps.places.management.commands.categorize_osm_places import OSM_CATEGORY_MAP
from apps.places.models import Place

CABANKALAN_CITY_ID = 2

# The interests a visitor can filter by.
HOBBIES = [
    {"name": "Hiking & Eco-Tourism", "icon": "ti-mountain",
     "description": "Nature trails, caves, and scenic mountain views"},
    {"name": "Photography", "icon": "ti-camera",
     "description": "Picturesque landscapes, heritage spots, and aesthetic spots"},
    {"name": "Culture & Heritage", "icon": "ti-building-arch",
     "description": "Museums, churches, monuments, and the city's history"},
    {"name": "Billiards", "icon": "ti-ball-8",
     "description": "Cue sports and pool halls"},
    {"name": "Coffee & Cafe Hopping", "icon": "ti-coffee",
     "description": "Cozy spots for specialty coffee and casual hangouts"},
    {"name": "Dining & Foodie", "icon": "ti-utensils",
     "description": "Local delicacies, chicken inasal, and dining spots"},
    {"name": "Karaoke & Nightlife", "icon": "ti-microphone",
     "description": "KTV bars, live music, and evening entertainment"},
]

# Which interests fit a category.
CATEGORY_HOBBIES = {
    "mountain-peak": ["Hiking & Eco-Tourism", "Photography"],
    "waterfall": ["Hiking & Eco-Tourism", "Photography"],
    "tourist-attraction": ["Hiking & Eco-Tourism", "Photography"],
    "museum": ["Culture & Heritage", "Photography"],
    "scenic-viewpoint": ["Photography", "Hiking & Eco-Tourism"],
    "park": ["Hiking & Eco-Tourism", "Photography"],
    "garden": ["Photography"],
}

FALLBACK_CATEGORY = ("Tourist Attraction", "tourist-attraction")

# The OSM extract with the Kabankalan rows, most specific file first.
SOURCE_FILES = (
    "data/osm/validation/attractions_full_adm3_validated.csv",
    "data/osm/matching/attractions_unique_matched.csv",
)


class Command(BaseCommand):
    help = ("Seeds the Kabankalan city, taxonomy and published OSM places; "
            "replaces hobby tags on matching existing places. Use an isolated fresh "
            "database, or obtain approval and a verified backup first.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            dest="csv",
            default=None,
            help="Optional path to an OSM attractions CSV (defaults to the shipped extract).",
        )

    def _source_path(self, option):
        if option:
            path = Path(option)
            if not path.is_file():
                raise CommandError(f"CSV not found: {path}")
            return path
        base = Path(__file__).resolve().parents[4]
        for relative in SOURCE_FILES:
            candidate = base / relative
            if candidate.is_file():
                return candidate
        raise CommandError(
            "No OSM attractions CSV found. Expected one of: "
            + ", ".join(SOURCE_FILES)
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            "WARNING: This command writes to the database and replaces hobby tags "
            "on matching existing places. Unmapped categories receive a default "
            "Photography tag. Use an isolated fresh database, or obtain approval "
            "and a verified backup first. This warning does not stop the command."
        ))
        self.stdout.write(self.style.WARNING("Seeding Kabankalan..."))

        city, created = City.objects.get_or_create(
            pk=CABANKALAN_CITY_ID,
            defaults={
                "name": "Kabankalan",
                "slug": "kabankalan",
                "province": "Negros Occidental",
                "country": "Philippines",
                "latitude": 9.9889,
                "longitude": 122.8142,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created city {city.name} (pk={city.pk})."))
        else:
            self.stdout.write(f"City {city.name} already exists (pk={city.pk}).")

        hobbies = {}
        for entry in HOBBIES:
            hobby, _ = Hobby.objects.get_or_create(
                slug=slugify(entry["name"]),
                defaults={
                    "name": entry["name"],
                    "icon": entry["icon"],
                    "description": entry["description"],
                },
            )
            hobbies[entry["name"]] = hobby
        self.stdout.write(self.style.SUCCESS(f"Seed {len(hobbies)} hobbies."))

        categories = {}
        for name, slug in set(OSM_CATEGORY_MAP.values()) | {FALLBACK_CATEGORY}:
            category, _ = Category.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )
            categories[slug] = category
        self.stdout.write(self.style.SUCCESS(f"Seed {len(categories)} categories."))

        source = self._source_path(options.get("csv"))
        places = self._load_places(city, categories, hobbies, source)
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed {len(places)} published Kabankalan places from {source.name}."
            )
        )
        self.stdout.write(
            "The OSM records carry no opening hours; add them in the staff dashboard "
            "if you want the \"open now\" badge."
        )

    def _load_places(self, city, categories, hobbies, source):
        places = []
        with source.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if (row.get("city_name") or "").strip().lower() != "kabankalan":
                    continue
                name = (row.get("name") or "").strip()
                if not name:
                    continue

                osm_key = (row.get("category") or "", row.get("subcategory") or "")
                category_name, category_slug = OSM_CATEGORY_MAP.get(
                    osm_key, FALLBACK_CATEGORY
                )
                category = categories.get(category_slug)
                if category is None:
                    category, _ = Category.objects.get_or_create(
                        slug=category_slug, defaults={"name": category_name}
                    )
                    categories[category_slug] = category

                description = (row.get("description") or "").strip()
                if not description:
                    description = (
                        f"{name} is a {category_name.lower()} in Kabankalan City, "
                        "Negros Occidental. The record comes from the OpenStreetMap "
                        "extract that ships with this project."
                    )

                place, _ = Place.objects.get_or_create(
                    city=city,
                    slug=slugify(name),
                    defaults={
                        "title": name,
                        "category": category,
                        "description": description,
                        "address": (row.get("address") or "").strip()
                        or "Kabankalan City, Negros Occidental",
                        "barangay": "",
                        "latitude": row.get("latitude") or None,
                        "longitude": row.get("longitude") or None,
                        "website": (row.get("website") or "").strip(),
                        "is_verified": True,
                        "is_active": True,
                    },
                )
                hobby_names = CATEGORY_HOBBIES.get(category_slug, ["Photography"])
                place.hobbies.set(
                    [hobbies[hobby_name] for hobby_name in hobby_names if hobby_name in hobbies]
                )
                places.append(place)
        return places
