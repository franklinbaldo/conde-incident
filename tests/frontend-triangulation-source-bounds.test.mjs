import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const read = (file) => readFileSync(new URL(file, import.meta.url), 'utf8');
const tri = read('../src/components/TriangulationDashboard.tsx');
const app = read('../src/App.tsx');

test('triangulation is a reachable site route, not an unused legacy string', () => {
  // A lazily imported route is still reachable; the compiled graph is audited separately.
  assert.match(app, /import\('\.\/components\/TriangulationDashboard'\)/);
  assert.match(app, /activeTab === 'triangulation'/);
  assert.match(app, /<TriangulationDashboard lang=\{lang\}/);
});

test('the 528 comparison is tied to genuine documentary references', () => {
  assert.match(tri, /19640001198\/downloads\/19640001198\.pdf/);
  assert.match(tri, /19640019314\/downloads\/19640019314\.pdf/);
  assert.match(tri, /C179#1/);
  assert.match(tri, /C197#1/);
  assert.match(tri, /GCAT/);
  assert.match(tri, /secondary-mirror TLE/);
});

test('neither branch promotes legacy orbits to observed reentry bounds', () => {
  assert.match(tri, /does not determine a reentry time, location or corridor/);
  assert.match(tri, /não determina hora, local ou corredor/);
  assert.match(tri, /uncalibrated assumptions/);
  assert.match(tri, /não calibradas/);
  assert.doesNotMatch(tri, /1963-11-08T19:48|19:48 UTC|certeza absoluta|strictly bounded|balizas geográficas|O que PROVA/);
  assert.doesNotMatch(tri, /CONDE_COORDINATES|computeInterTrackProximity/);
});

test('exploratory controls update date without asserting a measured time', () => {
  assert.match(tri, /EPOCH_528_MS \+ dayOffset \* DAY_MS/);
  assert.match(tri, /id="triangulation-day"/);
  assert.match(tri, /aria-valuetext=\{formatDate\(instant\)\}/);
  assert.match(tri, /value=\{dayOffset\}/);
  assert.match(tri, /onChange=\{\(e\) => setDayOffset\(Number\(e\.target\.value\)\)\}/);
  assert.match(tri, /historical observation/);
  assert.match(tri, /observação histórica/);
  assert.match(tri, /aria-live="off"/);
});

