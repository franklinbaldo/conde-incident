import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH } from '../src/lib/orbitPhysics.ts';
import { assessNumericalConvergence } from '../src/lib/orbitConvergence.ts';

// All states below are synthetic numerical controls, never 1963 observations.
const circular = {
  rKm: [EARTH.radiusKm + 500, 0, 0],
  vKmS: [0, Math.sqrt(EARTH.muKm3S2 / (EARTH.radiusKm + 500)), 0],
  tS: 0,
};
const descending = {
  rKm: [EARTH.radiusKm + 90, 0, 0],
  vKmS: [-0.15, 8.15, 0],
  tS: 0,
};
const controls = (halvings, positionKm = 0.1, velocityKmS = 1e-4, epochS = 0.02) =>
  ({ halvings, tolerance: { positionKm, velocityKmS, epochS } });

test('synthetic circular r/v orbit reaches two consecutive step-halving tolerances', () => {
  const assessed = assessNumericalConvergence(circular, 600, 100, 80, controls(5), { j2: true });
  assert.equal(assessed.status, 'STABLE');
  assert.equal(assessed.levels.length, 6);
  assert.equal(assessed.finest.event, 'elapsed');
  assert.equal(assessed.levels[0].stepS, 100);
  assert.equal(assessed.levels.at(-1).stepS, 3.125);
  assert.ok(assessed.levels.slice(-2).every(level => level.difference.withinTolerance));
});

test('within-step synthetic threshold event stabilizes in epoch, position and velocity', () => {
  const assessed = assessNumericalConvergence(descending, 400, 400, 80, controls(6));
  assert.equal(assessed.status, 'STABLE');
  assert.equal(assessed.finest.event, 'reentry-threshold');
  assert.ok(assessed.finest.state.tS > 0 && assessed.finest.state.tS < 200);
  assert.ok(assessed.levels.slice(-2).every(level => level.difference.withinTolerance));
});

test('negative control: 3000 s step MISSES event observed by refined coupled r/v propagation', () => {
  const assessed = assessNumericalConvergence(descending, 3000, 3000, 80, controls(5));
  assert.equal(assessed.levels[0].result.event, 'elapsed');
  assert.equal(assessed.levels[1].result.event, 'reentry-threshold');
  assert.equal(assessed.finest.event, 'reentry-threshold');
  assert.equal(assessed.status, 'EVENT_CONFLICT');
  assert.equal(assessed.levels[1].difference.eventAgrees, false);
  // Even if the last few steps agree, the coarse miss must not be erased.
  assert.ok(assessed.levels.slice(-2).every(level => level.difference.eventAgrees));
});

test('unresolved precision requirements are reported, never silently called convergence', () => {
  const assessed = assessNumericalConvergence(
    circular, 800, 800, 80, controls(2, 1e-14, 1e-14, 1e-14));
  assert.equal(assessed.status, 'NOT_RESOLVED');
  assert.equal(assessed.finest.event, 'elapsed');
  assert.ok(assessed.levels.slice(-2).some(level => !level.difference.withinTolerance));
});

test('invalid step-halving controls are refused before physical prediction', () => {
  assert.throws(() => assessNumericalConvergence(circular, 100, 10, 80, controls(1)), /halvings/);
  assert.throws(() => assessNumericalConvergence(circular, 100, 10, 80, controls(11)), /halvings/);
  assert.throws(() => assessNumericalConvergence(circular, 100, 10, 80, controls(3, NaN)), /tolerances/);
  assert.throws(() => assessNumericalConvergence(circular, 100, -1, 80, controls(3)), /step/);
});
