/* Lazy, bounded map preview. Coordinates and labels come only from the current
   published place queryset; no visitor location is requested or recorded. */
(() => {
    const container = document.getElementById('landing-map');
    const source = document.getElementById('landing-map-places');
    const status = document.getElementById('landing-map-status');
    const fallback = document.getElementById('landing-map-fallback');
    if (!container || !source || !status) return;
    let places;
    try { places = JSON.parse(source.textContent); } catch (_) { places = []; }
    if (!Array.isArray(places) || !places.length) return;
    let started = false;

    function loadAssets() {
        const css = document.createElement('link');
        css.rel = 'stylesheet'; css.href = container.dataset.leafletCss;
        const js = document.createElement('script');
        js.src = container.dataset.leafletJs;
        const ready = Promise.all([
            new Promise((resolve, reject) => { css.onload = resolve; css.onerror = reject; }),
            new Promise((resolve, reject) => { js.onload = resolve; js.onerror = reject; })
        ]);
        document.head.appendChild(css);
        document.head.appendChild(js);
        return ready;
    }

    function showFallback() {
        container.hidden = true;
        if (fallback) fallback.hidden = false;
        status.textContent = 'Map tiles are unavailable. Use Browse places & map to continue.';
    }

    function start() {
        if (started) return;
        started = true;
        status.textContent = 'Loading the map preview…';
        loadAssets().then(() => {
            const valid = places.filter(place => Number.isFinite(place.latitude) && Number.isFinite(place.longitude) && Math.abs(place.latitude) <= 90 && Math.abs(place.longitude) <= 180);
            if (!valid.length || !window.L) throw new Error('No mapped places');
            const map = L.map(container, { scrollWheelZoom: false, attributionControl: true });
            const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
            });
            let failedTiles = 0;
            tiles.on('tileerror', () => {
                failedTiles += 1;
                if (failedTiles === 2) showFallback();
            });
            tiles.addTo(map);
            const bounds = [];
            const icon = L.divIcon({ className: '', html: '<span class="map-marker" aria-hidden="true"></span>', iconSize: [16,16], iconAnchor: [8,8] });
            valid.forEach(place => {
                const point = [place.latitude, place.longitude]; bounds.push(point);
                const content = document.createElement('div');
                const label = document.createElement('strong'); label.textContent = place.title;
                const link = document.createElement('a'); link.href = place.url; link.textContent = 'View place';
                content.append(label, document.createElement('br'), link);
                L.marker(point, { icon, title: place.title, alt: place.title }).addTo(map).bindPopup(content);
            });
            map.fitBounds(bounds, { padding: [28,28], maxZoom: 15, animate: false });
            status.textContent = `Showing ${valid.length} mapped place${valid.length === 1 ? '' : 's'} in this preview. Use Browse places & map to see more.`;
        }).catch(showFallback);
    }
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(entries => {
            if (entries.some(entry => entry.isIntersecting)) { observer.disconnect(); start(); }
        }, { rootMargin: '150px' });
        observer.observe(container);
    } else start();
})();
