import test from 'node:test';
import assert from 'node:assert/strict';
import {
  CATALOGUE_528, PREDECLARED_DAY_SCENARIOS, catalogueDayLikelihood,
  calendarSpreadScenario, scenarioWeightedCells,
} from '../src/lib/catalogDayLikelihood.ts';

const HOUR=3_600_000;
const MID=Date.parse('1963-11-08T12:00:00Z');
const START=Date.parse('1963-11-08T00:00:00Z');
const END=Date.parse('1963-11-09T00:00:00Z');

test('NASA catalog day does not document physical impact time or sigma',()=>{
  assert.equal(CATALOGUE_528.evidence,'C197#1');
  assert.equal(CATALOGUE_528.sourceDocumentEstablishesUtcTerminalInstant,false);
  assert.equal(CATALOGUE_528.sourceDocumentEstablishesTemporalSigma,false);
  assert.equal(CATALOGUE_528.sourceDocumentEstablishesImpactTime,false);
});

test('likelihood symmetric around mid-day 8 Nov with two-sided nonzero tails',()=>{
  for(const sigma of PREDECLARED_DAY_SCENARIOS){
    for(const shift of [0,6,12,18,24,36]){
      const a=catalogueDayLikelihood(MID-shift*HOUR,sigma);
      const b=catalogueDayLikelihood(MID+shift*HOUR,sigma);
      assert.ok(Math.abs(a-b)<1e-11);
      assert.ok(a>=0&&a<=1);
    }
    assert.ok(catalogueDayLikelihood(START-6*HOUR,sigma)>0);
    assert.ok(catalogueDayLikelihood(END+6*HOUR,sigma)>0);
    assert.ok(catalogueDayLikelihood(END+6*HOUR,sigma)<
      catalogueDayLikelihood(MID,sigma));
  }
});

test('normalized day-8 spread has symmetric 6,12,24 hour tails',()=>{
  const expected={6:0.09973378,12:0.19522579,24:0.31562681};
  for(const sigma of PREDECLARED_DAY_SCENARIOS){
    const x=calendarSpreadScenario(sigma);
    assert.ok(Math.abs(x.probabilityBeforeNov8-expected[sigma])<2e-6);
    assert.equal(x.probabilityBeforeNov8,x.probabilityAfterNov8);
    assert.ok(Math.abs(x.probabilityBeforeNov8+x.probabilityDuringNov8+
      x.probabilityAfterNov8-1)<1e-12);
    assert.equal(x.historicalPrecisionCalibrated,false);
    assert.equal(x.physicalImpactInferred,false);
  }
});

test('explicit sigma required; no uncalibrated default',()=>{
  for(const sigma of [undefined,0,-1,NaN,Infinity,241]){
    assert.throws(()=>catalogueDayLikelihood(MID,sigma),/sigma/);
    assert.throws(()=>calendarSpreadScenario(sigma),/sigma/);
  }
  assert.throws(()=>catalogueDayLikelihood(NaN,12),/epoch/);
});

test('date, not distance to Conde, sets relative trajectory weights',()=>{
  const result=scenarioWeightedCells([
    {eventEpochMs:MID,cellId:'Conde',priorWeight:1},
    {eventEpochMs:MID+36*HOUR,cellId:'elsewhere',priorWeight:1},
  ],12);
  assert.ok(result.cellProbabilities.Conde>0.5);
  assert.equal(result.interpretedAsHistoricalPosterior,false);
  const same=scenarioWeightedCells([
    {eventEpochMs:MID,cellId:'Conde',priorWeight:1},
    {eventEpochMs:MID,cellId:'elsewhere',priorWeight:1},
  ],12);
  assert.ok(Math.abs(same.cellProbabilities.Conde-.5)<1e-12);
});

test('weighted cells normalize and ESS is numerical, not historical',()=>{
  const r=scenarioWeightedCells([
    {eventEpochMs:MID,cellId:'a',priorWeight:2},
    {eventEpochMs:MID+12*HOUR,cellId:'b',priorWeight:1},
    {eventEpochMs:MID,cellId:'c',priorWeight:0},
  ],12);
  assert.ok(Math.abs(Object.values(r.cellProbabilities).reduce((a,b)=>a+b,0)-1)<1e-12);
  assert.ok(r.effectiveSampleSize!==null&&r.effectiveSampleSize>1&&r.effectiveSampleSize<3);
  assert.equal(r.cellProbabilities.c,0);
});

test('reject absent or malformed sample weights and epochs',()=>{
  assert.throws(()=>scenarioWeightedCells([],12),/Candidate/);
  assert.throws(()=>scenarioWeightedCells([{eventEpochMs:MID,cellId:'x',priorWeight:0}],12),/zero/);
  assert.throws(()=>scenarioWeightedCells([{eventEpochMs:MID,cellId:'',priorWeight:1}],12),/cell ID/);
  assert.throws(()=>scenarioWeightedCells([{eventEpochMs:MID,cellId:'x',priorWeight:-1}],12),/prior weight/);
  assert.throws(()=>scenarioWeightedCells([{eventEpochMs:NaN,cellId:'x',priorWeight:1}],12),/epoch/);
});

test('new likelihood does not truncate November 9 events to zero',()=>{
  assert.ok(catalogueDayLikelihood(END+HOUR,12)>0);
  assert.ok(catalogueDayLikelihood(START-HOUR,12)>0);
  assert.equal(CATALOGUE_528.endExclusiveUtc,'1963-11-09T00:00:00.000Z');
});
