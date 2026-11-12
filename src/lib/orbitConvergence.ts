/**
 * Deterministic step-halving diagnostic for the experimental Cartesian RK4 kernel.
 * Numeric agreement is NOT an orbital observation, an absolute error certificate,
 * or a historical reentry prediction. Keep SGP4 mean-element baselines separate.
 */
import { propagate } from './orbitPhysics.ts';
import type { State, Dynamics, Propagation, Vec3 } from './orbitPhysics.ts';

export interface NumericalTolerance {
  readonly positionKm: number;
  readonly velocityKmS: number;
  readonly epochS: number;
}
export interface ConvergenceControls {
  /** At least two halvings: require the last TWO adjacent comparisons to agree. */
  readonly halvings: number;
  readonly tolerance: NumericalTolerance;
}
export interface AdjacentDifference {
  readonly eventAgrees: boolean;
  readonly positionKm: number;
  readonly velocityKmS: number;
  readonly epochS: number;
  readonly withinTolerance: boolean;
}
export interface ConvergenceLevel {
  readonly stepS: number;
  readonly result: Propagation;
  /** Comparison against the previous, coarser level. */
  readonly difference: AdjacentDifference | null;
}
/**
 * Reject resolved growth of adjacent r/v/epoch differences independently of
 * the user's (possibly very loose) absolute tolerances. This is the same
 * falsification principle as the Jacobi budget trend, but uses Cartesian
 * units directly and is applied to EVERY numerical holdout/ensemble consumer.
 *
 * A 64-ULP scale allowance is only an explicit floating-point heuristic.
 * Neither monotonicity nor step agreement certifies an absolute error bound.
 * C197#1 (NASA/Goddard SSR 15 Nov 1963 p.8) supplies a decay DAY only;
 * historical 527/529 Cartesian measurements remain unverified.
 */
export type CartesianTrendMetric = keyof NumericalTolerance;
export interface CartesianRefinementTrend {
  readonly status: 'NO_RESOLVED_GROWTH' | 'GROWTH_BEYOND_ROUNDOFF' | 'NONFINITE_DIFFERENCE';
  readonly growingMetrics: readonly CartesianTrendMetric[];
  readonly roundoffAllowance: NumericalTolerance;
  readonly interpretation: 'HEURISTIC_64_EPS_SCALE_NOT_ERROR_BOUND';
}
export function checkCartesianRefinementTrend(
  previous: AdjacentDifference, finest: AdjacentDifference,
  roundoffAllowance: NumericalTolerance,
): CartesianRefinementTrend {
  const metrics: readonly CartesianTrendMetric[] = ['positionKm', 'velocityKmS', 'epochS'];
  if (metrics.some(key => !Number.isFinite(roundoffAllowance[key]) ||
      roundoffAllowance[key] < 0))
    throw new RangeError('Cartesian trend allowances require nonnegative finite units');
  const finite = metrics.every(key => Number.isFinite(previous[key]) &&
    previous[key] >= 0 && Number.isFinite(finest[key]) && finest[key] >= 0);
  const growingMetrics = finite ? metrics.filter(key =>
    finest[key] > previous[key] + roundoffAllowance[key]) : [];
  return {
    status: !finite ? 'NONFINITE_DIFFERENCE' :
      growingMetrics.length ? 'GROWTH_BEYOND_ROUNDOFF' : 'NO_RESOLVED_GROWTH',
    growingMetrics, roundoffAllowance,
    interpretation: 'HEURISTIC_64_EPS_SCALE_NOT_ERROR_BOUND',
  };
}

export interface ConvergenceAssessment {
  /**
   * EVENT_CONFLICT overrides apparently good fine-step agreement: a coarse
   * integration MISSED or falsely announced the termination event.
   * STABLE only means the last three resolutions agree within caller tolerances.
   */
  readonly status: 'STABLE' | 'NOT_RESOLVED' | 'EVENT_CONFLICT';
  readonly levels: readonly ConvergenceLevel[];
  readonly finest: Propagation;
  readonly trend: CartesianRefinementTrend;
}

const separation = (a: Vec3, b: Vec3): number =>
  Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

/**
 * Reintegrate the full (r,v) state from the SAME epoch, halving the actual
 * integration step each time. Never blend, interpolate or "correct" a trajectory
 * by moving only its latitude/longitude or altitude after SGP4.
 *
 * All levels use the same assumed dynamics and inputs, hence they are NOT
 * independent observational validation. A STABLE outcome is necessary but
 * not sufficient for credible physical prediction or historical inference.
 */
export function assessNumericalConvergence(
  initial: State, durationS: number, stepS: number,
  terminationAltitudeKm: number, controls: ConvergenceControls,
  dynamics: Dynamics = {},
): ConvergenceAssessment {
  const { halvings, tolerance } = controls;
  if (!Number.isInteger(halvings) || halvings < 2 || halvings > 10 ||
      !tolerance ||
      ![tolerance.positionKm, tolerance.velocityKmS, tolerance.epochS].every(
        value => Number.isFinite(value) && value > 0)) {
    throw new RangeError('Require 2–10 halvings and positive, finite r/v/epoch tolerances');
  }
  const levels: ConvergenceLevel[] = [];
  for (let index = 0; index <= halvings; index++) {
    const refinedStepS = stepS / 2 ** index;
    if (!(refinedStepS > 0) || !Number.isFinite(refinedStepS)) {
      throw new RangeError('Refinement produced an invalid time step');
    }
    // The physical kernel checks duration, threshold, and the 1e6-step limit.
    const result = propagate(initial, durationS, refinedStepS, terminationAltitudeKm, dynamics);
    const previous = levels.at(-1);
    let difference: AdjacentDifference | null = null;
    if (previous) {
      const eventAgrees = previous.result.event === result.event;
      const positionKm = separation(previous.result.state.rKm, result.state.rKm);
      const velocityKmS = separation(previous.result.state.vKmS, result.state.vKmS);
      const epochS = Math.abs(previous.result.state.tS - result.state.tS);
      difference = {
        eventAgrees, positionKm, velocityKmS, epochS,
        withinTolerance: eventAgrees &&
          positionKm <= tolerance.positionKm &&
          velocityKmS <= tolerance.velocityKmS &&
          epochS <= tolerance.epochS,
      };
    }
    levels.push({ stepS: refinedStepS, result, difference });
  }
  const differences = levels.slice(1).map(level => level.difference!);
  const eventConflict = differences.some(difference => !difference.eventAgrees);
  // Heuristic 64*EPSILON at each physical scale, never taken from the
  // caller's acceptance limits (which could hide a growing numerical error).
  const recentStates = levels.slice(-3).map(level => level.result.state);
  const allowance = (values: readonly number[]): number =>
    64 * Number.EPSILON * Math.max(1, ...values.map(Math.abs));
  const trend = checkCartesianRefinementTrend(
    differences.at(-2)!, differences.at(-1)!, {
      positionKm: allowance(recentStates.map(s => Math.hypot(...s.rKm))),
      velocityKmS: allowance(recentStates.map(s => Math.hypot(...s.vKmS))),
      epochS: allowance(recentStates.map(s => s.tS)),
    });
  const stableAtFinest = differences.slice(-2).every(difference => difference.withinTolerance) &&
    trend.status === 'NO_RESOLVED_GROWTH';
  return {
    status: eventConflict ? 'EVENT_CONFLICT' : stableAtFinest ? 'STABLE' : 'NOT_RESOLVED',
    levels, finest: levels[levels.length - 1].result, trend,
  };
}
