import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH } from '../src/lib/orbitPhysics.ts';
import { auditVelocityDomain, runConditionalVelocityDomain } from '../src/lib/orbitAdmissibility.ts';

// SYNTHETIC premises only: NOT retrieved from NASA, NORAD, Lean or a 1963 sensor.
const epochUtc = '1963-10-27T14:40:16.132Z';
const inertialFrame = 'SYNTHETIC_ECI_FIXED_FRAME';
const velocity = Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500));
const initial = { rKm: [EARTH.radiusKm + 500, 0, 0], vKmS: [0, velocity, 0], tS: 0 };
const source = {
  evidenceOccurrence: 'SYNTHETIC-TEST-ONLY',
  sourceLineage: 'numerical unit test, NOT an independent historical sensor',
  leanPredicate: 'NOT_AVAILABLE: no Lean interval export or proof checked',
  premiseStatus: 'SYNTHETIC',
  epochUtc, inertialFrame,
};
const bound = (axis, lowerKmS, upperKmS) => ({ axis, lowerKmS, upperKmS, ...source });
const scenario = (...bounds) =>
  ({ objectNorad: 529, epochUtc, inertialFrame, initial, bounds });
const three = [
  bound('vx', -0.0004, 0.0004),
  bound('vy', velocity - 0.0004, velocity + 0.0004),
  bound('vz', -0.0004, 0.0004),
];
const controls = (seed = 1963, interiorDraws = 2, durationS = 600, stepS = 100) => ({
  seed, interiorDraws, durationS, stepS, terminationAltitudeKm: 80,
  convergence: { halvings: 3, tolerance: { positionKm: 0.1, velocityKmS: 1e-4, epochS: 0.02 } },
});

test('bounded intersection narrows each km/s axis and retains explicit absence of proof verification', () => {
  const domain = auditVelocityDomain(scenario(...three, bound('vx', -0.0001, 0.0003)));
  assert.equal(domain.status, 'BOUNDED');
  assert.deepEqual(domain.intervals.vx, [-0.0001, 0.0003]);
  assert.deepEqual(domain.intervals.vz, [-0.0004, 0.0004]);
  assert.equal(domain.proofVerification, 'NOT_RUN');
  assert.equal(domain.sourceCount, 4);
});

test('contradictory conditional premises produce EMPTY rather than an invented state', () => {
  const contradictory = scenario(...three, bound('vx', 0.01, 0.02));
  assert.equal(auditVelocityDomain(contradictory).status, 'EMPTY');
  const result = runConditionalVelocityDomain(contradictory, controls());
  assert.equal(result.status, 'NOT_RUN_EMPTY');
  assert.equal(result.samples.length, 0);
  assert.equal(result.exhaustivePhysicalEnclosure, false);
});

test('partially bounded domain is NOT silently completed from guessed priors or baseline v', () => {
  const partial = scenario(bound('vx', -1, 1), bound('vy', 7, 8));
  const domain = auditVelocityDomain(partial);
  assert.equal(domain.status, 'PARTIAL');
  assert.deepEqual(domain.stillFree, ['vz']);
  assert.equal(runConditionalVelocityDomain(partial, controls()).status, 'NOT_RUN_UNBOUNDED');
});

test('refuse mismatched frame/UTC, missing lineage, reversed intervals and invalid seed', () => {
  assert.throws(() => auditVelocityDomain(scenario({ ...three[0], inertialFrame: 'TEME' })), /frame/);
  assert.throws(() => auditVelocityDomain(scenario({ ...three[0], epochUtc: '1963-10-28T00:00:00Z' })), /epoch/);
  assert.throws(() => auditVelocityDomain(scenario({ ...three[0], sourceLineage: '' })), /provenance/);
  assert.throws(() => auditVelocityDomain(scenario(bound('vx', 2, 1))), /bounds/);
  assert.throws(() => auditVelocityDomain(scenario(bound('wx', 0, 1))), /bounds/);
  assert.throws(() => runConditionalVelocityDomain(scenario(...three), controls(0)), /seed/);
});

test('seeded conditional samples are repeatable, within every intersection, and not posterior', () => {
  const s = scenario(...three);
  const a = runConditionalVelocityDomain(s, controls(1963, 2));
  const b = runConditionalVelocityDomain(s, controls(1963, 2));
  const c = runConditionalVelocityDomain(s, controls(1964, 2));
  assert.deepEqual(a, b);
  assert.notDeepEqual(a.samples.map(x => x.vKmS), c.samples.map(x => x.vKmS));
  assert.equal(a.status, 'SAMPLED_CONDITIONALLY');
  assert.equal(a.samples.length, 11); // midpoint, eight corners, two interior points
  assert.ok(a.samples.every(s => s.numerical.status === 'STABLE'));
  for (const s of a.samples) {
    for (const [i, axis] of ['vx', 'vy', 'vz'].entries()) {
      const [lower, upper] = auditVelocityDomain(scenario(...three)).intervals[axis];
      assert.ok(s.vKmS[i] >= lower && s.vKmS[i] <= upper);
    }
  }
  assert.equal(a.historicalHoldout, 'NOT_RUN');
  assert.equal(a.geographicInference, 'NOT_SUPPORTED');
  assert.equal(a.proofVerification, 'NOT_RUN');
  assert.equal(a.exhaustivePhysicalEnclosure, false);
});

test('negative numerical control: a conditional domain does not erase a coarse missed event', () => {
  const terminal = {
    ...scenario(
      bound('vx', -0.15, -0.15),
      bound('vy', 8.15, 8.15),
      bound('vz', 0, 0),
    ),
    initial: { rKm: [EARTH.radiusKm + 90, 0, 0], vKmS: [-0.15, 8.15, 0], tS: 0 },
  };
  const a = runConditionalVelocityDomain(terminal, controls(1963, 0, 3000, 3000));
  assert.equal(a.status, 'SAMPLED_CONDITIONALLY');
  assert.equal(a.samples.length, 1);
  assert.equal(a.samples[0].numerical.status, 'EVENT_CONFLICT');
  assert.equal(a.samples[0].numerical.levels[0].result.event, 'elapsed');
  assert.equal(a.samples[0].numerical.finest.event, 'reentry-threshold');
  // A conditional simulation cannot authenticate a historical fall or prove exclusion.
  assert.equal(a.exhaustivePhysicalEnclosure, false);
  assert.equal(a.geographicInference, 'NOT_SUPPORTED');
});

test('degenerate interval has exactly one state even with requested random draws', () => {
  const s = scenario(bound('vx', 0, 0), bound('vy', velocity, velocity), bound('vz', 0, 0));
  const result = runConditionalVelocityDomain(s, controls(123, 3));
  assert.equal(result.samples.length, 1);
  assert.deepEqual(result.samples[0].vKmS, [0, velocity, 0]);
});
