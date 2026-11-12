import test from 'node:test';
import assert from 'node:assert/strict';
import {
  EARTH, rk4, accelerationKmS2, specificEnergyKm2S2,
  angularMomentumZ, potentialKm2S2, rotatingFrameIntegralKm2S2,
  dragJacobiPowerKm2S3, NumericalIntegrationBreakdown,
} from '../src/lib/orbitPhysics.ts';

// All states below are SYNTHETIC controls, never reconstructed NORAD states.
const radius = EARTH.radiusKm + 500;
const circular = { rKm: [radius, 0, 0], vKmS: [0, Math.sqrt(EARTH.muKm3S2 / radius), 0], tS: 0 };
const periodS = 2 * Math.PI * Math.sqrt(radius ** 3 / EARTH.muKm3S2);
const distanceKm = (a, b) => Math.hypot(...a.map((x, i) => x - b[i]));
function integrate(initial, durationS, stepS, dynamics = {}) {
  let state = initial;
  let elapsed = 0;
  while (elapsed < durationS) {
    const dt = Math.min(stepS, durationS - elapsed);
    if (dt <= 0) break;
    state = rk4(state, dt, dynamics);
    elapsed += dt;
  }
  return state;
}

test('central force has km/s² dimensional consistency at circular altitude', () => {
  const a = accelerationKmS2(circular);
  assert.ok(Math.abs(a[0] + EARTH.muKm3S2 / radius ** 2) < 1e-15);
  assert.equal(Math.abs(a[1]), 0);
  assert.equal(Math.abs(a[2]), 0);
  assert.ok(Math.abs(circular.vKmS[1] ** 2 / radius - EARTH.muKm3S2 / radius ** 2) < 1e-15);
});

test('central r/v RK4 conserves energy and Lz over a synthetic orbit', () => {
  const end = integrate(circular, periodS, 5);
  assert.ok(distanceKm(end.rKm, circular.rKm) < 0.001);
  assert.ok(Math.abs(specificEnergyKm2S2(end) - specificEnergyKm2S2(circular)) < 1e-9);
  assert.ok(Math.abs(angularMomentumZ(end) - angularMomentumZ(circular)) < 1e-7);
  assert.ok(Math.abs(end.tS - periodS) < 1e-7);
});

test('J2 gravity equals negative Cartesian gradient of the declared potential', () => {
  const state = { rKm: [EARTH.radiusKm + 450, 140, 750], vKmS: [0.7, 7.1, -0.1], tS: 0 };
  const actual = accelerationKmS2(state, { j2: true });
  const epsKm = 0.02;
  for (let axis = 0; axis < 3; axis++) {
    const plus = [...state.rKm], minus = [...state.rKm];
    plus[axis] += epsKm;
    minus[axis] -= epsKm;
    const grad = (potentialKm2S2({ ...state, rKm: plus }, true) -
      potentialKm2S2({ ...state, rKm: minus }, true)) / (2 * epsKm);
    assert.ok(Math.abs(actual[axis] + grad) < 2e-10, 'J2/potential force inconsistency axis=' + axis);
  }
});

test('axisymmetric J2 conserves energy and Lz, not generic Kepler orientation', () => {
  const inclined = { ...circular, vKmS: [0, circular.vKmS[1] * Math.cos(0.8), circular.vKmS[1] * Math.sin(0.8)] };
  const end = integrate(inclined, periodS * 3, 5, { j2: true });
  assert.ok(Math.abs(specificEnergyKm2S2(end, true) - specificEnergyKm2S2(inclined, true)) < 1e-7);
  assert.ok(Math.abs(angularMomentumZ(end) - angularMomentumZ(inclined)) < 1e-6);
  assert.ok(distanceKm(end.vKmS, inclined.vKmS) > 0.01, 'J2 changes osculating vector components');
});

test('step refinement converges on coupled position AND velocity, not separated longitude', () => {
  const duration = 1200;
  const reference = integrate(circular, duration, 10, { j2: true });
  const coarse = integrate(circular, duration, 200, { j2: true });
  const medium = integrate(circular, duration, 100, { j2: true });
  const fine = integrate(circular, duration, 50, { j2: true });
  assert.ok(distanceKm(fine.rKm, reference.rKm) < distanceKm(medium.rKm, reference.rKm));
  assert.ok(distanceKm(medium.rKm, reference.rKm) < distanceKm(coarse.rKm, reference.rKm));
  assert.ok(distanceKm(fine.vKmS, reference.vKmS) < distanceKm(medium.vKmS, reference.vKmS));
  assert.ok(distanceKm(medium.vKmS, reference.vKmS) < distanceKm(coarse.vKmS, reference.vKmS));
});

test('zero density gives exact vacuum; sourced synthetic drag dissipates E minus spin*Lz', () => {
  const zero = { source: 'SYNTHETIC zero-density control', densityKgM3: () => 0, cdAreaOverMassM2Kg: 0.1 };
  assert.deepEqual(accelerationKmS2(circular, { j2: true, atmosphere: zero }),
    accelerationKmS2(circular, { j2: true }));
  const drag = { source: 'SYNTHETIC stress density, not 1963', densityKgM3: () => 2e-9, cdAreaOverMassM2Kg: 0.1 };
  assert.ok(dragJacobiPowerKm2S3(circular, drag) < 0);
  const end = integrate(circular, 900, 5, { j2: true, atmosphere: drag });
  assert.ok(rotatingFrameIntegralKm2S2(end, true) < rotatingFrameIntegralKm2S2(circular, true));
});

test('no historical drag default and malformed atmospheric source cannot silently pass', () => {
  assert.deepEqual(accelerationKmS2(circular), accelerationKmS2(circular, { j2: false }));
  assert.throws(() => accelerationKmS2(circular, {
    atmosphere: { source: '', densityKgM3: () => 1e-10, cdAreaOverMassM2Kg: 0.1 },
  }), /requires source/);
  assert.throws(() => accelerationKmS2(circular, {
    atmosphere: { source: 'SYNTHETIC invalid', densityKgM3: () => -1, cdAreaOverMassM2Kg: 0.1 },
  }), /Density must be finite/);
  assert.throws(() => rk4(circular, 0), /positive/);
  assert.throws(() => accelerationKmS2({ ...circular, rKm: [0, 0, 0] }), /invalid osculating/);
  assert.throws(() => rk4({ ...circular, vKmS: [0, 1e308, 0] }, 30),
    error => error instanceof NumericalIntegrationBreakdown);
});
