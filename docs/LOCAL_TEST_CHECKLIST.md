# Local test checklist — existing Windows installation

This checklist is for a **local demo**, not public hosting. It uses your
existing `exploreanywhere` database and does not instruct you to seed, import,
migrate, publish, delete, or overwrite its data. The application itself writes
sessions and search logs; registration, reviews, saved places, itineraries,
visit reports, survey submissions and staff actions also write to the database.
Only perform such actions on data you are authorized to change.

## 1. Prepare without changing data

- Start XAMPP's MariaDB and open PowerShell in the project folder that contains
  `manage.py`. Confirm you have the intended code version; downloading only a
  single management command does not install the rest of a branch.
- The existing MariaDB 10.4 setup uses Python 3.12 and Django 5.0.14. The
  alternative `requirements-mariadb104.txt` records that local compatibility
  profile; do not reinstall over a working environment just to test it. Django
  5.0 is no longer security-supported and is not appropriate for public hosting.
- Make a recent database **and media folder** backup before approved changes.
  Do not run seed, import, purge, bulk publication, migration, or deletion
  commands on the existing database just because a checklist mentions them.

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m django --version
.\.venv\Scripts\python.exe manage.py showmigrations --plan
.\.venv\Scripts\python.exe manage.py check
```

`showmigrations --plan` lists a plan; it does not apply migrations. If a
migration is pending or a check reports an error, stop and investigate; do not
apply it without a reviewed backup and explicit approval. `check` does not
independently verify catalogue data.

## 2. Run locally

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/`. This Django development server is for local
review only. Sign in with your existing authorized account to use Explore
Places. Do not share passwords or database backups containing private data.

## 3. Visitor and staff walkthrough

1. Home → Explore Places → search for an existing place by its exact name.
2. Try a hobby phrase (for example, `photography`) and inspect the tag-match
   notice. Untagged places can still be relevant. Search for `where to buy a
   phone case`; category results do not guarantee that stock exists.
3. Open Nearby and test GPS permission or a landmark, a radius and the map.
   Distances are straight-line estimates, not road travel times. Check real
   tiles on the laptop's network; unavailable tiles do not prove a code error.
4. Open a place and check its details and photograph. Confirm that the image
   actually depicts that place and that its reuse is permitted. Save/review,
   itinerary and visit actions write to the connected database.
5. Open City Information. Its directory reuses published Places; editorial
   guides are separate. A place may appear in both the directory and interests.
6. If authorized, open the staff dashboard and inspect the place list, hobby
   review filter, City Information and visit review. Do not execute a write
   action or bulk operation unless approved.
7. Check the mobile layout, sign-out and the usability survey. Submitting the
   survey stores a response. For the actual system workflow see
   [workflow and handoff](WORKFLOW_AND_HANDOFF.md).

## 4. Isolated automated tests (separate PowerShell window)

Open a **new PowerShell window** in the same project folder so the temporary
SQLite settings do not affect your running local app. These tests create and
remove their own isolated test database, not `exploreanywhere`.

```powershell
$env:DJANGO_DB_ENGINE = 'django.db.backends.sqlite3'
$env:DJANGO_DB_NAME = ':memory:'
.\.venv\Scripts\python.exe manage.py test
```

Close that PowerShell window afterwards. Tests may report skipped legacy tests;
failures need investigation. A passing test run does not verify live photos,
location data, real GPS, external maps or the laptop's MariaDB configuration.

## 5. Review-only place discovery

See [candidate review](KABANKALAN_CANDIDATE_REVIEW.md). The command produces a
new CSV without importing or publishing places. Review identities, duplicates,
scope, current operation and licenses. It cannot guarantee complete coverage.
No import should take place without a later explicit approval.

## 6. Before submission

- Confirm you have tested the **same code version** that you will submit.
- Keep the existing database and media backup; confirm the intended project
  settings and that required pages work with the evaluator's test account.
- Clearly disclose unverified information and photo rights, incomplete OSM
  coverage, browser/network dependencies, and that search is rule-based—not a
  language model.
- A merged pull request does not update an existing laptop project automatically;
  confirm the installed code version. Public internet deployment requires a
  supported software stack, production security configuration and a separate
  deployment review; a local runserver demo is not that review.
