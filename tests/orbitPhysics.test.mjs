import test from 'node:test';
import assert from 'node:assert/strict';
import {
  EARTH, rk4, propagate, accelerationKmS2, specificEnergyKm2S2,
  angularMomentumZ, rotatingFrameIntegralKm2S2, altitudeKm,
  seededUniform, propagateEnsemble, fitInitialVelocity, positionResidualRmsKm,
} from '../src/lib/orbitPhysics.ts';
const circular = {
  rKm: [EARTH.radiusKm + 500, 0, 0],
  vKmS: [0, Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500)), 0],
  tS: 0,
};
const duration = 2 * Math.PI * Math.sqrt((EARTH.radiusKm + 500) ** 3 / EARTH.muKm3S2);
const relative = (a, b) => Math.abs(a - b) / Math.max(1, Math.abs(b));

test('central gravity conserves orbit, inertial energy, and angular momentum over 1 period', () => {
  const out = propagate(circular, duration, 5, 80);
  assert.equal(out.event, 'elapsed');
  assert.ok(relative(specificEnergyKm2S2(out.state), specificEnergyKm2S2(circular)) < 1e-9);
  assert.ok(relative(angularMomentumZ(out.state), angularMomentumZ(circular)) < 1e-9);
  assert.ok(Math.hypot(...out.state.rKm.map((v, i) => v - circular.rKm[i])) < 0.001);
});

test('J2 conserves conservative total energy and symmetry-axis angular momentum', () => {
  const inclined = { ...circular, vKmS: [0, circular.vKmS[1] * Math.cos(0.8), circular.vKmS[1] * Math.sin(0.8)] };
  const out = propagate(inclined, duration * 4, 5, 80, { j2: true });
  assert.equal(out.event, 'elapsed');
  assert.ok(relative(specificEnergyKm2S2(out.state, true), specificEnergyKm2S2(inclined, true)) < 1e-8);
  assert.ok(relative(angularMomentumZ(out.state), angularMomentumZ(inclined)) < 1e-8);
});

test('zero-density drag is exactly vacuum; nonzero sourced drag reduces rotating-frame integral', () => {
  const zero = { source: 'synthetic control (not historical)', densityKgM3: () => 0, cdAreaOverMassM2Kg: 0.02 };
  assert.deepEqual(accelerationKmS2(circular, { j2: true, atmosphere: zero }), accelerationKmS2(circular, { j2: true }));
  const mock = { source: 'synthetic density stress test (not 1963)', densityKgM3: () => 2e-9, cdAreaOverMassM2Kg: 0.1 };
  const out = propagate(circular, duration, 5, 80, { j2: true, atmosphere: mock });
  assert.equal(out.event, 'elapsed');
  assert.ok(rotatingFrameIntegralKm2S2(out.state, true) < rotatingFrameIntegralKm2S2(circular, true));
});

test('radial state triggers threshold with coupled velocity and event time refined within step', () => {
  const start = { rKm: [EARTH.radiusKm + 100, 0, 0], vKmS: [-1.2, 0, 0], tS: 0 };
  const out = propagate(start, 100, 15, 80);
  assert.equal(out.event, 'reentry-threshold');
  assert.ok(out.state.tS > 0 && out.state.tS < 20);
  assert.ok(Math.abs(altitudeKm(out.state) - 80) < 1e-7);
  assert.ok(out.state.vKmS[0] < start.vKmS[0]);
});

test('reject undocumented atmospheric density and nonphysical controls', () => {
  assert.throws(() => accelerationKmS2(circular, { atmosphere: { source: '', densityKgM3: () => 1e-10, cdAreaOverMassM2Kg: 0.1 }}));
  assert.throws(() => accelerationKmS2(circular, { atmosphere: { source: 'synthetic', densityKgM3: () => -1, cdAreaOverMassM2Kg: 0.1 }}));
  assert.throws(() => propagate(circular, 10, -1, 80));
  assert.throws(() => propagate(circular, 10, 1, NaN));
});

test('seeded ensemble repeats exactly and remains coupled to its state', () => {
  const a = propagateEnsemble(circular, 1963, 8, 0.004, 1000, 10, 80, { j2: true });
  const b = propagateEnsemble(circular, 1963, 8, 0.004, 1000, 10, 80, { j2: true });
  assert.deepEqual(a, b);
  assert.notDeepEqual(a, propagateEnsemble(circular, 1964, 8, 0.004, 1000, 10, 80, { j2: true }));
  assert.throws(() => seededUniform(0));
});

test('inverse fits known SYNTHETIC velocity against independent time-tagged Cartesian positions', () => {
  const truth = { ...circular, vKmS: [0.003, circular.vKmS[1] + 0.006, -0.004] };
  const observations = [800, 1600, 2400].map(elapsedS => ({
    elapsedS, rKm: propagate(truth, elapsedS, 20, 80, { j2: true }).state.rKm,
    source: 'synthetic truth generated in test, NOT historical 527/529 TLE',
  }));
  const before = positionResidualRmsKm(circular, observations, 20, 80, { j2: true });
  const fitted = fitInitialVelocity(circular, observations, 20, 80, 0.008, 9, { j2: true });
  assert.ok(before > 3);
  assert.ok(fitted.rmsKm < before / 10);
  assert.ok(fitted.evaluations >= 1);
});
