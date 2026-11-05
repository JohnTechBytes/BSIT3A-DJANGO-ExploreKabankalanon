/* Map a recorded destination; never request the visitor's location. */
(() => {
  const element = document.getElementById('pd-place-map');
  const status = document.getElementById('pd-map-status');
  if (!element || !status) return;
  const lat = Number(element.dataset.lat);
  const lng = Number(element.dataset.lng);
  if (!window.L || !Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) {
    status.textContent = 'The map could not load. Use the Google Maps links below.';
    return;
  }
  try {
    const map = L.map(element, {scrollWheelZoom: false}).setView([lat, lng], 16);
    const tiles = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      referrerPolicy: 'origin',
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
    });
    let errors = 0;
    tiles.on('tileerror', () => {
      if (++errors === 2) status.textContent = 'Map tiles could not load. Use the Google Maps links below.';
    });
    tiles.addTo(map);
    const popup = document.createElement('strong');
    popup.textContent = element.dataset.title || 'Destination';
    L.circleMarker([lat, lng], {radius: 9, color: '#0757d8', fillColor: '#0d9488', fillOpacity: 0.95, weight: 3})
      .addTo(map).bindPopup(popup);
    status.textContent = 'The pin shows the recorded destination coordinates.';
  } catch (_) {
    status.textContent = 'The map could not load. Use the Google Maps links below.';
  }
})();
