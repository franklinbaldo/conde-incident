import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { coastline110mPart1 } from '../src/lib/coastline110mPart1.js';
import { coastline110mPart2 } from '../src/lib/coastline110mPart2.js';
import { coastline110mPart3 } from '../src/lib/coastline110mPart3.js';
import { splitDateline } from '../src/lib/mapGeometry.js';

const coastlines = [...coastline110mPart1, ...coastline110mPart2, ...coastline110mPart3];
const component = readFileSync(new URL('../src/components/map/OrbitalMapSvg.tsx', import.meta.url), 'utf8');
const map = readFileSync(new URL('../src/components/OrbitalMap.tsx', import.meta.url), 'utf8');
const generator = readFileSync(new URL('../scripts/build_coastline_110m.py', import.meta.url), 'utf8');

test('offline coastline is a deterministic generalized Natural Earth derivative, not hand-drawn polygons', () => {
  assert.equal(coastlines.length, 134);
  assert.equal(coastlines.flat().length, 2451);
  assert.match(generator, /ca96624a56bd078437bca8184e78163e5039ad19/);
  assert.match(generator, /851f581ff5ffb844deed8ae1a9ce22e3c4bb3d74fa342cadb5d8e39b41ae7c3c/);
  assert.match(component, /COASTLINES\.map\(/);
  assert.doesNotMatch(component, /const LAND\s*:/);
  for (const name of [1, 2, 3]) {
    const source = readFileSync(new URL(`../src/lib/coastline110mPart${name}.js`, import.meta.url));
    assert.ok(source.length < 20_000, `chunk ${name} exceeds file-size policy`);
    assert.match(source.toString(), /Natural Earth 1:110m coastline, public domain/);
  }
});

test('all coastlines have valid lat/lon pairs and no uncut antimeridian chord', () => {
  for (const polyline of coastlines) {
    assert.ok(polyline.length >= 2);
    for (const [longitude, latitude] of polyline) {
      assert.ok(Number.isFinite(longitude) && longitude >= -180 && longitude <= 180);
      assert.ok(Number.isFinite(latitude) && latitude >= -90 && latitude <= 90);
    }
    for (let i = 1; i < polyline.length; i++) {
      assert.ok(Math.abs(polyline[i][0] - polyline[i - 1][0]) <= 180);
    }
    // Same production geometry helper, so split-at-seam semantics stay compatible.
    splitDateline(polyline.map(([longitude, latitude]) => ({ longitude, latitude })));
  }
});

test('source/scale are disclosed in PT/EN and map remains quota-free', () => {
  assert.match(map, /Litoral Natural Earth 1:110m embarcado/);
  assert.match(map, /Bundled Natural Earth 1:110m coastlines/);
  assert.match(map, /domínio público/);
  assert.match(map, /public domain/);
  assert.match(map, /https:\/\/www\.naturalearthdata\.com\/downloads\/110m-physical-vectors\//);
  assert.doesNotMatch(component + map, /APIProvider|gmp-quota-exceeded|GooglePolyline|maps\.googleapis\.com/);
  assert.match(map, /C179#1/);
  assert.match(map, /C197#1/);
});
