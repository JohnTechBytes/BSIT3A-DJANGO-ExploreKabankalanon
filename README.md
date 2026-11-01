# ExploreKabankalan — Kabankalan City

A Django web system for exploring **Kabankalan City, Negros Occidental**: a
hobby-weighted place directory, natural-language search, a Leaflet map with
live GPS, reviews, itineraries, visit tracking and a customized administrative
panel, backed by locally imported OpenStreetMap and PSGC data.

> **Documentation note.** This document states what the system does today. A
> feature that is only partly built, or that is planned but not yet written, is
> labelled as such in the *Implementation Status* table. Where the project
> title refers to an "AI-assisted" system, the note under *Background of the
> Project* explains exactly which part of that is implemented.

---

## INTRODUCTION

### Background of the Project

Kabankalan City is one of the major cities of Negros Occidental, with a growing
number of restaurants, recreation centers, sports venues, cafes, parks, and
other establishments that serve its residents and visitors. However,
information about these places is scattered across social media pages, word of
mouth, and separate online listings. Residents, newcomers, and visitors who
want to find a place that fits their interests, such as billiards, badminton,
coffee, or nature walks, must search through many sources, and the information
they find may be incomplete, outdated, or not tied to where they currently are.

General-purpose map and review platforms list places, but they do not match
places to a person's hobbies, and they are not designed around the information
needs of a specific city. Local business owners also have limited means to keep
their listings accurate, while city offices have no single platform for sharing
official city information.

To address this need, **Explore Kabankalan** was developed as a web-based,
single-city system built with the Django framework. A visitor can browse the
verified, published places of Kabankalan, filter them by category and hobby,
search in natural language, view results on an interactive map, sort and filter
nearby places by straight-line distance from the device's GPS position or from a
chosen city landmark, read and write reviews, save places, build itineraries,
read the city's public information page, answer a short usability survey, and
track visits, interests and searches on a personal dashboard called
**My Journey**. City staff
manage the same records through a customized administrative panel that includes
an OpenStreetMap review queue, so unverified imports never reach the public
directory.

The recommendation engine is **deterministic and rule-based**, not
machine-learning-based. It ranks places by hobby fit (60% weight) and average
rating (20% weight, applied only where reviews exist). Missing signals are
excluded from the denominator rather than treated as zero. Distance is not part
of the ranking score; it is used by the Nearby view for sorting and filtering.

> **Implementation status of "AI-assisted".** The project title names an
> AI-assisted recommendation system. In this build the AI-assisted layer is the
> knowledge-based (rule-based) interpretation and scoring engine: the
> natural-language search classifies the intent of a query and extracts the
> entities it names (`apps/places/views.py`), and the recommender scores every
> candidate place against the visitor's hobbies and average rating with a
> documented weighted function (`apps/places/recommendations.py`). No external
> or cloud-trained model is called — nothing in the repository talks to
> Anthropic, OpenAI or any other API — so the system needs no API key, keeps
> visitor data on its own server and costs nothing per query. Extending it with
> a cloud model is identified as future work; the local parser it would fall
> back to is already implemented and is what the system uses today.

### Statement of the Problem or Project Objectives

The main objective of this project is to design, develop, and evaluate a
web-based, hobby-based place recommendation and city information system for
Kabankalan City that will help users find places that match their interests.

Specifically, the project accomplishes the following technical objectives:

1. **Hobby-based recommendation module.** Allow visitors to filter the place
   directory by hobby and rank the matching places by hobby fit and average
   rating, using a transparent, rule-based scoring function.
2. **Natural-language search.** Interpret queries such as "coffee shops",
   "mag aso falls" or "places in Kabankalan" with a local intent-and-keyword
   parser, ignoring filler words and recognizing named places. The optional
   Claude API interpretation layer is specified as the next enhancement; the
   local parser that it would fall back to is already in use.
