import test from 'node:test';
import assert from 'node:assert/strict';
import {
  opticalAngularSeparationArcsec, auditFutureOpticalDirections,
} from '../src/lib/orbitOpticalHoldout.ts';

const cutoff = '1963-11-07T00:00:00Z';
const epoch = '1963-11-09T02:00:00Z';
const base = [6378, 0, 0];
const hash = 'a'.repeat(64);
const direction = (ra, dec) => {
  const a = ra * Math.PI / 180, d = dec * Math.PI / 180;
  return [1000 * Math.cos(d) * Math.cos(a),
    1000 * Math.cos(d) * Math.sin(a), 1000 * Math.sin(d)];
};
const input = (ra = 0, dec = 0) => ({
  kind: 'INSTRUMENT_ANGULAR', custody: 'SYNTHETIC',
  objectNorad: 529, matrixOccurrence: 'SYNTHETIC-G36-A',
  sourceUrl: 'https://example.invalid/fixture.pdf', sourcePdfSha256: hash,
  lineageRoot: 'SYNTHETIC_LINEAGE', instrumentRecordId: 'synthetic-film-01',
  calibrationReference: 'SYNTHETIC angular calibration',
  observedEpochUtc: epoch, frame: 'GCRF',
  rightAscensionDeg: ra, declinationDeg: dec, angularSigmaArcsec: 3,
  stationPositionKm: base, stationFrame: 'GCRF',
  stationEpochUtc: epoch, stationEphemerisReference: 'SYNTHETIC station in GCRF',
});
const predicted = (ra = 0, dec = 0) => {
  const d = direction(ra, dec);
  return { objectNorad: 529, epochUtc: epoch, frame: 'GCRF',
    rKm: [base[0] + d[0], base[1] + d[1], base[2] + d[2]] };
};
const control = { objectNorad: 529, frame: 'GCRF', cutoffEpochUtc: cutoff };
const audited = (o, p = predicted()) =>
  auditFutureOpticalDirections([o], [p], control);

test('conditional exact synthetic optical directions do not authenticate historical tracks', () => {
  const result = audited(input());
  assert.equal(result.status, 'CONDITIONAL_GEOMETRY_ONLY');
  assert.equal(result.points.length, 1);
  assert.ok(result.points[0].residualArcsec < 1e-7);
  assert.equal(result.originalInstrumentAuthenticated, false);
  assert.equal(result.independentTrackingConfirmed, false);
  assert.equal(result.stationEphemerisAuthenticated, false);
  assert.equal(result.dynamicPropagationAuthenticated, false);
  assert.equal(result.historicalHoldout, 'NOT_VALIDATED');
  assert.equal(result.impactInference, 'NOT_SUPPORTED');
  assert.equal(result.lightTimeAberrationRefraction, 'NOT_MODELED');
});

test('great-circle angular residual wraps right ascension at zero without 360-degree error', () => {
  const result = audited(input(359.999, 0), predicted(0.001, 0));
  assert.equal(result.status, 'CONDITIONAL_GEOMETRY_ONLY');
  assert.ok(Math.abs(result.points[0].residualArcsec - 7.2) < 1e-5);
  assert.ok(Math.abs(result.points[0].residualOverDeclaredSigma - 2.4) < 1e-5);
  const nearPole = opticalAngularSeparationArcsec(0, 89.999, direction(180, 89.999));
  assert.ok(Math.abs(nearPole - 7.2) < 1e-5, 'RA 180deg changes near-polar direction by only 0.002deg');
});

test('zero line of sight or invalid angular observation blocks whole batch', () => {
  for (const bad of [
    { rightAscensionDeg: 360 }, { rightAscensionDeg: -1 },
    { declinationDeg: 90.01 }, { angularSigmaArcsec: 0 },
    { angularSigmaArcsec: NaN }, { declinationDeg: null },
  ]) {
    const r = audited({ ...input(), ...bad });
    assert.equal(r.status, 'BLOCKED');
    assert.deepEqual(r.points, []);
    assert.equal(r.traces[0].reason, 'INVALID_ANGULAR_MEASUREMENT');
  }
  const coincident = audited(input(), { ...predicted(), rKm: base });
  assert.equal(coincident.traces[0].reason, 'DEGENERATE_LINE_OF_SIGHT');
  assert.throws(() => opticalAngularSeparationArcsec(0, 0, [0, 0, 0]), RangeError);
});

