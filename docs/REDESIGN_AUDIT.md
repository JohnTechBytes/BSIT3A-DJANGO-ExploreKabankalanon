# Explore Kabankalan redesign — phase 1 audit

Scope: source inspection, starting with the landing page. This is a baseline, not a claim that every screen has completed visual or accessibility testing. No existing views, database records, or recommendation rules were changed in this phase.

## Landing page: current state and direction

| Area | Current state | Next-phase direction |
| --- | --- | --- |
| Identity | A light slate-and-indigo landing page is layered over older landing styles, while other public screens use dark teal chrome. The purple gradient, floating chips and glass header conflict with the new brief. | Establish one warm, restrained identity using the approved tokens; simplify rather than add visual decoration. |
| Hierarchy | The hero has two action buttons, a search form, suggestions, a count and decorative badges. Three feature cards repeat links already in the header. | Make the main search or browse action unmistakable, reduce competing decoration, and keep useful navigation. |
| Content | Featured places are real active, verified Kabankalan records. Unmatched photos are labelled as illustrations. The cathedral image is credited; the user-supplied City Hall background still needs source/permission verification. | Preserve real records, sample labels, credits and existing image functionality. Do not claim an illustrative image is a destination photo. |
| Discovery | Search, category filters and a continuously moving, pausable carousel exist; the three-step explanation and interest links exist. There is currently no map preview on the landing page. | Improve readability and keyboard/touch use, keep search/filter/carousel behavior, and investigate a truthful, lightweight map preview in the landing phase. |
| Motion | The landing has entrance, scroll-reveal and continuous decorative badge motion; the carousel pauses on interaction, offscreen and for reduced motion. | Keep motion purposeful and respectful of reduced motion; do not remove existing carousel controls. |
| Accessibility | Search has a label, the page has a skip link, focus styles and reduced-motion support. Automated checks are not a substitute for keyboard, screen-reader and real-device testing. | Recheck contrast, focus, touch targets and all interactive states after each migrated screen. |

## Broader system observations

- Styling is distributed across landing, shared public, auth, admin and page-specific CSS, plus inline template styles. Public screens use `public-night.css`; login and registration are separate documents. Moving to one design system must be incremental so that existing forms and native admin actions remain functional.
- `static/css/explore.css` already existed and contains city-selection styling. Phase 1 **preserves** it and adds namespaced design tokens above it rather than replacing or editing vendor files. `.ek-theme` provides opt-in Bootstrap aliases; no page is switched to that class in this phase.
- `landing-reveal.js`, `landing-carousel.js`, `public-motion.js` and `public-reveal.js` have distinct responsibilities today. Consolidation needs to preserve carousel pause, reduced motion, focus behavior and no-JavaScript visibility; `motion.js` is not introduced prematurely in this audit phase.
- Login and registration already have labelled fields and server-side error output. Password visibility controls and floating labels need separate, accessible implementation and testing in the auth phase.
- Shared controls are currently authored directly in templates. Reusable partials will be introduced with their first real uses, retaining each form's names, IDs, validation and CSRF handling.

## Product behavior to confirm before later phases

These points differ from the supplied description, so redesign must not imply or silently implement them:

1. The existing `/hobbies/` selection route redirects to Explore Places; it is not currently a working 1–5 weight-selection wizard.
2. The existing recommendation function uses hobby and available review signals. Distance is reserved, **not included in that ranking**. Nearby separately offers optional browser-side straight-line distance sorting/filtering.
3. Match percentages and “Not scored” labels were deliberately removed from the visitor interface and have regression tests. A requested match-score ring would reverse that earlier decision.
4. Homepage smart search uses existing local intent/search logic and requires login. Do not present it as a generative AI service or promise streaming results that are not implemented.
5. A drag-to-reorder itinerary, travel times and other newly requested interactions need a separate capability review; a redesign alone must not represent them as already available.

Please confirm any intended product-logic changes separately before implementation. The current phase does not change these behaviors.

## Phase 1 token foundation

- `static/css/explore.css`: `--ek-*` colors, typography, spacing, radii, shadows and motion values; opt-in `.ek-theme` Bootstrap variables. Existing city-selection rules remain intact.
- Local variable fonts: Plus Jakarta Sans and Inter, with their SIL Open Font License texts in `static/fonts/`. The new fonts are declared but not applied in phase 1; pages fetch them when later phases actually use them. Font subsetting/compression and layout stability should be evaluated during performance QA.
- Contrast examples: requested muted text on the requested canvas is approximately **4.91:1**; white on the requested primary is **5.26:1**. White on the requested danger color is only **4.38:1**, so a separate darker danger-text token is provided for normal text on light surfaces. Every actual component and state still needs testing.
- The landing links the foundation file, but the current visual design remains in place until phase 2/3. No vendor files were modified.

## Future verification

At the appropriate phases, test 375/768/1280px layouts, keyboard and screen-reader flows, hover/focus/active/disabled/empty/error states, reduced motion and no-JavaScript fallbacks. Test Lighthouse and actual devices separately; no score or frame rate is guaranteed by the token file alone. For catalogue review, use existing records or a backed-up copy of them; do not add destinations, seed, purge or overwrite the user's MySQL. Automated test fixtures remain isolated from the real database.

## Landing implementation (following phase 1)

After approval to apply the landing design, the home page opted into the warm tokens and locally hosted fonts. Its styles are scoped to `.landing-page` in `explore.css`; other public, auth and staff screens remain unchanged. The existing search route (including its login requirement), category filters, published-place carousel, detail links and recommendation logic were retained. Reusable button, chip, input, card, badge, toast and skeleton partials establish a starting point for later migrations; only controls needed by the landing are used there.

