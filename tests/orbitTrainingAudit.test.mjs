import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagate } from '../src/lib/orbitPhysics.ts';
import { auditTrainingOrbitScore } from '../src/lib/orbitHoldoutAudit.ts';
import { fitConditionalVelocity } from '../src/lib/orbitConditionalFit.ts';

// Entirely SYNTHETIC r/v dynamics and observations. No historical NORAD track,
// authenticated Lean bounds, density, TLE conversion, or geographic inference.
const epoch = '1963-10-27T00:00:00.000Z';
const cutoff = '1963-10-27T00:28:00.000Z';
const frame = 'SYNTHETIC_OSCULATING_ECI';
const vc = Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500));
const baseline = { rKm: [EARTH.radiusKm + 500, 0, 0], vKmS: [0, vc, 0], tS: 0 };
const truth = { ...baseline, vKmS: [0.002, vc + 0.004, -0.002] };
const dynamics = { j2: true };
const bound = (axis, lowerKmS, upperKmS) => ({
  axis, lowerKmS, upperKmS, epochUtc: epoch, inertialFrame: frame,
  evidenceOccurrence: 'SYNTHETIC-ONLY', sourceLineage: 'generated in this test',
  leanPredicate: 'NOT_AVAILABLE', premiseStatus: 'SYNTHETIC',
});
const bounds = [
  bound('vx', 0, 0.004), bound('vy', vc, vc + 0.007), bound('vz', -0.004, 0),
];
const scenario = (initial = baseline, bs = bounds) =>
  ({ objectNorad: 529, initial, epochUtc: epoch, inertialFrame: frame, bounds: bs });
const obs = (state, seconds) => ({
  objectNorad: 529, inertialFrame: frame, elapsedS: seconds,
  epochUtc: new Date(Date.parse(epoch) + seconds * 1000).toISOString(),
  source: 'SYNTHETIC position, not an instrument observation',
  rKm: propagate(state, seconds, 2, 80, dynamics).state.rKm,
});
const training = [600, 1200, 1500].map(t => obs(truth, t));
const future = (state) => [2400, 2800].map(t => obs(state, t));
const controls = {
  stepS: 40, terminationAltitudeKm: 80, gridStepKmS: 0.003, rounds: 9,
  convergence: { halvings: 3,
    tolerance: { positionKm: 0.1, velocityKmS: 0.0001, epochS: 0.02 } },
};
const calibrate = (s, history, withheld, cfg = controls) =>
  fitConditionalVelocity(s, cutoff, history, withheld, cfg, dynamics);

test('independently refined in-sample gain does not conceal a WORSE future synthetic forecast', () => {
  const result = calibrate(scenario(), training, future(baseline));
  assert.equal(result.status, 'CALIBRATED_CONDITIONALLY');
  assert.equal(result.trainingAudit.phase, 'TRAINING');
  assert.equal(result.trainingAudit.status, 'APPARENT_FITTED_BETTER');
  assert.ok(result.trainingAudit.levels.at(-1).deltaRmsKm < 0);
  assert.equal(result.holdout.phase, 'HOLDOUT');
  assert.ok(result.holdout.levels.at(-1).deltaRmsKm > 0);
  assert.equal(result.trainingAudit.observationAuthenticity, 'NOT_VERIFIED');
  assert.equal(result.independentObservation, 'NOT_VERIFIED');
});

test('zero-width synthetic box cannot claim training gain when no velocity changes', () => {
  const bs = [bound('vx', 0, 0), bound('vy', vc, vc), bound('vz', 0, 0)];
  const history = [600, 1200].map(t => obs(baseline, t));
  const result = calibrate(scenario(baseline, bs), history, future(baseline));
  assert.equal(result.status, 'TRAINING_GAIN_UNCONFIRMED');
  assert.equal(result.trainingAudit.status, 'NUMERICALLY_INDISTINGUISHABLE');
  assert.deepEqual(result.fit.initialState, result.fit.fittedState);
  assert.equal(result.proofVerification, 'NOT_RUN');
});

test('unresolved numeric precision blocks training-gain claim despite a coarse optimizer', () => {
  const strict = { ...controls, convergence: { halvings: 2,
    tolerance: { positionKm: 1e-14, velocityKmS: 1e-14, epochS: 1e-14 } } };
  const result = calibrate(scenario(), training, future(truth), strict);
  assert.equal(result.status, 'TRAINING_GAIN_UNCONFIRMED');
  assert.equal(result.trainingAudit.status, 'NOT_RESOLVED');
  assert.equal(result.trainingAudit.levels.length, 0);
  assert.ok(result.fit.trainingFittedRmsKm < result.fit.trainingBaselineRmsKm,
    'coarse training gain is retained as unconfirmed, not erased');
});

test('training audit rejects future leakage, wrong object and absent provenance', () => {
  const result = calibrate(scenario(), training, future(truth));
  assert.throws(() => auditTrainingOrbitScore(result.fit, future(truth),
    controls.convergence), /leakage/);
  assert.throws(() => auditTrainingOrbitScore(result.fit,
    [{ ...training[0], objectNorad: 527 }], controls.convergence), /Mixed target/);
  assert.throws(() => auditTrainingOrbitScore(result.fit,
    [{ ...training[0], source: '' }], controls.convergence), /provenance/);
});

test('training numerical event conflict suppresses RMS ranking, including a coarse missed perigee', () => {
  const descending = { rKm: [EARTH.radiusKm + 90, 0, 0],
    vKmS: [-0.15, 8.15, 0], tS: 0 };
  const fake = {
    objectNorad: 529, initialEpochUtc: epoch,
    cutoffEpochUtc: '1963-10-27T01:00:00.000Z',
    inertialFrame: frame, initialState: descending, fittedState: descending,
    stepS: 3000, terminationAltitudeKm: 80, dynamics: {},
    evaluations: 0, trainingCount: 0,
    trainingBaselineRmsKm: 0, trainingFittedRmsKm: 0,
  };
  const artifact = { ...obs(baseline, 3000), rKm: descending.rKm };
  const audit = auditTrainingOrbitScore(fake, [artifact],
    { ...controls.convergence, halvings: 5 });
  assert.equal(audit.status, 'EVENT_CONFLICT');
  assert.equal(audit.levels.length, 0);
  assert.equal(audit.points[0].baseline.levels[0].result.event, 'elapsed');
  assert.equal(audit.points[0].baseline.finest.event, 'reentry-threshold');
});
