// Run with jsdom installed: node tools/tests/nearby_map_jsdom.cjs
// Exercises the real inline Nearby script with a stub Leaflet; this is not a
// layout, tile-provider or real-browser test.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');
const template = fs.readFileSync('templates/places/nearby_places.html', 'utf8');
const script = template.match(/<script>\s*\(function \(\) \{[\s\S]*?<\/script>/)[0]
  .replace(/^<script>/, '').replace(/<\/script>$/, '').replace(/\{%[^%]*%\}/g, '/static/mock').replace(/\{\{[^}]*\}\}/g, '');

function setup(reduced) {
  const card = (id, lat) => `<article class="ea6-card" data-lat="${lat}" data-lng="122.8" data-title="Place ${id}" data-detail-url="/p/${id}"><div class="ea6-cover" role="button" tabindex="0"></div><span class="ea6-distance"></span><button class="ea6g-card-map">Map</button></article>`;
  const dom = new JSDOM(`<div id="ea6g-layout"><div id="ea6-results">${card(1,9.8)}${card(2,9.9)}<article class="ea6-card"><div class="ea6-cover"></div></article></div><aside id="ea6g-map-shell" tabindex="-1" hidden><div id="ea6g-map"></div></aside></div><button id="ea6g-toggle" aria-expanded="false"></button><button id="ea6g-fit"></button><p id="ea6g-count"></p><p id="ea6g-map-status"></p><div id="ea6-drone-hud" hidden></div><span id="ea6-drone-target"></span>`, {runScripts:'outside-only'});
  const {window:w} = dom, document = w.document;
  w.matchMedia = () => ({matches:reduced});
  let scrolls = [];
  w.HTMLElement.prototype.scrollIntoView = function(opts) { scrolls.push([this.id,opts.behavior]); };
  let events = {}, lastFlight = null, popups = [];
  const layers = new Set();
  const map = {
    invalidateSize(){}, getZoom(){return 12}, setView(pos){ lastFlight = pos; return this; },
    fitBounds(){return this;}, hasLayer(x){return layers.has(x)}, removeLayer(x){layers.delete(x)},
    stop(){ return this; }, once(name,cb){ events[name] = cb; }, off(name,cb){if (events[name] === cb) delete events[name]},
    flyTo(pos){lastFlight = pos;}, finish(){const cb = events.moveend; delete events.moveend; cb?.();}
  };
  function layer() { return { on(){return this}, addTo(){return this}, bindPopup(){return this}, setStyle(){return this}, setPopupContent(){return this}, remove(){}, getLatLng(){return []}, openPopup(){popups.push(this.title)} }; }
  let markers = [];
  w.L = {map:()=>map, tileLayer:()=>layer(), layerGroup:()=>layer(), control:{layers:()=>layer()},
    latLngBounds:()=>({pad(){return this}}), circleMarker(pos, opts){const l=layer(); if(opts.radius===9){l.title=pos[0]; markers.push(l)} return l;}};
  w.eval(script);
  return {w, document, map, scrolls, popups, markers, getFlight:()=>lastFlight, close:()=>dom.window.close()};
}
const tick = () => new Promise(resolve => setImmediate(resolve));
(async () => {
  for (const reduced of [false,true]) {
    const t=setup(reduced), cards=t.document.querySelectorAll('.ea6-card'), shell=t.document.querySelector('#ea6g-map-shell');
    cards[0].querySelector('.ea6-cover').click();
    await tick();
    assert.equal(shell.hidden,false);
    assert.equal(t.document.activeElement,shell);
    assert.deepEqual(t.scrolls[0], ['ea6g-map-shell', reduced ? 'auto' : 'smooth']);
    assert.equal(t.getFlight()[0],9.8);
    if (!reduced) t.map.finish();
    assert.deepEqual(t.popups,[9.8]);
    cards[1].querySelector('.ea6-cover').dispatchEvent(new t.w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    await tick();
    assert.equal(t.getFlight()[0],9.9);
    if (!reduced) t.map.finish();
    assert.deepEqual(t.popups,[9.8,9.9]);
    t.close();
  }
  const t=setup(false), cards=t.document.querySelectorAll('.ea6-card');
  cards[0].querySelector('button').click();
  cards[1].querySelector('button').click();
  await tick();
  assert.equal(t.getFlight()[0],9.9);
  t.map.finish();
  assert.deepEqual(t.popups,[9.9], 'a stale selection must never open its popup');
  cards[0].querySelector('button').click();
  t.document.querySelector('#ea6g-toggle').click();
  await tick();
  assert.equal(t.document.querySelector('#ea6g-map-shell').hidden,true);
  assert.deepEqual(t.popups,[9.9], 'closing cancels pending selection');
  cards[2].querySelector('.ea6-cover').click();
  await tick();
  assert.equal(t.document.querySelector('#ea6g-map-shell').hidden,true);
  t.close();
  console.log('Nearby map interaction checks passed (jsdom + mocked Leaflet).');
})().catch(error => {console.error(error); process.exitCode=1;});
