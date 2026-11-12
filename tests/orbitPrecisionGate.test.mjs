import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagate } from '../src/lib/orbitPhysics.ts';
import { auditDocumentedHoldoutResolution } from '../src/lib/orbitPrecisionGate.ts';

// ALL Cartesian samples here are fabricated numerical controls, NOT 1963
// instrument observations. No observational covariance or Lean interval
// has been inferred from the real NASA decay-day record.
const origin = '1963-10-27T00:00:00Z';
const cutoff = '1963-10-27T00:20:00Z';
const frame = 'SYNTHETIC_ECI';
const radius = EARTH.radiusKm + 500;
const circular = {
  rKm: [radius, 0, 0], vKmS: [0, Math.sqrt(EARTH.muKm3S2 / radius), 0], tS: 0,
};
const dynamics = {j2: true};
const controls = {
  halvings: 3,
  tolerance: {positionKm: 0.02, velocityKmS: 0.0001, epochS: 0.02},
};
const epoch = sec => new Date(Date.parse(origin) + sec * 1000).toISOString();
const documented = (sec, record, fields = {}) => ({
  kind: 'ORIGINAL_INSTRUMENT_CARTESIAN', custody: 'SYNTHETIC',
  objectNorad: 529, matrixOccurrence: 'SYNTHETIC#' + record,
  documentUrl: 'https://example.test/synthetic-instrument-control',
  lineageRoot: 'SYNTHETIC_SINGLE_FACILITY',
  instrumentRecordId: record, calibrationReference: 'SYNTHETIC_ONLY',
  publicationDateUtc: null, observationEpochUtc: epoch(sec),
  inertialFrame: frame, sigmaKm: [10, 10, 10],
  rKm: propagate(circular, sec, 2, 80, dynamics).state.rKm,
  ...fields,
});
const training = [
  documented(300, 'TRAIN-1'),
  documented(900, 'TRAIN-2'),
];
const holdout = [
  documented(2600, 'FUTURE-1'),
  documented(3200, 'FUTURE-2'),
];
const fit = (fields = {}) => ({
  objectNorad: 529, initialEpochUtc: origin, cutoffEpochUtc: cutoff,
  inertialFrame: frame, initialState: circular, fittedState: circular,
  trainingCount: 2, trainingBaselineRmsKm: 0, trainingFittedRmsKm: 0,
  evaluations: 1, stepS: 80, terminationAltitudeKm: 80, dynamics,
  ...fields,
});

test('synthetic accurate-looking holdout: only a CONDITIONAL numerical resolution gate passes', () => {
  const result = auditDocumentedHoldoutResolution(fit(), training, holdout, controls, 0.1);
  assert.equal(result.status, 'CONDITIONAL_RESOLUTION_ONLY');
  assert.equal(result.numericalHoldout.status, 'NUMERICALLY_INDISTINGUISHABLE');
  assert.equal(result.minimumDeclaredSigmaKm, 10);
  assert.ok(result.resolutionScaleKm <= 1);
  assert.ok(result.worstRecentRefinementKm >= 0);
  assert.equal(result.verifiedInstrumentIndependence, false);
  assert.equal(result.covarianceOrLikelihoodCalibrated, false);
  assert.equal(result.historicalHoldoutValidated, false);
  assert.equal(result.impactInference, 'NOT_SUPPORTED');
});

test('a too-loose RK4 numerical tolerance is insufficient for fine reported sigma', () => {
  const tooPrecise = holdout.map(row => ({...row, sigmaKm: [1e-6, 1e-6, 1e-6]}));
  const result = auditDocumentedHoldoutResolution(fit(), training, tooPrecise, controls, 0.1);
  assert.equal(result.status, 'INSUFFICIENT_NUMERICAL_RESOLUTION');
  assert.equal(result.minimumDeclaredSigmaKm, 1e-6);
  assert.ok(result.resolutionScaleKm > 1e-7);
  assert.ok(result.numericalHoldout.levels.length >= 3);
});

test('predeclared strict fraction controls resolution budget, never a hidden p-value', () => {
  const wide = auditDocumentedHoldoutResolution(fit(), training, holdout, controls, 0.1);
  const narrow = auditDocumentedHoldoutResolution(fit(), training, holdout, controls, 1e-5);
  assert.equal(wide.status, 'CONDITIONAL_RESOLUTION_ONLY');
  assert.equal(narrow.status, 'INSUFFICIENT_NUMERICAL_RESOLUTION');
  assert.equal(wide.minimumDeclaredSigmaKm, narrow.minimumDeclaredSigmaKm);
  assert.deepEqual(wide.numericalHoldout.levels, narrow.numericalHoldout.levels);
  for (const fraction of [0, -1, 1.01, NaN, Infinity])
    assert.throws(() => auditDocumentedHoldoutResolution(fit(), training, holdout, controls, fraction), /predeclared fraction/);
});

test('C197 NASA primary only reports decay day: documentation gate prevents any holdout propagation', () => {
  const catalogue = documented(2600, 'NASA-DECAY-DAY', {
    objectNorad: 528, kind: 'CATALOG_DECAY_DAY', custody: 'CATALOG',
    matrixOccurrence: 'C197#1',
    documentUrl: 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf',
    observationEpochUtc: null, rKm: null, sigmaKm: null,
    calibrationReference: null,
  });
  const result = auditDocumentedHoldoutResolution(fit(), training, [catalogue], controls, 0.1);
  assert.equal(result.status, 'BLOCKED_DOCUMENTATION');
  assert.equal(result.intake.holdoutTraces[0].reason, 'NOT_ORIGINAL_CARTESIAN');
  assert.equal(result.numericalHoldout, null);
});

test('recycled instrument identity blocks entire train/holdout split, not just its duplicates', () => {
  const duplicated = documented(2600, 'TRAIN-1', {matrixOccurrence: 'SYNTHETIC#COPY'});
  const result = auditDocumentedHoldoutResolution(fit(), training, [duplicated], controls, 0.1);
  assert.equal(result.status, 'BLOCKED_DOCUMENTATION');
  assert.equal(result.intake.reusedRecords.length, 1);
  assert.deepEqual(result.intake.trainingPositions, []);
  assert.deepEqual(result.intake.holdoutPositions, []);
});

test('training-count mismatch and unresolved numerical refinement block ranking', () => {
  const unknownFit = auditDocumentedHoldoutResolution(fit({trainingCount: 0}),
    training, holdout, controls, 0.1);
  assert.equal(unknownFit.status, 'BLOCKED_DOCUMENTATION');
  const strict = auditDocumentedHoldoutResolution(fit(), training, holdout, {
    halvings: 2, tolerance: {positionKm: 1e-15, velocityKmS: 1e-15, epochS: 1e-15},
  }, 0.1);
  assert.equal(strict.status, 'BLOCKED_NUMERICAL_AUDIT');
  assert.equal(strict.numericalHoldout.status, 'NOT_RESOLVED');
  assert.equal(strict.resolutionScaleKm, null);
});
