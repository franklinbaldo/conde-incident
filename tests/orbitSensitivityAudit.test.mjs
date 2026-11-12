import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH } from '../src/lib/orbitPhysics.ts';
import { auditLocalVelocitySensitivity } from '../src/lib/orbitSensitivityAudit.ts';

// Entirely SYNTHETIC geometry, epochs, premises and training schedule.
const epochUtc = '1963-10-27T00:00:00.000Z';
const frame = 'SYNTHETIC_OSCULATING_ECI';
const radius = EARTH.radiusKm + 500;
const speed = Math.sqrt(EARTH.muKm3S2 / radius);
const initial = { rKm: [radius, 0, 0], vKmS: [0, speed, 0], tS: 0 };
const bound = (axis, lowerKmS, upperKmS) => ({
  axis, lowerKmS, upperKmS, epochUtc, inertialFrame: frame,
  evidenceOccurrence: 'SYNTHETIC-SENSITIVITY-' + axis,
  sourceLineage: 'in-repository fabricated premise, NO sensor source',
  leanPredicate: 'NOT_AVAILABLE', premiseStatus: 'SYNTHETIC',
});
const widths = [
  bound('vx', -0.01, 0.01),
  bound('vy', speed - 0.01, speed + 0.01),
  bound('vz', -0.01, 0.01),
];
const scenario = (bounds = widths) => ({
  objectNorad: 529, epochUtc, inertialFrame: frame, initial, bounds,
});
const scheduled = (t, extras = {}) => ({
  objectNorad: 529,
  epochUtc: new Date(Date.parse(epochUtc) + t * 1000).toISOString(),
  inertialFrame: frame,
  evidenceOccurrence: 'SYNTHETIC-PLANNED-EPOCH',
  sourceLineage: 'synthetic timestamp, NOT an empirical observation',
  ...extras,
});
const controls = {
  cutoffEpochUtc: '1963-10-27T00:30:00.000Z',
  stepS: 60, terminationAltitudeKm: 80, probeKmS: 0.001,
  minimumSignalKm: 0.02,
  convergence: { halvings: 3,
    tolerance: { positionKm: 0.001, velocityKmS: 0.00001, epochS: 0.01 } },
};

test('a later synthetic Cartesian position has three locally distinguishable velocity probes', () => {
  const a = auditLocalVelocitySensitivity(scenario(), [scheduled(600)], controls,
    { j2: true });
  const b = auditLocalVelocitySensitivity(scenario(), [scheduled(600)], controls,
    { j2: true });
  assert.deepEqual(a, b, 'deterministic at one explicit probe and tolerance');
  assert.equal(a.status, 'ASSESSED_CONDITIONALLY');
  assert.equal(a.localRankAtProbeAndThreshold, 3);
  assert.equal(a.unresolvedLocalDirections, 0);
  assert.ok(a.axes.every(x => x.entersNumericalBasis));
  assert.equal(a.historicalHoldout, 'NOT_RUN');
  assert.equal(a.proofVerification, 'NOT_RUN');
  assert.equal(a.globalIdentifiability, 'NOT_ESTABLISHED');
  assert.equal(a.observationAuthenticity, 'NOT_VERIFIED');
});

test('an epoch-only observation at initial time cannot observe velocity', () => {
  const result = auditLocalVelocitySensitivity(scenario(), [scheduled(0)], controls);
  assert.equal(result.status, 'ASSESSED_CONDITIONALLY');
  assert.equal(result.localRankAtProbeAndThreshold, 0);
  assert.equal(result.unresolvedLocalDirections, 3);
  assert.ok(result.axes.every(x => x.probeDisplacementKm === 0));
});

