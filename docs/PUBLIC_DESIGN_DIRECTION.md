# Public interface direction

ExploreKabankalan is a local directory first: visitors search for existing places, inspect details and maps, and manage their own saved places and reviews. The landing page can create atmosphere; task pages should help people find information and complete an action without friction. The cinematic direction uses midnight-blue navigation and page introductions, sandstone accents, and legible light content surfaces for forms, records and maps. Real published content and photo credits remain authoritative.

## Guidance reviewed

- **UI UX Pro Max**: prioritize contrast, focus, touch targets, responsive reflow and form feedback; use its style suggestions as recommendations rather than blindly adopting a mismatched palette.
- **Taste Skill**: start from the actual product and its supplied content, establish a clear primary action and use existing stack/components rather than fabricating attractions or rebuilding the application.
- **Emil Kowalski's skills**: motion needs a purpose; prefer short, interruptible, targeted transitions and reduced motion. Fast, frequent operations should not wait for animation.
- **Impeccable**: distinguish persuasive, operational and reading surfaces; reduce generic decoration, organize content around real user tasks, and review rendered layouts and states.

## Application

`public-system.css` and the newer `public-palette.css` harmonize the shared public header, footer, page introductions, authentication panel and error recovery with the existing homepage, while retaining the existing Django templates, Bootstrap, content, routes, search, maps and form behavior. Real data and attribution are never substituted. Admin is intentionally outside this public-facing pass. Maintain visible focus, 4.5:1 text contrast, clear labels, 44px controls where practical, mobile reflow, and reduced motion. Verify interactive and data-dependent states against a safe test database before declaring them complete.

## Cinematic public experience

The landing uses a credited Kabankalan landmark as a full-bleed desktop cover, while keeping the search prominent and the photograph readable on small screens. The directory carousel now uses wider image-led cards with recorded photo attribution, and browse cards fit three, two or one card by viewport rather than expanding to track width. Search and optional location tools form separate panels on large Nearby screens; smaller screens keep their natural reading order. Shared navigation, footer, account screens and task surfaces use the same visual language without changing their routes or data. Manual browse-carousel controls remain usable with reduced motion; automatic movement remains disabled for that preference. If a recorded cover fails to load, its credit is hidden rather than being attributed to the labeled fallback illustration.

This is a presentation and interaction pass, not verification of place information or image rights. The optional map depends on available map resources and network access. Check real accounts, records, forms and map tiles in the local app before relying on the design for a demonstration. The isolated preview is not the laptop database and blocks writes.

## Midnight and sandstone revision

The public palette now uses deep midnight blue for the cinematic shell, warm sandstone accents, porcelain content surfaces, and a consistent blue for primary tasks. Nearby is organized in the order visitors use it: search, an optional location or landmark reference, and then results with map controls. Before a reference is chosen, results are explicitly described as alphabetical rather than presented as distance-ranked. Autocomplete, voice search, GPS, landmark and distance filtering, and photo-to-map behavior remain connected to the existing logic; the interface makes no new claims about the records themselves. Admin remains outside this public palette.
