import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {
  GCAT_MASS_FIELDS, auditMassBudgetScenario, conditionalTrackedMassEnvelope,
  ballisticFromMassScenario, atmosphereForMassScenario,
  conditionalBallisticCompatibility,
} from '../src/lib/orbitMassConstraints.ts';
import { dragAccelerationKmS2, EARTH } from '../src/lib/orbitPhysics.ts';
import {
  makeConditionalMassBudgetMsiseAtmosphere,
  makeConditionalMsiseAtmosphere,
} from '../src/lib/orbitSpaceWeatherAdapter.ts';

// All allocations in THIS TEST are invented; the GCAT fields are secondary.
const scenario = (overrides={}) => ({
  schema:'conde.conditional-three-object-mass/v1',
  sourceOccurrence:'C61',
  basis:'GCAT_TOTMASS_1176',
  referenceEpochDescription:'SYNTHETIC separation inventory with one convention',
  massesKg:{527:900,528:150,529:76},
  untrackedKg:20,
  priorLossKg:30,
  catalogErrorKg:0,
  opsPayloadRetainedBy527Kg:306,
  ...overrides,
});
const geometry = (overrides={}) => ({
  object:528,
  projectedAreaM2:0.3,
  dragCoefficient:2,
  geometrySource:'SYNTHETIC test geometry; not a 1963 item',
  historicalGeometryAuthenticated:false,
  ...overrides,
});

test('C61 GCAT fields are source descriptions, not a mass for NORAD 528', () => {
  assert.equal(GCAT_MASS_FIELDS.payloadOPS0180MassKg,306);
  assert.equal(GCAT_MASS_FIELDS.payloadOPS0180DryMassKg,306);
  assert.equal(GCAT_MASS_FIELDS.agenaBMassKg,900);
  assert.equal(GCAT_MASS_FIELDS.agenaBDryMassKg,870);
  assert.equal(GCAT_MASS_FIELDS.totalMassAssociatedKg,1176);
  assert.equal(GCAT_MASS_FIELDS.originalComponentSumKg,1206);
  assert.equal(GCAT_MASS_FIELDS.massOf528Kg,null);
  assert.equal(GCAT_MASS_FIELDS.referenceUncertaintyKg,null);
  assert.equal(GCAT_MASS_FIELDS.completeThreeObjectPartitionAuthenticated,false);
});

test('exact conditional budget accepts 527/528/529 + X + loss + epsilon', () => {
  const result=auditMassBudgetScenario(scenario());
  assert.equal(result.mathematicallyConsistent,true);
  assert.equal(result.accountedKg,1176);
  assert.equal(result.catalogCorrectedKg,1176);
  assert.equal(result.historicalConstraintActive,false);
  assert.match(result.classification,/CONDITIONAL/);
});

test('budget compares against a separately signed epsilon and not against epsilon mass', () => {
  const s=scenario({catalogErrorKg:24,untrackedKg:44});
  assert.equal(auditMassBudgetScenario(s).mathematicallyConsistent,true);
  const minus=scenario({catalogErrorKg:-10,massesKg:{527:890,528:150,529:76}});
  assert.equal(auditMassBudgetScenario(minus).mathematicallyConsistent,true);
});

test('1206 insertion mass basis requires explicit declaration; 1176 is not universal', () => {
  const modified=scenario({basis:'PAYLOAD_PLUS_STAGE_AT_INSERTION_1206',massesKg:{527:930,528:150,529:76}});
  const result=auditMassBudgetScenario(modified);
  assert.equal(result.nominalKg,1206);
  assert.equal(result.mathematicallyConsistent,true);
  assert.equal(auditMassBudgetScenario(scenario({basis:'PAYLOAD_PLUS_STAGE_AT_INSERTION_1206'}))
    .mathematicallyConsistent,false);
});

test('cannot count the same 30 kg as both X and earlier loss without breaking budget', () => {
  const doubled=scenario({untrackedKg:50});
  assert.equal(auditMassBudgetScenario(doubled).mathematicallyConsistent,false);
});

test('reject missing 528, negative, zero, NaN masses, invalid source & epoch', () => {
  for(const s of [
    scenario({massesKg:{527:900,529:76}}),
    scenario({massesKg:{527:900,528:0,529:76}}),
    scenario({massesKg:{527:900,528:NaN,529:76}}),
    scenario({untrackedKg:-1}),
    scenario({priorLossKg:-1}),
    scenario({catalogErrorKg:Infinity}),
    scenario({sourceOccurrence:'invented'}),
    scenario({referenceEpochDescription:''}),
    scenario({basis:'guessed'}),
  ]) assert.throws(()=>auditMassBudgetScenario(s),RangeError);
});

test('OPS retained mass is a declared physical hypothesis, never entire 527 mass', () => {
  assert.equal(auditMassBudgetScenario(scenario({opsPayloadRetainedBy527Kg:306})).mathematicallyConsistent,true);
  assert.throws(()=>auditMassBudgetScenario(scenario({opsPayloadRetainedBy527Kg:307})),/OPS/);
  assert.throws(()=>auditMassBudgetScenario(scenario({
    massesKg:{527:300,528:150,529:626},opsPayloadRetainedBy527Kg:306,
  })),/Retained/);
});