test('singleton boxes constrain velocity by premise, not by orbital data', () => {
  const result = auditLocalVelocitySensitivity(scenario([
    bound('vx', 0, 0), bound('vy', speed, speed), bound('vz', 0, 0),
  ]), [scheduled(600)], controls);
  assert.equal(result.status, 'ASSESSED_CONDITIONALLY');
  assert.equal(result.localRankAtProbeAndThreshold, 0);
  assert.equal(result.unresolvedLocalDirections, 0);
  assert.deepEqual(result.fixedByPremise, ['vx', 'vy', 'vz']);
  assert.ok(result.axes.every(x => x.kind === 'FIXED_BY_DECLARED_DOMAIN'));
});

test('weak response under declared km threshold must not be called identified', () => {
  const result = auditLocalVelocitySensitivity(scenario(), [scheduled(1)],
    { ...controls, minimumSignalKm: 10 });
  assert.equal(result.status, 'ASSESSED_CONDITIONALLY');
  assert.equal(result.localRankAtProbeAndThreshold, 0);
  assert.equal(result.unresolvedLocalDirections, 3);
  assert.ok(result.axes.some(x => x.probeDisplacementKm > 0));
});

test('chronological leakage and mixed target/frame/source are rejected', () => {
  assert.throws(() => auditLocalVelocitySensitivity(scenario(),
    [scheduled(1800)], controls), /leakage/);
  assert.throws(() => auditLocalVelocitySensitivity(scenario(),
    [scheduled(400), scheduled(300)], controls), /order/);
  assert.throws(() => auditLocalVelocitySensitivity(scenario(),
    [scheduled(600, { objectNorad: 527 })], controls), /Mixed object/);
  assert.throws(() => auditLocalVelocitySensitivity(scenario(),
    [scheduled(600, { inertialFrame: 'TEME' })], controls), /Mixed object/);
  assert.throws(() => auditLocalVelocitySensitivity(scenario(),
    [scheduled(600, { sourceLineage: '' })], controls), /source lineage/);
  assert.throws(() => auditLocalVelocitySensitivity(scenario(), [scheduled(600)],
    { ...controls, minimumSignalKm: 0.0001 }), /resolvable signal/);
});

test('empty and partial declared boxes provide no fictitious rank', () => {
  const empty = auditLocalVelocitySensitivity(scenario([
    ...widths, bound('vx', 0.2, 0.3),
  ]), [scheduled(600)], controls);
  const partial = auditLocalVelocitySensitivity(scenario(widths.slice(0, 2)),
    [scheduled(600)], controls);
  assert.equal(empty.status, 'NOT_RUN_EMPTY');
  assert.equal(partial.status, 'NOT_RUN_UNBOUNDED');
  assert.equal(empty.localRankAtProbeAndThreshold, null);
  assert.equal(partial.localRankAtProbeAndThreshold, null);
});

test('a non-singleton subnormal box with an unresolvable requested probe refuses a rank', () => {
  const tiny = scenario([bound('vx', 0, Number.MIN_VALUE), widths[1], widths[2]]);
  const result = auditLocalVelocitySensitivity(tiny, [scheduled(600)], controls);
  assert.equal(result.status, 'NOT_RUN_PROBE_PRECISION');
  assert.equal(result.localRankAtProbeAndThreshold, null);
});

test('a missed coarse reentry suppresses sensitivity ranking, never proves a no-fall', () => {
  const near = scenario([
    bound('vx', -0.151, -0.149),
    bound('vy', 8.149, 8.151),
    bound('vz', -0.001, 0.001),
  ]);
  const result = auditLocalVelocitySensitivity({
    ...near, initial: { rKm: [EARTH.radiusKm + 90, 0, 0],
      vKmS: [-0.15, 8.15, 0], tS: 0 },
  }, [scheduled(3000)], {
    ...controls, cutoffEpochUtc: '1963-10-27T02:00:00.000Z',
    stepS: 3000, convergence: {
      ...controls.convergence,
      tolerance: { positionKm: 0.01, velocityKmS: 0.0001, epochS: 0.01 },
    },
  });
  assert.equal(result.status, 'NOT_RUN_EVENT_CONFLICT');
  assert.equal(result.localRankAtProbeAndThreshold, null);
  assert.equal(result.geographicInference, 'NOT_SUPPORTED');
});
