import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagate } from '../src/lib/orbitPhysics.ts';
import { normalizedCartesianResidual, auditDocumentedCovarianceHoldout } from '../src/lib/orbitCovarianceGate.ts';

// Every Cartesian state below is SYNTHETIC. NASA C197#1 is day-only;
 // neither C197 nor secondary TLE C179 supplies original 527/529 tracks.
const origin='1963-10-27T00:00:00Z', cutoff='1963-10-27T00:20:00Z';
const frame='SYNTHETIC_ECI', r=EARTH.radiusKm+500;
const initial={rKm:[r,0,0],vKmS:[0,Math.sqrt(EARTH.muKm3S2/r),0],tS:0};
const dynamics={j2:true};
const controls={halvings:3,tolerance:{
  positionKm:0.02,velocityKmS:0.0001,epochS:0.02,
}};
const epoch=s=>new Date(Date.parse(origin)+s*1000).toISOString();
const document=(sec,id,fields={})=>({
  kind:'ORIGINAL_INSTRUMENT_CARTESIAN',custody:'SYNTHETIC',objectNorad:529,
  matrixOccurrence:'SYNTHETIC#'+id,
  documentUrl:'https://example.test/orbit-control',
  lineageRoot:'SYNTHETIC_STATION',instrumentRecordId:id,
  calibrationReference:'SYNTHETIC_ONLY',publicationDateUtc:null,
  observationEpochUtc:epoch(sec),inertialFrame:frame,
  sigmaKm:[10,10,10],rKm:propagate(initial,sec,2,80,dynamics).state.rKm,
  ...fields,
});
const training=[document(300,'TRAIN1'),document(900,'TRAIN2')];
const heldout=[document(2600,'FUTURE1'),document(3200,'FUTURE2')];
const fit=(fields={})=>({
  objectNorad:529,initialEpochUtc:origin,cutoffEpochUtc:cutoff,
  inertialFrame:frame,initialState:initial,fittedState:initial,
  trainingCount:2,trainingBaselineRmsKm:0,trainingFittedRmsKm:0,
  evaluations:1,stepS:80,terminationAltitudeKm:80,dynamics,...fields,
});
const diagonal=[[100,0,0],[0,100,0],[0,0,100]];
const correlated=[[100,90,0],[90,100,0],[0,0,100]];
const covariance=(rows=heldout,c=diagonal)=>rows.map(d=>({
  matrixOccurrence:d.matrixOccurrence,instrumentRecordId:d.instrumentRecordId,
  documentUrl:d.documentUrl,
  covarianceSourceUrl:'https://example.test/synthetic-covariance',
  covarianceKm2:c,
}));
const audit=(rows=heldout,cov=covariance(rows),options={})=>
  auditDocumentedCovarianceHoldout(fit(options.fit),training,rows,cov,
    options.controls??controls,options.fraction??0.1);

test('explicit correlations change whitened residual metric, not a probability',()=>{
  assert.ok(Math.abs(normalizedCartesianResidual([10,10,0],diagonal,[10,10,10])-
    Math.sqrt(2))<1e-12);
  const n=normalizedCartesianResidual([10,10,0],correlated,[10,10,10]);
  assert.ok(Math.abs(n-Math.sqrt(2/1.9))<1e-12);
  assert.equal(normalizedCartesianResidual([10,10,0],diagonal,[10,10,10]),Math.sqrt(2));
});

test('asymmetric, non-positive and nearly-singular declared matrices cannot score',()=>{
  for(const bad of [
    [[100,20,0],[0,100,0],[0,0,100]],
    [[100,110,0],[110,100,0],[0,0,100]],
    [[100,100,0],[100,100,0],[0,0,100]],
    [[100,99.9999999999,0],[99.9999999999,100,0],[0,0,100]],
    [[100,0,0],[0,50,0],[0,0,100]],
    [[100,Infinity,0],[Infinity,100,0],[0,0,100]],
  ]) assert.equal(normalizedCartesianResidual([1,2,3],bad,[10,10,10]),null);
});

