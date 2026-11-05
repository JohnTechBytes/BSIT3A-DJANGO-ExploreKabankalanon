"""Create a starter set of City Information entries.

The entries describe widely documented, publicly known facts about
Kabankalan City. They are a starting point for a new installation: review and
edit them in the staff dashboard (Admin > City information) so that the public
page matches the official city record. The entries are created **published**,
because they are the curated starter content of the city; unpublish any of
them that should not be public.

    python manage.py seed_city_information           # only when the table is empty
    python manage.py seed_city_information --force   # replace the existing entries
"""
from django.core.management.base import BaseCommand

from apps.cities.locking import LOCKED_CITY_PK, locked_city
from apps.cities.models import City
from apps.info.models import CityInformation

STARTER_ENTRIES = [
    {
        "info_type": CityInformation.InfoType.ATTRACTION,
        "title": "City Government Center",
        "description": (
            "The administrative seat of Kabankalan City in Negros Occidental, "
            "Western Visayas, Philippines. The offices of the city government "
            "are housed here."
        ),
        "order": 1,
    },
    {
        "info_type": CityInformation.InfoType.ATTRACTION,
        "title": "New Kabankalan Cathedral",
        "description": (
            "The Roman Catholic cathedral of Kabankalan City and one of the "
            "recognisable landmarks in Barangay Talubangi."
        ),
        "order": 2,
    },
    {
        "info_type": CityInformation.InfoType.ATTRACTION,
        "title": "City Lions Arch",
        "description": (
            "A landmark arch in the city centre that serves as a meeting point "
            "for residents and visitors."
        ),
        "order": 3,
    },
    {
        "info_type": CityInformation.InfoType.ATTRACTION,
        "title": "Mag-aso Falls",
        "description": (
            "A waterfall attraction inside the city limits of Kabankalan and a "
            "popular day-trip destination within the province."
        ),
        "order": 4,
    },
    {
        "info_type": CityInformation.InfoType.FOOD,
        "title": "Local dining",
        "description": (
            "Restaurants, inasal stalls and small eateries serve local Negrenses "
            "cuisine across the city. The Explore Places list shows the "
            "published and verified dining records."
        ),
        "order": 1,
    },
    {
        "info_type": CityInformation.InfoType.TRANSPORT,
        "title": "Getting to Kabankalan",
        "description": (
            "Buses and jeepneys connect Kabankalan with Bacolod City and the "
            "other towns of Negros Occidental through the provincial highway."
        ),
        "order": 1,
    },
    {
        "info_type": CityInformation.InfoType.STAY,
        "title": "Places to stay",
        "description": (
            "Accommodation options inside the city are published as verified "
            "records; check the Explore Places list for the current entries."
        ),
        "order": 1,
    },
]


class Command(BaseCommand):
    help = "Create starter City Information entries for Kabankalan."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace the existing City Information entries.",
        )

    def handle(self, *args, **options):
        city = locked_city() or City.objects.filter(pk=LOCKED_CITY_PK).first()
        if city is None:
            self.stderr.write(
                "Kabankalan city (id %s) was not found. Import the city first."
                % LOCKED_CITY_PK
            )
            return

        existing = CityInformation.objects.filter(city=city).count()
        if existing and not options["force"]:
            self.stdout.write(
                "City Information already holds %s entries for %s. "
                "Use --force to replace them." % (existing, city.name)
            )
            return

        if options["force"]:
            CityInformation.objects.filter(city=city).delete()

        created = 0
        for entry in STARTER_ENTRIES:
            CityInformation.objects.create(
                city=city, is_published=True, **entry
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Created %s published City Information entries for %s. Review "
                "them in the staff dashboard and unpublish anything that should "
                "not be public." % (created, city.name)
            )
        )
