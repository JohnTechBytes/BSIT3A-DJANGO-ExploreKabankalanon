/* Run with: node tools/tests/test_map_guide.cjs */
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const layers = new Set(), requests = [];
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
let result = {code:'Ok', routes:[{distance:5000, geometry:{type:'LineString', coordinates:[[122,10],[122.1,10.2],[122.2,10.1]]}}],waypoints:[{distance:2},{distance:5}]};
const window = {setTimeout, clearTimeout, fetch: async (url, options) => { requests.push({url, options}); return {ok:true, json:async()=>result}; }};
const document = {createElement() { return {textContent: ''}; }};
vm.runInNewContext(fs.readFileSync('static/js/map-guide.js', 'utf8'), {window, document, Number, String, Date, AbortController});
const status = {textContent: ''};
const button = {hidden:true, addEventListener(event, cb) { this.click = cb; }};
const guide = window.EKMapGuide.create(map, L, status, button);
const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
  assert.equal(guide.setOrigin(91, 122, 'invalid'), false);
  assert.equal(guide.setOrigin(null, 122, 'invalid'), false);
  assert.equal(guide.setOrigin(10, 122, 'your location'), true);
  assert.equal(requests.length, 0);
  assert.equal(guide.setDestination(10.1, 122.2, '<Place>'), true);
  await wait(450);
  assert.equal(requests.length, 1);
  assert.match(requests[0].url, /122,10;122.2,10.1/);
  assert.equal(requests[0].options.credentials, 'omit');
  assert.equal([...layers].filter(x => x.type === 'line').length, 1);
  assert.match(status.textContent, /5.0 km on mapped roads/);
  assert.match(status.textContent, /<Place>/); // textContent, not HTML
  assert.equal(guide.fit(), true);
  assert.equal(map.fitOptions.animate, false);
  guide.setDestination(10.2, 122.3, 'Second');
  guide.setDestination(10.3, 122.4, 'Third');
  await wait(1250);
  assert.equal(requests.length, 2); // rapid selections coalesced
  assert.match(requests[1].url, /122.4,10.3/);
  assert.equal([...layers].filter(x => x.type === 'line').length, 1);
  result = {code:'NoRoute', routes:[]};
  guide.setDestination(10.4, 122.5, 'No route');
  await wait(1250);
  assert.match(status.textContent, /Road route unavailable/);
  assert.equal([...layers].filter(x => x.type === 'line').length, 0);
  assert.equal(button.hidden, false);
  result = {code:'Ok', routes:[{distance:1000, geometry:{type:'LineString',coordinates:[[122,10],[122.5,10.4]]}}],waypoints:[{distance:300}]};
  button.click(); await wait(1250);
  assert.match(status.textContent, /over 200 m/);
  assert.equal(button.hidden, true);
  guide.setDestination(10.5, 122.6, 'cancelled');
  guide.pause();
  await wait(1250);
  assert.equal(requests.length, 4);
  guide.clearDestination();
  guide.resume();
  assert.equal([...layers].filter(x => x.type === 'line').length, 0);
  assert.equal(guide.fit(), false);

  // Even if a transport ignores abort and returns late, it cannot restore a
  // stale route after a different destination or after the map was closed.
  let completeOld;
  window.fetch = () => new Promise(resolve => { completeOld = resolve; });
  guide.setDestination(10.6, 122.7, 'stale');
  await wait(1250);
  assert.equal(typeof completeOld, 'function');
  guide.pause();
  completeOld({ok:true, json: async () => result});
  await wait(20);
  assert.equal([...layers].filter(x => x.type === 'line').length, 0);
  guide.clearDestination();
  guide.resume();
  console.log('Road route guide unit tests passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
