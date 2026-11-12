import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagate } from '../src/lib/orbitPhysics.ts';
import { normalizedJointCartesianResidual, auditDocumentedJointCovarianceHoldout
} from '../src/lib/orbitJointCovariance.ts';

// All observations/covariances below are synthetic, never NORAD telemetry.
const matrix=(rho=0)=>{
  const a=Array.from({length:6},(_,i)=>Array.from({length:6},
    (_,j)=>i===j?100:0));
  a[0][3]=a[3][0]=rho*100;
  return a;
};
const sigma=[[10,10,10],[10,10,10]];
test('declared interepoch correlation changes a metric without becoming a p-value',()=>{
  const same=[[10,0,0],[10,0,0]], opposite=[[10,0,0],[-10,0,0]];
  assert.ok(Math.abs(normalizedJointCartesianResidual(same,sigma,matrix())-
    Math.SQRT2)<1e-12);
  const positive=normalizedJointCartesianResidual(same,sigma,matrix(0.9));
  const negative=normalizedJointCartesianResidual(opposite,sigma,matrix(0.9));
  assert.ok(Math.abs(positive-Math.sqrt(2/1.9))<1e-12);
  assert.ok(Math.abs(negative-Math.sqrt(2/0.1))<1e-12);
  assert.ok(positive<negative);
  assert.equal(normalizedJointCartesianResidual(same,sigma,matrix(1)),null);
  assert.equal(normalizedJointCartesianResidual(same,sigma,matrix(-1)),null);
});
test('dimension, asymmetry, diagonal discrepancy and nonfinite values block',()=>{
  const r=[[1,2,3],[4,5,6]];
  for(const bad of [
    matrix().slice(0,5),
    matrix().map((row,i)=>i===0?row.slice(0,5):row),
    matrix().map((row,i)=>row.map((x,j)=>i===0&&j===3?20:x)),
    matrix().map((row,i)=>row.map((x,j)=>i===0&&j===0?101:x)),
    matrix().map((row,i)=>row.map((x,j)=>i===0&&j===3?Infinity:x)),
  ]) assert.equal(normalizedJointCartesianResidual(r,sigma,bad),null);
  assert.equal(normalizedJointCartesianResidual([[NaN,0,0],[1,0,0]],
    sigma,matrix()),null);
});
const origin='1963-10-27T00:00:00Z',cutoff='1963-10-27T00:20:00Z';
const radius=EARTH.radiusKm+500;
const state={rKm:[radius,0,0],vKmS:[0,Math.sqrt(EARTH.muKm3S2/radius),0],tS:0};
const epoch=s=>new Date(Date.parse(origin)+s*1000).toISOString();
const observation=(s,id,extra={})=>({
  kind:'ORIGINAL_INSTRUMENT_CARTESIAN',custody:'SYNTHETIC',
  objectNorad:529,matrixOccurrence:'SYNTHETIC#'+id,
  documentUrl:'https://example.test/synthetic-orbit',
  lineageRoot:'SYNTHETIC_STATION',instrumentRecordId:id,
  calibrationReference:'SYNTHETIC_ONLY',publicationDateUtc:null,
  observationEpochUtc:epoch(s),inertialFrame:'SYNTHETIC_ECI',
  sigmaKm:[10,10,10],
  rKm:propagate(state,s,2,80,{j2:true}).state.rKm,...extra,
});
const training=[observation(300,'T1'),observation(900,'T2')];
const holdout=[observation(2600,'H1'),observation(3200,'H2')];
const perEpoch=holdout.map(d=>({
  matrixOccurrence:d.matrixOccurrence,instrumentRecordId:d.instrumentRecordId,
  documentUrl:d.documentUrl,covarianceSourceUrl:'https://example.test/per-epoch',
  covarianceKm2:[[100,0,0],[0,100,0],[0,0,100]],
}));
const joint=(m=matrix(0.6))=>({
  covarianceSourceUrl:'https://example.test/interepoch',
  observations:holdout.map(d=>({
    matrixOccurrence:d.matrixOccurrence,instrumentRecordId:d.instrumentRecordId,
    documentUrl:d.documentUrl,observationEpochUtc:d.observationEpochUtc,
  })),covarianceKm2:m,
});
const fit={
  objectNorad:529,initialEpochUtc:origin,cutoffEpochUtc:cutoff,
  inertialFrame:'SYNTHETIC_ECI',initialState:state,fittedState:state,
  trainingCount:2,trainingBaselineRmsKm:0,trainingFittedRmsKm:0,
  evaluations:1,stepS:80,terminationAltitudeKm:80,dynamics:{j2:true},
};
const controls={halvings:3,tolerance:{
  positionKm:0.02,velocityKmS:0.0001,epochS:0.02,
}};
const audit=(h=holdout,p=perEpoch,j=joint(),frac=0.1)=>
  auditDocumentedJointCovarianceHoldout(fit,training,h,p,j,controls,frac);
test('joint diagnostic consumes refined Cartesian r/v, remains conditional',()=>{
  const result=audit();
  assert.equal(result.status,'CONDITIONAL_INDISTINGUISHABLE');
  assert.equal(result.levels.length,4);
  assert.equal(result.declaredJointCovarianceUsed,true);
  assert.ok(result.resolutionBudgetSigma<0.1);
  assert.equal(result.covarianceCalibrationVerified,false);
  assert.equal(result.crossEpochCorrelationEmpiricallyVerified,false);
  assert.equal(result.likelihoodComputed,false);
  assert.equal(result.impactInference,'NOT_SUPPORTED');
});
test('missing source, swapped epochs and diagonal inconsistency are rejected',()=>{
  assert.equal(audit(holdout,perEpoch,{...joint(),covarianceSourceUrl:''}).status,
    'BLOCKED_JOINT_COVARIANCE');
  assert.equal(audit(holdout,perEpoch,{...joint(),
    observations:[...joint().observations].reverse()}).status,
    'BLOCKED_JOINT_COVARIANCE');
  assert.equal(audit(holdout,perEpoch,joint(matrix().map((row,i)=>
    row.map((x,j)=>i===0&&j===0?110:x)))).status,
    'BLOCKED_JOINT_COVARIANCE');
});
test('C197 day-only record is NOT an original instrument holdout',()=>{
  const day=observation(2600,'DAY',{
    objectNorad:528,kind:'CATALOG_DECAY_DAY',custody:'CATALOG',
    observationEpochUtc:null,rKm:null,sigmaKm:null,
    matrixOccurrence:'C197#1',
    documentUrl:'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf',
  });
  assert.equal(audit([day],perEpoch,joint()).status,'BLOCKED_DOCUMENTATION');
});
test('underdocumented numeric budget refuses joint ranking',()=>{
  const result=audit(holdout,perEpoch,joint(),1e-10);
  assert.equal(result.status,'INSUFFICIENT_NUMERICAL_RESOLUTION');
  assert.ok(result.resolutionBudgetSigma>1e-10);
  for(const bad of [0,-1,1.1,NaN,Infinity])
    assert.throws(()=>audit(holdout,perEpoch,joint(),bad),/Predeclare/);
});
