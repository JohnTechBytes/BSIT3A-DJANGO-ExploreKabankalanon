/* Keep place browsing user-controlled. Without JavaScript this remains a
   native horizontal list, and reduced-motion users get the same behavior. */
(() => {
    const viewport = document.querySelector('.places-carousel');
    const track = viewport?.querySelector('.places-grid');
    const controls = document.querySelector('.carousel-controls');
    if (!viewport || !track || !controls) return;

    const prev = controls.querySelector('[data-carousel-prev]');
    const next = controls.querySelector('[data-carousel-next]');
    if (!prev || !next) return;

    function cardStep() {
        const card = track.querySelector('.place-card');
        if (!card) return viewport.clientWidth;
        return card.getBoundingClientRect().width
            + (parseFloat(getComputedStyle(track).gap) || 0);
    }

    function updateControls() {
        const scrollable = viewport.scrollWidth > viewport.clientWidth + 1;
        controls.hidden = !scrollable;
        if (!scrollable) return;
        const atStart = viewport.scrollLeft <= 1;
        const atEnd = viewport.scrollLeft + viewport.clientWidth >= viewport.scrollWidth - 1;
        prev.disabled = atStart;
        next.disabled = atEnd;
    }

    function step(direction) {
        viewport.scrollBy({
            left: direction * cardStep(),
            behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
                ? 'auto'
                : 'smooth',
        });
    }

    prev.addEventListener('click', () => step(-1));
    next.addEventListener('click', () => step(1));
    viewport.addEventListener('scroll', updateControls, { passive: true });

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(updateControls, 120);
    });
    updateControls();
})();
