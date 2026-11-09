# Public interface direction

ExploreKabankalan is a local directory first: visitors search for existing places, inspect details and maps, and manage their own saved places and reviews. The landing page can create atmosphere; task pages should help people find information and complete an action without friction. The cinematic direction uses deep forest navigation and page introductions, with legible light content surfaces for forms, records and maps. Real published content and photo credits remain authoritative.

## Guidance reviewed

- **UI UX Pro Max**: prioritize contrast, focus, touch targets, responsive reflow and form feedback; use its style suggestions as recommendations rather than blindly adopting a mismatched palette.
- **Taste Skill**: start from the actual product and its supplied content, establish a clear primary action and use existing stack/components rather than fabricating attractions or rebuilding the application.
- **Emil Kowalski's skills**: motion needs a purpose; prefer short, interruptible, targeted transitions and reduced motion. Fast, frequent operations should not wait for animation.
- **Impeccable**: distinguish persuasive, operational and reading surfaces; reduce generic decoration, organize content around real user tasks, and review rendered layouts and states.

## Application

`public-system.css` harmonizes the shared public header, footer, page introductions, authentication panel and error recovery with the existing homepage, while retaining the existing Django templates, Bootstrap, content, routes, search, maps and form behavior. Real data and attribution are never substituted. Admin is intentionally outside this public-facing pass. Maintain visible focus, 4.5:1 text contrast, clear labels, 44px controls where practical, mobile reflow, and reduced motion. Verify interactive and data-dependent states against a safe test database before declaring them complete.
