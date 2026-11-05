# ExploreKabankalan — Kabankalan City

A Django web system for exploring **Kabankalan City, Negros Occidental**: a
shared place directory, hobby-based matching, natural-language search, a Leaflet map with
live GPS, reviews, saved places and a customized administrative panel, backed by
locally imported OpenStreetMap and PSGC data. Itinerary, journey and visit-reward
features remain accessible through their existing URLs but are not promoted in
the main navigation.

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
published places of Kabankalan, filter them by category and hobby,
search in natural language, view results on an interactive map, sort and filter
nearby places by straight-line distance from the device's GPS position or from a
chosen city landmark, read and write reviews, save places, read the city's
public information page and answer a short usability survey. Previous journey,
itinerary and visit-reward pages are retained at their existing URLs but are no
longer linked from the main discovery interface. City staff
manage the same records through a customized administrative panel that includes
an OpenStreetMap review queue. Public listing requires the active and
`is_verified` flags, but the flags alone do not establish that the information,
coordinates or photographs were independently checked.

The recommendation engine is **deterministic and rule-based**, not
machine-learning-based. It ranks places by hobby fit (60% weight) and average
rating (20% weight, applied only where reviews exist). The hobby component is
always in the denominator; it is zero when no hobbies are selected. The rating
component is excluded when there are no reviews. Distance is not part
of the ranking score; it is used by the Nearby view for sorting and filtering.

> **Implementation status of "AI-assisted".** Despite the project title,
> search and recommendation currently use deterministic rules and database
> metadata, not a language model or machine learning. Search does not call an
> external AI API. Map tiles use external providers and MapTiler requires a
> client-visible key. A language-model integration is only a possible future
> enhancement, not a current feature.

### Statement of the Problem or Project Objectives

The main objective of this project is to design, develop, and evaluate a
web-based, hobby-based place recommendation and city information system for
Kabankalan City that will help users find places that match their interests.

Specifically, the project accomplishes the following technical objectives:

1. **Hobby-based recommendation module.** Allow visitors to filter the place
   directory by staff-assigned hobby tags and rank the matching places by hobby
   fit and average rating, using a rule-based scoring function.
2. **Natural-language search.** Interpret queries such as "coffee shops",
   "mag aso falls" or "places in Kabankalan" with a local intent-and-keyword
   parser, ignoring filler words and recognizing supported named places. Search
   is rule-based and does not call an external AI service; it does not understand
   every possible question.
3. **Interactive map and nearby search.** Integrate Leaflet with tiles built
   from OpenStreetMap data, live GPS positioning in the browser, in-browser
   distance filtering and sorting, place details, and a landmark reference for
   visitors who decline location access.
4. **Places directory with reviews.** Present published Kabankalan
   places and their available descriptions, categories, hobbies, coordinates,
   photos and visitor ratings, with one review per user per place. Listing data
   can be incomplete or require independent verification.
5. **Saved places.** Let signed-in visitors keep a personal list of published
   places and remove places from it.
6. **Retained legacy features.** The existing itinerary builder, My Journey and
   staff-reviewed visit rewards still work at their direct URLs, but are hidden
   from main discovery navigation. Their records have not been deleted. Stops
   are manual; the system does not generate suggested itineraries.
7. **Administrative panel and data import.** Provide city administrators and
   staff with a customized Django admin for place listings, verification,
   photo management, bulk publication actions, visit moderation, a business
   review queue for OSM imports, and city information records, together with
   management commands that import PSGC codes, an OSM extract and Wikimedia
   imagery.
8. **Accounts and administrative access.** Define four roles on the custom
   user model (user, business owner, city administrator, system administrator).
   Administrative access is controlled by Django's staff, superuser and model
   permissions, not automatically granted by the role field. A business-owner
   portal and role-based city scoping are not implemented.
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
  distance, details and maps in one platform, save places for later, and share
  reviews. Previously available planning and visit pages remain at their direct
  URLs but are not part of the main navigation.