The new Leaflet preview displays at most 24 coordinate-bearing places from the same filtered, active and verified queryset as the landing carousel. It does not obtain visitor location or change ranking. It loads local Leaflet files only when approached and uses OpenStreetMap tiles with attribution. If tiles or assets cannot load, the page presents links to real mapped records instead of a fictional map. In the isolated preview environment external tiles were unavailable; the fallback was tested. The browse link leads to the existing map button, not directly to an automatically opened map.

The snapshot preview contains the user's 181 published places from the October 30 export, not a live MySQL connection. One inaccessible external image was cleared only in the temporary preview copy, so its existing illustrative sample is visibly labelled. Neither the user's original export nor their database was changed. The Cathedral photo remains credited to Lightningscale / Wikimedia Commons, CC BY 4.0. The provenance and permission for the supplied City Hall background are still unverified and should be confirmed before publication.

Landing QA covers responsive Chromium widths 320, 375, 768 and 1280px, category filtering, carousel controls, search's login redirect, no-JavaScript scrolling, reduced motion, asset loading, map fallback and an automated axe scan. These checks do not establish screen-reader usability, real-device performance, Lighthouse scores, or compatibility with the user's Windows/MariaDB setup; those remain for later review. The redesign of auth, hobby selection, results, details, staff screens and the remaining requested pages still requires phased confirmation.

## Account screens (next approved work)

Sign-in and registration now use the same opt-in cream and green system as the landing, with a shared account shell and the credited cathedral photo. Mobile layouts put the form first. The existing Django form fields, CSRF protection, validation, privacy consent, legacy login alias and redirect behavior were kept. Password visibility is an optional enhancement; passwords stay masked and forms remain usable without JavaScript. The existing login implementation still redirects to `/hobbies/` after sign-in, regardless of `next`, and that route then redirects to Explore Places; this is not a new hobby wizard.

The retired hobby-selection template was not reactivated: doing so would change the existing route and user flow rather than simply restyle it. If a weighted hobby-selection step is wanted, its behavior and the earlier decision to remove match percentages need separate confirmation before implementation.

Chromium checks covered the account screens at 320, 375, 768 and 1280px, initial and invalid form states, CSRF, password toggle and no-JavaScript behavior. Automated axe checks found no violations on the initial account screens; this does not replace screen-reader or device testing. Existing registration and login behavior was additionally tested using isolated Django test databases. No live MySQL data was accessed or modified.

## Discovery, nearby, map and place details

The user confirmed keeping the existing `/hobbies/` redirect to Explore Places. This remains the current decision; no separate selection wizard or ranking changes were introduced.

The Explore Places carousel, Nearby, map views, destination details and legacy paginated catalogue now opt into the warm system. The existing all-places / nearby / map navigation is visible again and stays in sync with the list/map buttons. Search, category and hobby filters, recommendation order, review and save forms, visitor-provided location, labelled illustrative images and real published records remain intact. Unmapped Nearby photos no longer advertise an unavailable map interaction. Nearby's microphone keeps live transcription but has no looping microphone animation.

Both maps now load the project's bundled Leaflet files; Nearby previously requested the library from an external CDN. Existing MapTiler tile layers, credits and photo-to-map interactions are unchanged. In the sandbox, external map tiles are blocked, so the map reports that failure while listing cards and detail links remain usable. The QA server used a separate copy of the October 30 snapshot and a temporary account; neither the user's MySQL nor the original snapshot was modified.

Chromium checks covered 320, 375, 768 and 1280px, no horizontal overflow, search redirection, the mobile menu, list/map toggles, photo-to-map selection, simulated live speech, reduced motion and automated axe scans of the initial four screens. Automated tests use isolated databases. This does not certify a Lighthouse score, real microphone hardware, MapTiler access, or the user's Windows/MariaDB installation. At that point Journey, itineraries, city information, staff, SUS and error pages remained for later phases.


## Journey, planning and remaining public screens

Journey, saved places and reviews; itinerary list, creation, chooser and builder; City Information; visits and check-ins; privacy; SUS survey and result; and 404/500 pages now opt into the same cream-and-green design system. Existing URLs, authenticated views, forms, CSRF protections, counts, staff-reviewed visit status, published content and planner actions remain in place. The retired hobby route remains a redirect; no match percentages or new recommendation logic were introduced.

The revised privacy notice (version 1.1, November 2026) now reflects the locally bundled Leaflet library, public reviews, map providers and account-deletion behavior. Account consent remains a boolean and timestamp, not a version-specific consent record. The survey copy distinguishes a current session result from earlier retained submissions, and the 500 page no longer guarantees that data was saved. These are code-based corrections, not legal review. The landing's City Hall background now has a single short arrival animation, disabled for reduced motion; it does not loop. The photo's source and permission remain unverified.

Chromium covered the eight Journey/planning/city screens and seven visits/survey/privacy/error screens at 320, 375, 768 and 1280 pixels, with no horizontal overflow; automated axe scans of initial desktop states found no violations. Browser checks used isolated, explicitly labelled QA-only trip, review and City Information fixtures, not the user's real database. Tests also covered mobile navigation, city-information search/filter, survey selection, planner/check-in controls and reduced motion. The full isolated Django suite ran 250 tests: 235 passed and 15 skipped. These checks do not establish real-device performance, screen-reader usability, Lighthouse scores or Windows/MariaDB compatibility.

The Arena embedded preview does not forward cookies to the Django server on the user's phone. With user approval, a temporary, read-only preview uses a non-staff visitor and a separate SQLite copy; mutations are blocked and request writes rolled back. It is not a test of login, registration, saving or editing. The preview contains 181 published places from the October 30 historical snapshot; City Information was not imported into that preview. Staff/admin refinements and full production/PC testing remain separate work.
