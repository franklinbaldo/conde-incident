import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, dragJacobiPowerKm2S3, rotatingFrameIntegralKm2S2 } from '../src/lib/orbitPhysics.ts';
import { auditPhysicalBudget, auditRefinedPhysicalBudget, checkRefinementTrend } from '../src/lib/orbitEnergyAudit.ts';

// All states and density functions below are SYNTHETIC, not 1963 tracking.
const radiusKm = EARTH.radiusKm + 500;
const initial = {
  rKm: [radiusKm, 0, 0],
  vKmS: [0, Math.sqrt(EARTH.muKm3S2 / radiusKm), 0.4],
  tS: 0,
};
const drag = {
  source: 'SYNTHETIC constant density: not a 1963 atmospheric reconstruction',
  densityKgM3: () => 2e-10,
  cdAreaOverMassM2Kg: 0.1,
};

test('axisymmetric central+J2 without drag conserves E - omega Lz numerically', () => {
  const audit = auditPhysicalBudget(initial, 900, 20, 80, 1e-7, { j2: true });
  assert.equal(audit.status, 'NUMERICALLY_CONSISTENT');
  assert.equal(audit.terminationEvent, 'elapsed');
  assert.equal(audit.steps.length, 45);
  assert.equal(audit.modeledWorkKm2S2, 0);
  assert.ok(Math.abs(audit.deltaJacobiKm2S2) < 1e-7);
  assert.equal(audit.historicalHoldout, 'NOT_RUN');
  assert.equal(audit.historicalCalibration, 'NOT_RUN');
  assert.equal(audit.geographicInference, 'NOT_SUPPORTED');
});

test('co-rotating drag must dissipate the Jacobi integral, and balance modeled work', () => {
  const dynamics = { j2: true, atmosphere: drag };
  const audit = auditPhysicalBudget(initial, 900, 20, 80, 5e-6, dynamics);
  assert.equal(audit.terminationEvent, 'elapsed');
  assert.equal(audit.status, 'NUMERICALLY_CONSISTENT');
  assert.ok(dragJacobiPowerKm2S3(initial, drag) < 0);
  assert.ok(audit.modeledWorkKm2S2 < 0);
  assert.ok(audit.deltaJacobiKm2S2 < 0);
  assert.ok(Math.abs(audit.closureResidualKm2S2) < 5e-6);
  assert.ok(audit.steps.every(s => s.modeledWorkKm2S2 <= 0));
  assert.equal(audit.dragSource, drag.source);
  assert.ok(Math.abs(
    rotatingFrameIntegralKm2S2(audit.final, true) -
    rotatingFrameIntegralKm2S2(initial, true) - audit.deltaJacobiKm2S2,
  ) < 1e-12);
});

test('step-halving reduces the physical-work balance discrepancy for synthetic drag', () => {
  const dynamics = { j2: true, atmosphere: drag };
  const coarse = auditPhysicalBudget(initial, 1200, 200, 80, 1e-16, dynamics);
  const fine = auditPhysicalBudget(initial, 1200, 20, 80, 1e-16, dynamics);
  assert.equal(coarse.status, 'NUMERICALLY_UNRESOLVED');
  assert.ok(
    Math.abs(fine.closureResidualKm2S2) < Math.abs(coarse.closureResidualKm2S2),
    'a coarse budget must not be marked valid merely because drag power is negative',
  );
  assert.ok(fine.largestStepClosureKm2S2 < coarse.largestStepClosureKm2S2);
});

test('first descending numerical event truncates the budget; not an impact', () => {
  const descending = {
    rKm: [EARTH.radiusKm + 90, 0, 0],
    vKmS: [-0.15, 8.15, 0], tS: 0,
  };
  const budget = auditPhysicalBudget(descending, 400, 400, 80, 1e-8);
  assert.equal(budget.terminationEvent, 'reentry-threshold');
  assert.ok(budget.final.tS > 0 && budget.final.tS < 400);
  assert.equal(budget.steps.length, 1);
  assert.ok(budget.steps[0].intervalS < 400);
  assert.equal(budget.geographicInference, 'NOT_SUPPORTED');
});

