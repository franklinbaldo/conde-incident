import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagate } from '../src/lib/orbitPhysics.ts';
import { fitConditionalVelocity } from '../src/lib/orbitConditionalFit.ts';

// ALL Cartesian positions, premises and bounds below are SYNTHETIC.
// No 1963 sensor, verified Lean export, atmosphere or SGP4 result is used.
const epoch = '1963-10-27T00:00:00.000Z';
const cutoff = '1963-10-27T00:28:00.000Z';
const frame = 'SYNTHETIC_OSCULATING_ECI';
const vc = Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500));
const baseline = { rKm: [EARTH.radiusKm + 500, 0, 0], vKmS: [0, vc, 0], tS: 0 };
const truth = { ...baseline, vKmS: [0.002, vc + 0.004, -0.002] };
const dynamics = { j2: true };
const src = {
  evidenceOccurrence: 'SYNTHETIC-FIT-ONLY', sourceLineage: 'synthetic RK4 generator',
  leanPredicate: 'NOT_AVAILABLE', premiseStatus: 'SYNTHETIC', epochUtc: epoch,
  inertialFrame: frame,
};
const bound = (axis, lowerKmS, upperKmS) =>
  ({ axis, lowerKmS, upperKmS, ...src });
const bounds = [
  bound('vx', 0, 0.004),
  bound('vy', vc, vc + 0.007),
  bound('vz', -0.004, 0),
];
const scenario = (s = baseline, bs = bounds, objectNorad = 529) => ({
  initial: s, bounds: bs, epochUtc: epoch, inertialFrame: frame, objectNorad,
});
const obs = (state, elapsedS, objectNorad = 529) => ({
  elapsedS, objectNorad, inertialFrame: frame,
  epochUtc: new Date(Date.parse(epoch) + elapsedS * 1000).toISOString(),
  source: 'SYNTHETIC RK4 2-second numerical generator',
  rKm: propagate(state, elapsedS, 2, 80, dynamics).state.rKm,
});
const training = [600, 1200, 1500].map(t => obs(truth, t));
const future = (state) => [2400, 2800].map(t => obs(state, t));
const controls = {
  stepS: 40, terminationAltitudeKm: 80, gridStepKmS: 0.003,
  rounds: 9, convergence: { halvings: 3,
    tolerance: { positionKm: 0.1, velocityKmS: 0.0001, epochS: 0.02 } },
};
const fit = (s = scenario(), train = training, heldout = future(truth), cfg = controls) =>
  fitConditionalVelocity(s, cutoff, train, heldout, cfg, dynamics);

test('closed conditional domain constrains EVERY fitted velocity axis and improves synthetic training', () => {
  const result = fit();
  assert.equal(result.status, 'CALIBRATED_CONDITIONALLY');
  assert.equal(result.domain.status, 'BOUNDED');
  assert.ok(result.fit.trainingFittedRmsKm < result.fit.trainingBaselineRmsKm);
  for (const [i, b] of bounds.entries()) {
    assert.ok(result.fit.fittedState.vKmS[i] >= b.lowerKmS);
    assert.ok(result.fit.fittedState.vKmS[i] <= b.upperKmS);
  }
  assert.equal(result.fit.trainingCount, 3);
  assert.equal(result.holdout.points.length, 2);
  assert.equal(result.proofVerification, 'NOT_RUN');
  assert.equal(result.historicalHoldout, 'NOT_VERIFIED');
  assert.equal(result.geographicInference, 'NOT_SUPPORTED');
  assert.deepEqual(fit(), result, 'deterministic calibration and holdout');
});

test('negative falsification: fitting past positions makes future synthetic baseline worse', () => {
  const result = fit(scenario(), training, future(baseline));
  assert.equal(result.status, 'CALIBRATED_CONDITIONALLY');
  assert.ok(result.fit.trainingFittedRmsKm < result.fit.trainingBaselineRmsKm);
  assert.ok(result.holdout.levels.at(-1).deltaRmsKm > 0);
  assert.ok(['APPARENT_BASELINE_BETTER', 'NUMERICALLY_INDISTINGUISHABLE',
    'NOT_RESOLVED'].includes(result.holdout.status));
  assert.equal(result.independentObservation, 'NOT_VERIFIED');
});

test('contradictory and partly unconstrained domains NEVER fabricate a state or score', () => {
  const empty = fit(scenario(baseline,
    [...bounds, bound('vx', -0.004, -0.001)]), [], []);
  assert.equal(empty.status, 'NOT_RUN_EMPTY');
  assert.equal(empty.fit, null);
  assert.equal(empty.holdout, null);
  assert.equal(empty.evaluations, 0);
  const unbounded = fit(scenario(baseline, bounds.slice(0, 2)), [], []);
  assert.equal(unbounded.status, 'NOT_RUN_UNBOUNDED');
  assert.equal(unbounded.domain.stillFree[0], 'vz');
  assert.equal(unbounded.fit, null);
});

test('an out-of-bounds seed is projected and explicitly reported, never silently passed to RK4', () => {
  const far = { ...baseline, vKmS: [-0.1, vc - 0.04, 0.2] };
  const result = fit(scenario(far));
  assert.equal(result.status, 'CALIBRATED_CONDITIONALLY');
  assert.equal(result.baselineProjectedIntoDomain, true);
  assert.deepEqual(result.fit.initialState.vKmS, [0, vc, 0]);
});

test('wrong target, frame, UTC and leaked holdout positions fail closed', () => {
  assert.throws(() => fit(scenario(baseline, bounds, 528)), /527 or 529/);
  assert.throws(() => fit(scenario(), training.map(o => ({ ...o,
    inertialFrame: 'TEME' }))), /Mixed target/);
  assert.throws(() => fit(scenario(), [training[0], future(truth)[0]]), /leakage/);
  assert.throws(() => fit(scenario(), training,
    [ { ...future(truth)[0], objectNorad: 527 } ]), /Mixed target/);
  assert.throws(() => fit(scenario(), training,
    [ { ...future(truth)[0], epochUtc: '1963-10-27T00:12:00.000Z',
      elapsedS: 720 } ]), /leakage/);
  assert.throws(() => fit(scenario(), training, future(truth),
    { ...controls, rounds: 0 }), /iteration budget/);
});

test('negative near-Earth control: all pre-cutoff runs terminate, no finite training score', () => {
  const descending = { rKm: [EARTH.radiusKm + 90, 0, 0],
    vKmS: [-0.15, 8.15, 0], tS: 0 };
  const clipped = [bound('vx', -0.15, -0.15), bound('vy', 8.15, 8.15),
    bound('vz', 0, 0)];
  const artificial = (t) => ({
    elapsedS: t, objectNorad: 529, inertialFrame: frame,
    epochUtc: new Date(Date.parse(epoch) + t * 1000).toISOString(),
    source: 'SYNTHETIC impossible control, no sensor',
    rKm: descending.rKm,
  });
  const result = fitConditionalVelocity(scenario(descending, clipped), cutoff,
    [artificial(600), artificial(1200)], [artificial(2400)], controls, {});
  assert.equal(result.status, 'NO_FINITE_TRAINING_SCORE');
  assert.equal(result.fit, null);
  assert.equal(result.holdout, null);
});
