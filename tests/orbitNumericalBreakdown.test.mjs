import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, rk4, NumericalIntegrationBreakdown } from '../src/lib/orbitPhysics.ts';
import { runConditionalVelocityDomain } from '../src/lib/orbitAdmissibility.ts';

// These deliberately pathological speeds are SYNTHETIC stress inputs, NOT
// possible reconstructions of NORAD 527/529 or historical velocity bounds.
const epochUtc = '1963-10-27T00:00:00.000Z';
const inertialFrame = 'SYNTHETIC_ECI';
const radius = EARTH.radiusKm + 500;
const circular = Math.sqrt(EARTH.muKm3S2 / radius);
const initial = { rKm: [radius, 0, 0], vKmS: [0, circular, 0], tS: 0 };
const bound = (axis, lo, hi) => ({
  axis, lowerKmS: lo, upperKmS: hi, epochUtc, inertialFrame,
  evidenceOccurrence: 'SYNTHETIC-NUMERIC-' + axis,
  sourceLineage: 'synthetic in-repository test, no historical observation',
  leanPredicate: 'NOT_AVAILABLE', premiseStatus: 'SYNTHETIC',
});
const scenario = (lo, hi) => ({
  objectNorad: 529, epochUtc, inertialFrame, initial,
  bounds: [bound('vx', 0, 0), bound('vy', lo, hi), bound('vz', 0, 0)],
});
const controls = {
  seed: 1963, interiorDraws: 5,
  durationS: 60, stepS: 30, terminationAltitudeKm: 80,
  convergence: { halvings: 2,
    tolerance: { positionKm: 0.1, velocityKmS: 0.001, epochS: 0.01 } },
};

test('a finite extreme witness cannot erase a valid conditional J2 trajectory', () => {
  const box = scenario(circular, 1e308);
  const first = runConditionalVelocityDomain(box, controls, { j2: true });
  const again = runConditionalVelocityDomain(box, controls, { j2: true });
  assert.deepEqual(first, again, 'same seed retains all success and failure records');
  assert.equal(first.status, 'SAMPLED_WITH_NUMERICAL_BREAKDOWNS');
  assert.ok(first.numericalBreakdownCount > 0);
  assert.ok(first.numericalBreakdownCount < first.samples.length);
  assert.equal(first.samples.length,
    first.samples.filter(s => s.numericalStatus === 'ASSESSED').length +
    first.numericalBreakdownCount);
  assert.ok(first.samples.some(s =>
    s.vKmS[1] === circular && s.numericalStatus === 'ASSESSED' &&
    s.numerical?.finest.event === 'elapsed'));
  for (const sample of first.samples) {
    assert.ok(sample.vKmS[1] >= circular && sample.vKmS[1] <= 1e308);
    if (sample.numericalStatus === 'NOT_RUN_NUMERICAL_BREAKDOWN') {
      assert.equal(sample.numerical, null);
      assert.match(sample.failureReason, /finite phase space/);
    } else {
      assert.equal(sample.failureReason, null);
      assert.ok(sample.numerical?.levels.length >= 3);
    }
  }
  assert.equal(first.exhaustivePhysicalEnclosure, false);
  assert.equal(first.geographicInference, 'NOT_SUPPORTED');
  assert.equal(first.historicalHoldout, 'NOT_RUN');
  assert.equal(first.proofVerification, 'NOT_RUN');
});

test('all finite but non-integrable sampled speeds produce NO accepted trajectory', () => {
  const result = runConditionalVelocityDomain(scenario(1e308, 1e308),
    { ...controls, interiorDraws: 100 }, { j2: true });
  assert.equal(result.status, 'NOT_RUN_ALL_NUMERICAL_BREAKDOWNS');
  assert.equal(result.samples.length, 1);
  assert.equal(result.numericalBreakdownCount, 1);
  assert.equal(result.samples[0].numerical, null);
  assert.equal(result.samples[0].numericalStatus, 'NOT_RUN_NUMERICAL_BREAKDOWN');
});

test('valid narrow velocity box still propagates with zero breakdowns', () => {
  const result = runConditionalVelocityDomain(scenario(circular, circular), controls, { j2: true });
  assert.equal(result.status, 'SAMPLED_CONDITIONALLY');
  assert.equal(result.numericalBreakdownCount, 0);
  assert.equal(result.samples.length, 1);
  assert.equal(result.samples[0].numericalStatus, 'ASSESSED');
  assert.equal(result.samples[0].failureReason, null);
  assert.equal(result.samples[0].numerical.status, 'STABLE');
});

test('global invalid atmosphere and numerical controls are never swallowed per sample', () => {
  const box = scenario(circular, circular);
  assert.throws(() => runConditionalVelocityDomain(box, controls, {
    atmosphere: { source: '', cdAreaOverMassM2Kg: 0.01, densityKgM3: () => 1e-12 },
  }), /Atmospheric model requires source/);
  assert.throws(() => runConditionalVelocityDomain(box, controls, {
    atmosphere: { source: 'synthetic-invalid-density', cdAreaOverMassM2Kg: 0.01,
      densityKgM3: () => -1 },
  }), /Density must be finite/);
  assert.throws(() => runConditionalVelocityDomain(box, {
    ...controls, convergence: { halvings: 1, tolerance: controls.convergence.tolerance },
  }), /2–10 halvings/);
});

test('RK4 numerical breakdown differs from a malformed declared UTC state', () => {
  assert.throws(() => rk4({ ...initial, vKmS: [0, 1e308, 0] }, 30),
    e => e instanceof NumericalIntegrationBreakdown);
  assert.throws(() => runConditionalVelocityDomain({
    ...scenario(circular, circular),
    initial: { ...initial, tS: 1 },
  }, controls), /Invalid target, explicit UTC epoch/);
});
