import test from 'node:test';
import assert from 'node:assert/strict';
import { EARTH, dragJacobiPowerKm2S3, rotatingFrameIntegralKm2S2 } from '../src/lib/orbitPhysics.ts';
import { auditPhysicalBudget } from '../src/lib/orbitEnergyAudit.ts';

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
