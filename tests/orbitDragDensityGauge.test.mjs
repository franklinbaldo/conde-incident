import test from 'node:test';
import assert from 'node:assert/strict';
import {
  EARTH, accelerationKmS2, dragAccelerationKmS2, propagate,
} from '../src/lib/orbitPhysics.ts';

// C241-P27: purely synthetic, NOT reconstructed 1963 satellite states.
// Three distinct trajectories expose the shared-amplitude / per-object drag gauge.
const cases = [
  { id: 'synthetic-527', beta: 0.05,
    state: { rKm: [EARTH.radiusKm + 500, 0, 0], vKmS: [0, 1.15, 7.52], tS: 200 } },
  { id: 'synthetic-528', beta: 0.08,
    state: { rKm: [0, EARTH.radiusKm + 460, 500], vKmS: [-7.65, 0.15, 0.05], tS: 500 } },
  { id: 'synthetic-529', beta: 0.12,
    state: { rKm: [-400, 100, EARTH.radiusKm + 560], vKmS: [7.60, 0.35, 0.2], tS: 800 } },
];
const baseDensity = (altitudeKm, tS) =>
  3e-11 * Math.exp(-(altitudeKm - 500) / 70) *
  (1 + 0.15 * Math.sin(tS / 720));
const atmosphere = (beta, amplitude = 1) => ({
  source: 'synthetic positive, nonstationary density; NOT 1963 metrology',
  densityKgM3: (altitudeKm, tS) => amplitude * baseDensity(altitudeKm, tS),
  cdAreaOverMassM2Kg: beta,
});
const norm3 = v => Math.hypot(...v);

test('C241-P27: three-body log-product Jacobian has a one-dimensional exact gauge', () => {
  // d_j = log(A) + log(beta_j); columns (log A, log beta_527, log beta_528, log beta_529).
  const j = [
    [1, 1, 0, 0],
    [1, 0, 1, 0],
    [1, 0, 0, 1],
  ];
  const gauge = [1, -1, -1, -1];
  assert.deepEqual(j.map(row => row.reduce((sum, x, i) => sum + x * gauge[i], 0)), [0, 0, 0]);
  assert.deepEqual(j.map(row => row.slice(1)), [
    [1, 0, 0], [0, 1, 0], [0, 0, 1],
  ]); // Three independent rows, four parameters: rank exactly 3, nullity exactly 1.
  // Fixing either the amplitude or one object's coefficient removes this specific gauge.
  assert.deepEqual(j.map(row => row.slice(1).reduce((a, b) => a + b, 0)), [1, 1, 1]);
});

test('C241-P27: physical acceleration J2 + nonstationary drag is invariant under A*2, beta/2', () => {
  for (const { id, state, beta } of cases) {
    const raw = dragAccelerationKmS2(state, atmosphere(beta));
    assert.ok(norm3(raw) > 0, id);
    const scaled = dragAccelerationKmS2(state, atmosphere(beta / 2, 2));
    assert.deepEqual(scaled, raw, id);
    const gravityAndDrag = accelerationKmS2(state, { j2: true, atmosphere: atmosphere(beta) });
    const gravityAndDragScaled = accelerationKmS2(state, { j2: true, atmosphere: atmosphere(beta / 2, 2) });
    assert.deepEqual(gravityAndDragScaled, gravityAndDrag, id);
  }
});

test('C241-P27: three propagated orbits remain observationally identical at multiple epochs', () => {
  for (const { id, state, beta } of cases) {
    for (const elapsedS of [600, 1800, 3600]) {
      const plain = propagate(state, elapsedS, 30, 80, { j2: true, atmosphere: atmosphere(beta) });
      const gauged = propagate(state, elapsedS, 30, 80, { j2: true, atmosphere: atmosphere(beta / 2, 2) });
      assert.equal(plain.event, 'elapsed', id);
      assert.deepEqual(gauged, plain, id);
    }
  }
});

test('C241-P27: changing density alone DOES change the drag, so an external anchor matters', () => {
  for (const { id, state, beta } of cases) {
    const original = dragAccelerationKmS2(state, atmosphere(beta));
    const doubled = dragAccelerationKmS2(state, atmosphere(beta, 2));
    assert.ok(norm3(original) > 0, id);
    assert.ok(Math.abs(norm3(doubled) / norm3(original) - 2) < 1e-12, id);
  }
});

test('C241-P27: no information on beta from zero density, even with perfectly known state', () => {
  const s = cases[0].state;
  assert.deepEqual(
    accelerationKmS2(s, { j2: true, atmosphere: {
      source: 'synthetic zero-atmosphere negative control',
      densityKgM3: () => 0,
      cdAreaOverMassM2Kg: 100,
    }}),
    accelerationKmS2(s, { j2: true }),
  );
});
