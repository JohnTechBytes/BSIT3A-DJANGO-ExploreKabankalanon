/* Reveal only whole result sections, never carousel items or map elements. */
(() => {
    if (!('IntersectionObserver' in window) || !window.matchMedia) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (motion.matches) return;
    const targets = document.querySelectorAll('.city-info-page .eainfo-group, .nearby-page .ea6-list, .browse-page #ea-list-panel');
    if (!targets.length) return;
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            entry.target.classList.remove('is-reveal-pending');
            observer.unobserve(entry.target);
        });
    }, { rootMargin: '0px 0px -32px 0px' });
    targets.forEach(element => {
        if (element.getBoundingClientRect().top < window.innerHeight) return;
        element.classList.add('public-reveal', 'is-reveal-pending');
        observer.observe(element);
    });
    document.addEventListener('focusin', event => {
        const target = event.target.closest('.public-reveal.is-reveal-pending');
        if (!target) return;
        target.classList.remove('public-reveal', 'is-reveal-pending');
        observer.unobserve(target);
    });
    motion.addEventListener('change', event => {
        if (!event.matches) return;
        targets.forEach(element => element.classList.remove('is-reveal-pending'));
        observer.disconnect();
    });
})();
