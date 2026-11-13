import test from 'node:test';
import assert from 'node:assert/strict';
import { auditTemeInertialComparison } from '../src/lib/orbitFrameKinematics.ts';

// These values are synthetic vectors/kinematics, not 1963 observations.
const t = '1963-10-27T14:40:16.132Z';
const identity = [1,0,0,0,1,0,0,0,1];
const zero = Array(9).fill(0);
const teme = {
  status: 'SECONDARY_MODEL_ONLY', frame: 'TEME', model: 'SGP4', epochUtc: t,
  stateTeme: {rKm: [7000, 0, 0], vKmS: [0, 7.5, 0], tS: 0},
  sourceOccurrence: 'C179#1', custody: 'DECLARED_DIGEST_NOT_AUTHENTICATED',
  independentHistoricalHoldout: 'NOT_RUN', impactInference: 'NOT_SUPPORTED', tleAgeDays: 0,
};
const inertial = {frame: 'ECI_DECLARED', epochUtc: t,
  state: {rKm: [7000, 0, 0], vKmS: [0, 7.5, 0], tS: 0}};
const scenario = {
  from: 'TEME', to: 'ECI_DECLARED', epochUtc: t,
  rotationRowMajor: identity, rotationRateRowMajorPerS: zero,
  sourceOccurrence: 'SYNTHETIC#FRAME', sourceUrl: 'https://example.test/synthetic-frame',
  sourceSha256: 'a'.repeat(64), positionFrameSigmaKm: 1,
  velocityFrameSigmaKmS: 0.01, provenance: 'SYNTHETIC_CONTROL',
};
const audit = (k = scenario, target = inertial, sample = teme) =>
  auditTemeInertialComparison(sample, target, k);

test('no documented TEME->ECI transform: never subtract raw SGP4 from RK4', () => {
  const result = audit(null);
  assert.equal(result.status, 'FRAME_NOT_DOCUMENTED');
  assert.equal(result.positionSeparationKm, null);
  assert.equal(result.historicalHoldoutValidated, false);
});

test('identity only permitted as explicitly synthetic calibration control', () => {
  const result = audit();
  assert.equal(result.status, 'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(result.positionSeparationKm, 0);
  assert.equal(result.velocitySeparationKmS, 0);
  assert.equal(result.framePositionSigmaKm, 1);
  assert.equal(result.originalTrackingValidated, false);
  assert.equal(result.impactInference, 'NOT_SUPPORTED');
});

test('time-dependent rotation includes Rdot*r: ignoring it gives 0.51 km/s error', () => {
  const omega = 7.292115e-5; // synthetic rotation rate, not measured EOP
  const k = {...scenario, rotationRateRowMajorPerS: [0,-omega,0,omega,0,0,0,0,0]};
  const result = audit(k);
  assert.equal(result.status, 'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.ok(Math.abs(result.transformed.vKmS[1] - (7.5 + 7000 * omega)) < 1e-12);
  assert.ok(Math.abs(result.velocitySeparationKmS - 7000 * omega) < 1e-12);
  assert.equal(result.positionSeparationKm, 0);
});

test('proper quarter-turn transforms r, v and derivative in consistent axes', () => {
  const q = [0,-1,0,1,0,0,0,0,1];
  const omega = 7.292115e-5;
  const dq = [-omega,0,0,0,-omega,0,0,0,0];
  const result = audit({...scenario, rotationRowMajor: q, rotationRateRowMajorPerS: dq});
  assert.deepEqual(result.transformed.rKm, [0,7000,0]);
  assert.ok(Math.abs(result.transformed.vKmS[0] - (-7.5 - 7000*omega)) < 1e-12);
  assert.equal(result.transformed.vKmS[1], 0);
});

test('reflections, shear, non-tangent rotation rates, and infinite elements fail closed', () => {
  const invalid = [
    {...scenario, rotationRowMajor: [-1,0,0,0,1,0,0,0,1]},
    {...scenario, rotationRowMajor: [1,0.1,0,0,1,0,0,0,1]},
    {...scenario, rotationRateRowMajorPerS: [1,0,0,0,0,0,0,0,0]},
    {...scenario, rotationRateRowMajorPerS: [0,-1e-2,0,1e-2,0,0,0,0,0]},
    {...scenario, rotationRowMajor: [NaN,0,0,0,1,0,0,0,1]},
  ];
  for (const candidate of invalid) assert.equal(audit(candidate).status, 'TRANSFORM_INADMISSIBLE');
});

test('source, epoch and uncertainty are mandatory, not filled from catalog day', () => {
  for (const candidate of [
    {...scenario, positionFrameSigmaKm: -1}, {...scenario, velocityFrameSigmaKmS: NaN},
    {...scenario, sourceSha256: ''}, {...scenario, sourceOccurrence: ''},
    {...scenario, provenance: 'DOCUMENTED_CONDITIONAL'},
    {...scenario, to: 'ITRF'},
  ]) assert.equal(audit(candidate).status, 'TRANSFORM_INADMISSIBLE');
  assert.equal(audit({...scenario, epochUtc: '1963-11-08T00:00:00Z'}).status, 'EPOCH_MISMATCH');
  assert.equal(audit(scenario, {...inertial, epochUtc: '1963-10-27T14:40:17.132Z'}).status, 'EPOCH_MISMATCH');
  assert.equal(audit(scenario, inertial, {...teme, epochUtc: '1963-11-08'}).status, 'EPOCH_MISMATCH');
});

test('declared EOP lineage only allows conditional, never historical holdout certification', () => {
  const result = audit({...scenario, provenance: 'DOCUMENTED_CONDITIONAL',
    eopEpochSourceUrl: 'https://example.test/eop-unknown', eopEpochSourceSha256: 'b'.repeat(64)});
  assert.equal(result.status, 'CONDITIONAL_DIAGNOSTIC_ONLY');
  assert.equal(result.historicalHoldoutValidated, false);
});

test('secondary SGP4 numerical failure or counterfeit scenario cannot be compared', () => {
  assert.equal(audit(scenario, inertial, {...teme, status: 'SGP4_UNRESOLVED', stateTeme: null}).status, 'SGP4_NOT_AVAILABLE');
  assert.equal(audit(scenario, inertial, {...teme, status: 'SOURCE_NOT_ADMISSIBLE'}).status, 'SGP4_NOT_AVAILABLE');
  assert.equal(audit(scenario, {...inertial, state: {...inertial.state, rKm: [NaN,0,0]}}).status, 'TRANSFORM_INADMISSIBLE');
});
