import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveLabHash, hashForLabTab } from '../src/lib/labRoutes.ts';

test('no fragment opens the summary without inventing a source', () => {
  assert.equal(resolveLabHash(''), 'summary');
  assert.equal(resolveLabHash('#'), 'summary');
});
test('map and documentary views have copyable, round-trip URLs', () => {
  for (const tab of ['research', 'map', 'summary', 'inverse', 'triangulation', 'sensitivity', 'montecarlo', 'tles', 'documents']) {
    assert.equal(resolveLabHash(hashForLabTab(tab)), tab);
  }
});
test('a missing view is not silently translated into another tab', () => {
  for (const bad of ['#/evidence', '#/missing', '#/map/extra', '#/map?x=1', '#/../map', '#/MAP', '#/']) {
    assert.equal(resolveLabHash(bad), null, bad);
  }
});
test('internal modal does not gain a fabricated public route', () => {
  assert.throws(() => hashForLabTab('python'), /rota pública/);
});

test('the evidence tab is an implemented deep link, not a nonexistent promise', () => {
  assert.equal(hashForLabTab('research'), '#/research');
  assert.equal(resolveLabHash('#/research/'), 'research');
});
