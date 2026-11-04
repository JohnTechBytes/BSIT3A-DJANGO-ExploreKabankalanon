/* Small, progressive motion layer. Content and controls work without JS. */
(() => {
    const header = document.querySelector('.site-header');
    if (header) {
        let scheduled = false;
        const syncHeader = () => {
            header.classList.toggle('is-scrolled', window.scrollY > 24);
            scheduled = false;
        };
        window.addEventListener('scroll', () => {
            if (!scheduled) { scheduled = true; requestAnimationFrame(syncHeader); }
        }, { passive: true });
        syncHeader();
    }
    if (!('IntersectionObserver' in window) || !window.matchMedia) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motion.matches) return;

    const targets = document.querySelectorAll([
        '.workflow-heading', '.steps > div', '.section-heading', '.filters',
        '.directory-meta', '.places-carousel', '.empty-state', '.browse-more',
        '.intro-heading', '.interest-links', '.map-copy', '.map-panel',
        '.quick-explore', '.closing-inner'
    ].join(', '));
    const reveal = element => {
        element.classList.remove('is-reveal-pending');
        observer.unobserve(element);
    };
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => { if (entry.isIntersecting) reveal(entry.target); });
    }, { rootMargin: '0px 0px -32px 0px' });
    targets.forEach((element, index) => {
        if (element.getBoundingClientRect().top < innerHeight) return;
        element.classList.add('landing-reveal', 'is-reveal-pending');
        element.style.transitionDelay = `${(index % 3) * 50}ms`;
        observer.observe(element);
    });
    document.addEventListener('focusin', event => {
        const pending = event.target.closest('.is-reveal-pending');
        if (pending) { pending.classList.remove('landing-reveal'); pending.style.transitionDelay = ''; reveal(pending); }
    });
    const onMotionChange = event => {
        if (!event.matches) return;
        targets.forEach(element => { element.classList.remove('is-reveal-pending'); element.style.transitionDelay = ''; });
        observer.disconnect();
    };
    if (motion.addEventListener) motion.addEventListener('change', onMotionChange);
    else if (motion.addListener) motion.addListener(onMotionChange);
})();
