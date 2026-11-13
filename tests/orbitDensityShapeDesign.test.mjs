import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, dragAccelerationKmS2 } from '../src/lib/orbitPhysics.ts';

// C241-P28: all positions, velocities, densities and drag accelerations below
// are SYNTHETIC. Inference from actual 1963 tracking remains NOT_RUN.
const ids = [527, 528, 529];
const B = { 527: 0.05, 528: 0.08, 529: 0.12 };
const A = 1.7;
const H = 68; // km: synthetic scale height, NOT an atmospheric calibration.
const h0 = 500;
const q = tS => 1 + 0.1 * Math.sin(tS / 1000);
const makeState = (altitudeKm, tS) => ({
  rKm: [EARTH.radiusKm + altitudeKm, 0, 0],
  vKmS: [0, 1.1, 7.5],
  tS,
});
const relativeSpeedSquared = s => {
  const v = [s.vKmS[0] + EARTH.spinRadS * s.rKm[1],
    s.vKmS[1] - EARTH.spinRadS * s.rKm[0], s.vKmS[2]];
  return v.reduce((sum, x) => sum + x * x, 0);
};
const acceleration = (id, s, amp = A, scaleHeight = H, coeff = B[id]) =>
  dragAccelerationKmS2(s, {
    source: 'synthetic exponential atmosphere; not observational evidence',
    cdAreaOverMassM2Kg: coeff,
    densityKgM3: (h, tS) => amp * 3e-11 * q(tS) * Math.exp(-(h - h0) / scaleHeight),
  });
const logDragNormalized = (id, s, amp = A, scaleHeight = H, coeff = B[id]) => {
  const a = acceleration(id, s, amp, scaleHeight, coeff);
  const magnitude = Math.hypot(...a);
  return Math.log(magnitude / (500 * relativeSpeedSquared(s) * q(s.tS) * 3e-11));
};

// Exact integer Gaussian elimination is valid for these integer design rows.
const rank = rows => {
  const m = rows.map(row => row.slice());
  let k = 0;
  for (let c = 0; c < m[0].length; c++) {
    const pivot = m.findIndex((row, i) => i >= k && Math.abs(row[c]) > 1e-9);
    if (pivot < 0) continue;
    [m[k], m[pivot]] = [m[pivot], m[k]];
    const v = m[k][c];
    for (let j = c; j < m[k].length; j++) m[k][j] /= v;
    for (let i = k + 1; i < m.length; i++) {
      const f = m[i][c];
      for (let j = c; j < m[i].length; j++) m[i][j] -= f * m[k][j];
    }
    k++;
    if (k === m.length) break;
  }
  return k;
};
const design = (id, altKm) => [1, ...ids.map(j => Number(id === j)), -(altKm - h0)];
const anchor527 = [0, 1, 0, 0, 0]; // independently calibrated B527, NOT data.

test('C241-P28: within-object two-altitude contrast identifies 1/H but not A or B individually', () => {
  const s1 = makeState(480, 200);
  const s2 = makeState(550, 800);
  const delta = logDragNormalized(529, s2) - logDragNormalized(529, s1);
  assert.ok(Math.abs(delta + (550 - 480) / H) < 1e-12);
  const recoveredH = -(550 - 480) / delta;
  assert.ok(Math.abs(recoveredH - H) < 1e-10);
  const g1 = logDragNormalized(529, s1, A * 2, H, B[529] / 2);
  const g2 = logDragNormalized(529, s2, A * 2, H, B[529] / 2);
  assert.ok(Math.abs(g1 - logDragNormalized(529, s1)) < 1e-12);
  assert.ok(Math.abs(g2 - logDragNormalized(529, s2)) < 1e-12);
});

test('C241-P28: rank shows why cross-object observations at one altitude cannot identify shape', () => {
  const once = ids.map(id => design(id, 500));
  assert.equal(rank(once), 3); // 5 parameters: logA, three logB, gamma=1/H.
  assert.equal(rank([...once, anchor527]), 4); // B anchor alone does not determine H.
  const withSecondAltitude = [...once, design(529, 550)];
  assert.equal(rank(withSecondAltitude), 4); // Shape yes, amplitude gauge persists.
  assert.equal(rank([...withSecondAltitude, anchor527]), 5);
  assert.equal(rank([...withSecondAltitude, design(527, 600)]), 4);
});

test('C241-P28: unchanged altitude admits any H with object-specific beta adjustments', () => {
  for (const id of ids) {
    const altitude = 480 + (id - 527) * 30;
    const s = makeState(altitude, 350 + (id - 527) * 100);
    const alternativeH = 100;
    const alternativeB = B[id] * Math.exp((altitude - h0) * (1 / alternativeH - 1 / H));
    const a = acceleration(id, s);
    const alternative = acceleration(id, s, A, alternativeH, alternativeB);
    const discrepancy = Math.hypot(...a.map((x, i) => x - alternative[i]));
    assert.ok(discrepancy / Math.hypot(...a) < 1e-12);
  }
});

test('C241-P28: controls plus anchor leave missing 528 coefficient unidentifiable', () => {
  const controls = [design(527, 480), design(527, 550), design(529, 490), design(529, 560)];
  assert.equal(rank([...controls, anchor527]), 4); // B528 column is zero.
  assert.equal(rank([...controls, anchor527, design(528, 500)]), 5);
  assert.equal(rank([...controls, anchor527, design(529, 620)]), 4);
});

test('C241-P28: identical altitudes give no scale-height contrast even across dates', () => {
  const s1 = makeState(540, 100);
  const s2 = makeState(540, 500);
  assert.ok(Math.abs(logDragNormalized(527, s2) - logDragNormalized(527, s1)) < 1e-12);
  assert.equal(rank([design(527, 540), design(527, 540)]), 1);
});
