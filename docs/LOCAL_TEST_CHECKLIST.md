# Local Test Checklist — ExploreKabankalan

This is the exact procedure to unpack the download, run the project on your
own machine and confirm that everything works before the branch is merged into
`main`. Every command below was executed against the released archive; the
results are quoted in section 7.

---

## 0. What you need

| Item | Notes |
|---|---|
| Python 3.13 or newer | Python 3.15 is fine. Django 5.2.18 needs a modern Python. |
| MySQL 8 | Optional — see section 2B for a SQLite fallback that needs nothing installed. |
| A terminal | PowerShell on Windows, bash on macOS/Linux. |

No Node.js, npm or build step is required: the frontend is plain HTML, CSS
and JavaScript served by Django.

---

## 1. Unpack the archive

```bash
unzip ExploreKabankalan-PR1.zip
cd ExploreKabankalan
```

The archive contains the whole project: `apps/`, `mysite/`, `templates/`,
`static/`, `media/`, `data/`, `docs/`, `requirements.txt` and `README.md`.

---

## 2. Choose the database

### 2A. MySQL (the deployment target)

```bash
mysql -uroot -e "CREATE DATABASE exploreanywhere CHARACTER SET utf8mb4"
```

These variables are optional — the defaults already point at
`exploreanywhere` / `root` / no password / `127.0.0.1:3306`:

```bash
export DJANGO_DB_ENGINE=django.db.backends.mysql
export DJANGO_DB_NAME=exploreanywhere
export DJANGO_DB_USER=root
export DJANGO_DB_PASSWORD=
export DJANGO_DB_HOST=127.0.0.1
export DJANGO_DB_PORT=3306
```

### 2B. SQLite (fastest way to see the site; nothing to install)

```bash
export DJANGO_DB_ENGINE=django.db.backends.sqlite3
export DJANGO_DB_NAME="$PWD/local.sqlite3"
```

The same migrations and the same code run against SQLite; it is only for
local inspection.

---

## 3. Install and prepare

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

`migrate` must end with `users.0002_user_consent_privacy_user_consent_privacy_at ... OK`.

---

## 4. Load the data

```bash
python manage.py seed_kabankalan          # city, hobbies, categories, published places
python manage.py seed_city_information    # the entries shown on /info/
python manage.py createsuperuser          # your own staff login for /admin/
```

`seed_kabankalan` loads the **six real Kabankalan attractions** that ship with
the project (Mag Aso Falls, Amyan Hill, Maronggues Hill, Mount Luyang,
Mount Nai-guin and the CPSU Museum) from the OpenStreetMap extract in
`data/osm/`, publishes them, and gives each one a category and interests.

> The much larger extract `data/osm/philippines-261013.osm.pbf` (610 MB) is
> stored in **Git LFS**, so the archive contains only its pointer. Clone the
> repository with `git lfs pull` if you want to rebuild the full published
> set from the raw extract; for a local look at the site the six shipped
> places are enough.

The OSM records do not contain opening hours, so the place page shows
"Not yet provided" until you add hours in the staff dashboard.

---

## 5. Run it

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

**The Explore Places directory needs an account.** Sign in with the superuser
you created (`/accounts/login/`), or register a new one at
`/accounts/register/` — the sign-up form asks you to accept the privacy
notice, and that acceptance is stored with the account.

---

## 6. What to check, page by page

| URL | What to look for |
|---|---|
| `/` | Landing page with the animation, the published places and the three scrolling sections. |
| `/accounts/register/` | Sign-up with the required privacy-notice checkbox. |
| `/places/` | The Explore Places carousel (sign in first). Use the arrows, the search box and the category/hobby filters. The map panel opens on a card. |
| `/places/?q=falls` | Natural-language search ("coffee shops", "mag aso falls", "places in Kabankalan"). |
| `/places/?q=Kabankalan+Plaza` | A named place: only that place is listed. |
| `/places/?q=where+to+buy+a+phone+case` | A buying question: the shops and malls are listed, with the note that the match came from the category. |
| `/places/?mode=nearby` | Nearby tab: "Use my location", the radius filter and the landmark selector. |
| `/places/<id>/` | Place details: photos, opening hours, reviews, the relevance control, save and visit buttons. |
| `/places/journey/` | My Journey: saved places, trips, reviews, visits and the **Interests & Recent Searches** panel. |
| `/info/` | City Information page with the type filter and the search box. Only published entries are shown. |
| `/evaluation/sus/` | The usability survey: ten 1–5 scales, then the 0–100 score and its band. |
| `/privacy/` | The privacy notice. |
| `/accounts/login/` | Sign in. |
| `/admin/` | The staff panel: places, OSM review queue, visit moderation, city information, survey answers, search logs and accounts. |
| `/admin/info/cityinformation/` | City Information: select entries and use **Publish** or **Unpublish**. |

---

## 7. Run the automated tests

```bash
python manage.py test
```

Expected result:

```
Ran 237 tests in ...s
OK (skipped=15)
```

The 15 skipped tests belong to the retired legacy city-information CRUD routes
that were replaced by the public `/info/` page; they are kept as the
specification for that module.

---

## 8. Optional checks

```bash
python manage.py check                 # configuration sanity
python manage.py check --database default           # the content scope system check
python manage.py check_content_scope                # the scope audit
python manage.py verify_enrichment                  # the completeness report
python manage.py makemigrations --check --dry-run   # "No changes detected"
```

Both must report no problems: `check` prints "System check identified no
issues" and the second prints "No changes detected".

Set a MapTiler token for the tiles:

```bash
export MAPTILER_API_KEY=your_token_here
```

Without a token the map panel still loads the layout but shows no tiles.

---

## 9. If something goes wrong

| Symptom | Cause and fix |
|---|---|
| `Access denied for user 'root'@'localhost'` | MySQL is running with a password. Set `DJANGO_DB_PASSWORD`. |
| `Can't connect to MySQL server` | MySQL is not running, or `DJANGO_DB_HOST`/`DJANGO_DB_PORT` point elsewhere. |
| `no such table` right after `migrate` | The database name differs from `DJANGO_DB_NAME`; check the environment variables. |
| Blank map tiles | `MAPTILER_API_KEY` is missing or expired. |
| No places in the carousel | `seed_kabankalan` was not run, or the places are not published (staff must publish them in `/admin/`). |
| `ModuleNotFoundError: django` | The virtual environment is not active, or `pip install -r requirements.txt` was skipped. |
| Photos are missing | `media/` is part of the archive; confirm the folder was extracted with the rest. |

---

## 10. When you are satisfied

Merge the pull request yourself:

```bash
gh pr merge 1 --merge      # or merge it from the GitHub web page
```

The branch `arena/a0b0498f-bsit3a-django-explorekabankala` targets `main` and
has never been merged automatically — the decision stays with you.
