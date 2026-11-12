import test from 'node:test';
import assert from 'node:assert/strict';
import { sampleVelocityBox } from '../src/lib/orbitBoxSampling.ts';
import { runConditionalVelocityDomain } from '../src/lib/orbitAdmissibility.ts';
import { EARTH } from '../src/lib/orbitPhysics.ts';

const max = Number.MAX_VALUE, min = Number.MIN_VALUE;
const box = [[-max, max], [-min, min], [0, 0]];
const inside = (points, ranges) => {
  for (const p of points) for (let i=0;i<3;i++) {
    assert.ok(Number.isFinite(p[i]), 'Every sampled component must be finite');
    assert.ok(p[i] >= ranges[i][0] && p[i] <= ranges[i][1],
      'axis ' + i + ' escaped declared interval');
  }
};
test('opposing finite Float64 extremes cannot overflow the midpoint or interior', () => {
  assert.equal(Number.isFinite((-max) + (max - (-max)) / 2),false,
    'regression: old interpolation becomes Infinity');
  const p = sampleVelocityBox(box,19763,100);
  assert.deepEqual(p[0],[0,0,0]);
  inside(p,box);
  assert.ok(p.some(v=>v[0]===-max));
  assert.ok(p.some(v=>v[0]===max));
  assert.ok(p.some(v=>v[1]===-min));
  assert.ok(p.some(v=>v[1]===min));
  assert.ok(p.length>8);
});
test('signed subnormal singleton boxes are exact, not collapsed to zero', () => {
  const ranges=[[min,min],[-min,-min],[1,1]];
  assert.deepEqual(sampleVelocityBox(ranges,9,100),[[min,-min,1]]);
});
test('same-sign huge finite intervals and narrow ranges stay inside', () => {
  const ranges=[[max/2,max],[-max,-max/2],[min,2*min]];
  inside(sampleVelocityBox(ranges,999,100),ranges);
});
test('synthetic seeds are repeatable, distinct, with finite bounded witnesses', () => {
  const range=[[-0.1,0.1],[7.5,7.6],[-0.01,0.01]];
  const a=sampleVelocityBox(range,101,90);
  assert.deepEqual(a,sampleVelocityBox(range,101,90));
  assert.notDeepEqual(a,sampleVelocityBox(range,102,90));
  assert.ok(a.length>9);
  inside(a,range);
});
test('negative zero and degenerate corners never multiply physical witnesses', () => {
  assert.deepEqual(sampleVelocityBox([[0,0],[-0,0],[0,0]],1,0),[[0,0,0]]);
  for(const bad of [
    [[1,0],[0,1],[0,1]],[[0,Infinity],[0,1],[0,1]],
    [[0,1],[0,1]],[[NaN,1],[0,1],[0,1]],
  ]) assert.throws(()=>sampleVelocityBox(bad,1,2),/three finite/);
  assert.throws(()=>sampleVelocityBox([[0,1],[0,1],[0,1]],0,2),/uint32/);
  assert.throws(()=>sampleVelocityBox([[0,1],[0,1],[0,1]],1,101),/uint32/);
});
test('physically coupled J2 propagation consumes exactly the sampled velocity witnesses', () => {
  const epochUtc='1963-10-27T00:00:00.000Z';
  const inertialFrame='SYNTHETIC_ECI';
  const radius=EARTH.radiusKm+500;
  const speed=Math.sqrt(EARTH.muKm3S2/radius);
  const ranges=[[-0.01,0.01],[speed-0.01,speed+0.01],[-0.001,0.001]];
  const scenario={
    objectNorad:529,epochUtc,inertialFrame,
    initial:{rKm:[radius,0,0],vKmS:[0,speed,0],tS:0},
    bounds:ranges.map(([lowerKmS,upperKmS],i)=>({
      axis:['vx','vy','vz'][i],lowerKmS,upperKmS,
      evidenceOccurrence:'SYNTHETIC-BOX-'+i,
      sourceLineage:'synthetic self-contained test',
      leanPredicate:'NOT_AVAILABLE',
      premiseStatus:'SYNTHETIC',epochUtc,inertialFrame,
    })),
  };
  const controls={
    seed:19763,interiorDraws:3,durationS:60,stepS:30,
    terminationAltitudeKm:80,
    convergence:{halvings:2,tolerance:{
      positionKm:0.1,velocityKmS:0.001,epochS:0.01,
    }},
  };
  const run=runConditionalVelocityDomain(scenario,controls,{j2:true});
  const repeated=runConditionalVelocityDomain(scenario,controls,{j2:true});
  assert.equal(run.status,'SAMPLED_CONDITIONALLY');
  assert.deepEqual(run,repeated);
  assert.deepEqual(run.samples.map(s=>s.vKmS),
    sampleVelocityBox(ranges,controls.seed,controls.interiorDraws));
  assert.ok(run.samples.every(s=>s.numerical.levels.length===3));
  assert.equal(run.historicalHoldout,'NOT_RUN');
  assert.equal(run.proofVerification,'NOT_RUN');
  assert.equal(run.exhaustivePhysicalEnclosure,false);
  assert.equal(run.geographicInference,'NOT_SUPPORTED');
});