test('synthetic correlated holdout can only yield a conditional result',()=>{
  const result=audit(heldout,covariance(heldout,correlated));
  assert.equal(result.status,'CONDITIONAL_INDISTINGUISHABLE');
  assert.ok(result.levels.length>=3);
  assert.ok(result.resolutionBudgetSigma<=0.1);
  assert.equal(result.authenticatedHistoricalObservations,false);
  assert.equal(result.crossEpochCorrelationsResolved,false);
  assert.equal(result.covarianceCalibrationVerified,false);
  assert.equal(result.likelihoodComputed,false);
  assert.equal(result.impactInference,'NOT_SUPPORTED');
});

test('missing or unrelated covariance cannot be filled from component sigma',()=>{
  assert.equal(audit(heldout,[]).status,'BLOCKED_COVARIANCE');
  assert.equal(audit(heldout,covariance(heldout).map((c,i)=>
    i===0?{...c,instrumentRecordId:'SOMEONE_ELSE'}:c)).status,'BLOCKED_COVARIANCE');
  assert.equal(audit(heldout,covariance(heldout).map((c,i)=>
    i===0?{...c,covarianceSourceUrl:''}:c)).status,'BLOCKED_COVARIANCE');
  assert.equal(audit(heldout,[...covariance(heldout),covariance(heldout)[0]]).status,
    'BLOCKED_COVARIANCE');
});

test('sigma and covariance diagonal MUST agree; synthetic inconsistency is rejected',()=>{
  const rows=heldout.map(x=>({...x,sigmaKm:[1,1,1]}));
  assert.equal(audit(rows,covariance(rows)).status,'BLOCKED_COVARIANCE');
  assert.deepEqual(audit(rows,covariance(rows)).rejectedOccurrences,
    ['SYNTHETIC#FUTURE1','SYNTHETIC#FUTURE2']);
});

test('numerical error budget in covariance units must be predeclared',()=>{
  const fine=audit(), impossible=audit(heldout,covariance(),{fraction:1e-10});
  assert.equal(fine.status,'CONDITIONAL_INDISTINGUISHABLE');
  assert.equal(impossible.status,'INSUFFICIENT_NUMERICAL_RESOLUTION');
  assert.ok(impossible.resolutionBudgetSigma>1e-10);
  for(const fraction of [0,-1,1.01,Infinity,NaN])
    assert.throws(()=>auditDocumentedCovarianceHoldout(fit(),training,heldout,
      covariance(),controls,fraction),/Predeclare numerical fraction/);
});

test('documented day-only NASA C197 is not a Cartesian holdout even with fake covariance',()=>{
  const nasa=document(2600,'NASA-DAY',{
    matrixOccurrence:'C197#1',objectNorad:528,kind:'CATALOG_DECAY_DAY',
    custody:'CATALOG',observationEpochUtc:null,rKm:null,sigmaKm:null,
    documentUrl:'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf',
  });
  const result=audit([nasa],covariance([nasa]));
  assert.equal(result.status,'BLOCKED_DOCUMENTATION');
  assert.deepEqual(result.levels,[]);
});

test('reused training record or unknown fit provenance blocks any covariance ranking',()=>{
  const replay=document(2600,'TRAIN1',{matrixOccurrence:'SYNTHETIC#COPY'});
  assert.equal(audit([replay],covariance([replay])).status,'BLOCKED_DOCUMENTATION');
  assert.equal(audit(heldout,covariance(),{fit:{trainingCount:1}}).status,
    'BLOCKED_DOCUMENTATION');
});

test('unresolved numerical convergence blocks covariance ranking',()=>{
  const strict={halvings:2,tolerance:{
    positionKm:1e-15,velocityKmS:1e-15,epochS:1e-15,
  }};
  assert.equal(audit(heldout,covariance(),{controls:strict}).status,
    'BLOCKED_NUMERICAL_AUDIT');
});