3. **Interactive map and nearby search.** Integrate Leaflet with tiles built
   from OpenStreetMap data, live GPS positioning in the browser, in-browser
   distance filtering and sorting, place details, and a landmark reference for
   visitors who decline location access.
4. **Places directory with reviews.** Present verified, published Kabankalan
   places with descriptions, categories, hobbies, coordinates, photos and
   visitor ratings, with one review per user per place.
5. **Itinerary builder.** Let visitors create trips, add stops from the
   directory, set arrival times, reorder or remove stops, and delete trips.
   Stops are chosen manually; the system does not generate suggested
   itineraries.
6. **My Journey dashboard.** Organize a visitor's saved places, itinerary
   plans, reviews, verified visit check-ins, remembered interests and recent
   searches in one page, with visit points and badges.
7. **Administrative panel and data import.** Provide city administrators and
   staff with a customized Django admin for place listings, verification,
   photo management, bulk publication actions, visit moderation, a business
   review queue for OSM imports, and city information records, together with
   management commands that import PSGC codes, an OSM extract and Wikimedia
   imagery.
8. **Role-based access control.** Define the four roles required by the system
   (user, business owner, city administrator, system administrator) on a custom
   user model, and enforce access through Django's staff, superuser and model
   permissions so that administrative screens are restricted to authorized
   accounts.
9. **Evaluation instruments.** Build the System Usability Scale (SUS)
   instrument and a recommendation-relevance instrument into the system's data
   model, including the standard 0–100 SUS scoring, so that a usability
   evaluation can be administered with residents, visitors, and city or
   business representatives. Both instruments are reachable by respondents: the
   survey at `/evaluation/sus/` and the relevance control on a destination
   reached from a search.
10. **Privacy and data protection.** Publish a privacy notice that states what
    the system stores and what it deliberately does not store, and record a
    visitor's acceptance of it when an account is created.

### Significance of the Project

The system provides practical value to the following beneficiaries:

- **Residents and Visitors.** Find places that match their hobbies, see
  distance, details and maps in one platform, plan outings through itineraries,
  save places for later, and keep their reviews and verified visits together on
  the My Journey dashboard.
- **Local Business Owners.** Gain visibility through verified, published
  listings whose details can be corrected by city staff. A self-service
  interface for owners to edit their own listings is identified as future work.
- **City Administrators and Tourism Personnel.** Have a central panel for
  verifying and publishing place listings, reviewing imported OSM records
  before publication, moderating visit evidence, and maintaining city
  information records.
- **Future Researchers and Students.** Have a working reference for a
  single-city, hobby-weighted recommender built on Django, including its data
  model, import pipeline, administrative workflow and automated test suite.

### Alignment with Institutional Research Agenda and Sustainable Development Goals

**Institutional Research Agenda Alignment.** The project aligns with the
Institutional IT research priority by applying web technologies to improve
access to local information and services, and by documenting a reproducible
development and verification process.

**Sustainable Development Goal Alignment.**

- **SDG 9 (Industry, Innovation, and Infrastructure):** contributes through
  the use of open data (OpenStreetMap, PSA PSGC) and open web technology to
  build a local information infrastructure for one city.
- **SDG 11 (Sustainable Cities and Communities):** contributes by improving
  residents' and visitors' access to city information, public spaces, and
  recreational places.

---

## SCOPE AND LIMITATIONS

### System Scope and Technical Architecture

