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
export interface ConvergenceAssessment {
  /**
   * EVENT_CONFLICT overrides apparently good fine-step agreement: a coarse
   * integration MISSED or falsely announced the termination event.
   * STABLE only means the last three resolutions agree within caller tolerances.
   */
  readonly status: 'STABLE' | 'NOT_RESOLVED' | 'EVENT_CONFLICT';
  readonly levels: readonly ConvergenceLevel[];
  readonly finest: Propagation;
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
  const stableAtFinest = differences.slice(-2).every(difference => difference.withinTolerance);
  return {
    status: eventConflict ? 'EVENT_CONFLICT' : stableAtFinest ? 'STABLE' : 'NOT_RESOLVED',
    levels, finest: levels[levels.length - 1].result,
  };
}
