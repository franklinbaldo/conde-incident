import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagate } from '../src/lib/orbitPhysics.ts';
import { auditFutureOrbitScore } from '../src/lib/orbitHoldoutAudit.ts';

// These observations and states are GENERATED SYNTHETIC CONTROLS.
// They are NOT original 1963 tracks, TLE-to-ECI conversion or Lean intervals.
const epoch = '1963-10-27T00:00:00.000Z';
const cutoff = '1963-10-27T00:20:00.000Z';
const frame = 'SYNTHETIC-CARTESIAN-INERTIAL';
const v = Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500));
const circular = { rKm: [EARTH.radiusKm + 500, 0, 0], vKmS: [0, v, 0], tS: 0 };
const shifted = { ...circular, vKmS: [0.001, v + 0.009, -0.003] };
const dynamics = { j2: true };
const controls = {
  halvings: 4,
  tolerance: { positionKm: 0.1, velocityKmS: 0.0001, epochS: 0.02 },
};
const fit = (initialState, fittedState, stepS = 100, options = dynamics) => ({
  objectNorad: 529, initialEpochUtc: epoch, cutoffEpochUtc: cutoff, inertialFrame: frame,
  initialState, fittedState, stepS, terminationAltitudeKm: 80, dynamics: options,
  evaluations: 0, trainingCount: 0, trainingBaselineRmsKm: 0, trainingFittedRmsKm: 0,
});
const withheld = (state, seconds, options = dynamics) => ({
  objectNorad: 529, inertialFrame: frame,
  epochUtc: new Date(Date.parse(epoch) + 1000 * seconds).toISOString(),
  elapsedS: seconds,
  source: 'SYNTHETIC heldout position, no independent 1963 source',
  rKm: propagate(state, seconds, 2, 80, options).state.rKm,
});
const samples = (state) => [withheld(state, 2600), withheld(state, 3200)];

test('synthetic future truly favoring the altered fitted state stays apparent, not historically verified', () => {
  const score = auditFutureOrbitScore(fit(circular, shifted), samples(shifted), controls);
  assert.equal(score.status, 'APPARENT_FITTED_BETTER');
  assert.equal(score.levels.length, 5);
  assert.ok(score.levels.at(-1).deltaRmsKm < 0);
  assert.equal(score.observationAuthenticity, 'NOT_VERIFIED');
  assert.equal(score.observationIndependence, 'NOT_VERIFIED');
  assert.equal(score.historicalCalibration, 'NOT_RUN');
  assert.equal(score.impactInference, 'NOT_SUPPORTED');
  assert.equal(score.rigorousErrorEnclosure, false);
  assert.ok(score.points.every(p => p.baseline.status === 'STABLE' && p.fitted.status === 'STABLE'));
});

test('negative synthetic holdout: fitted state is worse than unfitted baseline and this is not hidden', () => {
  const score = auditFutureOrbitScore(fit(circular, shifted), samples(circular), controls);
  assert.equal(score.status, 'APPARENT_BASELINE_BETTER');
  assert.ok(score.levels.at(-1).deltaRmsKm > 0);
  assert.ok(Number.isFinite(score.recentDeltaSensitivityKm));
});

test('identical hypotheses cannot be called an empirical win or numerical proof', () => {
  const score = auditFutureOrbitScore(fit(circular, circular), samples(circular), controls);
  assert.equal(score.status, 'NUMERICALLY_INDISTINGUISHABLE');
  assert.ok(score.levels.every(l => l.deltaRmsKm === 0));
});

test('unresolved step precision blocks ranking even with available synthetic future', () => {
  const veryStrict = {
    halvings: 2,
    tolerance: { positionKm: 1e-14, velocityKmS: 1e-14, epochS: 1e-14 },
  };
  const score = auditFutureOrbitScore(fit(circular, shifted, 300), samples(circular), veryStrict);
  assert.equal(score.status, 'NOT_RESOLVED');
  assert.equal(score.levels.length, 0);
});

const descending = { rKm: [EARTH.radiusKm + 90, 0, 0], vKmS: [-0.15, 8.15, 0], tS: 0 };
const artificialFuture = (seconds) => ({
  objectNorad: 529, inertialFrame: frame,
  epochUtc: new Date(Date.parse(epoch) + 1000 * seconds).toISOString(),
  elapsedS: seconds, rKm: [EARTH.radiusKm + 90, 0, 0],
  source: 'SYNTHETIC impossible future used solely to test rejection',
});

test('negative event falsification: coarse missed descent overrides later apparent agreement', () => {
  const score = auditFutureOrbitScore(
    fit(descending, descending, 3000, {}), [artificialFuture(3000)],
    { ...controls, halvings: 5 });
  assert.equal(score.status, 'EVENT_CONFLICT');
  assert.equal(score.levels.length, 0);
  assert.equal(score.points[0].baseline.levels[0].result.event, 'elapsed');
  assert.equal(score.points[0].baseline.finest.event, 'reentry-threshold');
});

test('a stable assumed threshold is NOT converted into a later position or ground impact', () => {
  const score = auditFutureOrbitScore(
    fit(descending, descending, 100, {}), [artificialFuture(3000)], controls);
  assert.equal(score.status, 'MODEL_TERMINATED');
  assert.equal(score.levels.length, 0);
  assert.equal(score.impactInference, 'NOT_SUPPORTED');
});

test('strict chronological source/frame/identity gate is reused before any numerical score', () => {
  const good = withheld(circular, 2600);
  assert.throws(() => auditFutureOrbitScore(fit(circular, shifted), [
    { ...good, epochUtc: '1963-10-27T00:15:00.000Z', elapsedS: 900 },
  ], controls), /leakage/);
  assert.throws(() => auditFutureOrbitScore(fit(circular, shifted), [
    { ...good, objectNorad: 527 },
  ], controls), /Mixed target/);
  assert.throws(() => auditFutureOrbitScore(fit(circular, shifted), [
    { ...good, inertialFrame: 'TEME' },
  ], controls), /Mixed target/);
  assert.throws(() => auditFutureOrbitScore(fit(circular, shifted), [
    { ...good, source: '' },
  ], controls), /provenance/);
});