| Component | Description and Coverage |
|---|---|
| **Setting and Coverage** | Kabankalan City, Negros Occidental only. `KabankalanOnlyMiddleware` pins every session to Kabankalan (city pk 2), and the public and administrative querysets filter to that city. Places, information, users and evaluation activities are limited to Kabankalan. |
| **Accounts and Roles** | Custom user model with the four roles required by the system — user, business owner, city administrator, system administrator — plus a managed-city field, avatar, bio and coordinates. Registration creates a `user`. Administrative access is governed by Django's staff, superuser and model permissions. |
| **Kabankalan City Information** | `CityInformation` records (title, type, description, thumbnail, photo credit, display order) are maintained through the administrative panel and shown on the public City Information page (`/info/`), grouped by type with a type filter and a free-text search. Each entry carries a publish flag: staff publish and unpublish entries with the bulk actions in the staff dashboard, and only published entries are public. The page says so when nothing is published yet. |
| **Hobbies and Hobby Selection** | Hobbies are attached to places. Visitors filter the directory by category and by a single hobby from the search panel, and the chosen hobby is kept in the session, so it also shapes the recommendation score on later pages and is listed in My Journey. The earlier standalone hobby-selection route now redirects to the place directory. |
| **Places Directory with Details and Map Location** | Verified, published Kabankalan places with category, hobbies, description, address, coordinates, cover photo and gallery. The public listing is a looping carousel with list and map views and a details panel. Cover-photo labels indicate whether an image is set, not whether its usage rights were verified. |
| **Natural-Language Search** | A local intent-and-keyword parser handles queries such as "coffee shops", "mag aso falls" or "places in Kabankalan", ignoring filler words and matching named Kabankalan places. A query that names a place ("Kabankalan Plaza") returns that place only; a question that asks for a product ("where to buy a phone case") is answered by the business category that sells such things, and the page states that the match came from the category instead of from a listing name. No external AI service is called. |
| **Content Scope and Guardrail** | The catalogue has two pillars: **Places** (a real destination a visitor chooses for a hobby or a local errand, filed under an existing category and at least one hobby) and **City Information** (an editorial fact published by staff). The rules live in `apps/core/scope.py` and are enforced by code: `manage.py check_content_scope` audits the published catalogue, `manage.py purge_off_scope_places` unpublishes records outside the scope (dry run by default) and `manage.py check --database default` reports them as a system check. Records that are educational institutions are outside the scope: they are not destinations a visitor picks for a hobby and the recommendation score can never rank them, so they belong in City Information as a single curated fact instead. |
| **Recommendation Engine** | Deterministic ranking: hobby fit 60%, average rating 20% where reviews exist, with missing signals excluded from the denominator. Results are ordered by score, then by number of matched hobbies, then by title. Match percentages are not displayed to visitors. |
| **Interactive Map** | Leaflet 1.9.4, loaded on demand, with streets, satellite and hybrid layers from MapTiler (built on OpenStreetMap data) and OpenStreetMap/MapTiler attribution. Markers open a title and category popup; selecting a card flies the map to the place. |
| **Nearby Search and Live GPS** | The Nearby view reads the browser's geolocation, computes straight-line distance to each place, and filters or sorts results by distance (any distance, 1, 3, 5, 10 or 25 km). A curated Kabankalan landmark can serve as the reference point when GPS is unavailable or declined. Distances are straight-line estimates, not driving routes or travel times. |
| **Reviews and Ratings** | One review per user per place, 1–5 stars plus an optional comment; reviews can be updated or deleted; the average rating feeds both the place page and the recommender. Reviews are opinions and do not by themselves prove an in-person visit. |
| **Saved Places** | Visitors save and unsave places; saved places appear on a dedicated page and on the My Journey dashboard. |
| **Itinerary Builder** | Trips with a title and day number. Stops can be added from the directory, time-stamped, reordered and removed, and trips can be deleted. Itinerary suggestions are not generated by the system. |
| **My Journey Dashboard** | One page aggregating saved places, itinerary plans, the visitor's reviews and visit check-ins, with visit points and badges, plus a panel with the visitor's interests, the five most recent searches and the relevance feedback given so far. |
| **Visit Check-ins and Rewards** | A visitor reports a visit with a date and a corroborating note. Staff approve or reject the check-in in the administrative panel; only approved visits count toward points and badges. |
| **Administrative Panel** | Customized Django admin with destination management (search, category/verification/publication filters), bulk publication actions, per-place verification, photo actions, a business review queue for OSM imports, visit moderation, city information records, the evaluation records and account management (role and managed city). The index lists only the modules the city office uses; Django's own group editor stays reachable at `/admin/auth/group/` for a superuser. Native Django permissions and safeguards are preserved. |
| **Data Import** | Management commands import PSA PSGC codes, an OpenStreetMap extract and Wikimedia imagery, and enrich, categorize or attach photos to imported places. |
| **Evaluation Instruments** | The public System Usability Scale survey (`/evaluation/sus/`) asks the ten standard items on a 1–5 scale and scores them with the standard 0–100 formula, then shows the score and the interpretation band. `RecommendationRating` stores relevant, partially relevant or irrelevant ratings for a query and place; a destination reached from a search offers that control. Both records are also managed in the administrative panel. |
| **Privacy and Data Protection** | A public privacy notice (`/privacy/`) states what the system stores, what it never stores (the live GPS position is calculated in the browser and never sent to the server), who can see the data and how to have it deleted. Creating an account requires accepting the notice, and the acceptance and its date are stored with the account. |
| **Technology Stack** | Python 3 and Django 5.2.18 for the server; MySQL for storage, accessed through the PyMySQL driver; HTML5, CSS3 and JavaScript with Bootstrap 5.3.3 for the interface; Leaflet 1.9.4 with MapTiler tiles for maps; Pillow for image handling. Deployment values (secret key, debug flag, allowed hosts, database credentials, MapTiler token) are read from environment variables with development defaults. |
| **Target Users** | Residents, visitors and tourists who look for places that match their hobbies; business owners whose listings appear in the directory; city administrators and tourism personnel who verify and publish places and maintain city information records; and system administrators. |

