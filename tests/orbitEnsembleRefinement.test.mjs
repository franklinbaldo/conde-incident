import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, propagateEnsemble } from '../src/lib/orbitPhysics.ts';
import { auditSeededEnsembleRefinement } from '../src/lib/orbitEnsembleRefinement.ts';

// Every orbit and parameter here is SYNTHETIC, not a 1963 instrument record.
const radius=EARTH.radiusKm+500;
const circular={
  rKm:[radius,0,0],
  vKmS:[0,Math.sqrt(EARTH.muKm3S2/radius),0],
  tS:0,
};
const controls={halvings:3,tolerance:{
  positionKm:0.02,velocityKmS:0.0001,epochS:0.02,
}};
const audit=(seed=1963,count=6,spread=0.004,c=controls,state=circular,
  duration=1200,step=40,threshold=80)=>
  auditSeededEnsembleRefinement(state,seed,count,spread,duration,step,
    threshold,c,{j2:true});

test('same seeded member is repropagated at every resolution (no reroll)',()=>{
  const a=audit(),b=audit();
  assert.deepEqual(a,b,'deterministic seed and controls');
  assert.equal(a.status,'STABLE_ELAPSED_ONLY');
  assert.equal(a.members.length,6);
  assert.equal(a.samplingContract,'SEEDED_UNIFORM_CARTESIAN_VELOCITY_CUBE');
  assert.equal(a.distributionCalibrated,false);
  assert.equal(a.historicalHoldoutValidated,false);
  assert.equal(a.likelihoodComputed,false);
  assert.equal(a.impactInference,'NOT_SUPPORTED');
  assert.ok(a.worstRecentPositionDifferenceKm>=0);
  const original=propagateEnsemble(circular,1963,6,0.004,1200,40,80,{j2:true});
  a.members.forEach((member,i)=>{
    assert.equal(member.index,i);
    assert.equal(member.numericalBreakdown,false);
    assert.equal(member.convergence.status,'STABLE');
    assert.deepEqual(member.convergence.levels[0].result,original[i],
      'coarse run must use exactly the original xorshift32 draw');
    assert.deepEqual(member.convergence.levels.map(x=>x.stepS),
      [40,20,10,5]);
  });
  assert.notDeepEqual(a.members.map(x=>x.deltaVKmS),
    audit(1964).members.map(x=>x.deltaVKmS));
});

test('zero velocity spread is a repeated control, not independent evidence',()=>{
  const a=audit(7,3,0);
  assert.deepEqual(a.members[0].convergence,a.members[1].convergence);
  assert.deepEqual(a.members[1].convergence,a.members[2].convergence);
  assert.ok(a.members[0].deltaVKmS.every(x=>x===0),
    'signed zero is physically zero and does not alter the state');
  assert.equal(a.status,'STABLE_ELAPSED_ONLY');
});

test('tight numerical tolerances veto a seemingly deterministic ensemble',()=>{
  const strict={halvings:3,tolerance:{
    positionKm:1e-18,velocityKmS:1e-21,epochS:1e-20,
  }};
  const out=audit(1963,3,0.004,strict);
  assert.equal(out.status,'NOT_RESOLVED');
  assert.ok(out.members.some(x=>x.convergence.status==='NOT_RESOLVED'));
  assert.equal(out.impactInference,'NOT_SUPPORTED');
});

test('a physical threshold crossing cannot become a claimed impact probability',()=>{
  const descending={
    rKm:[EARTH.radiusKm+100,0,0],vKmS:[-1.2,0,0],tS:0,
  };
  const out=audit(9,2,0,controls,descending,100,5,80);
  assert.equal(out.status,'TERMINATION_PRESENT');
  assert.ok(out.members.every(x=>
    x.convergence.finest.event==='reentry-threshold'));
  assert.equal(out.impactInference,'NOT_SUPPORTED');
});

test('unrepresentable member is retained as numerical failure, not excluded',()=>{
  const unrepresentable={
    rKm:[radius,0,0],vKmS:[1e308,1e308,1e308],tS:0,
  };
  const out=audit(11,2,0,controls,unrepresentable);
  assert.equal(out.status,'NOT_RESOLVED');
  assert.ok(out.members.every(x=>x.numericalBreakdown));
  assert.ok(out.members.every(x=>x.convergence===null));
  assert.equal(out.worstRecentPositionDifferenceKm,null);
});

test('invalid seed, count, spread or refinement controls must fail closed',()=>{
  assert.throws(()=>audit(0),/Seed/);
  assert.throws(()=>audit(1,0),/members/);
  assert.throws(()=>audit(1,129),/members/);
  assert.throws(()=>audit(1,2,Infinity),/members/);
  assert.throws(()=>audit(1,2,-0.1),/members/);
  assert.throws(()=>audit(1,2,0.004,{halvings:1,tolerance:controls.tolerance}),
    /halvings/);
});
