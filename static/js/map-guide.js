/* A local, straight-line map guide. This is not routing or turn-by-turn navigation. */
(function (window) {
  'use strict';
  function create(map, L, status) {
    let origin = null;
    let destination = null;
    let originMarker = null;
    let line = null;

    function point(lat, lng) {
      lat = Number(lat); lng = Number(lng);
      return Number.isFinite(lat) && Number.isFinite(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180
        ? [lat, lng] : null;
    }
    function update() {
      if (line) { map.removeLayer(line); line = null; }
      if (origin && destination) {
        line = L.polyline([origin.point, destination.point], {
          color: '#28547e', weight: 4, opacity: .9, dashArray: '8 8',
          interactive: false, className: 'ek-straight-guide'
        }).addTo(map);
        if (status) status.textContent = 'Straight-line guide from ' + origin.label + ' to ' + destination.label + '. This is not a road route or navigation.';
      } else if (status) {
        status.textContent = origin
          ? 'Starting point set: ' + origin.label + '. Select a place to show a straight-line guide.'
          : 'Select a place and use your location to show a straight-line guide. It does not follow roads.';
      }
    }
    return {
      setOrigin(lat, lng, label) {
        const coords = point(lat, lng);
        if (!coords) return false;
        origin = {point: coords, label: String(label)};
        if (originMarker) map.removeLayer(originMarker);
        originMarker = L.circleMarker(coords, {
          radius: 8, color: '#ffffff', weight: 3, fillColor: '#28547e', fillOpacity: 1,
          className: 'ek-origin-marker'
        }).addTo(map);
        const text = document.createElement('span');
        text.textContent = 'Starting point: ' + origin.label;
        originMarker.bindPopup(text);
        update();
        return true;
      },
      setDestination(lat, lng, label) {
        const coords = point(lat, lng);
        if (!coords) return false;
        destination = {point: coords, label: String(label)};
        update();
        return true;
      },
      clearDestination() { destination = null; update(); },
      hasOrigin() { return !!origin; },
      fit() {
        if (!origin || !destination) return false;
        if (origin.point[0] === destination.point[0] && origin.point[1] === destination.point[1]) {
          map.setView(destination.point, 16, {animate: false});
        } else {
          map.fitBounds(L.latLngBounds([origin.point, destination.point]).pad(.18), {maxZoom: 16, animate: false});
        }
        return true;
      }
    };
  }
  window.EKMapGuide = {create};
})(window);