### Implementation Status

| Module | Status | Notes |
|---|---|---|
| Places directory, carousel, details panel | Implemented | Verified, published places only; the carousel loops through every match (capped at 500 as a guard) |
| Hobby filtering and recommendation engine | Implemented | Rule-based; 60% hobby, 20% rating |
| Natural-language search (local parser) | Implemented | No external service; a named place returns that place, a buying question returns the business category and says so |
| Claude API interpretation layer | Planned | Not present in the codebase |
| Leaflet map, drone fly-to | Implemented | Needs a network connection and a MapTiler key |
| Nearby search, live GPS, radius filter | Implemented | Straight-line distance |
| Reviews and ratings | Implemented | One review per user per place |
| Saved places | Implemented | — |
| Itinerary builder | Implemented | Manual stops only |
| Itinerary suggestions | Planned | Not present |
| My Journey dashboard | Implemented | Saved places, trips, reviews, visits, interests, search history and relevance feedback |
| Visit check-ins and rewards | Implemented | Staff approval required |
| Administrative panel and OSM review queue | Implemented | Bulk approval refuses unverified OSM imports |
| Data import commands | Implemented | PSGC, OSM extract, Wikimedia imagery |
| City information records | Implemented | Public page at `/info/`; entries are published and unpublished with the bulk actions in the admin panel |
| Roles and access control | Partially implemented | Four roles defined; enforced through Django permissions; no business-owner portal and no city-level scoping |
| SUS instrument | Implemented | Public survey at `/evaluation/sus/` with the standard 0–100 scoring |
| Recommendation relevance rating | Implemented | In-page control on a destination reached from a search |
| Privacy notice and registration consent | Implemented | Public notice at `/privacy/`; the acceptance and its date are stored with the account |
| Search history and remembered interests | Implemented | Every submitted search is logged with the account; the chosen hobby is kept in the session |
| Account management in the staff dashboard | Implemented | Roles and managed city are editable at `/admin/users/user/` |
| Environment-driven deployment configuration | Implemented | Secret key, debug flag, allowed hosts, database and MapTiler token come from environment variables |
| Content scope guardrail | Implemented | `apps/core/scope.py` holds the two pillars; `check_content_scope`, `purge_off_scope_places` and a database-scoped system check enforce them |
| Distance in the ranking score | Planned | Distance is used by the Nearby view only |