- **Local Business Owners.** Gain visibility through published
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
| **Setting and Coverage** | The directory and public city information focus on Kabankalan City, Negros Occidental (city pk 2). `KabankalanOnlyMiddleware` pins the session to this city, and the Place admin is city-scoped. Accounts and survey respondents are not restricted by their physical location. |
| **Accounts and Roles** | Custom user model with the four roles required by the system — user, business owner, city administrator, system administrator — plus a managed-city field, avatar, bio and coordinates. Registration creates a `user`. Administrative access is governed by Django's staff, superuser and model permissions. |
| **Kabankalan City Information** | `/info/` combines a browsable directory of existing published Places with separate staff-published `CityInformation` guides. A relevant Place can appear both here and in hobby search without duplicating it. Grouping is a search aid, not independent verification. Staff can publish and unpublish guides. |
| **Hobbies and Hobby Selection** | Hobbies are attached to places. Visitors filter the directory by category and by a single hobby from the search panel, and the chosen hobby is kept in the session, so it also shapes the recommendation score on later pages and is listed in My Journey. The earlier standalone hobby-selection route now redirects to the place directory. |
| **Places Directory with Details and Map Location** | Active places with the `is_verified` publication flag are publicly listed. Category, hobbies, descriptions, coordinates and photographs may be missing or need confirmation. The flag is not proof of independent verification or photo rights. The public listing is a looping carousel with list and map views and a details panel. |
| **Natural-Language Search** | A local intent-and-keyword parser handles supported queries such as "coffee shops", "mag aso falls" or "places in Kabankalan". Exact-title matches take priority, but duplicate names can match multiple records and other queries may be ambiguous. A buying question such as "where to buy a phone case" suggests a business category and discloses that inventory is unconfirmed. Clear hobby phrases use existing assigned tags and disclose that untagged places may also be relevant. Search does not call an external AI service or understand every possible question. |
| **Content Scope and Guardrail** | The shared directory is intended for Kabankalan places relevant to hobbies or local needs; educational institutions are outside the intended scope. Existing records still require review, and missing hobby tags are not proof that a place is irrelevant. `check_content_scope` is a read-only audit using narrow title patterns and cannot find every school. `purge_off_scope_places` is a separate potentially destructive action and must not be applied without review, explicit approval and backup. |
| **Recommendation Engine** | Deterministic ranking: hobby fit 60%, average rating 20% where reviews exist; the hobby component remains in the denominator even when no hobby is selected. Results are ordered by score, then by number of matched hobbies, then by title. Match percentages are not displayed to visitors. |
| **Interactive Map** | Browse and Nearby use Leaflet 1.9.4 with MapTiler streets, satellite and hybrid layers and attribution; the landing map uses OpenStreetMap tiles. Markers show place information. On Browse and Nearby, selecting a mapped photo/card can fly the map to the place. Maps require network access; MapTiler requires a client-visible key. |
| **Voice Search** | Browse and Nearby use the browser speech-recognition API to enter search text. Availability depends on browser support, microphone permission and the browser's speech service; typing remains available. |
| **Place Photos** | A recorded cover is displayed when available. Missing covers show a message or a clearly labelled illustrative category sample. If a marked cover cannot load, JavaScript shows a "Photo unavailable" message. A sample is not a photo of the place. |
| **Nearby Search and Live GPS** | The Nearby view reads the browser's geolocation, computes straight-line distance to each place, and filters or sorts results by distance (any distance, 1, 3, 5, 10 or 25 km). A curated Kabankalan landmark can serve as the reference point when GPS is unavailable or declined. Distances are straight-line estimates, not driving routes or travel times. |
| **Reviews and Ratings** | One review per user per place, 1–5 stars plus an optional comment; reviews can be updated or deleted; the average rating feeds both the place page and the recommender. Reviews are opinions and do not by themselves prove an in-person visit. |
| **Saved Places** | Visitors save and unsave places; saved places appear on a dedicated page and on the My Journey dashboard. |
| **Itinerary Builder** | Retained at existing direct URLs but hidden from main navigation and place/saved actions. Trips and manual stops can still be managed there; no itinerary suggestions are generated. Existing data is preserved. |
| **My Journey Dashboard** | Retained at its existing direct URL but hidden from main navigation. It aggregates saved places, itineraries, reviews, visit check-ins, interests, recent searches and relevance feedback. |
| **Visit Check-ins and Rewards** | Retained at existing direct URLs but hidden from main navigation and place actions. Staff can still approve or reject reports; only approved visits count toward points and badges. Data remains stored. |
| **Administrative Panel** | Customized Django admin with destination management (search, category/verification/publication filters), bulk publication actions, per-place verification, photo actions, a business review queue for OSM imports, visit moderation, city information records, the evaluation records and account management (role and managed city). The index lists only the modules the city office uses; Django's own group editor stays reachable at `/admin/auth/group/` for a superuser. Native Django permissions and safeguards are preserved. |
| **Data Import** | Management commands import PSA PSGC codes, an OpenStreetMap extract and Wikimedia imagery, and enrich, categorize or attach photos to imported places. |
| **Evaluation Instruments** | The public System Usability Scale survey (`/evaluation/sus/`) asks the ten standard items on a 1–5 scale and scores them with the standard 0–100 formula, then shows the score and the interpretation band. `RecommendationRating` stores relevant, partially relevant or irrelevant ratings for a query and place; a destination reached from a search offers that control. Both records are also managed in the administrative panel. |
| **Privacy and Data Protection** | A public privacy notice (`/privacy/`) states what the system stores, what it never stores (the live GPS position is calculated in the browser and never sent to the server), who can see the data and how to have it deleted. Creating an account requires accepting the notice, and the acceptance and its date are stored with the account. |
| **Technology Stack** | Python and Django (see the compatibility profiles below) for the server; MySQL or compatible MariaDB for storage, accessed through the PyMySQL driver; HTML5, CSS3 and JavaScript with Bootstrap 5.3.3 for the interface; Leaflet 1.9.4 with MapTiler tiles for maps; Pillow for image handling. Deployment values (secret key, debug flag, allowed hosts, database credentials, MapTiler token) are read from environment variables with development defaults. |
| **Target Users** | Residents, visitors and tourists who look for places that match their hobbies; business owners whose listings appear in the directory; city administrators and tourism personnel who verify and publish places and maintain city information records; and system administrators. |

