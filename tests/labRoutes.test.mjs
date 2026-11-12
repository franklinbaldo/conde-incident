import test from 'node:test';
import assert from 'node:assert/strict';
import {
  resolveLabHash, hashForLabTab, evidenceRecordIds,
  evidenceRecordFromHash, hashForEvidenceRecord,
} from '../src/lib/labRoutes.ts';

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
test('each trace record has a stable, individually addressable route', () => {
  assert.equal(new Set(evidenceRecordIds).size, evidenceRecordIds.length);
  for (const id of evidenceRecordIds) {
    const url = hashForEvidenceRecord(id);
    assert.equal(evidenceRecordFromHash(url), id);
    assert.equal(evidenceRecordFromHash(url + '/'), id);
    assert.equal(resolveLabHash(url), 'research');
  }
});
test('reused matrix IDs need occurrence keys; arbitrary evidence routes are refused', () => {
  for (const bad of [
    '#/research/c44', '#/research/c45', '#/research/c46',
    '#/research/c01/unknown', '#/research/unknown', '#/research/../c01',
    '#/research/C01', '#/research/c01?claimed=true', '#/research/',
  ]) {
    assert.equal(evidenceRecordFromHash(bad), null, bad);
    assert.equal(resolveLabHash(bad), null, bad);
  }
  assert.throws(() => hashForEvidenceRecord('invented'), /desconhecida/);
});