test('NASA catalog and secondary mirror may not masquerade as instrument angles', () => {
  for (const bad of [
    { kind: 'DECAY_CATALOG' }, { kind: 'CATALOG_ELEMENT' },
    { custody: 'SECONDARY' }, { custody: 'CATALOG' },
  ]) {
    assert.equal(audited({ ...input(), ...bad }).traces[0].reason,
      'NOT_INSTRUMENT_OBSERVATION');
  }
  for (const bad of [
    { sourcePdfSha256: '' }, { sourceUrl: 'http://not-a-custody-chain' },
    { calibrationReference: '' }, { lineageRoot: '' }, { instrumentRecordId: '' },
  ]) assert.equal(audited({ ...input(), ...bad }).traces[0].reason,
    'MISSING_DOCUMENTARY_CUSTODY');
});

test('publication day is not an observation timestamp: no substitution accepted', () => {
  assert.equal(audited({ ...input(), observedEpochUtc: null }).traces[0].reason,
    'INVALID_OBSERVATION_EPOCH');
  assert.equal(audited({ ...input(), observedEpochUtc: '1963-11-08T00:00:00Z' })
    .traces[0].reason, 'FRAME_OR_EPOCH_MISMATCH');
  assert.equal(audited({ ...input(), observedEpochUtc: cutoff,
    stationEpochUtc: cutoff }, { ...predicted(), epochUtc: cutoff })
    .traces[0].reason, 'NOT_FUTURE_HOLDOUT');
  assert.equal(audited({ ...input(), stationEpochUtc: '1963-11-09T02:00:01Z' })
    .traces[0].reason, 'FRAME_OR_EPOCH_MISMATCH');
  assert.equal(audited({ ...input(), observedEpochUtc: '1963-11-31T02:00:00Z' })
    .traces[0].reason, 'INVALID_OBSERVATION_EPOCH');
});

test('station frame, frame, object, and calibration must match exactly', () => {
  for (const bad of [
    { frame: 'TEME' }, { stationFrame: 'TEME' }, { objectNorad: 527 },
  ]) assert.equal(audited({ ...input(), ...bad }).traces[0].reason,
    'FRAME_OR_EPOCH_MISMATCH');
  assert.equal(audited(input(), { ...predicted(), frame: 'TEME' })
    .traces[0].reason, 'FRAME_OR_EPOCH_MISMATCH');
  assert.equal(audited({ ...input(), stationPositionKm: null })
    .traces[0].reason, 'MISSING_STATION_EPHEMERIS');
  assert.equal(audited({ ...input(), stationEphemerisReference: '' })
    .traces[0].reason, 'MISSING_STATION_EPHEMERIS');
  assert.equal(audited({ ...input(), stationPositionKm: [0, 0, 0] })
    .traces[0].reason, 'MISSING_STATION_EPHEMERIS');
});

test('duplicates and one invalid record veto the entire batch, not only a sample', () => {
  const a = input(), b = { ...input(), matrixOccurrence: 'SYNTHETIC-G36-B' };
  const r = auditFutureOpticalDirections([a, b], [predicted(), predicted()], control);
  assert.equal(r.status, 'BLOCKED');
  assert.equal(r.points.length, 0);
  assert.equal(r.traces[0].reason, null);
  assert.equal(r.traces[1].reason, 'INVALID_OR_DUPLICATED_SENSOR_RECORD');
  assert.throws(() => auditFutureOpticalDirections([a], [], control), RangeError);
  assert.throws(() => auditFutureOpticalDirections([], [], control), RangeError);
});