### Implementation Status

| Module | Status | Notes |
|---|---|---|
| Places directory, carousel, details panel | Implemented | Active records with the publication flag; publication does not prove independent verification. Carousel capped at 500. |
| Hobby filtering and recommendation engine | Implemented | Rule-based; 60% hobby, 20% rating |
| Natural-language search (local parser) | Implemented | Rule-based, no external AI; exact titles take priority and buying questions disclose category-based matches |
| External AI interpretation | Not implemented | No language-model API is called by search |
| Leaflet map, drone fly-to | Implemented | Needs a network connection and a MapTiler key |
| Voice search | Implemented | Browser speech-recognition support and microphone permission required; typing remains available |
| Missing or failed place photos | Implemented | Missing covers show a message or labelled sample; failed marked covers show a message when JavaScript is available |
| Nearby search, live GPS, radius filter | Implemented | Straight-line distance |
| Reviews and ratings | Implemented | One review per user per place |
| Saved places | Implemented | — |
| Itinerary builder | Retained; hidden from main interface | Direct URLs and existing data remain; manual stops only |
| Itinerary suggestions | Planned | Not present |
| My Journey dashboard | Retained; hidden from main interface | Direct URL and existing data remain |
| Visit check-ins and rewards | Retained; hidden from main interface | Direct URLs and existing data remain; staff approval required |
| Administrative panel and OSM review queue | Implemented | Bulk approval refuses unverified OSM imports |
| Data import commands | Implemented | PSGC, OSM extract, Wikimedia imagery |
| City Information | Implemented | Shared directory of published Places plus separately published guides at `/info/`. |
| Roles and access control | Partially implemented | Four roles defined; enforced through Django permissions; no business-owner portal and no city-level scoping |
| SUS instrument | Implemented | Public survey at `/evaluation/sus/` with the standard 0–100 scoring |
| Recommendation relevance rating | Implemented | In-page control on a destination reached from a search |
| Privacy notice and registration consent | Implemented | Public notice at `/privacy/`; the acceptance and its date are stored with the account |
| Search history and remembered interests | Implemented | Nonempty Browse and Nearby searches are logged; signed-in visitors can see their history. The chosen hobby is kept in the session. |
| Account management in the staff dashboard | Implemented | Roles and managed city are editable at `/admin/users/user/` |
| Environment-driven deployment configuration | Partially implemented | Secret, debug, hosts, database and map token can be configured; HTTPS, secure cookies and production deployment still require configuration and verification. |
| Content scope guardrail | Partial | Narrow title-based audit only; manual review is required and deletion or unpublishing is never automatic. |
| Recommendation distance | Not used for ranking | Nearby uses straight-line distance separately for filtering and sorting. |

### Limitations

- The system covers **Kabankalan City only**. Places, information and evaluation
  involving other cities are not included.
- **Maps and GPS are browser-dependent**: external tiles require connectivity;
  geolocation requires browser permission and a secure context (localhost may be
  treated as secure). Availability and accuracy vary. Search and recommendation
  logic run on the server without an external AI service.
- Explore/Nearby maps use a client-visible **MapTiler API key** configured by
  `MAPTILER_API_KEY`; apply provider-side restrictions. The landing map uses
  OpenStreetMap tiles. Tile availability and geolocation depend on the network,
  browser, permissions and provider.
