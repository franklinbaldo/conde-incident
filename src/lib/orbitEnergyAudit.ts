/**
 * Conditional mechanical-budget falsification for the coupled r/v integrator.
 *
 * In an axisymmetric, time-independent Earth/J2 potential and co-rotating
 * atmosphere, J = kinetic + potential - omega*Lz has drag power
 * dJ/dt = a_drag dot (v - omega cross r) <= 0. This is a model identity,
 * NOT an observation of 1963, a rigorous global error bound or impact proof.
 */
import {
  EARTH, accelerationKmS2, dragJacobiPowerKm2S3, propagate,
  rotatingFrameIntegralKm2S2,
} from './orbitPhysics.ts';
import type { Dynamics, Propagation, State } from './orbitPhysics.ts';

export interface BudgetStep {
  readonly elapsedS: number;
  readonly intervalS: number;
  readonly deltaJacobiKm2S2: number;
  /** Trapezoid integration of theoretical drag power, NOT exact physical work. */
  readonly modeledWorkKm2S2: number;
  readonly closureResidualKm2S2: number;
}
export interface PhysicalBudget {
  /** Only a numerical diagnostic under caller-provided force model and tolerance. */
  readonly status: 'NOT_EVALUATED' | 'NUMERICALLY_CONSISTENT' | 'NUMERICALLY_UNRESOLVED';
  readonly terminationEvent: Propagation['event'];
  readonly final: State;
  readonly deltaJacobiKm2S2: number;
  readonly modeledWorkKm2S2: number;
  readonly closureResidualKm2S2: number;
  readonly largestStepClosureKm2S2: number;
  /** > 0 indicates numerical increase despite non-positive modeled drag power. */
  readonly largestPositiveJacobiStepKm2S2: number;
  readonly steps: readonly BudgetStep[];
  readonly dragSource: string | null;
  readonly historicalCalibration: 'NOT_RUN';
  readonly historicalHoldout: 'NOT_RUN';
  readonly geographicInference: 'NOT_SUPPORTED';
}

/**
 * Compare numerical change in J with the integral of the same drag law used
 * by RK4. A coarse RK4 step or trapezoid quadrature can give a false balance:
 * repeat with smaller steps and report disagreements, never assert a proof.
 * Threshold is caller supplied; crossing denotes neither ground impact nor
 * historical fragmentation. The final partial step stops at the first
 * descending threshold event as determined by propagate().
 */
export function auditPhysicalBudget(
  initial: State, durationS: number, stepS: number, terminationAltitudeKm: number,
  closureToleranceKm2S2: number, dynamics: Dynamics = {},
): PhysicalBudget {
  if (!Number.isFinite(durationS) || durationS < 0 ||
      !Number.isFinite(stepS) || stepS <= 0 ||
      !Number.isFinite(closureToleranceKm2S2) || closureToleranceKm2S2 <= 0 ||
      !Number.isFinite(terminationAltitudeKm) || terminationAltitudeKm < 0 ||
      !Number.isSafeInteger(Math.ceil(durationS / stepS)) ||
      Math.ceil(durationS / stepS) > 100_000) {
    throw new RangeError('Invalid finite duration, step, threshold or energy tolerance');
  }
  // Validate even zero-duration inputs, rather than treating bad states as safe.
  accelerationKmS2(initial, { j2: dynamics.j2 });
  const power = (s: State): number =>
    dynamics.atmosphere ? dragJacobiPowerKm2S3(s, dynamics.atmosphere) : 0;
  let current = initial;
  let currentJ = rotatingFrameIntegralKm2S2(current, dynamics.j2);
  if (!Number.isFinite(currentJ) || !Number.isFinite(power(current))) {
    throw new RangeError('Invalid initial model energy or drag power');
  }
  let elapsedS = 0;
  let modeledWork = 0;
  let maxClosure = 0;
  let maxPositiveIncrease = 0;
  let event: Propagation['event'] = 'elapsed';
  const steps: BudgetStep[] = [];
  if (Math.hypot(...initial.rKm) <= EARTH.radiusKm + terminationAltitudeKm) {
    event = 'reentry-threshold';
  }
  while (elapsedS < durationS - 1e-10 && event !== 'reentry-threshold') {
    const h = Math.min(stepS, durationS - elapsedS);
    const result = propagate(current, h, h, terminationAltitudeKm, dynamics);
    const actualDt = result.state.tS - current.tS;
    if (!(actualDt > 0) || actualDt > h + 1e-7) {
      throw new RangeError('Invalid propagated event epoch');
    }
    const nextJ = rotatingFrameIntegralKm2S2(result.state, dynamics.j2);
    const work = actualDt * (power(current) + power(result.state)) / 2;
    const deltaJ = nextJ - currentJ;
    const residual = deltaJ - work;
    if (![nextJ, work, deltaJ, residual].every(Number.isFinite)) {
      throw new RangeError('Nonfinite mechanical-work diagnostic');
    }
    maxClosure = Math.max(maxClosure, Math.abs(residual));
    maxPositiveIncrease = Math.max(maxPositiveIncrease, deltaJ);
    modeledWork += work;
    elapsedS += h;
    steps.push({
      elapsedS: result.state.tS - initial.tS, intervalS: actualDt,
      deltaJacobiKm2S2: deltaJ, modeledWorkKm2S2: work,
      closureResidualKm2S2: residual,
    });
    currentJ = nextJ;
    current = result.state;
    event = result.event;
  }
  const deltaJacobi = currentJ - rotatingFrameIntegralKm2S2(initial, dynamics.j2);
  const closure = deltaJacobi - modeledWork;
  return {
    status: steps.length === 0 ? 'NOT_EVALUATED' :
      maxClosure <= closureToleranceKm2S2 && maxPositiveIncrease <= closureToleranceKm2S2 &&
      Math.abs(closure) <= closureToleranceKm2S2
        ? 'NUMERICALLY_CONSISTENT' : 'NUMERICALLY_UNRESOLVED',
    terminationEvent: event, final: current, deltaJacobiKm2S2: deltaJacobi,
    modeledWorkKm2S2: modeledWork, closureResidualKm2S2: closure,
    largestStepClosureKm2S2: maxClosure,
    largestPositiveJacobiStepKm2S2: maxPositiveIncrease,
    steps, dragSource: dynamics.atmosphere?.source ?? null,
    historicalCalibration: 'NOT_RUN', historicalHoldout: 'NOT_RUN',
    geographicInference: 'NOT_SUPPORTED',
  };
}
