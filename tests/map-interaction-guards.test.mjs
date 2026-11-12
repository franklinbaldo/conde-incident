import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { canPanWithPointer, shouldShowScenarioConnections } from '../src/lib/mapInteraction.js';

const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');

test('scenario links never outlive the 527/529 visibility layer', () => {
  for (const connections of [false, true]) {
    for (const sisters of [false, true]) {
      for (const primary of [false, true]) {
        assert.equal(
          shouldShowScenarioConnections(connections, sisters, primary),
          connections && sisters && primary,
        );
      }
    }
  }
  const svg = read('src/components/map/OrbitalMapSvg.tsx');
  assert.match(svg, /shouldShowScenarioConnections\(showConnections, showSisters, Boolean\(positions\[528\]\)\)/);
});

test('touch keeps native mobile scrolling; mouse and pen can pan', () => {
  assert.equal(canPanWithPointer('touch'), false);
  assert.equal(canPanWithPointer('mouse'), true);
  assert.equal(canPanWithPointer('pen'), true);
  assert.equal(canPanWithPointer(''), false);
  const svg = read('src/components/map/OrbitalMapSvg.tsx');
  const parent = read('src/components/OrbitalMap.tsx');
  assert.match(svg, /canPanWithPointer\(event.pointerType\)/);
  assert.match(svg, /touchAction: 'pan-y'/);
  assert.doesNotMatch(svg, /onWheel=/);
  assert.match(parent, /No celular, deslize para rolar a página/);
  assert.match(parent, /On mobile, swipe to scroll the page/);
  assert.match(parent, /setZoom\(/);
});