- **GPS accuracy depends on the user's device**, and all distances are
  straight-line estimates rather than driving distances or travel times.
- **Voice input depends on the browser's speech-recognition service and
  microphone permission.** It may require network access; typing remains
  available when voice recognition is unsupported or denied.
- **Recommendation quality depends on the completeness and accuracy of place
  data.** Public records and images can still be inaccurate or lack confirmed
  reuse rights. The admin bulk-approval action skips `osm-` slugs, but other
  publication paths or manual database updates can set flags without independent
  verification.
- Recommendations and search are implemented with **rule-based logic, not
  machine learning or a language model**. No external AI interpretation layer
  is implemented.
- The **City Information page** combines published Places with separate
  published guides. Guide content and individual listings require review;
  seed commands write to the database and should not be run on existing data
  without explicit approval and backup.
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

- `requirements.txt` pins Django 5.2.18, PyMySQL, openpyxl and Pillow.
- For the existing Windows/XAMPP MariaDB 10.4 local demo, use Python 3.12 and
  `requirements-mariadb104.txt` (Django 5.0.14). Do not overwrite a working
  environment without checking it first. Django 5.0 is no longer security
  supported; this compatibility profile is **not suitable for public hosting**.
- For public deployment, use a supported Django/database/Python combination,
  run the tests against that exact stack, configure HTTPS/security settings,
  and run `manage.py check --deploy` before launch.

### Local setup and safety

See [the Windows local test checklist](docs/LOCAL_TEST_CHECKLIST.md) and
[workflow and handoff guide](docs/WORKFLOW_AND_HANDOFF.md). Existing database:
back up database and media before any changes. **Do not run seed commands,
imports, `migrate`, cleanup commands, or bulk actions on existing data unless
explicitly approved.** Registration, login sessions, searching and visitor
actions can write to the connected database. Tests should use isolated SQLite,
not the existing MySQL/MariaDB database.

The environment defaults to local `exploreanywhere`, MySQL root, no password;
these are development defaults and not secure for public deployment. Use the
`DJANGO_DB_*` environment variables for the intended database and verify the
connection before running commands.

### Place photos and local test imports

A cover is not proof of a place's identity, current operation or image reuse
rights. Some local-test photos have unverified rights and must be removed or
replaced with properly licensed or permitted images before public use. Do not
remove watermarks without permission. Missing covers use a message or clearly
labelled illustrative category sample; if a marked image fails to load, the
browser shows a separate unavailable message when JavaScript is enabled.

The optional local photo tools are described in
[`tools/photo_import/README.txt`](tools/photo_import/README.txt). The reviewed
batch tools save source links and rights notes in each batch's `sources.csv`;
keep those files. The direct importer updates the cover field without the
admin form's rights validation and does **not** populate blank photographer,
source or licence fields. Verify identity, permission, attribution and any
privacy concerns before publication; a source link alone is not a licence.
Back up the database and media and review each candidate before applying any
batch. Import results and remaining missing-cover counts must be checked on the
actual database, not inferred from historical exports.

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

Import and seed commands write records and can publish or update content. Do
not run them against existing data without explicit approval, a recent backup,
and review. OSM records are source data, not proof of verified facts.

For a read-only external candidate CSV covering malls, waterfalls, food/cafés,
shops and services, see [candidate review](docs/KABANKALAN_CANDIDATE_REVIEW.md).
It does not import or publish records and does not establish completeness.

### Environment variables

Read at runtime. The defaults are for local development, not public hosting:

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

Run tests against isolated SQLite, never the existing MariaDB database. See
[local test checklist](docs/LOCAL_TEST_CHECKLIST.md) for PowerShell commands.
The suite covers account, search, map page, reviews, saved places, itinerary,
visits, administration, directory and survey flows. Automated tests do not
prove that the laptop database, real map tiles, GPS or photo rights are correct.

### Documentation

- `docs/CAPSTONE_DEFENSE_CHECKLIST.md` — objective-by-objective local defense walkthrough
- `docs/LOCAL_TEST_CHECKLIST.md` — safely test the existing Windows installation
- `docs/WORKFLOW_AND_HANDOFF.md` — workflow, limitations and submission checklist
- `docs/KABANKALAN_CANDIDATE_REVIEW.md` — read-only OSM candidate report
- `docs/VERIFICATION.md` — historical verification record; not a current guarantee
- `docs/QUICK_REFERENCE.md` — historical photo-tool notes, not the submission checklist
- `docs/PHASE6P_OPTIMIZATION_GUIDE.md` — photo discovery setup
- `docs/PHASE7_FEATURES_PLAN.md` — feature roadmap
