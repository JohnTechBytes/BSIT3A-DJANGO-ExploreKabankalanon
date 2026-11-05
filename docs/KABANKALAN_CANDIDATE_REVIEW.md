# Read-only Kabankalan candidate review

`review_kabankalan_directory` creates a **review CSV only**. It does not add,
publish, modify or delete database records, assign hobby tags, or fetch photos.
Only a later separately approved import could create drafts.

From the project folder in PowerShell, with the existing database available:

```powershell
.\.venv\Scripts\python.exe manage.py review_kabankalan_directory --output .\kabankalan_candidates_review.csv
```

Use a new filename each time; an existing file is never overwritten. The command
uses Nominatim once to identify the Kabankalan, Negros Occidental administrative
relation, then queries the mapped OSM area in separate requests. It stops if the
boundary cannot be confirmed or any response reports an error/partial data. If
there is a network or rate-limit error, wait and try later rather than repeatedly
retrying. A successful run still **does not establish a complete inventory**.
OSM has omissions and stale, duplicate or incorrect information; only named
objects with coordinates and supported tags are included. Smaller shops,
services, waterfalls and businesses with other tagging may be missing. Areas and
coordinates can also need correction.

Each row preserves the OSM object URL/ID, source tags, retrieval time, boundary
relation and © OpenStreetMap contributors (ODbL) attribution. Objects appearing
in multiple groups are combined. Both published and draft city records are
compared by exact OSM slug and normalized title; name matches may be different
branches and do not prove a duplicate. Education amenities are excluded;
education-like names are flagged for scope review so a school-supply shop is
not silently lost. Review staff must check identity, location, operational
status, category, relevance, licensing and whether a candidate already exists.
For a business, neither its stock nor its services are confirmed by this file.
Do not import schools. No hobby is inferred from OSM category alone.

OSM data: © OpenStreetMap contributors, Open Database License (ODbL),
https://www.openstreetmap.org/copyright. Review ODbL requirements before any
redistribution or future database import. The CSV contains external text; its
spreadsheet formula-like cells are prefixed with an apostrophe for safety.
