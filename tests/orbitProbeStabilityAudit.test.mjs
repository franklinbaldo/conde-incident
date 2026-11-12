import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH } from '../src/lib/orbitPhysics.ts';
import { auditVelocityProbeStability } from '../src/lib/orbitProbeStabilityAudit.ts';

// ALL states, labels and orbital positions below are SYNTHETIC.
const epochUtc = '1963-10-27T00:00:00.000Z';
const inertialFrame = 'SYNTHETIC_ECI';
const radius = EARTH.radiusKm + 500;
const speed = Math.sqrt(EARTH.muKm3S2 / radius);
const initial = { rKm: [radius, 0, 0], vKmS: [0, speed, 0], tS: 0 };
const bound = (axis, lowerKmS, upperKmS) => ({
  axis, lowerKmS, upperKmS, epochUtc, inertialFrame,
  evidenceOccurrence: 'SYNTHETIC-PROBE-' + axis,
  sourceLineage: 'in-repository fabricated premise, not historical tracking',
  leanPredicate: 'NOT_AVAILABLE', premiseStatus: 'SYNTHETIC',
});
const bounds = [
  bound('vx', -0.01, 0.01), bound('vy', speed - 0.01, speed + 0.01),
  bound('vz', -0.01, 0.01),
];
const scenario = (b = bounds) => ({
  objectNorad: 529, epochUtc, inertialFrame, initial, bounds: b,
});
const scheduled = t => [{
  objectNorad: 529,
  epochUtc: new Date(Date.parse(epochUtc) + t * 1000).toISOString(),
  inertialFrame, evidenceOccurrence: 'SYNTHETIC-TIMESTAMP',
  sourceLineage: 'fabricated UTC; no sensor observation',
}];
const controls = {
  cutoffEpochUtc: '1963-10-27T00:30:00.000Z',
  stepS: 60, terminationAltitudeKm: 80, probeKmS: 0.001,
  minimumSignalKm: 0.02,
  convergence: { halvings: 3, tolerance: {
    positionKm: 0.001, velocityKmS: 0.00001, epochS: 0.01,
  } },
};

test('J2 r/v reintegration gives a repeatable three-probe conditional rank at 600 s', () => {
  const a = auditVelocityProbeStability(scenario(), scheduled(600), controls, { j2: true });
  const b = auditVelocityProbeStability(scenario(), scheduled(600), controls, { j2: true });
  assert.deepEqual(a, b);
  assert.equal(a.status, 'CONSISTENT_AT_THREE_PROBES');
  assert.deepEqual(a.rankAtEachProbe, [3, 3, 3]);
  assert.equal(a.conditionallyConsistentRank, 3);
  assert.equal(a.spans.length, 3);
  assert.ok(a.spans.every(x => x.appliedWidthsKmS[0] <
    x.appliedWidthsKmS[1] && x.appliedWidthsKmS[1] < x.appliedWidthsKmS[2]));
  assert.equal(a.historicalHoldout, 'NOT_RUN');
  assert.equal(a.globalIdentifiability, 'NOT_ESTABLISHED');
  assert.equal(a.observationAuthenticity, 'NOT_VERIFIED');
  assert.equal(a.geographicInference, 'NOT_SUPPORTED');
});

test('a short-epoch synthetic rank can flip solely as probe amplitude changes', () => {
  const a = auditVelocityProbeStability(scenario(), scheduled(1), {
    ...controls, probeKmS: 0.003, minimumSignalKm: 0.01,
  });
  assert.equal(a.status, 'RANK_CHANGES_WITH_PROBE');
  assert.equal(a.conditionallyConsistentRank, null);
  assert.ok(new Set(a.rankAtEachProbe).size > 1);
  assert.ok(a.rankAtEachProbe[0] < a.rankAtEachProbe[2]);
});

test('domain truncation can repeat the same velocity difference despite three labels', () => {
  const b = [bound('vx', -0.0001, 0.0001), bounds[1], bounds[2]];
  const a = auditVelocityProbeStability(scenario(b), scheduled(600), controls);
  assert.equal(a.status, 'NOT_RESOLVED_SATURATED_PROBE');
  assert.equal(a.conditionallyConsistentRank, null);
  const vx = a.spans.find(x => x.axis === 'vx');
  assert.equal(vx.appliedWidthsKmS[0], vx.appliedWidthsKmS[1]);
  assert.equal(vx.appliedWidthsKmS[1], vx.appliedWidthsKmS[2]);
});

test('all fixed velocity axes are premises, not evidence of rank three', () => {
  const b = [bound('vx', 0, 0), bound('vy', speed, speed), bound('vz', 0, 0)];
  const a = auditVelocityProbeStability(scenario(b), scheduled(600), controls);
  assert.equal(a.status, 'NO_FREE_VELOCITY_DIRECTIONS');
  assert.deepEqual(a.rankAtEachProbe, [0, 0, 0]);
  assert.equal(a.conditionallyConsistentRank, null);
});

test('unresolved numeric probe at any level does not yield a certified rank', () => {
  const b = [bound('vx', 0, Number.MIN_VALUE), bounds[1], bounds[2]];
  const a = auditVelocityProbeStability(scenario(b), scheduled(600), controls);
  assert.equal(a.status, 'NOT_RUN_A_PROBE');
  assert.equal(a.conditionallyConsistentRank, null);
  assert.ok(a.checks.some(c => c.audit.status === 'NOT_RUN_PROBE_PRECISION'));
});

test('invalid probe range and chronology are not silently converted to an audit', () => {
  assert.throws(() => auditVelocityProbeStability(scenario(), scheduled(600),
    { ...controls, probeKmS: Number.MIN_VALUE }), /three distinct/);
  assert.throws(() => auditVelocityProbeStability(scenario(), scheduled(600),
    { ...controls, probeKmS: Number.MAX_VALUE }), /three distinct/);
  assert.throws(() => auditVelocityProbeStability(scenario(), scheduled(1800),
    controls), /leakage/);
  assert.throws(() => auditVelocityProbeStability(scenario(), [{
    ...scheduled(600)[0], objectNorad: 527,
  }], controls), /Mixed object/);
});