test('invalid or unsourced atmosphere and model controls fail closed', () => {
  assert.throws(() => auditPhysicalBudget(initial, -1, 20, 80, 1e-5), /Invalid finite/);
  assert.throws(() => auditPhysicalBudget(initial, 900, 0, 80, 1e-5), /Invalid finite/);
  assert.throws(() => auditPhysicalBudget(initial, 900, 20, 80, 0), /Invalid finite/);
  assert.throws(() => auditPhysicalBudget(initial, 900, 0.00001, 80, 1e-5), /Invalid finite/);
  assert.throws(() => auditPhysicalBudget(initial, 100, 20, 80, 1e-5,
    { atmosphere: { ...drag, source: '' } }), /requires source/);
  assert.throws(() => auditPhysicalBudget(initial, 100, 20, 80, 1e-5,
    { atmosphere: { ...drag, densityKgM3: () => -1 } }), /Density/);
  const idle = auditPhysicalBudget(initial, 0, 20, 80, 1e-5);
  assert.equal(idle.status, 'NOT_EVALUATED');
  assert.equal(idle.steps.length, 0);
});


// The following controls are deliberately SYNTHETIC. They are neither
// 1963 orbital ephemerides nor validated uncertainty intervals.
const looseRefinement = Object.freeze({
  positionKm: 500, velocityKmS: 5, epochS: 500,
  jacobiKm2S2: 5, modeledWorkKm2S2: 5,
});

test('independent r/v reintegrations agree when generous dimensional limits are declared', () => {
  const audit = auditRefinedPhysicalBudget(
    initial, 1200, 200, 80, 5, looseRefinement, 2, { j2: true, atmosphere: drag });
  assert.equal(audit.status, 'REFINEMENT_CONSISTENT');
  assert.deepEqual(audit.levels.map(x => x.steps.length), [6, 12, 24]);
  assert.equal(audit.differences.length, 2);
  assert.ok(audit.differences.every(d => Object.values(d).every(Number.isFinite)));
  assert.ok(audit.levels.every(x => x.dragSource === drag.source));
  assert.equal(audit.interpretation, 'NUMERICAL_ONLY_NOT_HISTORICAL');
});

test('a green energy-work budget is NOT enough when independent r/v states disagree', () => {
  const limits = { ...looseRefinement, positionKm: 1e-14 };
  const audit = auditRefinedPhysicalBudget(
    initial, 1200, 200, 80, 5, limits, 2, { j2: true });
  assert.ok(audit.levels.every(x => x.status === 'NUMERICALLY_CONSISTENT'));
  assert.ok(audit.differences.at(-1).positionKm > limits.positionKm);
  assert.equal(audit.status, 'REFINEMENT_UNRESOLVED');
  assert.equal(audit.levels.at(-1).geographicInference, 'NOT_SUPPORTED');
});

test('physical budget error in finest two runs cannot be hidden by large state tolerances', () => {
  const audit = auditRefinedPhysicalBudget(
    initial, 1200, 200, 80, 1e-16, looseRefinement, 2,
    { j2: true, atmosphere: drag });
  assert.notEqual(audit.status, 'REFINEMENT_CONSISTENT');
  assert.ok(audit.levels.some(x => x.status === 'NUMERICALLY_UNRESOLVED'));
});

test('the threshold event is compared across step sizes without claiming impact', () => {
  const descending = {
    rKm: [EARTH.radiusKm + 90, 0, 0],
    vKmS: [-0.15, 8.15, 0], tS: 0,
  };
  const audit = auditRefinedPhysicalBudget(
    descending, 400, 400, 80, 5, looseRefinement, 2);
  assert.ok(audit.levels.every(x => x.terminationEvent === 'reentry-threshold'));
  assert.ok(audit.levels.every(x => x.final.tS > 0 && x.final.tS < 400));
  assert.equal(audit.interpretation, 'NUMERICAL_ONLY_NOT_HISTORICAL');
});

