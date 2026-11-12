import { readFileSync } from 'node:fs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH } from '../src/lib/orbitPhysics.ts';
import { assessNumericalConvergence, checkCartesianRefinementTrend } from '../src/lib/orbitConvergence.ts';

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

test('resolved Cartesian refinement growth cannot hide inside generous tolerances', () => {
  // SYNTHETIC differences: both adjacent comparisons could satisfy a
  // 1 km user tolerance even though refinement grows from 0.0001 to 0.9 km.
  const previous = { eventAgrees: true, positionKm: 0.0001,
    velocityKmS: 1e-7, epochS: 1e-8, withinTolerance: true };
  const finest = { eventAgrees: true, positionKm: 0.9,
    velocityKmS: 2e-7, epochS: 1e-8, withinTolerance: true };
  const trend = checkCartesianRefinementTrend(previous, finest, {
    positionKm: 1e-10, velocityKmS: 1e-12, epochS: 1e-10,
  });
  assert.equal(trend.status, 'GROWTH_BEYOND_ROUNDOFF');
  assert.deepEqual(trend.growingMetrics, ['positionKm', 'velocityKmS']);
  assert.equal(trend.interpretation, 'HEURISTIC_64_EPS_SCALE_NOT_ERROR_BOUND');
});

test('roundoff-scale jitter is not declared resolved Cartesian growth', () => {
  const previous = { eventAgrees: true, positionKm: 2e-11,
    velocityKmS: 3e-15, epochS: 2e-12, withinTolerance: true };
  const finest = { ...previous, positionKm: 2.1e-11,
    velocityKmS: 3.1e-15, epochS: 2.1e-12 };
  const trend = checkCartesianRefinementTrend(previous, finest, {
    positionKm: 1e-10, velocityKmS: 1e-12, epochS: 1e-10,
  });
  assert.equal(trend.status, 'NO_RESOLVED_GROWTH');
  assert.deepEqual(trend.growingMetrics, []);
});

test('nonfinite differences and invalid dimensional allowances fail closed', () => {
  const valid = { eventAgrees: true, positionKm: 1,
    velocityKmS: 1, epochS: 1, withinTolerance: true };
  const allowance = { positionKm: 1e-9, velocityKmS: 1e-9, epochS: 1e-9 };
  assert.equal(checkCartesianRefinementTrend(valid,
    { ...valid, positionKm: Infinity }, allowance).status, 'NONFINITE_DIFFERENCE');
  assert.throws(() => checkCartesianRefinementTrend(valid, valid,
    { ...allowance, epochS: -1 }), /allowances/);
  assert.throws(() => checkCartesianRefinementTrend(valid, valid,
    { ...allowance, positionKm: NaN }), /allowances/);
});

test('coupled RK4/J2 convergence returns independently auditable trend metadata', () => {
  const out = assessNumericalConvergence(
    circular, 600, 100, 80, controls(5), { j2: true });
  assert.equal(out.status, 'STABLE');
  assert.equal(out.trend.status, 'NO_RESOLVED_GROWTH');
  assert.ok(out.trend.roundoffAllowance.positionKm > 0);
  assert.ok(out.trend.roundoffAllowance.velocityKmS > 0);
  assert.ok(out.trend.roundoffAllowance.epochS > 0);
  assert.ok(out.trend.growingMetrics.length === 0);
});

test('G25 conditional graph links the guard without manufacturing a historical bound', () => {
  const graph = JSON.parse(readFileSync(
    new URL('../research/constraints/orbit_cartesian_refinement_growth_g25.json',
      import.meta.url), 'utf8'));
  assert.equal(graph.classification,
    'NUMERICAL_FALSIFICATION_NOT_EMPIRICAL_ORBITAL_CONSTRAINT');
  assert.equal(graph.epsilon_coefficient, 64);
  assert.ok(graph.source_occurrences.includes('C197#1'));
  assert.equal(graph.historical_initial_state, null);
  assert.equal(graph.authenticated_527_529_holdout, null);
  assert.equal(graph.historical_trajectory_domain_reduced, false);
  assert.equal(graph.sgp4_baseline_validated, false);
  assert.equal(graph.confidence_or_impact_probability, null);
});
