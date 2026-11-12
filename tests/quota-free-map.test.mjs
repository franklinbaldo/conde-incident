import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { splitDateline, projectedSegments, projectFlat, projectGlobe, clampZoom } from '../src/lib/mapGeometry.js';

const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
const map = read('src/components/OrbitalMap.tsx');
const svg = read('src/components/map/OrbitalMapSvg.tsx');
const app = read('src/App.tsx');
const packageJson = JSON.parse(read('package.json'));

test('world map does not draw spurious transcontinental antimeridian lines', () => {
  const points = [
    { longitude: 170, latitude: 10 },
    { longitude: 179, latitude: 11 },
    { longitude: -179, latitude: 12 },
    { longitude: -160, latitude: 13 },
  ];
  const segments = splitDateline(points);
  assert.deepEqual(segments.map(s => s.length), [2, 2]);
  assert.equal(projectedSegments(points, projectFlat).length, 2);
});

test('unwrapped longitudes never draw a false antimeridian chord', () => {
  // Both sequences cross the 180° seam, even without prewrapped input.
  const eastbound = [
    { longitude: 179, latitude: 0 },
    { longitude: 181, latitude: 1 },
    { longitude: 190, latitude: 2 },
  ];
  const westbound = [
    { longitude: -179, latitude: 0 },
    { longitude: -181, latitude: 1 },
    { longitude: -190, latitude: 2 },
  ];
  assert.deepEqual(splitDateline(eastbound).map(s => s.length), [1, 2]);
  assert.deepEqual(splitDateline(westbound).map(s => s.length), [1, 2]);
  assert.deepEqual(splitDateline(eastbound)[1].map(p => p.longitude), [-179, -170]);
  assert.equal(projectedSegments(eastbound, projectFlat).length, 1);
  assert.equal(projectedSegments(westbound, projectFlat).length, 1);
  // Expected to remain one contiguous line if no seam is crossed.
  assert.deepEqual(splitDateline([{ longitude: 181, latitude: 0 },
    { longitude: 190, latitude: 1 }]).map(s => s.length), [2]);
});

test('invalid coordinates are discarded instead of painted as evidence', () => {
  assert.deepEqual(splitDateline([{ longitude: 1, latitude: 2 }, { longitude: NaN, latitude: 1 }, { longitude: 4, latitude: 5 }]).map(s => s.length), [1, 1]);
  assert.equal(projectedSegments([{ longitude: 1, latitude: 2 }], projectFlat).length, 0);
});

test('globe hides back hemisphere and longitude wraps', () => {
  assert.equal(projectGlobe(0, 0).visible, true);
  assert.equal(projectGlobe(180, 0).visible, false);
  assert.equal(projectFlat(190, 0).x, projectFlat(-170, 0).x);
});

test('zoom is bounded and rejects non-finite values', () => {
  assert.equal(clampZoom(999), 6);
  assert.equal(clampZoom(-10), 1);
  assert.equal(clampZoom(Number.NaN), 1);
});

test('all production map controls are local, accessible and quota free', () => {
  assert.ok(!(' @vis.gl/react-google-maps' in packageJson.dependencies));
  // The package stays in the untouched frozen legacy bun.lock until its separate migration.
  assert.equal(typeof packageJson.dependencies['@vis.gl/react-google-maps'], 'string');
  assert.doesNotMatch(map + svg + app, /@vis\.gl|APIProvider|gmp-quota-exceeded|GooglePolyline/);
  assert.match(map, /aria-pressed=/);
  assert.match(map, /type="range"/);
  assert.match(map, /type="date"/);
  assert.match(map, /type="checkbox"/);
  assert.match(svg, /role="img"/);
  assert.match(svg, /onPointerDown=/);
  assert.match(svg, /onPointerCancel=/);
  assert.match(svg, /onPan\(/);
  assert.match(svg, /onZoom\(/);
});

test('unknown reentry coordinates are not pinned; sources and limitations visible in both languages', () => {
  assert.doesNotMatch(map + app, /1963-11-08T19:48|CONDE_IMPACT_PASS_MS|showImpactBanner/);
  assert.match(map, /C197#1/);
  assert.match(map, /C179#1/);
  assert.match(map, /NÃO observações históricas/);
  assert.match(map, /NOT historical observations/);
  assert.match(map, /Nenhuma observação radar com posição\/erro autenticados/);
  assert.match(map, /No radar observation with an authenticated position\/error/);
  assert.match(map, /NORAD 527 e 529: vetores de cenário legado/);
});

test('no verified observation is turned into a point from a documentary-only decay day', () => {
  assert.doesNotMatch(svg, /OBS-08|decayLongitude|impactCoordinates/);
  assert.match(map, /noMarkers/);
  assert.match(map, /NONE|NÃO|Nenhuma/);
});
