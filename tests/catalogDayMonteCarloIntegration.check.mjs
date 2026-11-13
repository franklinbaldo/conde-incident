import test from 'node:test';
import assert from 'node:assert/strict';
import { runMonteCarloSimulation } from '../src/lib/monteCarlo.ts';

// Loaded by tsx in dedicated C241 CI; kept out of vanilla Node glob.
test('existing Monte Carlo returns 3 timing scenarios, without historical claim',()=>{
  const original=Math.random;
  let seed=19631108;
  Math.random=()=>{
    seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;
    return (seed>>>0)/2**32;
  };
  try{
    const r=runMonteCarloSimulation(400);
    assert.equal(r.twoSidedDaySensitivity.length,3);
    for(const row of r.twoSidedDaySensitivity){
      assert.ok([6,12,24].includes(row.sigmaHoursAssumed));
      assert.equal(row.provenance,'C197_DAY_LABEL_SCENARIO_NOT_HISTORICAL_IMPACT');
      assert.ok(row.effectiveSampleSize!==null && row.effectiveSampleSize>0
        && row.effectiveSampleSize<=400.00001);
      const a=row.weightedWithin100Km;
      const b=row.weightedWithin500Km;
      const c=row.weightedWithin2000Km;
      assert.ok(a!==null&&b!==null&&c!==null);
      assert.ok(0<=a&&a<=b&&b<=c&&c<=1);
    }
  }finally{Math.random=original;}
});

