/* Driving road routes from the public OSRM demo, not turn-by-turn navigation. */
(function (window) {
  'use strict';
  // The demo policy permits no more than one request per second.
  let lastRequestAt = 0;
  const endpoint = 'https://router.project-osrm.org/route/v1/driving/';

  function create(map, L, status, retryButton) {
    let origin = null, destination = null, originMarker = null, line = null;
    let roadPoints = null, controller = null, timer = null, generation = 0, paused = false;

    function point(lat, lng) {
      if (lat === null || lng === null || lat === '' || lng === '') return null;
      lat = Number(lat); lng = Number(lng);
      return Number.isFinite(lat) && Number.isFinite(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180
        ? [lat, lng] : null;
    }
    function message(text) { if (status) status.textContent = text; }
    function showRetry(show) { if (retryButton) retryButton.hidden = !show; }
    function cancel() {
      generation += 1;
      if (timer !== null) { window.clearTimeout(timer); timer = null; }
      if (controller) { controller.abort(); controller = null; }
    }
    function removeLine() {
      if (line) map.removeLayer(line);
      line = null;
      roadPoints = null;
    }
    function fit() {
      if (!origin || !destination) return false;
      const points = roadPoints ? roadPoints.concat([origin.point, destination.point]) : [origin.point, destination.point];
      if (points.every(p => p[0] === points[0][0] && p[1] === points[0][1])) {
        map.setView(destination.point, 16, {animate: false});
      } else {
        map.fitBounds(L.latLngBounds(points).pad(.12), {maxZoom: 16, animate: false});
      }
      return true;
    }
    function update() {
      cancel();
      removeLine();
      showRetry(false);
      if (paused) return;
      if (!origin || !destination) {
        message(origin ? 'Starting point set: ' + origin.label + '. Select a place to request a driving route.'
          : 'Select a place and use your location to request a driving route.');
        return;
      }
      const version = generation;
      message('Requesting a driving route from OSRM…');
      // Coalesce quick selection changes and respect the demo rate limit.
      const delay = Math.max(300, lastRequestAt + 1100 - Date.now());
      timer = window.setTimeout(async function () {
        timer = null;
        if (version !== generation || paused) return;
        lastRequestAt = Date.now();
        const request = new AbortController();
        controller = request;
        let timedOut = false;
        const timeout = window.setTimeout(function () { timedOut = true; request.abort(); }, 12000);
        try {
          const coords = [origin.point, destination.point].map(p => p[1] + ',' + p[0]).join(';');
          const response = await window.fetch(endpoint + coords + '?overview=full&geometries=geojson&steps=false', {
            signal: request.signal, credentials: 'omit', referrerPolicy: 'no-referrer'
          });
          if (!response.ok) throw new Error('Routing service unavailable');
          const data = await response.json();
          const route = data && data.code === 'Ok' && Array.isArray(data.routes) && data.routes[0];
          const coordsList = route && route.geometry && route.geometry.type === 'LineString' && route.geometry.coordinates;
          if (!route || !Array.isArray(coordsList) || coordsList.length < 2 || coordsList.length > 100000 ||
              !Number.isFinite(route.distance) || route.distance < 0) throw new Error('No driving route');
          const points = coordsList.map(pair => Array.isArray(pair) ? point(pair[1], pair[0]) : null);
          if (points.some(p => !p)) throw new Error('Invalid road geometry');
          if (version !== generation || paused) return;
          roadPoints = points;
          line = L.polyline(points, {color: '#1756a0', weight: 5, opacity: .95,
            interactive: false, className: 'ek-road-route'}).addTo(map);
          const snappedFar = Array.isArray(data.waypoints) && data.waypoints.some(w => Number.isFinite(w.distance) && w.distance > 200);
          message('Estimated driving route from ' + origin.label + ' to ' + destination.label + ': ' +
            (route.distance / 1000).toFixed(1) + ' km on mapped roads. ' +
            (snappedFar ? 'A point is over 200 m from the nearest mapped road; check access. ' : '') +
            'OSRM / OpenStreetMap data may be incomplete; this is not turn-by-turn navigation.');
          fit();
        } catch (error) {
          if (version !== generation || paused) return;
          message((timedOut ? 'The road route request timed out. ' : 'Road route unavailable. ') +
            'No route line is shown. Check your connection or try again; you can also open Directions.');
          showRetry(true);
        } finally {
          window.clearTimeout(timeout);
          if (controller === request) controller = null;
        }
      }, delay);
    }
    if (retryButton) retryButton.addEventListener('click', update);
    return {
      setOrigin(lat, lng, label) {
        const coords = point(lat, lng);
        if (!coords) return false;
        if (origin && origin.point[0] === coords[0] && origin.point[1] === coords[1] && origin.label === String(label)) return true;
        origin = {point: coords, label: String(label)};
        if (originMarker) map.removeLayer(originMarker);
        originMarker = L.circleMarker(coords, {radius: 8, color: '#ffffff', weight: 3,
          fillColor: '#28547e', fillOpacity: 1, className: 'ek-origin-marker'}).addTo(map);
        const text = document.createElement('span');
        text.textContent = 'Starting point: ' + origin.label;
        originMarker.bindPopup(text);
        update();
        return true;
      },
      setDestination(lat, lng, label) {
        const coords = point(lat, lng);
        if (!coords) return false;
        if (destination && destination.point[0] === coords[0] && destination.point[1] === coords[1] && destination.label === String(label)) return true;
        destination = {point: coords, label: String(label)};
        update();
        return true;
      },
      clearDestination() { destination = null; update(); },
      hasOrigin() { return !!origin; },
      fit,
      pause() { paused = true; cancel(); showRetry(false); },
      resume() { if (paused) { paused = false; if (!line) update(); } }
    };
  }
  window.EKMapGuide = {create};
})(window);