### Limitations

- The system covers **Kabankalan City only**. Places, information and evaluation
  involving other cities are not included.
- An **internet connection is required for the interactive map and live GPS**:
  Browse loads a bundled copy of Leaflet on demand; other map pages may load
  Leaflet from a CDN. Map tiles come from MapTiler and require connectivity.
  Search and recommendation logic run on the server and need no external service.
- Map tiles require a **MapTiler API key**, which is currently embedded in the
  page template and should be moved to server-side configuration before public
  deployment.
- **GPS accuracy depends on the user's device**, and all distances are
  straight-line estimates rather than driving distances or travel times.
- **Recommendation quality depends on the completeness and accuracy of place
  data.** The administrative panel reports missing cover photos and refuses to
  publish unverified imports in bulk for this reason.
- Recommendations and search are implemented with **rule-based logic, not
  machine learning or a language model**. The Claude API layer described in the
  project title is not yet implemented.
- The public **City Information page** shows only what the city administration
  has published, so it stays empty until entries are entered. The starter set
  created by `manage.py seed_city_information` is published, because it is the
  curated starter content of the city, and it still has to be reviewed against
  the official city record before it is used.
- The **SUS survey** can be answered more than once and an anonymous answer is
  not linked to a person. A signed-in answer is stored with the account.
- The **chosen hobby is held in the browser session** and is lost when the
  session ends; the search history and the relevance ratings are stored with
  the account.
- **Business-owner self-service** and **city-level administrative scoping** are
  not implemented.
- The **privacy notice** describes the behaviour of this implementation. It has
  not been reviewed by a legal adviser and no formal data-processing agreement
  is signed.
- **Online booking, reservations, payment integration, and native mobile
  applications** are excluded from the current development phase.

---

## Technical Reference

### Requirements

- Python 3
- MySQL
- Dependencies from `requirements.txt`: Django 5.2.18, PyMySQL, openpyxl,
  Pillow 13 (`openpyxl` is retained for spreadsheet imports but is not imported
  by the current code)

Django is pinned to 5.2.18 because earlier 5.x releases crash on
`BaseContext.__copy__` under Python 3.13 and later (`'super' object has no
attribute 'dicts'`). `mysite/compat.py` is imported from `mysite/__init__.py` as
a safety net for environments still running an affected Django version.

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

mysql -uroot -e "CREATE DATABASE exploreanywhere CHARACTER SET utf8mb4"

python manage.py migrate
python manage.py seed_cities           # provinces and cities
python manage.py seed_kabankalan       # hobbies, categories and places
python manage.py seed_city_information # the entries shown on /info/
python manage.py createsuperuser       # staff login for /admin/
python manage.py runserver
```

Three read-only audits keep the installation inside the scope of the system
and show how a question is answered:

```bash
python manage.py check_content_scope   # the two pillars and any record outside them
python manage.py verify_enrichment     # how complete the published catalogue is
python manage.py check_search "where to buy a phone case"
```

`check_content_scope --strict` exits with status 1 when a published record is
outside the scope, and `purge_off_scope_places` unpublishes those records
(a dry run until `--apply` is given). `manage.py check --database default`
reports the same records as a Django system check.

Database settings come from the environment with development defaults
(`exploreanywhere`, user `root`, no password, `127.0.0.1:3306`, `utf8mb4`).
Set `DJANGO_DB_*` variables to point the project at a real MySQL server. To
try the project without MySQL, use the SQLite fallback — the same code and
migrations run against it:

```bash
export DJANGO_DB_ENGINE=django.db.backends.sqlite3
export DJANGO_DB_NAME="$PWD/local.sqlite3"
```

Virtual environments are gitignored under any name (`venv*`, `.venv/`).

`docs/LOCAL_TEST_CHECKLIST.md` walks through the whole local test: unpacking
the archive, choosing the database, loading the data, the pages to open, the
expected test result and what to do when something fails.

### Project layout

```
manage.py
mysite/      settings, urls, wsgi, compat (Django/Python context-copy shim)
apps/        cities, core, evaluation, hobbies, info, itineraries, places,
             users, visits