test('interval algebra: caps on epsilon X and prior loss provide conditional ONLY boundaries',()=>{
  const v=conditionalTrackedMassEnvelope({
    basis:'GCAT_TOTMASS_1176',maxAbsCatalogErrorKg:25,
    maxUntrackedKg:50,maxPriorLossKg:30,minRetainedPayloadIn527Kg:306,
  });
  assert.equal(v.trackedTotalInfimumKg,1071);
  assert.equal(v.trackedTotalSupremumKg,1201);
  assert.equal(v.individualMassUpperExclusiveKg,1201);
  assert.equal(v.othersPlusXAndLossUpperKgIfPayloadRetained,895);
  assert.equal(v.historicalConstraintActive,false);
});

test('no historically sourced epsilon bound means no finite mass upper bound',()=>{
  const missing=conditionalTrackedMassEnvelope({
    basis:'GCAT_TOTMASS_1176',maxAbsCatalogErrorKg:null,
    maxUntrackedKg:0,maxPriorLossKg:0,
  });
  assert.equal(missing.trackedTotalSupremumKg,null);
  assert.equal(missing.individualMassUpperExclusiveKg,null);
  assert.equal(missing.trackedTotalInfimumKg,null);
  const unknownX=conditionalTrackedMassEnvelope({
    basis:'GCAT_TOTMASS_1176',maxAbsCatalogErrorKg:0,
    maxUntrackedKg:null,maxPriorLossKg:0,
  });
  assert.equal(unknownX.trackedTotalInfimumKg,0);
});

test('no geometry or Cd from GCAT: fail closed on fabricated historical geometry',()=>{
  assert.throws(()=>ballisticFromMassScenario(scenario(),geometry({
    historicalGeometryAuthenticated:true,
  })),/authenticated 1963/);
  assert.throws(()=>ballisticFromMassScenario(scenario(),geometry({
    geometrySource:'',
  })),/source/);
  assert.throws(()=>ballisticFromMassScenario(scenario(),geometry({
    projectedAreaM2:0,
  })),/Positive/);
});

test('conditional B=Cd A/m derives only from explicitly assigned 528 mass, area, Cd',()=>{
  const b=ballisticFromMassScenario(scenario(),geometry());
  assert.equal(b.object,528);
  assert.ok(Math.abs(b.areaOverMassM2Kg-0.002)<1e-14);
  assert.ok(Math.abs(b.cdAreaOverMassM2Kg-0.004)<1e-14);
  assert.equal(b.historicalConstraintActive,false);
  assert.equal(b.budgetConsistent,true);
});

test('real Cartesian J2/drag engine uses mass-constrained B, not a stale caller B',()=>{
  const state={rKm:[EARTH.radiusKm+430,0,0],vKmS:[0,7.65,0],tS:0};
  const base={source:'synthetic rho; NOT NASA',densityKgM3:()=>1e-11,cdAreaOverMassM2Kg:0.6};
  const mass=atmosphereForMassScenario(base,scenario(),geometry());
  assert.ok(Math.abs(mass.cdAreaOverMassM2Kg-0.004)<1e-14);
  const expected=dragAccelerationKmS2(state,{...base,cdAreaOverMassM2Kg:0.004});
  assert.deepEqual(dragAccelerationKmS2(state,mass),expected);
  assert.match(mass.source,/SCENARIO_ONLY/);
  assert.throws(()=>atmosphereForMassScenario(base,scenario({untrackedKg:21}),geometry()),
    /conservation/);
});

test('inverse-required B only rejects a CHOSEN scenario, not a physical orbit',()=>{
  const matched=conditionalBallisticCompatibility(.004,scenario(),geometry(),0);
  assert.equal(matched.compatibleWithChosenScenario,true);
  assert.equal(matched.historicalExclusion,false);
  const mismatch=conditionalBallisticCompatibility(.02,scenario(),geometry(),.01);
  assert.equal(mismatch.compatibleWithChosenScenario,false);
  assert.equal(mismatch.historicalErrorBound,null);
});

const snapshot=JSON.parse(readFileSync(new URL(
  '../research/meteorology/space_weather_msise_inputs_1963_11_07_09.json',import.meta.url)));
const msiseOptions={
  snapshot,originEpochUtc:'1963-11-08T05:59:50Z',originStateTS:100,
  inertialFrame:'SYNTHETIC',
  frameTransformSource:'SYNTHETIC_ONLY',
  toGeodetic:()=>({latitudeDeg:0,longitudeDeg:0,altitudeKm:500,localSolarTimeHours:6}),
  densityModelSource:'SYNTHETIC_ONLY',
  evaluateDensityKgM3:()=>1e-12,
};

test('same mass budget feeds actual sourced MSISE/J2 drag and refuses inconsistent mass',()=>{
  const state={rKm:[EARTH.radiusKm+500,0,0],vKmS:[0,7.6,0],tS:100};
  const m=makeConditionalMassBudgetMsiseAtmosphere(msiseOptions,scenario(),geometry());
  assert.equal(m.cdAreaOverMassM2Kg,.004);
  assert.match(m.source,/SCENARIO_ONLY/);
  const baseline=makeConditionalMsiseAtmosphere({
    ...msiseOptions,cdAreaOverMassM2Kg:.004,
  });
  assert.deepEqual(dragAccelerationKmS2(state,m),dragAccelerationKmS2(state,baseline));
  assert.throws(()=>makeConditionalMassBudgetMsiseAtmosphere(
    msiseOptions,scenario({massesKg:{527:900,528:152,529:76}}),geometry()),/budget/);
});
