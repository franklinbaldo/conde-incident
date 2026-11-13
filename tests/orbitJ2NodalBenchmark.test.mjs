import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { compareJ2NodalDrift, scenarioOsculatingState, ascendingNodeDeg } from '../src/lib/orbitJ2NodalBenchmark.ts';
import { EARTH, specificEnergyKm2S2 } from '../src/lib/orbitPhysics.ts';

// Replays published NASA/Goddard October 15 compiled dimensions, C241-L12.
// Primary facsimile NTRS 19640000428; NOT raw state/epoch/instrumental 527/529.
const ledger = JSON.parse(readFileSync(new URL('../research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json', import.meta.url)));
const b = ledger.catalog_rows.find(row => row.international_designator === '1963-003B');
const scenario = (trueAnomalyDeg = 0, inclinationDeg = Number(b.inclination_deg_printed)) => ({
  sourceOccurrence: 'C241-L12#1',
  perigeeAltitudeKm: Number(b.perigee_km_printed),
  apogeeAltitudeKm: Number(b.apogee_km_printed),
  inclinationDeg,
  trueAnomalyDeg,
  durationS: 86400,
  stepS: 30,
});

test('primary compiled ledger drives a Keplerian osculating scenario, not an observation', () => {
  assert.equal(ledger.record_id, 'C241-L12');
  assert.equal(ledger.source.ntrs_id, '19640000428');
  assert.equal(ledger.source.measurement_lineage, 'NASA_PUBLICATION_COMPILED_FROM_TRACKING_NOT_RAW_SENSOR_RECORD');
  assert.equal(ledger.epistemic.observation_epoch, null);
  assert.equal(ledger.epistemic.raan_deg, null);
  assert.equal(ledger.epistemic.sigma, null);
  assert.equal(b.perigee_km_printed, 376);
  assert.equal(b.apogee_km_printed, 401);
  assert.equal(b.inclination_deg_printed, '81.87');
  const state = scenarioOsculatingState(scenario());
  assert.ok(Math.abs(Math.hypot(...state.rKm) - (EARTH.radiusKm + 376)) < 1e-9);
  assert.ok(specificEnergyKm2S2(state) < 0);
  assert.ok(Math.abs(ascendingNodeDeg(state)) < 1e-12);
});

test('RK4/J2 nodal regression agrees in sign and scale with first-order secular physics', () => {
  const rates = [0, 90, 180, 270].map(phase => compareJ2NodalDrift(scenario(phase)));
  for (const r of rates) {
    assert.equal(r.classification, 'CONDITIONAL_J2_MODEL_BENCHMARK');
    assert.equal(r.historicalHoldout, 'NOT_RUN');
    assert.equal(r.historicNodalLongitude, null);
    assert.equal(r.condeImpact, 'NOT_EVALUABLE');
    assert.ok(Math.abs(r.firstOrderJ2DegPerDay + 1.1456986158) < 0.00001);
    assert.ok(r.integratedJ2DegPerDay < -1.1 && r.integratedJ2DegPerDay > -1.2);
    assert.ok(Math.abs(r.integratedTwoBodyDegPerDay) < 1e-7);
    assert.ok(Math.abs(r.differenceFromFirstOrderDegPerDay) < 0.01);
    assert.ok(r.refinementDifferenceDegPerDay < 0.00001);
  }
  // Actual negative result: same published a/e/i, different arbitrary phase,
  // measurably different one-day osculating node changes. NOT a phase interval.
  assert.ok(Math.abs(rates[0].integratedJ2DegPerDay - rates[1].integratedJ2DegPerDay) > 0.002);
});

test('J2 nodal regression reverses for retrograde and disappears for polar orbit', () => {
  const forward = compareJ2NodalDrift(scenario(0, 81.87));
  const retro = compareJ2NodalDrift(scenario(0, 180 - 81.87));
  const polar = compareJ2NodalDrift(scenario(0, 90));
  assert.ok(forward.integratedJ2DegPerDay < 0);
  assert.ok(retro.integratedJ2DegPerDay > 0);
  assert.ok(Math.abs(retro.integratedJ2DegPerDay + forward.integratedJ2DegPerDay) < 0.001);
  assert.ok(Math.abs(polar.integratedJ2DegPerDay) < 1e-6);
  assert.ok(Math.abs(polar.firstOrderJ2DegPerDay) < 1e-12);
});

test('invalid source, phase, geometry and unresolvable steps fail closed', () => {
  for (const variant of [
    { sourceOccurrence: '' }, { perigeeAltitudeKm: -10 },
    { apogeeAltitudeKm: 100 }, { inclinationDeg: 0 },
    { trueAnomalyDeg: 360 }, { durationS: Infinity },
    { durationS: 500000 }, { stepS: 0 }, { stepS: 1e-10 },
    { apogeeAltitudeKm: 50000, perigeeAltitudeKm: 200 },
  ]) assert.throws(() => scenarioOsculatingState({ ...scenario(), ...variant }), RangeError);
});
