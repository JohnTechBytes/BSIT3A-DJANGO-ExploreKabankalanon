/* One decorative light layer per page; no animation if JS, observation, or
   motion permission is unavailable. Content never depends on this layer. */
(() => {
    if (!('IntersectionObserver' in window) || !window.matchMedia) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const surface = document.querySelector([
        '.ea-attractions-header', '.ea6-top', '.eainfo-hero', '.pd-heading',
        '.ea4b-hero', '.ea-saved .ea-c-page-hero', '.ea-trip .hero',
        '.ea-choose .hero', '.ea-checkin .hero', '.ea-myreviews > .ea-c-page-hero',
        '.ea-visits > .ea-c-page-hero', '.easus-hero', '.eath-hero',
        '.eapriv-hero', '.discovery-header', '.auth-brand-panel'
    ].join(', '));
    if (!surface) return;
    let layer = null;
    let observer = null;
    let visible = false;
    const sync = () => {
        if (layer) layer.classList.toggle('is-motion-paused', !visible || document.hidden);
    };
    const stop = () => {
        if (observer) observer.disconnect();
        if (layer) layer.remove();
        surface.classList.remove('public-motion-surface', 'has-motion-layer');
        observer = null;
        layer = null;
        visible = false;
    };
    const start = () => {
        if (motion.matches || layer) return;
        layer = document.createElement('span');
        layer.className = 'public-motion-layer is-motion-paused';
        layer.setAttribute('aria-hidden', 'true');
        surface.classList.add('public-motion-surface', 'has-motion-layer');
        surface.appendChild(layer);
        observer = new IntersectionObserver(entries => {
            visible = entries[0].isIntersecting;
            sync();
        });
        observer.observe(surface);
    };
    document.addEventListener('visibilitychange', sync);
    motion.addEventListener('change', () => { if (motion.matches) stop(); else start(); });
    start();
})();
