import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const custody = JSON.parse(readFileSync('research/archive/wayback_pilot_2026-11-12.json', 'utf8'));
const ui = readFileSync('src/components/DocumentArchive.tsx', 'utf8');

test('Wayback panel uses authoritative manifest and accessible links', () => {
  assert.match(ui, /import custody from/);
  assert.match(ui, /custody\.records\.filter/);
  assert.match(ui, /aria-labelledby="custody-heading"/);
  assert.match(ui, /<time dateTime=/);
  assert.match(ui, /rel="noopener noreferrer"/);
  assert.match(ui, /r\.replay\?\.sha256/);
  assert.match(ui, /no exact-URL capture/);
});
test('two distinct archival replays and a delimited negative; no historical inference', () => {
  assert.equal(custody.rules.historical_authentication, false);
  assert.equal(custody.rules.no_new_orbital_constraint, true);
  const verified = custody.records.filter(r => r.status === 'VERIFIED_REPLAY');
  assert.equal(verified.length, 2);
  for (const r of verified) {
    assert.ok(r.archived_url.startsWith('https://web.archive.org/web/'));
    assert.match(r.replay.sha256, /^[a-f0-9]{64}$/);
    assert.equal(r.replay.sha1_base32, r.cdx_record.digest);
  }
  const nasa = custody.records.find(r => r.id === 'WB-NASA-SSR-19631115');
  assert.equal(nasa.status, 'NO_EXACT_CAPTURE_IN_QUERIED_INDEX');
  assert.equal(nasa.archived_url, null);
  assert.equal(nasa.replay, null);
  assert.match(ui, /isso não prova ausência do documento/);
});
