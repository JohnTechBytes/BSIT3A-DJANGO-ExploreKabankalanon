/* Run with: node tools/tests/test_map_guide.cjs */
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const layers = new Set();
const map = {
  removeLayer(layer) { layers.delete(layer); },
  fitBounds(bounds, options) { this.bounds = bounds; this.fitOptions = options; },
  setView(coords, zoom) { this.view = {coords, zoom}; }
};
const L = {
  circleMarker(coords, style) { return layer('origin', coords, style); },
  polyline(coords, style) { return layer('line', coords, style); },
  latLngBounds(coords) { return {coords, pad() { return this; }}; }
};
function layer(type, coords, style) {
  return {type, coords, style, addTo() { layers.add(this); return this; }, bindPopup(popup) { this.popup = popup; return this; }};
}
const window = {};
const document = {createElement() { return {textContent: ''}; }};
vm.runInNewContext(fs.readFileSync('static/js/map-guide.js', 'utf8'), {window, document, Number, String});
const status = {textContent: ''};
const guide = window.EKMapGuide.create(map, L, status);
assert.equal(guide.setOrigin(91, 122, 'invalid'), false);
assert.equal(layers.size, 0);
assert.equal(guide.setOrigin(10, 122, 'your location'), true);
assert.equal(layers.size, 1);
assert.equal(guide.setDestination(10.1, 122.2, '<Place>'), true);
assert.equal([...layers].filter(x => x.type === 'line').length, 1);
assert.match(status.textContent, /not a road route or navigation/);
assert.match(status.textContent, /<Place>/); // textContent, never interpreted as HTML
assert.equal(guide.fit(), true);
assert.equal(map.fitOptions.animate, false);
guide.setDestination(10.2, 122.3, 'Next');
assert.equal([...layers].filter(x => x.type === 'line').length, 1);
guide.setOrigin(10.2, 122.3, 'Updated location');
assert.equal(layers.size, 2);
guide.fit();
assert.equal(map.view.zoom, 16);
guide.clearDestination();
assert.equal([...layers].filter(x => x.type === 'line').length, 0);
assert.equal(guide.fit(), false);
console.log('Map guide unit tests passed.');
