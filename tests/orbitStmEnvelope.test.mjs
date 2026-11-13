import test from 'node:test';
import assert from 'node:assert/strict';
import { auditTemeInertialCovariance } from '../src/lib/orbitFrameCovariance.ts';
import { auditStmNonlinearEnvelope } from '../src/lib/orbitStmEnvelope.ts';

const epoch='1963-10-27T14:40:16.132Z';
const zero=Array(9).fill(0), identity=[1,0,0,0,1,0,0,0,1];
const frame={
  from:'TEME',to:'ECI_DECLARED',epochUtc:epoch,
  rotationRowMajor:identity,rotationRateRowMajorPerS:zero,
  sourceOccurrence:'SYNTHETIC#G32-FRAME',sourceUrl:'https://example.test/frame',
  sourceSha256:'a'.repeat(64),positionFrameSigmaKm:1,
  velocityFrameSigmaKmS:0.01,provenance:'SYNTHETIC_CONTROL',
};
const diag=[4,9,16,0.04,0.09,0.16];
const c=diag.map((v,i)=>diag.map((_,j)=>i===j?v:0));
const source={epochUtc:epoch,sourceOccurrence:'SYNTHETIC#G32-COV',
  sourceUrl:'https://example.test/cov',sourceSha256:'b'.repeat(64),
  provenance:'SYNTHETIC_CONTROL',covariance:c};
const admitted=auditTemeInertialCovariance(source,frame);
const initial={frame:'ECI_DECLARED',epochUtc:epoch,
  state:{rKm:[7000,0,0],vKmS:[0,7.5,1],tS:0}};
const resolution={positionPerturbationKm:0.01,velocityPerturbationKmS:0.00001,
  maxScaledJacobianDrift:1e-3,maxStateDifferenceKm:0.01,
  maxVelocityDifferenceKmS:0.00001};
const budget={sigmaMultiplier:1,maxPositionRemainderKm:0.05,
  maxVelocityRemainderKmS:0.001};
const audit=(i=initial,cov=admitted,duration=10,step=2,
  dynamics={j2:true},r=resolution,b=budget,threshold=100)=>
  auditStmNonlinearEnvelope(i,cov,duration,step,threshold,dynamics,r,b);

test('G32 evaluates 12 correlated finite-amplitude controls without historical inference',()=>{
  const out=audit();
  assert.equal(out.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(out.controlsEvaluated,12);
  assert.ok(out.positionRemainderKm>=0 && out.positionRemainderKm<budget.maxPositionRemainderKm);
  assert.ok(out.velocityRemainderKmS>=0 && out.velocityRemainderKmS<budget.maxVelocityRemainderKmS);
  assert.equal(out.historicalHoldoutValidated,false);
  assert.equal(out.frameSystematicsIncluded,false);
  assert.equal(out.impactInference,'NOT_SUPPORTED');
});

test('G32 zero-duration identity produces only roundoff-scale remainder',()=>{
  const out=audit(initial,admitted,0);
  assert.equal(out.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(out.controlsEvaluated,12);
  assert.ok(out.positionRemainderKm < 1e-8);
});

test('finite-amplitude nonlinearity can defeat a numerically stable G31 Jacobian',()=>{
  const out=audit(initial,admitted,240,30,{j2:true},resolution,
    {...budget,maxPositionRemainderKm:1e-12,maxVelocityRemainderKmS:1e-15});
  assert.equal(out.status,'LINEARIZATION_UNRESOLVED');
  assert.equal(out.controlsEvaluated,12);
  assert.ok(out.positionRemainderKm > 1e-12 ||
    out.velocityRemainderKmS > 1e-15);
});

test('correlated position/velocity covariance is admitted and tested',()=>{
  const correlated=c.map(row=>[...row]);
  correlated[0][3]=0.08; correlated[3][0]=0.08;
  const cov=auditTemeInertialCovariance({...source,covariance:correlated},frame);
  assert.equal(cov.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(audit(initial,cov).controlsEvaluated,12);
});

test('unadmitted covariance and incompatible epoch fail closed',()=>{
  assert.equal(audit(initial,auditTemeInertialCovariance(source,null)).status,
    'BASELINE_NOT_ADMITTED');
  assert.equal(audit({...initial,epochUtc:'1963-11-08T00:00:00Z'}).status,
    'BASELINE_NOT_ADMITTED');
  assert.equal(audit({...initial,frame:'TEME'}).status,'BASELINE_NOT_ADMITTED');
});

test('invalid budgets, sigma size and RK4 step cannot pass as diagnostics',()=>{
  assert.equal(audit(initial,admitted,10,0).status,'INVALID_ENVELOPE_CONTRACT');
  assert.equal(audit(initial,admitted,10,2,{},resolution,
    {...budget,sigmaMultiplier:0}).status,'INVALID_ENVELOPE_CONTRACT');
  assert.equal(audit(initial,admitted,10,2,{},resolution,
    {...budget,maxVelocityRemainderKmS:NaN}).status,'INVALID_ENVELOPE_CONTRACT');
});

test('G31 unresolved timestep prevents declaring a G32 envelope',()=>{
  const out=audit(initial,admitted,240,80,{j2:true},
    {...resolution,maxScaledJacobianDrift:1e-22,
      maxStateDifferenceKm:1e-22,maxVelocityDifferenceKmS:1e-22});
  assert.equal(out.status,'STM_UNRESOLVED');
  assert.equal(out.controlsEvaluated,0);
});

test('event threshold crossing in sigma-point propagation rejects envelope',()=>{
  const out=audit(initial,admitted,10,2,{},resolution,budget,700);
  assert.equal(out.status,'STM_UNRESOLVED');
  assert.equal(out.controlsEvaluated,0);
});

test('documented-conditional covariance remains conditional, not historical',()=>{
  const conditionalFrame={...frame,provenance:'DOCUMENTED_CONDITIONAL',
    eopEpochSourceUrl:'https://example.test/eop',
    eopEpochSourceSha256:'c'.repeat(64)};
  const conditional=auditTemeInertialCovariance(
    {...source,provenance:'DOCUMENTED_CONDITIONAL'},conditionalFrame);
  assert.equal(conditional.status,'CONDITIONAL_DIAGNOSTIC_ONLY');
  const out=audit(initial,conditional);
  assert.equal(out.status,'CONDITIONAL_DIAGNOSTIC_ONLY');
  assert.equal(out.historicalHoldoutValidated,false);
});
