import test from 'node:test';
import assert from 'node:assert/strict';
import { stageDocumentedCartesianPositions } from '../src/lib/orbitObservationIntake.ts';

// ALL Cartesian measurements below are synthetic controls, not 1963 tracks.
// C197 is a REAL original document, but only for the catalogue decay day.
const context = {
  objectNorad: 529,
  initialEpochUtc: '1963-10-27T14:40:16Z',
  cutoffEpochUtc: '1963-10-28T00:00:00Z',
  inertialFrame: 'SYNTHETIC_ECI',
  phase: 'HOLDOUT',
};
const synthetic = (epoch, overrides = {}) => ({
  kind: 'ORIGINAL_INSTRUMENT_CARTESIAN',
  objectNorad: 529,
  matrixOccurrence: 'SYNTHETIC#1',
  documentUrl: 'https://example.test/synthetic-orbit-test',
  lineageRoot: 'SYNTHETIC_SINGLE_INSTRUMENT',
  observationEpochUtc: epoch,
  publicationDateUtc: '1963-11-15T00:00:00Z',
  inertialFrame: 'SYNTHETIC_ECI',
  rKm: [6800, 100, 200],
  sigmaKm: [0.5, 0.5, 1],
  instrumentRecordId: 'SYNTHETIC-ONLY',
  calibrationReference: 'SYNTHETIC-ONLY',
  custody: 'SYNTHETIC',
  ...overrides,
});

test('C197#1 day-only NASA original is NEVER a Cartesian observation', () => {
  const nasa = synthetic(null, {
    kind: 'CATALOG_DECAY_DAY', objectNorad: 528, matrixOccurrence: 'C197#1',
    documentUrl: 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf',
    lineageRoot: 'NASA_SSR_1963_11_15',
    custody: 'CATALOG',
    instrumentRecordId: null, calibrationReference: null,
    rKm: null, sigmaKm: null,
  });
  const result = stageDocumentedCartesianPositions([nasa], context);
  assert.equal(result.status, 'CONNECTED_PENDING_CALIBRATION');
  assert.deepEqual(result.positions, []);
  assert.equal(result.traces[0].reason, 'NOT_ORIGINAL_CARTESIAN');
  assert.equal(result.historicalHoldoutValidated, false);
});

test('secondary C179 TLE cannot masquerade as a directly measured Cartesian state', () => {
  const tle = synthetic('1963-10-29T00:00:00Z', {
    kind: 'DERIVED_ORBITAL_ELEMENTS', matrixOccurrence: 'C179#1', custody: 'SECONDARY',
  });
  const result = stageDocumentedCartesianPositions([tle], context);
  assert.equal(result.traces[0].reason, 'NOT_ORIGINAL_CARTESIAN');
  assert.equal(result.positions.length, 0);
});

test('two conditionally admissible SYNTHETIC future vectors preserve exact epochs and lineage', () => {
  const result = stageDocumentedCartesianPositions([
    synthetic('1963-10-29T00:00:00Z'),
    synthetic('1963-10-29T01:00:00Z'),
  ], context);
  assert.equal(result.status, 'CONDITIONAL_UNWEIGHTED_INPUTS');
  assert.equal(result.positions.length, 2);
  assert.equal(result.positions[1].elapsedS - result.positions[0].elapsedS, 3600);
  assert.match(result.positions[0].source, /lineage=SYNTHETIC_SINGLE_INSTRUMENT/);
  assert.equal(result.uncertaintyUsedInFit, false);
  assert.equal(result.independentInstrumentObservationsVerified, false);
  assert.equal(result.impactInference, 'NOT_SUPPORTED');
});

test('mixed batch fails atomically instead of silently dropping bad historical rows', () => {
  const result = stageDocumentedCartesianPositions([
    synthetic('1963-10-29T00:00:00Z'),
    synthetic(null),
  ], context);
  assert.equal(result.status, 'CONNECTED_PENDING_CALIBRATION');
  assert.equal(result.traces[0].reason, null);
  assert.equal(result.traces[1].reason, 'MISSING_OR_INVALID_OBSERVATION_EPOCH');
  assert.deepEqual(result.positions, []);
});

test('no future leakage or duplicate instrument-derived epoch is admitted', () => {
  const early = stageDocumentedCartesianPositions([
    synthetic('1963-10-27T18:00:00Z'),
  ], context);
  assert.equal(early.traces[0].reason, 'OUTSIDE_PREDECLARED_SPLIT');
  const duplicate = stageDocumentedCartesianPositions([
    synthetic('1963-10-29T00:00:00Z'),
    synthetic('1963-10-29T00:00:00Z', {lineageRoot: 'RENAMED_COPY'}),
  ], context);
  assert.equal(duplicate.traces[1].reason, 'DUPLICATE_OR_NONMONOTONE_EPOCH');
  assert.deepEqual(duplicate.positions, []);
});

test('missing calibration, uncertainty, instrument identity, frame, and honest UTC block admission', () => {
  const cases = [
    [{sigmaKm: null}, 'INVALID_POSITION_OR_UNCERTAINTY'],
    [{sigmaKm: [0, 0.5, 1]}, 'INVALID_POSITION_OR_UNCERTAINTY'],
    [{sigmaKm: [1, Infinity, 1]}, 'INVALID_POSITION_OR_UNCERTAINTY'],
    [{calibrationReference: ''}, 'MISSING_INSTRUMENT_CALIBRATION'],
    [{instrumentRecordId: null}, 'MISSING_INSTRUMENT_CALIBRATION'],
    [{inertialFrame: 'TEME'}, 'INCOMPATIBLE_TARGET_OR_FRAME'],
    [{observationEpochUtc: '1963-10-29'}, 'MISSING_OR_INVALID_OBSERVATION_EPOCH'],
    [{documentUrl: ''}, 'MISSING_DOCUMENTARY_LINEAGE'],
  ];
  for (const [fields, expected] of cases) {
    const result = stageDocumentedCartesianPositions([
      synthetic('1963-10-29T00:00:00Z', fields),
    ], context);
    assert.equal(result.traces[0].reason, expected, JSON.stringify(fields));
    assert.deepEqual(result.positions, []);
  }
});

test('training observations are accepted only before predeclared cutoff', () => {
  const training = {...context, phase: 'TRAINING'};
  const accepted = stageDocumentedCartesianPositions([
    synthetic('1963-10-27T18:00:00Z'),
  ], training);
  assert.equal(accepted.status, 'CONDITIONAL_UNWEIGHTED_INPUTS');
  const future = stageDocumentedCartesianPositions([
    synthetic('1963-10-29T00:00:00Z'),
  ], training);
  assert.equal(future.traces[0].reason, 'OUTSIDE_PREDECLARED_SPLIT');
});
