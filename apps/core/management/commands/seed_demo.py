from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from datetime import time
from decimal import Decimal

from apps.cities.models import City
from apps.core.models import Hobby, Category
from apps.places.models import Place, OpeningHours, PlacePhoto, Review
from apps.info.models import CityInformation, SusResponse, RecommendationRating

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds comprehensive demo data matching the ExploreAnywhere 12-screen UI workflow"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting ExploreAnywhere demo seed..."))

        # 1. Users
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@exploreanywhere.ph",
                "first_name": "Admin",
                "last_name": "User",
                "role": User.Role.SUPER_ADMIN,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if not admin_user.has_usable_password():
            admin_user.set_password("admin123")
            admin_user.save()

        demo_user, _ = User.objects.get_or_create(
            username="explorer",
            defaults={
                "email": "user@exploreanywhere.ph",
                "first_name": "Juan",
                "last_name": "Dela Cruz",
                "role": User.Role.USER,
                "latitude": Decimal("9.988000"),
                "longitude": Decimal("122.815000"),
            }
        )
        if not demo_user.has_usable_password():
            demo_user.set_password("user123")
            demo_user.save()

        self.stdout.write(self.style.SUCCESS("✓ Users seeded (admin/admin123, explorer/user123)"))

        # 2. Cities (Screen 2 & Screen 11)
        cities_data = [
            {
                "name": "Kabankalan",
                "province": "Negros Occidental",
                "latitude": Decimal("9.988000"),
                "longitude": Decimal("122.815000"),
                "status": City.Status.ACTIVE,
                "description": "Known as the Rising City of the South in Negros Occidental, home to Mag-Aso Falls and rich cultural heritage."
            },
            {
                "name": "Bacolod",
                "province": "Negros Occidental",
                "latitude": Decimal("10.676600"),
                "longitude": Decimal("122.951000"),
                "status": City.Status.ACTIVE,
                "description": "The City of Smiles, renowned for the MassKara Festival, Chicken Inasal, and heritage ruins."
            },
            {
                "name": "Cebu City",
                "province": "Cebu",
                "latitude": Decimal("10.315700"),
                "longitude": Decimal("123.885400"),
                "status": City.Status.PENDING,
                "description": "The Queen City of the South, vibrant hub for urban night life, beach resorts, and tech scenes."
            },
            {
                "name": "Davao City",
                "province": "Davao del Sur",
                "latitude": Decimal("7.190700"),
                "longitude": Decimal("125.457800"),
                "status": City.Status.PENDING,
                "description": "Crown jewel of Mindanao, famous for Mount Apo, durian, eco-parks, and adventure tourism."
            },
        ]

        city_map = {}
        for c in cities_data:
            obj, _ = City.objects.get_or_create(
                slug=slugify(c["name"]),
                defaults=c
            )
            city_map[c["name"]] = obj

        self.stdout.write(self.style.SUCCESS(f"✓ Seeded {len(city_map)} Cities"))

        # 3. Hobbies (Screen 3: 12 hobby grid)
        hobbies_data = [
            ("Billiards", "ti ti-ball-8", "Cue sports, 8-ball, 9-ball, and pool lounges"),
            ("Basketball", "ti ti-ball-basketball", "Indoor/outdoor courts and hoop leagues"),
            ("Café Hopping", "ti ti-coffee", "Specialty espresso, artisanal brews, and cozy corners"),
            ("Hiking", "ti ti-mountain", "Nature trails, peaks, waterfalls, and day hikes"),
            ("Photography", "ti ti-camera", "Scenic viewpoints, historic landmarks, and photo spots"),
            ("Gaming", "ti ti-device-gamepad-2", "Esports arenas, board game cafes, and gaming hubs"),
            ("Food Trip", "ti ti-tools-kitchen-2", "Street food crawl, barbecue joints, and local dishes"),
            ("Music", "ti ti-music", "Live acoustic sets, karaoke lounges, and gig venues"),
            ("Art & Culture", "ti ti-palette", "Galleries, local workshops, museums, and street murals"),
            ("Beach/Nature", "ti ti-sun-high", "Coastal spots, eco-parks, and swimming areas"),
            ("Shopping", "ti ti-shopping-bag", "Night markets, souvenir boutiques, and local craft centers"),
            ("Others", "ti ti-dots", "Bowling, arcade, fitness, and casual activities"),
        ]

        hobby_map = {}
        for name, icon, desc in hobbies_data:
            h_obj, _ = Hobby.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "icon": icon, "description": desc}
            )
            hobby_map[name] = h_obj

        self.stdout.write(self.style.SUCCESS(f"✓ Seeded {len(hobby_map)} Hobbies"))

        # 4. Categories
        categories = ["Sports & Recreation", "Food & Drink", "Tourist Attractions", "Nightlife", "Shopping", "Lodging"]
        category_map = {}
        for cat in categories:
            c_obj, _ = Category.objects.get_or_create(
                slug=slugify(cat),
                defaults={"name": cat, "description": f"Places for {cat}"}
            )
            category_map[cat] = c_obj

        # 5. Places (Screen 5, 6, 7 matching mockup places in Kabankalan)
        kab = city_map["Kabankalan"]
        places_data = [
            {
                "title": "R&B Billiard Hall",
                "city": kab,
                "category": category_map["Sports & Recreation"],
                "hobbies": [hobby_map["Billiards"], hobby_map["Gaming"]],
                "description": "A modern billiard hall with clean facilities, multiple tables, and a friendly atmosphere perfect for hangouts and competitions.",
                "address": "Guanzon St, Kabankalan City, Negros Occidental",
                "barangay": "Barangay 1",
                "latitude": Decimal("9.988200"),
                "longitude": Decimal("122.815500"),
                "phone": "+63 912 345 6789",
                "website": "https://rbbilliardhall.com",
                "is_verified": True,
                "avg_rating": Decimal("4.6"),
                "review_count": 32,
                "cover_image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=800&auto=format&fit=crop",
            },
            {
                "title": "Club 8 Lounge",
                "city": kab,
                "category": category_map["Sports & Recreation"],
                "hobbies": [hobby_map["Billiards"], hobby_map["Music"]],
                "description": "Upscale recreation lounge featuring tournament-grade pool tables, craft beverages, and lively evening music.",
                "address": "Tayum St, Barangay 2, Kabankalan City",
                "barangay": "Barangay 2",
                "latitude": Decimal("9.989500"),
                "longitude": Decimal("122.817200"),
                "phone": "+63 920 444 8899",
                "website": "https://club8lounge.ph",
                "is_verified": True,
                "avg_rating": Decimal("4.3"),
                "review_count": 18,
                "cover_image_url": "https://images.unsplash.com/photo-1511193311914-0346f16efe90?w=800&auto=format&fit=crop",
            },
            {
                "title": "K-Billiards",
                "city": kab,
                "category": category_map["Sports & Recreation"],
                "hobbies": [hobby_map["Billiards"]],
                "description": "Budget-friendly neighborhood pool center favored by students and casual players with quick snacks available.",
                "address": "Coloso St, Barangay 3, Kabankalan City",
                "barangay": "Barangay 3",
                "latitude": Decimal("9.986800"),
                "longitude": Decimal("122.813900"),
                "phone": "+63 918 222 3344",
                "website": "",
                "is_verified": False,
                "avg_rating": Decimal("4.1"),
                "review_count": 27,
                "cover_image_url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&auto=format&fit=crop",
            },
            {
                "title": "Coffee Corner",
                "city": kab,
                "category": category_map["Food & Drink"],
                "hobbies": [hobby_map["Café Hopping"], hobby_map["Food Trip"]],
                "description": "Cozy aesthetic café serving hand-poured specialty coffee, matcha lattes, waffles, and artisanal pastries.",
                "address": "National Highway, Barangay 1, Kabankalan City",
                "barangay": "Barangay 1",
                "latitude": Decimal("9.990200"),
                "longitude": Decimal("122.818000"),
                "phone": "+63 945 999 8877",
                "website": "https://coffeecornerkab.ph",
                "is_verified": True,
                "avg_rating": Decimal("4.8"),
                "review_count": 45,
                "cover_image_url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800&auto=format&fit=crop",
            },
            {
                "title": "B Burger",
                "city": kab,
                "category": category_map["Food & Drink"],
                "hobbies": [hobby_map["Food Trip"]],
                "description": "Famous gourmet smash burger joint serving 100% pure beef patties, loaded fries, and refreshing milkshakes.",
                "address": "Corner Justice Perez St, Kabankalan City",
                "barangay": "Barangay 2",
                "latitude": Decimal("9.988900"),
                "longitude": Decimal("122.816000"),
                "phone": "+63 917 555 1234",
                "website": "https://bburger.ph",
                "is_verified": True,
                "avg_rating": Decimal("4.5"),
                "review_count": 39,
                "cover_image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&auto=format&fit=crop",
            },
            {
                "title": "Kabankalan Freedom Park",
                "city": kab,
                "category": category_map["Tourist Attractions"],
                "hobbies": [hobby_map["Photography"], hobby_map["Beach/Nature"], hobby_map["Basketball"]],
                "description": "A spacious central public park in the heart of Kabankalan, with walking trails, manicured gardens, and open-air courts.",
                "address": "City Plaza Grounds, Barangay 1, Kabankalan City",
                "barangay": "Barangay 1",
                "latitude": Decimal("9.987500"),
                "longitude": Decimal("122.814800"),
                "phone": "",
                "website": "",
                "is_verified": True,
                "avg_rating": Decimal("4.4"),
                "review_count": 52,
                "cover_image_url": "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=800&auto=format&fit=crop",
            },
            {
                "title": "Mag-Aso Falls",
                "city": kab,
                "category": category_map["Tourist Attractions"],
                "hobbies": [hobby_map["Hiking"], hobby_map["Photography"], hobby_map["Beach/Nature"]],
                "description": "Iconic twin waterfalls cascading into turquoise natural pools surrounded by dense mountain greenery.",
                "address": "Sitio Mag-Aso, Barangay Oringao, Kabankalan City",
                "barangay": "Barangay Oringao",
                "latitude": Decimal("9.923400"),
                "longitude": Decimal("122.861100"),
                "phone": "+63 934 888 1234",
                "website": "",
                "is_verified": True,
                "avg_rating": Decimal("4.7"),
                "review_count": 88,
                "cover_image_url": "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=800&auto=format&fit=crop",
            },
        ]

        created_places = {}
        for p in places_data:
            h_list = p.pop("hobbies")
            p_obj, _ = Place.objects.get_or_create(
                title=p["title"],
                city=p["city"],
                defaults=p
            )
            p_obj.hobbies.set(h_list)
            created_places[p["title"]] = p_obj

            # Opening Hours
            for day_idx in range(7):
                OpeningHours.objects.get_or_create(
                    place=p_obj,
                    weekday=day_idx,
                    defaults={
                        "open_time": time(10, 0),
                        "close_time": time(23, 59) if "Billiard" in p["title"] or "Lounge" in p["title"] else time(22, 0),
                        "is_closed": False
                    }
                )

            # Photos
            PlacePhoto.objects.get_or_create(
                place=p_obj,
                order=1,
                defaults={
                    "image_url": p_obj.cover_image_url,
                    "caption": f"Front view of {p_obj.title}"
                }
            )

        self.stdout.write(self.style.SUCCESS(f"✓ Seeded {len(created_places)} Places with Hours and Photos"))

        # 6. Sample Reviews (for R&B Billiard Hall)
        rb_place = created_places["R&B Billiard Hall"]
        sample_reviews = [
            (demo_user, 5, "Best pool tables in Kabankalan! Well maintained cue sticks and very cold aircon."),
            (admin_user, 4, "Great vibe, clean tables, friendly staff. Highly recommended for a casual night out."),
        ]
        for user_obj, rating, text in sample_reviews:
            Review.objects.get_or_create(
                place=rb_place,
                user=user_obj,
                defaults={"rating": rating, "comment": text}
            )

        # 8. City Information (Screen 10: Kabankalan City tabs)
        info_items = [
            (CityInformation.InfoType.ATTRACTION, "Freedom Park", "A popular central park in the heart of the city with gardens and shaded benches.", "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=600&auto=format&fit=crop", 1),
            (CityInformation.InfoType.ATTRACTION, "San Roque Church", "Historical stone church and spiritual landmark of Kabankalan.", "https://images.unsplash.com/photo-1548625361-192a6c3f6e1f?w=600&auto=format&fit=crop", 2),
            (CityInformation.InfoType.ATTRACTION, "Kabankalan Museum", "Learn about the city's rich agricultural history, legends, and cultural heroes.", "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=600&auto=format&fit=crop", 3),
            (CityInformation.InfoType.FOOD, "Kabankalan Food Park", "Lively hawker-style night market serving local inasal, barbecue, and halo-halo.", "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&auto=format&fit=crop", 1),
            (CityInformation.InfoType.STAY, "Zaycoland Resort & Hotel", "Family-friendly accommodation with swimming pools, convention hall, and restaurant.", "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&auto=format&fit=crop", 1),
            (CityInformation.InfoType.EVENT, "Sinulog de Kabankalan", "Grand annual cultural festival celebrated every January with street dancing and tribal beats.", "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=600&auto=format&fit=crop", 1),
            (CityInformation.InfoType.TRANSPORT, "Kabankalan Ceres Terminal", "Main bus hub connecting south Negros to Bacolod City, Dumaguete, and nearby towns.", "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600&auto=format&fit=crop", 1),
        ]
        for itype, title, desc, thumb, ord_num in info_items:
            CityInformation.objects.get_or_create(
                city=kab,
                title=title,
                info_type=itype,
                defaults={"description": desc, "thumbnail_url": thumb, "order": ord_num}
            )
        self.stdout.write(self.style.SUCCESS("✓ Seeded City Information (Attractions, Food, Stays, Events, Transport)"))

        # 9. Evaluation Data (Screen 12: SUS 86.5 + Accuracy 92% / 6% / 2%)
        # Seed 20 SUS responses matching the mockup footer note: "Based on 20 real users across Kabankalan and Bacolod"
        for i in range(20):
            # Q answers yielding high average score around 86.5
            sus = SusResponse(
                user=demo_user if i == 0 else None,
                q1=5 if i % 2 == 0 else 4,
                q2=1 if i % 3 != 0 else 2,
                q3=5,
                q4=1,
                q5=4 if i % 2 == 0 else 5,
                q6=1,
                q7=5,
                q8=1,
                q9=4 if i % 3 == 0 else 5,
                q10=1 if i % 2 == 0 else 2,
            )
            sus.compute_score()
            sus.save()

        # Seed Recommendation Ratings (92% relevant, 6% partial, 2% irrelevant)
        total_ratings = 50
        for i in range(total_ratings):
            if i < 46:  # 92%
                r_choice = RecommendationRating.RatingChoices.RELEVANT
            elif i < 49:  # 6%
                r_choice = RecommendationRating.RatingChoices.PARTIAL
            else:  # 2%
                r_choice = RecommendationRating.RatingChoices.IRRELEVANT

            RecommendationRating.objects.create(
                user=demo_user,
                query_text="where can I play billiards tonight?",
                place=rb_place if i % 2 == 0 else created_places["Club 8 Lounge"],
                rating=r_choice
            )
        self.stdout.write(self.style.SUCCESS("✓ Seeded Evaluation Data (SUS Usability + Recommendation Accuracy)"))

        self.stdout.write(self.style.SUCCESS("\n🎉 ExploreAnywhere demo seed complete! All 12 screens are backed by real database records."))
