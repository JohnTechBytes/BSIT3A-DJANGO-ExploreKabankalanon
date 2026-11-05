> **Historical document.** Historical verification record for an older build, not a guarantee for the current system. Use [the current local checklist](LOCAL_TEST_CHECKLIST.md) and [handoff guide](WORKFLOW_AND_HANDOFF.md). Do not run seed, import, bulk or destructive commands on an existing database without explicit approval and a backup.

# Verification Record

How this build was checked, what the numbers are, and how to reproduce every
check yourself. Written for the panel defence: every claim in the concept
paper about "the system works" can be re-run in a few minutes.

**Build:** branch `arena/a0b0498f-bsit3a-django-explorekabankala` @ `5ed7ef6`
**Date:** 29 October 2026
**Stack under test:** Python 3 · Django 5.2.18 · SQLite (local) / MySQL (deployment) · Bootstrap 5.3.3 · Leaflet 1.9.4

---

## 1. Automated test suite

The result below was refreshed on 1 November 2026 against the current redesign
working tree using SQLite. Other historical audit results retain their original
build and date.

```bash
python manage.py test
```

```
Ran 237 tests in 43.766s
OK (skipped=15)
```

| Area | Tests | File |
|---|---|---|
| Public flows (search, filters, save/unsave, reviews, itineraries, check-ins, nearby) | 22 | `apps/places/tests_flows.py`, `apps/places/tests.py` |
| Discovery query behaviour (no duplicated scan, filter options) | 5 | `apps/places/tests_performance.py` |
| My Journey dashboard (interests, search log, privacy between accounts) | 11 | `apps/places/tests_journey.py` |
| Relevance ratings | 8 | `apps/places/tests_relevance.py` |
| Usability survey (SUS scoring, storage, result page) | 8 | `apps/evaluation/tests.py` |
| City Information module | 10 | `apps/info/tests_info.py` |
| City Information publish workflow | 8 | `apps/info/tests_publish.py` |
| Question-search accuracy (named place, buying question) | 13 | `apps/places/tests_search_accuracy.py` |
| Content scope rules and guardrail | 11 | `apps/core/tests_scope.py` |
| Account routes, privacy notice, admin | 12 | `apps/users/tests.py` |
| Photo handling and licensing | 9 | `apps/places/tests_photos.py` |
| Configuration and environment | 6 | `apps/core/tests_config.py` |
| Local seeding command | 2 | `apps/core/tests_seed.py` |
| Legacy city-information CRUD (routes retired) | 15 **skipped** | `apps/info/tests.py` |

The 15 skipped tests belong to the retired legacy CRUD routes that the public
`/info/` page replaced; they are kept as the specification for that module.

Two of them are regression guards rather than features:
`test_query_count_does_not_grow_with_the_number_of_published_places` and
`JourneyDashboardQueryTests.test_query_count_does_not_grow_with_the_number_of_saved_places`.
If a future change reintroduces a per-row query, the suite fails.

---

## 2. Browser verification (Chromium, real clicks)

| Audit | Result | What it covers |
|---|---|---|
| Navigation sweep | **24/24** | Every header link, the "More" menu, the footer links, the mobile menu, landing-page anchors, zero JavaScript errors |
| Public flows | **22/22** | Search, category/hobby filters, sort, save → unsave → save, review, itinerary create, visit check-in, "use my location", radius filter, quick-search chips, landmark selector |
| Admin panel | **54/54** | Every model page, filters, bulk actions, the OSM review queue, photo actions, account management, log out. The index lists only the seven modules the city office uses (Destinations, Business review, City information, Visit approvals, Sus responses, Recommendation ratings, Query logs, Users); Django's group editor is hidden from the index but still reachable at `/admin/auth/group/` |
| Clean-install smoke test | **13/13** | Registration with the privacy checkbox on a fresh database, carousel, search, `/info/`, SUS survey, `/privacy/`, My Journey, admin login, zero JavaScript errors |

The clean-install smoke test is the one that matters for a fresh download: it
runs against an empty SQLite database that was created with `migrate` and
filled with `seed_kabankalan` and `seed_city_information`.

---

## 3. Response-time and query budget

Measured with `CaptureQueriesContext` on a database holding 181 published
places (worst case for the directory):

