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
