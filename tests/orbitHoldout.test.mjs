import test from 'node:test';
import assert from 'node:assert/strict';
import {
  EARTH, propagate, potentialKm2S2, accelerationKmS2,
  fitPreCutoffOrbit, scoreFutureOrbit,
} from '../src/lib/orbitPhysics.ts';

// ALL observations here are MODEL-GENERATED SYNTHETIC controls, NOT 1963 TLEs.
const initialEpochUtc = '1963-10-27T00:00:00.000Z';
const cutoffEpochUtc = '1963-10-27T00:35:00.000Z';
const frame = 'synthetic-cartesian-ECI (not verified TEME/J2000)';
const initial = {
  rKm: [EARTH.radiusKm + 500, 0, 0],
  vKmS: [0, Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500)), 0],
  tS: 0,
};
const trueState = { ...initial, vKmS: [0.003, initial.vKmS[1] + 0.006, -0.004] };
const dynamics = { j2: true };
const observation = (state, elapsedS, objectNorad = 529) => ({
  objectNorad,
  epochUtc: new Date(Date.parse(initialEpochUtc) + elapsedS * 1000).toISOString(),
  elapsedS,
  rKm: propagate(state, elapsedS, 20, 80, dynamics).state.rKm,
  inertialFrame: frame,
  source: 'SYNTHETIC coupled RK4 generator, not independent or historical',
});
const training = [600, 1200, 1800].map(t => observation(trueState, t));
const fit = () => fitPreCutoffOrbit(initial, 529, initialEpochUtc, cutoffEpochUtc,
  frame, training, 20, 80, 0.008, 9, dynamics);

test('predeclared 529 chronological split: train on past, score held-out future without refit', () => {
  const fitted = fit();
  const future = [2600, 3200].map(t => observation(trueState, t));
  const score = scoreFutureOrbit(fitted, future);
  assert.ok(fitted.trainingFittedRmsKm < fitted.trainingBaselineRmsKm / 10);
  assert.ok(score.fittedRmsKm < score.baselineRmsKm);
  assert.equal(score.observationCount, 2);
  assert.ok(score.deltaRmsKm < 0);
  assert.deepEqual(fitted, fit()); // deterministic fit on same past
});

test('negative falsification: train improvement can DAMAGE future prediction', () => {
  const fitted = fit();
  // Deliberately contradictory synthetic future, generated from *initial* baseline.
  const future = [2600, 3200].map(t => observation(initial, t));
  const score = scoreFutureOrbit(fitted, future);
  assert.ok(fitted.trainingFittedRmsKm < fitted.trainingBaselineRmsKm);
  assert.ok(score.fittedRmsKm > score.baselineRmsKm);
  assert.ok(score.deltaRmsKm > 0);
  assert.ok(score.baselineRmsKm < 1e-10);
});

test('temporal leakage, mixed 527/529, mixed frames and untraced epochs are rejected', () => {
  const args = (o) => fitPreCutoffOrbit(initial, 529, initialEpochUtc, cutoffEpochUtc,
    frame, o, 20, 80, 0.008, 3, dynamics);
  assert.throws(() => args([training[0], observation(trueState, 2400)]), /leakage/);
  assert.throws(() => args([training[0], { ...training[1], objectNorad: 527 }]), /Mixed target/);
  assert.throws(() => args([training[0], { ...training[1], epochUtc: training[0].epochUtc }]), /leakage/);
  assert.throws(() => args([training[0], { ...training[1], elapsedS: 1201 }]), /UTC/);
  assert.throws(() => args([training[0], { ...training[1], source: '' }]), /provenance/);
  assert.throws(() => args([training[0], { ...training[1], epochUtc: '1963-02-30T00:00:00Z' }]), /calendar/);
  const fitted = fit();
  assert.throws(() => scoreFutureOrbit(fitted, [observation(trueState, 1900)]), /leakage/);
  assert.throws(() => scoreFutureOrbit(fitted, [observation(trueState, 2600, 527)]), /Mixed target/);
  assert.throws(() => scoreFutureOrbit(fitted, [{ ...observation(trueState, 2600), inertialFrame: 'TEME' }]), /Mixed target/);
});

test('same model supports separately identified 527 without mixing objects', () => {
  const obs527 = [600, 1200].map(t => observation(trueState, t, 527));
  const trained = fitPreCutoffOrbit(initial, 527, initialEpochUtc, cutoffEpochUtc,
    frame, obs527, 20, 80, 0.008, 5, dynamics);
  const score = scoreFutureOrbit(trained, [observation(trueState, 2600, 527)]);
  assert.equal(trained.objectNorad, 527);
  assert.ok(Number.isFinite(score.fittedRmsKm));
});

test('J2 Cartesian acceleration matches negative spatial gradient of its potential', () => {
  const state = { ...initial, rKm: [6878.137, 1024, 3091] };
  const hKm = 0.01;
  const accel = accelerationKmS2(state, { j2: true });
  for (let axis = 0; axis < 3; axis++) {
    const plus = [...state.rKm];
    const minus = [...state.rKm];
    plus[axis] += hKm;
    minus[axis] -= hKm;
    const gradient = (potentialKm2S2({ ...state, rKm: plus }, true) -
      potentialKm2S2({ ...state, rKm: minus }, true)) / (2 * hKm);
    assert.ok(Math.abs(accel[axis] + gradient) < 2e-10, 'force and potential disagree on axis ' + axis);
  }
});