| Page | Queries | Time | Payload |
|---|---|---|---|
| `/places/?browse=all` (carousel, 181 places) | 11 | 56 ms | 429 KB |
| `/places/?q=falls` (search) | 11 | 7.6 ms | 60 KB |
| `/places/?hobby=…` (hobby filter) | 10 | 7.3 ms | 60 KB |
| `/places/?sort=rating` | 10 | 7.1 ms | 60 KB |
| `/places/?mode=nearby` | 10 | 62 ms | 452 KB |
| `/places/discover/` (paginated, 24 rows) | 4 | 5.8 ms | 38 KB |
| `/places/<pk>/` (place detail) | 12 | 8.9 ms | 33 KB |
| `/places/journey/` (My Journey) | 13 | 9.0 ms | 25 KB |
| `/` (home) | 6 | 8.3 ms | 16 KB |
| `/info/` (city information) | 5 | 3.9 ms | 18 KB |
| `/evaluation/sus/` (survey) | 3 | 9.8 ms | 26 KB |
| `/privacy/` (privacy notice) | 2 | 2.0 ms | 17 KB |

What the optimisation pass changed:

- the filter-option lists used to scan the published set a second time; the
  carousel now loads it once (SQL payload 8 481 → 6 424 bytes),
- `Place.is_open_now()` reuses prefetched opening hours instead of one query
  per place,
- the home page counters use a single `aggregate()` instead of three counts,
- the My Journey dashboard counts approved and pending check-ins with one
  conditional aggregate instead of two queries.

---

## 4. Data honesty

| Item | Status |
|---|---|
| Places | Historical OSM data under ODbL; publication flags do not prove independent verification |
| Photos | Some records have attributed Wikimedia photos; not all existing photo rights or identities are verified. Samples are labelled. |
| Reviews | Written by signed-in visitors, one review per user per place; they are opinions and do not prove an in-person visit |
| Visits | Reported by visitors and approved by staff before they count toward points and badges |
| Search history | Stored per account, shown only to that account, five entries on the dashboard |
| Live GPS position | Computed in the browser and never sent to the server; no location history is kept |
| Consent | The acceptance of the privacy notice and its date are stored with the account |

---

## 5. Question search, content scope and the publish workflow

| Check | Result | What it proves |
|---|---|---|
| Named place (`"Kabankalan Plaza"`) | 1 match | A query that names a place returns that place, not every record that contains one of its words |
| Named place with another spelling (`"Mag Aso Falls"`) | 1 match | The comparison ignores punctuation and spacing |
| Buying question (`"where to buy a phone case"`) | a historical category result (wording since corrected) | Current results disclose that availability is not confirmed |
| Buying question for any other product | the same category | The answer does not depend on a hard-coded list of products |
| Buying question for a haircut | the barbershop only | A product that belongs to one category uses that category |
| Content scope (`check_content_scope`) | 0 off-pillar records | Records outside the two pillars (educational institutions, for example) are reported, and `purge_off_scope_places` unpublishes them |
| City Information publish workflow | only published entries are public | Staff publish and unpublish entries from the staff dashboard; the public page and the type counts use published entries only |

These checks are automated (`apps/places/tests_search_accuracy.py`,
`apps/core/tests_scope.py`, `apps/info/tests_publish.py`). The browser audits
in section 2 were recorded before these three features and were not re-run for
them.

---

## 6. Reproducing everything

**Fresh, isolated database only:** the commands below create and modify data.
Do not run them against the existing `exploreanywhere` laptop database as a
search or data-quality fix. In particular, `seed_kabankalan` replaces hobby
associations on matching existing places and assigns Photography by default
when a category has no mapping. A no-duplicate rerun does not mean it preserves
existing tags. Any changes to the laptop database require explicit approval
and a verified database and media backup. The seed command's warning does not
stop it from writing.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# a database that needs no server
export DJANGO_DB_ENGINE=django.db.backends.sqlite3
export DJANGO_DB_NAME="$PWD/local.sqlite3"

python manage.py migrate
python manage.py seed_kabankalan
python manage.py seed_city_information
python manage.py createsuperuser

python manage.py test          # 237 tests, 15 skipped
python manage.py check         # System check identified no issues
python manage.py check --database default          # the content scope system check
python manage.py check_content_scope              # the scope audit
python manage.py verify_enrichment                # the completeness report
python manage.py check_search "where to buy a phone case"
python manage.py makemigrations --check --dry-run   # No changes detected
python manage.py runserver
```

`docs/LOCAL_TEST_CHECKLIST.md` lists every page to open and what to look for.

### City Information starter-data correction

The starter seed no longer creates the incorrectly located “Central Philippine University” entry. This change does not modify existing databases. If that entry exists locally, review and unpublish it in **Admin → City information**. Migration `info.0004` publishes existing entries, so review the entry after applying it as well. Do not use `seed_city_information --force` to correct this: it replaces all City Information entries.