test('refinement controls are dimensioned, finite and bounded for reproducibility', () => {
  const run = (limits, n) => auditRefinedPhysicalBudget(
    initial, 100, 20, 80, 1e-5, limits, n);
  assert.throws(() => run(looseRefinement, 1), /2..5 halvings/);
  assert.throws(() => run(looseRefinement, 6), /2..5 halvings/);
  assert.throws(() => run({ ...looseRefinement, epochS: 0 }, 2), /positive finite/);
  assert.throws(() => run({ ...looseRefinement, velocityKmS: NaN }, 2), /positive finite/);
  const x = run(looseRefinement, 2);
  const y = run(looseRefinement, 2);
  assert.deepEqual(x, y, 'identical seed-free state/model/controls must be repeatable');
});

test('G16 adversarial: limits cannot mask 9000x growth in refinement differences', () => {
  // Gavião issue franklinbaldo/castor#2: the previous condition
  // final <= max(limit, 1.25 * previous) is implied by final <= limit.
  const previous = {
    positionKm: 0.0001, velocityKmS: 0, epochS: 0,
    jacobiKm2S2: 0, modeledWorkKm2S2: 0,
  };
  const final = { ...previous, positionKm: 0.9 };
  const callerLimitKm = 1;
  assert.ok(final.positionKm <= callerLimitKm);
  assert.ok(final.positionKm <= Math.max(callerLimitKm, 1.25 * previous.positionKm),
    'the old supposed trend gate incorrectly approves this growth');
  const roundoff = {
    positionKm: 64 * Number.EPSILON * 7000, velocityKmS: 1e-12,
    epochS: 1e-12, jacobiKm2S2: 1e-12, modeledWorkKm2S2: 1e-12,
  };
  const trend = checkRefinementTrend(previous, final, roundoff);
  assert.equal(trend.status, 'GROWTH_BEYOND_ROUNDOFF');
  assert.deepEqual(trend.growingMetrics, ['positionKm']);
  assert.deepEqual(trend.roundoffAllowance, roundoff);
  assert.equal(trend.method, 'HEURISTIC_64_EPS_SCALE_NOT_ERROR_BOUND');
});

test('near-roundoff growth is reported as unresolved trend rather than a numerical proof', () => {
  const previous = {
    positionKm: 0, velocityKmS: 0, epochS: 0,
    jacobiKm2S2: 0, modeledWorkKm2S2: 0,
  };
  const final = { ...previous, positionKm: 1e-12 };
  const floor = { ...previous, positionKm: 1e-10 };
  const trend = checkRefinementTrend(previous, final, floor);
  assert.equal(trend.status, 'NO_RESOLVED_GROWTH');
  assert.deepEqual(trend.growingMetrics, []);
  assert.throws(() => checkRefinementTrend(previous, final,
    { ...floor, jacobiKm2S2: -1 }), /nonnegative finite/);
  assert.throws(() => checkRefinementTrend(previous, final,
    { ...floor, epochS: Infinity }), /nonnegative finite/);
});

test('coupled refinement exposes a separate, dimensioned growth audit', () => {
  const audit = auditRefinedPhysicalBudget(
    initial, 1200, 200, 80, 5, looseRefinement, 2, { j2: true, atmosphere: drag });
  assert.equal(audit.trend.method, 'HEURISTIC_64_EPS_SCALE_NOT_ERROR_BOUND');
  assert.ok(Object.values(audit.trend.roundoffAllowance).every(
    x => Number.isFinite(x) && x > 0));
  assert.ok(audit.trend.growingMetrics.every(k => Object.hasOwn(audit.limits, k)));
  if (audit.trend.status === 'GROWTH_BEYOND_ROUNDOFF') {
    assert.equal(audit.status, 'REFINEMENT_UNRESOLVED');
  }
  assert.equal(audit.interpretation, 'NUMERICAL_ONLY_NOT_HISTORICAL');
});
