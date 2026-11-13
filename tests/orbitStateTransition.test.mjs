import test from 'node:test';
import assert from 'node:assert/strict';
import { auditTemeInertialCovariance } from '../src/lib/orbitFrameCovariance.ts';
import { auditCartesianStateTransition } from '../src/lib/orbitStateTransition.ts';

// Synthetic 1963-dated control: no original tracking, EOP or covariance claim.
const t='1963-10-27T14:40:16.132Z';
const identity=[1,0,0,0,1,0,0,0,1], zero=Array(9).fill(0);
const frame={
  from:'TEME',to:'ECI_DECLARED',epochUtc:t,rotationRowMajor:identity,
  rotationRateRowMajorPerS:zero,sourceOccurrence:'SYNTHETIC#FRAME',
  sourceUrl:'https://example.test/axes',sourceSha256:'a'.repeat(64),
  positionFrameSigmaKm:1,velocityFrameSigmaKmS:0.01,provenance:'SYNTHETIC_CONTROL',
};
const diagonal=[4,9,16,0.04,0.09,0.16];
const covariance=diagonal.map((v,i)=>diagonal.map((_,j)=>i===j?v:0));
const source={
  epochUtc:t,sourceOccurrence:'SYNTHETIC#COV',
  sourceUrl:'https://example.test/cov',sourceSha256:'b'.repeat(64),
  provenance:'SYNTHETIC_CONTROL',covariance,
};
const admitted=auditTemeInertialCovariance(source,frame);
const initial={frame:'ECI_DECLARED',epochUtc:t,state:{rKm:[7000,0,0],vKmS:[0,7.5,1],tS:0}};
const resolution={
  positionPerturbationKm:0.01,velocityPerturbationKmS:0.00001,
  maxScaledJacobianDrift:1e-3,maxStateDifferenceKm:0.01,
  maxVelocityDifferenceKmS:0.00001,
};
const audit=(i=initial,c=admitted,duration=10,step=2,dynamics={j2:true},r=resolution,threshold=100)=>
  auditCartesianStateTransition(i,c,duration,step,threshold,dynamics,r);

test('G29 covariance retains exact epoch required by G31',()=>{
  assert.equal(admitted.epochUtc,t);
  assert.equal(auditTemeInertialCovariance(source,null).epochUtc,null);
});

test('full 6D transition is nontrivial: velocity uncertainty grows position variance',()=>{
  const out=audit();
  assert.equal(out.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(out.transitionMatrix.length,6);
  assert.equal(out.propagatedCovariance.length,6);
  assert.ok(Math.abs(out.transitionMatrix[0][3]-10)<0.01); // seconds
  assert.ok(out.propagatedCovariance[0][0]>diagonal[0]+3);
  assert.ok(Math.abs(out.propagatedCovariance[0][3])>0.1); // km²/s
  assert.equal(out.frameSystematicsIncluded,false);
  assert.equal(out.historicalHoldoutValidated,false);
  assert.equal(out.impactInference,'NOT_SUPPORTED');
});

test('zero time has identity STM, no fictitious dynamics or variance',()=>{
  const out=audit(initial,admitted,0);
  assert.equal(out.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.deepEqual(out.propagatedCovariance,covariance);
  assert.deepEqual(out.transitionMatrix.map((row,i)=>row[i]),Array(6).fill(1));
  assert.equal(out.jacobianTimeDrift,0);
});

test('central and J2 propagation yield distinct state-transition sensitivities',()=>{
  const central=audit(initial,admitted,240,30,{j2:false});
  const oblate=audit(initial,admitted,240,30,{j2:true});
  assert.equal(central.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(oblate.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.ok(Math.abs(central.transitionMatrix[3][0]-oblate.transitionMatrix[3][0])>1e-9);
});

test('original-covariance and epoch admission are mandatory',()=>{
  assert.equal(audit(initial,auditTemeInertialCovariance(source,null)).status,'INITIAL_COVARIANCE_UNAVAILABLE');
  assert.equal(audit({...initial,epochUtc:'1963-11-08T00:00:00Z'}).status,'EPOCH_OR_FRAME_MISMATCH');
  assert.equal(audit({...initial,frame:'TEME'}).status,'EPOCH_OR_FRAME_MISMATCH');
});

test('invalid tolerances, negative duration and invalid steps fail closed',()=>{
  assert.equal(audit(initial,admitted,-1).status,'INVALID_RESOLUTION_CONTRACT');
  assert.equal(audit(initial,admitted,10,0).status,'INVALID_RESOLUTION_CONTRACT');
  assert.equal(audit(initial,admitted,10,2,{}, {...resolution,maxScaledJacobianDrift:0}).status,
    'INVALID_RESOLUTION_CONTRACT');
});

test('unresolved reentry threshold in any perturbation prevents covariance claims',()=>{
  const out=audit(initial,admitted,10,2,{},resolution,700);
  assert.equal(out.status,'PROPAGATION_UNRESOLVED');
  assert.equal(out.propagatedCovariance,null);
});

test('unresolved independent refinement blocks an apparently precise covariance',()=>{
  const out=audit(initial,admitted,240,80,{j2:true},
    {...resolution,maxStateDifferenceKm:1e-22,maxVelocityDifferenceKmS:1e-22,
      maxScaledJacobianDrift:1e-22});
  assert.equal(out.status,'NUMERICAL_UNRESOLVED');
  assert.equal(out.propagatedCovariance,null);
});

test('documented-conditional labels never become historical validation',()=>{
  const documentedFrame={...frame,provenance:'DOCUMENTED_CONDITIONAL',
    eopEpochSourceUrl:'https://example.test/unverified-eop',eopEpochSourceSha256:'c'.repeat(64)};
  const documented=auditTemeInertialCovariance({...source,provenance:'DOCUMENTED_CONDITIONAL'},
    documentedFrame);
  assert.equal(audit(initial,documented).status,'CONDITIONAL_DIAGNOSTIC_ONLY');
  assert.equal(audit(initial,documented).historicalHoldoutValidated,false);
});
