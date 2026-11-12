import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { sgp4ReferenceAtUtc, validTleChecksum } from '../src/lib/orbitSgp4Baseline.ts';

// C179#1: literal secondary mirror, same lineage as the retrospective Parquet.
// The SHA checks custody of THESE BYTES, not 1963 NORAD authenticity.
const raw = readFileSync(new URL('../research/tle_custody/mirror_528_1963-10-27.tle', import.meta.url));
const sha = '18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd';
const [line1, line2] = raw.toString('utf8').trimEnd().split('\n');
const source = {
  norad: 528, line1, line2, occurrence: 'C179#1',
  sourceUrl: 'https://www.itau.magnetic-declination.com/satellite/?s=528',
  sourceSha256: sha, sourceClass: 'SECONDARY_LITERAL',
};
const epoch = '1963-10-27T14:40:16.132Z';
const at = (seconds) => sgp4ReferenceAtUtc(source,
  new Date(Date.parse(epoch) + seconds * 1000).toISOString());

test('pinned 528 bytes are intact and both TLE checksums pass', () => {
  assert.equal(createHash('sha256').update(raw).digest('hex'), sha);
  assert.equal(validTleChecksum(line1), true);
  assert.equal(validTleChecksum(line2), true);
  assert.equal(line1.slice(2, 7), '00528');
});

test('SGP4 returns a finite TEME r/v model with dimensional rate consistency', () => {
  const zero = at(0), minus = at(-1), plus = at(1);
  for (const sample of [zero, minus, plus]) {
    assert.equal(sample.status, 'SECONDARY_MODEL_ONLY');
    assert.equal(sample.frame, 'TEME');
    assert.equal(sample.model, 'SGP4');
    assert.equal(sample.sourceOccurrence, 'C179#1');
    assert.equal(sample.custody, 'DECLARED_DIGEST_NOT_AUTHENTICATED');
    assert.equal(sample.independentHistoricalHoldout, 'NOT_RUN');
    assert.equal(sample.impactInference, 'NOT_SUPPORTED');
    assert.ok(Math.hypot(...sample.stateTeme.rKm) > 6500);
    assert.ok(Math.hypot(...sample.stateTeme.vKmS) > 6);
  }
  assert.ok(Math.abs(zero.tleAgeDays) < 1e-6);
  // Independent central finite difference of model TEME position, not SGP4
  // self-comparison; this detects accidental m/s vs km/s or minutes vs seconds.
  const fd = zero.stateTeme.vKmS.map((_, axis) =>
    (plus.stateTeme.rKm[axis] - minus.stateTeme.rKm[axis]) / 2);
  assert.ok(Math.hypot(...fd.map((v, i) => v - zero.stateTeme.vKmS[i])) < 0.02);
});

test('SGP4 never injects the historical decay day as an observed time cutoff', () => {
  const later = sgp4ReferenceAtUtc(source, '1963-11-09T00:00:00.000Z');
  // A long extrapolation may fail numerically: neither case identifies a
  // terminal position or converts the catalogue date into a timestamp.
  assert.ok(['SECONDARY_MODEL_ONLY', 'SGP4_UNRESOLVED'].includes(later.status));
  assert.equal(later.impactInference, 'NOT_SUPPORTED');
  assert.equal(later.independentHistoricalHoldout, 'NOT_RUN');
  assert.ok(later.tleAgeDays > 12);
});

test('scenario placeholders are not treated as instrumental or secondary TLE results', () => {
  const legacy = sgp4ReferenceAtUtc({ ...source, sourceClass: 'SCENARIO_PLACEHOLDER' }, epoch);
  assert.equal(legacy.status, 'SOURCE_NOT_ADMISSIBLE');
  assert.equal(legacy.stateTeme, null);
});

test('rejects altered TLE checksum, identity, epoch and absent custody', () => {
  assert.throws(() => sgp4ReferenceAtUtc({ ...source, line2: line2.slice(0, -1) + '0' }, epoch), /Invalid source/);
  assert.throws(() => sgp4ReferenceAtUtc({ ...source, norad: 527 }, epoch), /Invalid source/);
  assert.throws(() => sgp4ReferenceAtUtc({ ...source, sourceSha256: 'invalid' }, epoch), /Invalid source/);
  assert.throws(() => sgp4ReferenceAtUtc({ ...source, occurrence: '' }, epoch), /Invalid source/);
  assert.throws(() => sgp4ReferenceAtUtc(source, '1963-11-08'), /explicit ISO-8601/);
});
