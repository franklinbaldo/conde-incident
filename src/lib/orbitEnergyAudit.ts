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


/** Independent step-halving is a falsification check, not a certified error enclosure. */
export interface BudgetRefinementLimits {
  readonly positionKm: number;
  readonly velocityKmS: number;
  readonly epochS: number;
  readonly jacobiKm2S2: number;
  readonly modeledWorkKm2S2: number;
}
export interface BudgetRefinementDifference {
  readonly positionKm: number;
  readonly velocityKmS: number;
  readonly epochS: number;
  readonly jacobiKm2S2: number;
  readonly modeledWorkKm2S2: number;
}
export interface RefinementTrendAudit {
  readonly status: 'NO_RESOLVED_GROWTH' | 'GROWTH_BEYOND_ROUNDOFF';
  /** Unit-matched 64*EPSILON*scale heuristic, NOT a certified error bound. */
  readonly roundoffAllowance: BudgetRefinementDifference;
  readonly growingMetrics: readonly (keyof BudgetRefinementLimits)[];
  readonly method: 'HEURISTIC_64_EPS_SCALE_NOT_ERROR_BOUND';
}

/**
 * A distinct trend check: neither an absolute tolerance nor budget closure
 * can excuse resolved growth after step halving. Compare quantities of the
 * SAME physical dimension and permit only an explicitly reported floating-
 * point scale allowance, not the much larger user acceptance limits.
 */
export function checkRefinementTrend(
  previous: BudgetRefinementDifference,
  final: BudgetRefinementDifference,
  roundoffAllowance: BudgetRefinementDifference,
): RefinementTrendAudit {
  const keys: readonly (keyof BudgetRefinementLimits)[] =
    ['positionKm', 'velocityKmS', 'epochS', 'jacobiKm2S2', 'modeledWorkKm2S2'];
  if (keys.some(k => ![previous[k], final[k], roundoffAllowance[k]].every(
    x => Number.isFinite(x) && x >= 0,
  ))) throw new RangeError('Trend differences/roundoff allowances must be nonnegative finite');
  const growingMetrics = keys.filter(k =>
    final[k] > previous[k] + roundoffAllowance[k]);
  return {
    status: growingMetrics.length ? 'GROWTH_BEYOND_ROUNDOFF' : 'NO_RESOLVED_GROWTH',
    roundoffAllowance,
    growingMetrics,
    method: 'HEURISTIC_64_EPS_SCALE_NOT_ERROR_BOUND',
  };
}

export interface RefinedPhysicalBudget {
  readonly status: 'NOT_EVALUATED' | 'EVENT_CONFLICT' | 'BUDGET_UNRESOLVED' |
    'REFINEMENT_UNRESOLVED' | 'REFINEMENT_CONSISTENT';
  readonly levels: readonly PhysicalBudget[];
  /** Difference of levels i and i+1; last entry compares the two finest runs. */
  readonly differences: readonly BudgetRefinementDifference[];
  readonly limits: BudgetRefinementLimits;
  /** Independent resolved-growth diagnostic, not numerical certification. */
  readonly trend: RefinementTrendAudit;
  readonly interpretation: 'NUMERICAL_ONLY_NOT_HISTORICAL';
}

/**
 * Independently repropagate the SAME initial r/v and force model with h, h/2,
 * h/4 (optionally finer). Require stable event classification, Jacobi balance
 * at BOTH finest resolutions, final-state agreement and no resolved growth
 * beyond a separately reported floating-point roundoff heuristic.
 * Neither a small energy budget nor agreement of two RK4 steps by itself
 * constitutes an error bound or empirical orbit determination.
 */
export function auditRefinedPhysicalBudget(
  initial: State, durationS: number, stepS: number, terminationAltitudeKm: number,
  closureToleranceKm2S2: number, limits: BudgetRefinementLimits,
  halvings = 2, dynamics: Dynamics = {},
): RefinedPhysicalBudget {
  const keys: readonly (keyof BudgetRefinementLimits)[] =
    ['positionKm', 'velocityKmS', 'epochS', 'jacobiKm2S2', 'modeledWorkKm2S2'];
  if (!Number.isInteger(halvings) || halvings < 2 || halvings > 5 ||
      !limits || keys.some(k => !Number.isFinite(limits[k]) || limits[k] <= 0))
    throw new RangeError('Refinement requires 2..5 halvings and positive finite dimensional limits');
  const levels: PhysicalBudget[] = [];
  for (let i = 0; i <= halvings; i++) {
    levels.push(auditPhysicalBudget(
      initial, durationS, stepS / 2 ** i, terminationAltitudeKm,
      closureToleranceKm2S2, dynamics,
    ));
  }
  const differences: BudgetRefinementDifference[] = [];
  for (let i = 1; i < levels.length; i++) {
    const a = levels[i - 1], b = levels[i];
    const diff = (x: readonly number[], y: readonly number[]) =>
      Math.hypot(...x.map((v, j) => v - y[j]));
    const difference = {
      positionKm: diff(a.final.rKm, b.final.rKm),
      velocityKmS: diff(a.final.vKmS, b.final.vKmS),
      epochS: Math.abs(a.final.tS - b.final.tS),
      jacobiKm2S2: Math.abs(a.deltaJacobiKm2S2 - b.deltaJacobiKm2S2),
      modeledWorkKm2S2: Math.abs(a.modeledWorkKm2S2 - b.modeledWorkKm2S2),
    };
    if (keys.some(k => !Number.isFinite(difference[k])))
      throw new RangeError('Nonfinite numerical refinement difference');
    differences.push(difference);
  }
  const eventsAgree = levels.every(l => l.terminationEvent === levels[0].terminationEvent);
  const final = differences.at(-1)!;
  const previous = differences.at(-2)!;
  const finalWithinLimits = keys.every(k => final[k] <= limits[k]);
  // Heuristic numerical scale from actual state/diagnostic values, with
  // dimensional units matching each difference. 64*EPSILON is a conservative
  // roundoff allowance, NOT a rigorous upper bound on accumulated RK4 error.
  // Crucially it is INDEPENDENT of the caller's acceptance limits.
  const roundoff = (values: readonly number[]) => {
    const scale = Math.max(1, ...values.map(Math.abs));
    const allowance = 64 * Number.EPSILON * scale;
    if (!Number.isFinite(allowance))
      throw new RangeError('Nonfinite refinement roundoff scale');
    return allowance;
  };
  const trend = checkRefinementTrend(previous, final, {
    positionKm: roundoff(levels.map(l => Math.hypot(...l.final.rKm))),
    velocityKmS: roundoff(levels.map(l => Math.hypot(...l.final.vKmS))),
    epochS: roundoff(levels.map(l => l.final.tS)),
    jacobiKm2S2: roundoff(levels.map(l => l.deltaJacobiKm2S2)),
    modeledWorkKm2S2: roundoff(levels.map(l => l.modeledWorkKm2S2)),
  });
  const latestBalances = levels.slice(-2).every(l => l.status === 'NUMERICALLY_CONSISTENT');
  const status: RefinedPhysicalBudget['status'] =
    levels.every(l => l.status === 'NOT_EVALUATED') ? 'NOT_EVALUATED' :
    !eventsAgree ? 'EVENT_CONFLICT' :
    !latestBalances ? 'BUDGET_UNRESOLVED' :
    !finalWithinLimits || trend.status === 'GROWTH_BEYOND_ROUNDOFF'
      ? 'REFINEMENT_UNRESOLVED' : 'REFINEMENT_CONSISTENT';
  return { status, levels, differences, limits, trend, interpretation: 'NUMERICAL_ONLY_NOT_HISTORICAL' };
}
