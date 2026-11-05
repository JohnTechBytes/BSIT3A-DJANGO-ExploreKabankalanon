/* Progressive enhancement: without JavaScript or IntersectionObserver every
   section stays visible. Reveal the carousel as a unit so its looping clones
   and horizontally scrolling records remain independent of this effect. */
(() => {
    if (!('IntersectionObserver' in window) || !window.matchMedia) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motion.matches) return;

    // Stop the decorative drift when its opening section is out of view.
    const hero = document.querySelector('.hero');
    const main = document.querySelector('main');
    if (hero && main) {
        new IntersectionObserver(entries => {
            main.classList.toggle('background-paused', !entries[0].isIntersecting);
        }).observe(hero);
    }

    const targets = document.querySelectorAll([
        '.feature-heading', '.quick-explore', '.closing-inner',
        '.discover .section-heading', '.discover .filters', '.discover .directory-meta',
        '.discover .places-carousel', '.discover .empty-state', '.discover .browse-more',
        '.introduction .intro-heading', '.introduction .intro-content',
        '.workflow-heading', '.steps > div'
    ].join(', '));

    const reveal = element => {
        element.classList.remove('is-reveal-pending');
        observer.unobserve(element);
    };
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) reveal(entry.target);
        });
    }, { rootMargin: '0px 0px -32px 0px' });

    targets.forEach(element => {
        // Never hide content already visible on load, including anchor links.
        if (element.getBoundingClientRect().top < window.innerHeight) return;
        element.classList.add('landing-reveal', 'is-reveal-pending');
        observer.observe(element);
    });

    document.addEventListener('focusin', event => {
        const pending = event.target.closest('.is-reveal-pending');
        if (pending) {
            // Focus must be visible immediately, without waiting for the fade.
            pending.classList.remove('landing-reveal');
            reveal(pending);
        }
    });
    motion.addEventListener('change', event => {
        if (!event.matches) return;
        targets.forEach(element => element.classList.remove('is-reveal-pending'));
        observer.disconnect();
    });
})();