templates/   Django templates
static/      css, js, images, third-party libraries  (served at /static/)
media/       uploaded images                        (served at /media/)
data/        source datasets, read by management commands
docs/        documentation
```

### Data

`data/` holds source datasets — keep it. These are import inputs, not site
content: the boundary files and OSM extract cover the whole country because the
import commands need them to match Kabankalan records.

| Path | Contents |
|------|----------|
| `data/boundaries/` | geoBoundaries Philippines ADM2/ADM3 |
| `data/osm/` | `philippines-261013.osm.pbf` (stored in Git LFS, so a clone needs `git lfs pull`) plus `extracted/`, `matching/`, `validation/` |
| `data/psgc_2026_q3_exploreanywhere.csv` | PSA PSGC place codes |

Loaded through management commands such as:

```bash
python manage.py seed_kabankalan        # city, hobbies, categories, published places
python manage.py seed_city_information   # starter City Information entries
python manage.py load_psgc
python manage.py categorize_osm_places
python manage.py import_wikimedia_photos
```

`seed_kabankalan` loads the real Kabankalan attractions that ship in
`data/osm/validation/` and publishes them, so a fresh installation shows
verifiable records rather than invented sample names.

### Environment variables

Optional, read at runtime with safe defaults:

| Variable | Used by |
|----------|---------|
| `DJANGO_SECRET_KEY` | session and token signing; set a real key in production |
| `DJANGO_DEBUG` | debug mode (`1`, `true`, `yes`, `on`); defaults to on for development |
| `DJANGO_ALLOWED_HOSTS` | comma-separated list of host names allowed to serve the site |
| `DJANGO_DB_ENGINE` | database engine, e.g. `django.db.backends.mysql` |
| `DJANGO_DB_NAME` | database name |
| `DJANGO_DB_USER` | database user |
| `DJANGO_DB_PASSWORD` | database password |
| `DJANGO_DB_HOST` | database host |
| `DJANGO_DB_PORT` | database port |
| `MAPTILER_API_KEY` | access token for the MapTiler map tiles |
| `EXPLOREANYWHERE_PHOTO_USER_AGENT` | photo discovery commands |
| `WIKIMEDIA_USER_AGENT` | Wikimedia photo lookup commands |

`.env` is not tracked by git; export these in your shell instead.

### Tests

```bash
python manage.py test          # Django runner: 236 tests, 15 skipped
```

The suite covers the public flows (search, filters, save/unsave, reviews,
itineraries, check-ins, nearby, the city information page, the usability
survey and the relevance feedback), the discovery query behaviour, the
accuracy of the question search (a named place returns that place, a buying
question returns the business category), the content scope rules and the
administrative screens. Fifteen tests for the retired legacy city-information
CRUD routes are skipped: those routes were replaced by the public City
Information page, and the tests are kept as the specification for that module.

A `pytest.ini` is included for tooling that expects it, but pytest is not a
project dependency; use the Django runner.

### Documentation

- `docs/LOCAL_TEST_CHECKLIST.md` — unpack, run and verify the project locally
- `docs/VERIFICATION.md` — the verification record: test suite, browser audits, query and timing budget
- `docs/QUICK_REFERENCE.md` — day-to-day commands and troubleshooting
- `docs/PHASE6P_OPTIMIZATION_GUIDE.md` — photo discovery setup
- `docs/PHASE7_FEATURES_PLAN.md` — feature roadmap
