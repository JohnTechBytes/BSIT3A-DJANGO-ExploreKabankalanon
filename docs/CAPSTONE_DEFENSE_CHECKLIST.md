# Capstone defense checklist — ExploreKabankalan

This checklist follows the **Project Objectives** in the current [README](../README.md).
It is for a **local laptop demonstration**, not public hosting. The agreed
simplified interface is in the current working branch; verify that the exact
version you intend to submit is installed before the defense. The sandbox
preview uses an older catalogue snapshot and simulated sign-in, so it cannot
certify the laptop database or real account actions.

## Preparation

- [ ] Confirm the defense copy contains the agreed simplified interface and uses
      the intended `exploreanywhere` database. No automatic synchronization from
      the sandbox to the laptop is implied.
- [ ] Keep a recent, private backup of the database **and media**. Do not share
      database dumps; they can contain personal data.
- [ ] Prepare authorized visitor and staff accounts. Do not share their
      passwords in chat or presentation materials. Save, review, survey,
      login/session and search actions may write to the connected database.
- [ ] Start XAMPP MariaDB. In PowerShell, from the project folder, check the
      versions and system without applying changes:

  ```powershell
  .\.venv\Scripts\python.exe --version
  .\.venv\Scripts\python.exe -m django --version
  .\.venv\Scripts\python.exe manage.py showmigrations --plan
  .\.venv\Scripts\python.exe manage.py check
  ```

  For the existing MariaDB 10.4 setup, the documented local profile is Python
  3.12 and Django 5.0.14. If a migration is pending or a check fails, stop and
  investigate; do not migrate, seed, import, publish or delete without review,
  explicit approval and backup. Django 5.0 is unsupported for public hosting.
- [ ] Start the app with `.\.venv\Scripts\python.exe manage.py runserver`,
      then open `http://127.0.0.1:8000/` on the laptop. Check the actual network,
      browser, projector, map tiles, GPS and voice permissions before presenting.

## Objective-by-objective demonstration

Mark a box only after testing it on the actual laptop; these are not results.

| README objective | What to demonstrate or verify | Important qualification |
|---|---|---|
| 1. Hobby recommendations | [ ] Sign in, select an available hobby and inspect the matching published places and recommended ordering. | Matches depend on existing tags; untagged places can still be relevant. Ranking is rule-based, not machine learning. |
| 2. Natural-language search | [ ] Search an actual place by name; try a supported interest and `where to buy a phone case`. | The buying answer is a category suggestion, not confirmed stock. Queries are interpreted by local rules, not a language model. |
| 3. Map and Nearby | [ ] Open Nearby, use GPS permission or select a landmark, apply a distance filter, and open a mapped place and directions. | GPS and tiles depend on browser, permissions and network. Distances are straight-line estimates, not road distance or travel time. |
| 4. Directory and reviews | [ ] Open a published place; check the details and image. With authorization, submit or update a review using a test account. | A publication flag, rating or photo does not prove that facts, location or reuse rights have been independently verified. Review writes data. |
| 5. Saved Places | [ ] With authorization, save a place, find it under Saved Places, and remove the test save if appropriate. | This changes the real database on the laptop. |
| 6. Retained legacy features | [ ] Confirm Journey, itineraries and visit/reward links are hidden from the main interface. | Their existing URLs and data are retained; hiding them does not disable them. They are not the main defense workflow. |
| 7. Administration and data import | [ ] As authorized staff, inspect a place, its hobby tags, publication status and City Information. | Merely inspect unless a write is authorized and backed up. Imports and bulk actions can change existing records; do not run them during the demo without approval. |
| 8. Accounts and access | [ ] Verify visitor sign-in and that an authorized staff account can reach the staff dashboard. | Access is controlled by Django staff/model permissions; a role label alone does not grant access. An owner portal and role-based city scoping are not implemented. |
| 9. Evaluation instruments | [ ] Open the SUS survey and, after an applicable search, the relevance control on a place. Submit only if authorized. | Submissions are stored. Having instruments does not mean respondent data has been collected or analyzed. Report only actual results. |
| 10. Privacy and consent | [ ] Show the privacy notice and registration consent screen without creating an account unless authorized. | The notice has not been presented as a legal review; do not claim formal compliance or a completed agreement without evidence. |

Also open **City Information** and show that it uses the same published place
records as the directory alongside separate staff-published guides. Confirm
that Save and Reviews remain visible while itinerary and visit actions are
hidden from the main place and saved pages.

## How to explain the recommendations

- The system uses a **deterministic rule**, not an AI or language model.
- Hobby fit has a weight of `0.60`. Rating has a weight of `0.20` only when a
  place has reviews; the available weights are used to normalize the score.
  Without a selected hobby the hobby component is zero. Ties use matched hobby
  count and then title. Match percentages are not displayed to visitors.
- A fully hobby-matched place with no reviews can rank above a fully matched
  place with a rating below five stars, because the missing rating is excluded
  rather than penalized. This order is a rule outcome, not proof of quality.
- Distance is **not part of the recommendation ranking**. Nearby uses it
  separately for straight-line sorting and filtering.
- A selected hobby can match only tags that already exist; staff should review
  missing or uncertain tags, not assume an untagged place is irrelevant.

## Data and presentation readiness

- [ ] Verify the names, branches, categories, hobby tags and coordinates of the
      places selected for the demo. The catalogue and school-exclusion audit are
      not proven complete. Review, rather than invent, missing information.
- [ ] Check each displayed photo's identity, source and permission. Some local
      trial photos have unverified rights; do not present them as cleared for
      public reuse. Keep batch `sources.csv` files. Where no suitable photo is
      available, use the existing missing-photo message or labelled illustration.
- [ ] Rehearse the demo and a backup plan for unavailable map tiles, GPS or
      voice recognition. Do not promise that offline maps or GPS will work.
- [ ] Record actual test and evaluation results, including skipped tests and
      any unresolved issues. Automated SQLite tests do not prove that the real
      Windows/MariaDB setup, external services, photos or catalogue are correct.
- [ ] Review the simplified objectives with the adviser if the approved paper
      still requires features now hidden from the main interface. Do not claim
      a requirement is removed from the approved scope without confirmation.

For the detailed technical walkthrough and isolated test commands, see the
[local test checklist](LOCAL_TEST_CHECKLIST.md) and
[workflow and handoff](WORKFLOW_AND_HANDOFF.md).
