import test from 'node:test';
import assert from 'node:assert/strict';
import { auditTemeInertialCovariance } from '../src/lib/orbitFrameCovariance.ts';

// All inputs here are deliberately synthetic, NOT satellite observations.
const t = '1963-10-27T14:40:16.132Z';
const identity = [1,0,0,0,1,0,0,0,1];
const zero = Array(9).fill(0);
const frame = {
  from: 'TEME', to: 'ECI_DECLARED', epochUtc: t,
  rotationRowMajor: identity, rotationRateRowMajorPerS: zero,
  sourceOccurrence: 'SYNTHETIC#FRAME', sourceUrl: 'https://example.test/frame',
  sourceSha256: 'a'.repeat(64), positionFrameSigmaKm: 1,
  velocityFrameSigmaKmS: 0.01, provenance: 'SYNTHETIC_CONTROL',
};
const diag = [4,9,16,0.04,0.09,0.16];
const matrix = (diagonal) => diagonal.map((x,i) =>
  diagonal.map((_,j) => i===j ? x : 0));
const observation = {
  epochUtc: t, sourceOccurrence: 'SYNTHETIC#MEASUREMENT',
  sourceUrl: 'https://example.test/covariance', sourceSha256: 'b'.repeat(64),
  provenance: 'SYNTHETIC_CONTROL', covariance: matrix(diag),
};
const audit = (o=observation, f=frame) => auditTemeInertialCovariance(o,f);
const close = (actual, expected, tol=1e-10) =>
  assert.ok(Math.abs(actual-expected) < tol, `${actual} != ${expected}`);

test('absence of documented TEME-to-ECI axes blocks covariance transport', () => {
  const result=audit(observation,null);
  assert.equal(result.status,'FRAME_NOT_DOCUMENTED');
  assert.equal(result.transformedCovariance,null);
});

test('identity transports all six SI-compatible diagonal units unchanged', () => {
  const result=audit();
  assert.equal(result.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.deepEqual(result.transformedCovariance,observation.covariance);
  assert.equal(result.rateCouplingIncluded,true);
  assert.equal(result.frameSystematicsIncluded,false);
  assert.equal(result.measurementCovarianceAuthenticated,false);
  assert.equal(result.historicalHoldoutValidated,false);
  assert.equal(result.impactInference,'NOT_SUPPORTED');
});

test('Rdot position errors produce velocity variance and cross-block covariance', () => {
  const omega=7.292115e-5; // demonstration, not a documented 1963 EOP record
  const d=[0,-omega,0,omega,0,0,0,0,0];
  const c=audit(observation,{...frame,rotationRateRowMajorPerS:d}).transformedCovariance;
  close(c[4][4],diag[4]+omega*omega*diag[0]);
  close(c[0][4],omega*diag[0]); // km^2 / s
  close(c[4][0],omega*diag[0]);
  close(c[1][3],-omega*diag[1]);
  close(c[3][3],diag[3]+omega*omega*diag[1]);
  assert.notEqual(c[4][4],diag[4]);
});

test('proper quarter-turn rotates position/velocity covariance, not just a scalar sigma', () => {
  const q=[0,-1,0,1,0,0,0,0,1];
  const result=audit(observation,{...frame,rotationRowMajor:q});
  assert.equal(result.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.deepEqual(result.transformedCovariance.map((row,i)=>row[i]),
    [9,4,16,0.09,0.04,0.16]);
});

test('forward plus inverse rate transport recovers all 36 original covariance entries', () => {
  const omega=7.292115e-5;
  const d=[0,-omega,0,omega,0,0,0,0,0];
  const forward=audit(observation,{...frame,rotationRateRowMajorPerS:d});
  const reverse=audit({...observation,covariance:forward.transformedCovariance},
    {...frame,rotationRateRowMajorPerS:d.map(x=>-x)});
  assert.equal(reverse.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  for(let i=0;i<6;i++) for(let j=0;j<6;j++)
    close(reverse.transformedCovariance[i][j],observation.covariance[i][j]);
});

test('rejects asymmetric, singular, indefinite and ill-conditioned covariance', () => {
  const asymmetric=matrix(diag); asymmetric[0][1]=0.1;
  const singular=matrix(diag); singular[0][0]=0;
  const indefinite=matrix(diag); indefinite[0][1]=100; indefinite[1][0]=100;
  const nearly=matrix(diag); nearly[0][1]=6*(1-1e-12);
  nearly[1][0]=nearly[0][1];
  for(const covariance of [asymmetric,singular,indefinite,nearly])
    assert.equal(audit({...observation,covariance}).status,'COVARIANCE_INADMISSIBLE');
});

test('rejects absent lineage, non-finite values and wrong covariance dimension', () => {
  for (const sample of [
    {...observation,sourceOccurrence:''},
    {...observation,sourceSha256:'bad'},
    {...observation,covariance:matrix(diag).slice(1)},
    {...observation,covariance:matrix([4,9,16,NaN,0.09,0.16])},
  ]) assert.equal(audit(sample).status,'COVARIANCE_INADMISSIBLE');
});

test('rejects missing EOP lineage and epoch mismatch instead of guessing history', () => {
  assert.equal(audit(observation,{...frame,provenance:'DOCUMENTED_CONDITIONAL'}).status,
    'TRANSFORM_INADMISSIBLE');
  assert.equal(audit({...observation,epochUtc:'1963-11-08T00:00:00Z'}).status,
    'EPOCH_MISMATCH');
  assert.equal(audit(observation,{...frame,rotationRowMajor:[-1,0,0,0,1,0,0,0,1]}).status,
    'TRANSFORM_INADMISSIBLE');
});

test('even two declared source lineages cannot establish historical holdout', () => {
  const f={...frame,provenance:'DOCUMENTED_CONDITIONAL',
    eopEpochSourceUrl:'https://example.test/uncorroborated-eop',
    eopEpochSourceSha256:'c'.repeat(64)};
  const result=audit({...observation,provenance:'DOCUMENTED_CONDITIONAL'},f);
  assert.equal(result.status,'CONDITIONAL_DIAGNOSTIC_ONLY');
  assert.equal(result.frameSystematicsIncluded,false);
  assert.equal(result.historicalHoldoutValidated,false);
});
