import test from 'node:test';
import assert from 'node:assert/strict';
import { auditTemeInertialCovariance } from '../src/lib/orbitFrameCovariance.ts';
import { auditStmNonlinearEnvelope, correlatedSigmaControls } from '../src/lib/orbitStmEnvelope.ts';

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

test('G33 evaluates 72 correlated axial and mixed controls without historical inference',()=>{
  const out=audit();
  assert.equal(out.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(out.controlsEvaluated,72);
  assert.ok(out.positionRemainderKm>=0 && out.positionRemainderKm<budget.maxPositionRemainderKm);
  assert.ok(out.velocityRemainderKmS>=0 && out.velocityRemainderKmS<budget.maxVelocityRemainderKmS);
  assert.ok(out.mixedPositionRemainderKm >= 0);
  assert.ok(out.axialPositionRemainderKm >= 0);
  assert.equal(out.historicalHoldoutValidated,false);
  assert.equal(out.frameSystematicsIncluded,false);
  assert.equal(out.impactInference,'NOT_SUPPORTED');
});

test('G32 zero-duration identity produces only roundoff-scale remainder',()=>{
  const out=audit(initial,admitted,0);
  assert.equal(out.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(out.controlsEvaluated,72);
  assert.ok(out.positionRemainderKm < 1e-8);
});

test('finite-amplitude nonlinearity can defeat a numerically stable G31 Jacobian',()=>{
  const out=audit(initial,admitted,240,30,{j2:true},resolution,
    {...budget,maxPositionRemainderKm:1e-12,maxVelocityRemainderKmS:1e-15});
  assert.equal(out.status,'LINEARIZATION_UNRESOLVED');
  assert.equal(out.controlsEvaluated,72);
  assert.ok(out.positionRemainderKm > 1e-12 ||
    out.velocityRemainderKmS > 1e-15);
});

test('correlated position/velocity covariance is admitted and tested',()=>{
  const correlated=c.map(row=>[...row]);
  correlated[0][3]=0.08; correlated[3][0]=0.08;
  const cov=auditTemeInertialCovariance({...source,covariance:correlated},frame);
  assert.equal(cov.status,'SYNTHETIC_DIAGNOSTIC_ONLY');
  assert.equal(audit(initial,cov).controlsEvaluated,72);
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

// Cross-interaction counterexample: F(u) = u_0*u_1, J(0)=0.
// Every axial sigma direction reports zero error; pair directions do not.
test('G33 catches bilinear cross term invisible to all G32 axial controls',()=>{
  const probes=correlatedSigmaControls(c,1);
  assert.equal(probes.length,72);
  assert.equal(probes.filter(p=>p.kind==='AXIAL').length,12);
  assert.equal(probes.filter(p=>p.kind==='MIXED').length,60);
  const coupling=p=>p.delta[0]*p.delta[1];
  assert.ok(probes.filter(p=>p.kind==='AXIAL').every(p=>coupling(p)===0));
  assert.ok(probes.some(p=>p.kind==='MIXED' && Math.abs(coupling(p))>1));
  assert.equal(correlatedSigmaControls(c,0),null);
});

test('G33 uses equal Mahalanobis radius for axes and correlated pairs',()=>{
  const correlated=c.map(row=>[...row]);
  correlated[0][3]=0.08; correlated[3][0]=0.08;
  const controls=correlatedSigmaControls(correlated,2);
  assert.equal(controls.length,72);
  // Independent check: invert covariance via full Gauss-Jordan pivoting.
  const matrix=correlated.map((row,i)=>[
    ...row,...Array.from({length:6},(_,j)=>+(i===j))]);
  for(let k=0;k<6;k++) {
    const pivot=matrix[k][k]; assert.ok(pivot>0);
    for(let j=0;j<12;j++) matrix[k][j]/=pivot;
    for(let i=0;i<6;i++) if(i!==k) {
      const factor=matrix[i][k];
      for(let j=0;j<12;j++) matrix[i][j]-=factor*matrix[k][j];
    }
  }
  const inv=matrix.map(row=>row.slice(6));
  for(const probe of controls) {
    const r2=probe.delta.reduce((sum,x,i)=>sum+x*inv[i].reduce(
      (acc,y,j)=>acc+y*probe.delta[j],0),0);
    assert.ok(Math.abs(r2-4)<1e-10,`${probe.kind}: ${r2}`);
  }
});
