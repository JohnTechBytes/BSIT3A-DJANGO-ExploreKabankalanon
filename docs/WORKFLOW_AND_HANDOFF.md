# ExploreKabankalan — workflow and handoff

## Purpose and catalogue

This is a Kabankalan-only shared place directory for hobbies and local needs,
with separate staff-authored city guides. Schools are outside the agreed
catalogue scope; no school audit in the project is exhaustive. A Place may
appear in both City Information and interest-based search without copying the
record. Public place queries require city ID 2, `is_active=True`, and
`is_verified=True`; these are database flags, **not proof** that facts, photos,
coordinates, hours, inventory, or business operations were independently checked.

## Visitor flow

1. **Home → sign in or register.** Registration asks for privacy consent. The
   Explore Places page requires an account. The retired `/hobbies/` route
   redirects to Explore Places rather than showing a separate selection wizard.
2. **Explore Places.** Browse, search for a name or a supported interest phrase,
   or use category/hobby filters. Exact titles have priority. Clear interest
   phrases match existing staff-assigned hobby tags; untagged places might also
   be relevant. Product questions show possible categories, not confirmed stock.
   Nearby supports selected service categories. Search uses deterministic rules,
   not generative AI, and cannot understand every possible question.
3. **Browse / Nearby / Map.** Published results may have recorded coordinates.
   Nearby calculates straight-line distances in the browser using GPS with
   consent or a selected landmark. These are not travel times or route rankings.
   Browse displays up to 500 matches and Nearby up to 250; the UI reports when
   the limit is reached. Map tiles, GPS, voice input and browser permissions
   require real-device tests.
4. **Place details.** See available information, photos, reviews, and links to
   maps. Signed-in users can save the place or write/update/delete a review;
   these actions write to the connected database.
5. **Saved Places and My Reviews.** Signed-in users can revisit their saved
   places and reviews from the navigation. My Journey, itinerary and visit
   features are hidden from the main interface but their direct URLs, behaviour
   and existing data are retained. Hiding does not disable these features.
6. **City Information.** Browse existing published Places by city-directory
   groups and read the separately published staff guides. Classification and
   publication do not guarantee up-to-date or independently verified facts.
7. **Evaluation and privacy.** The SUS survey can be submitted anonymously or
   while signed in. A relevance response may be submitted on a place reached
   through search. These save data; the privacy notice describes collection.

## Staff flow

Authorized staff use Django admin permissions. Inspect and edit existing Places,
review missing hobby tags, assess images and their rights, and maintain city
information guides. The OSM review queue and read-only candidate CSV help
identify leads; an OSM listing is not proof of current operation or coordinates.
Compare exact IDs, names and addresses before resolving duplicates. **No
candidate import or publication is automatic.** Any later import needs explicit
approval and a backup, with candidates reviewed as unpublished drafts first.

Staff review visitor-submitted check-ins separately. Approval requires a review
note of at least 20 characters about independent corroboration; the application
cannot prove that the evidence is genuine. Roles on the user model do not by
themselves provide an owner portal or city-level administrative permissions.

## Ranking and data limitations

The Browse recommended sort uses a deterministic hobby/rating function (hobby
weight 0.60 always in the denominator, rating 0.20 when there are reviews).
No hobby selected means zero hobby fit. Distance is not part of this ranking;
Nearby uses distance separately. Match percentages are not shown to visitors.
The catalogue may omit places and may include stale information, duplicate
branches, unconfirmed coordinates, missing hobbies or photos with uncertain
rights. Do not represent publication, an OSM pin, a photo, or a category match
as independent proof. Confirm important details before travelling.

## Submission readiness

- **Automated checks:** run against isolated SQLite as described in the
  [local checklist](LOCAL_TEST_CHECKLIST.md). Tests are useful but do not certify
  real Windows/MariaDB, external services, or data accuracy.
- **Local demo:** test the submitted code version on the actual PC and database,
  including login, map tiles, GPS/voice permissions, images, the shared directory
  and a staff account. Actions may create or change records; use only authorized
  demo data and backups.
- **Public deployment:** not yet certified. Development settings enable DEBUG,
  use a development secret and permit broad hosts; HTTPS redirect, HSTS and secure
  cookies require production configuration. The MariaDB 10.4 compatibility
  profile uses unsupported Django 5.0 and is for local testing only. Before
  public hosting, choose and test a supported stack, configure HTTPS, security,
  restricted hosts/provider keys, static/media serving and backups, and run
  `manage.py check --deploy` against production settings.
- **Data quality:** independently review active records, hobby evidence, photo
  identity/rights, category, duplicates, hours, address, coordinates and closure
  status. OSM discovery and a `is_verified` flag do not prove completeness.
