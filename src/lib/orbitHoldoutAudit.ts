/**
 * Refinement-aware chronological 527/529 holdout scoring for the experimental
 * coupled Cartesian r/v model, not a conversion of mean TLEs and not SGP4.
 *
 * Deliberately does not infer independent observation, atmospheric calibration,
 * historic validity, a geographic impact, or a certified numerical error bound.
 */
import { utcMilliseconds, validateTimedPositions } from './orbitPhysics.ts';
import { assessNumericalConvergence } from './orbitConvergence.ts';
import type { PreCutoffOrbitFit, TimedOrbitPosition, Vec3 } from './orbitPhysics.ts';
import type { ConvergenceAssessment, ConvergenceControls } from './orbitConvergence.ts';

export interface RefinementHoldoutLevel {
  readonly stepS: number;
  readonly baselineRmsKm: number;
  readonly fittedRmsKm: number;
  /** Positive => fitted hypothesis is WORSE on the withheld positions. */
  readonly deltaRmsKm: number;
}
export interface AuditedHoldoutPoint {
  readonly epochUtc: string;
  readonly source: string;
  readonly baseline: ConvergenceAssessment;
  readonly fitted: ConvergenceAssessment;
}
export type HoldoutAuditStatus =
  | 'EVENT_CONFLICT'
  | 'NOT_RESOLVED'
  | 'MODEL_TERMINATED'
  | 'REFINEMENT_RANKING_CONFLICT'
  | 'NUMERICALLY_INDISTINGUISHABLE'
  | 'APPARENT_FITTED_BETTER'
  | 'APPARENT_BASELINE_BETTER';
export interface AuditedHoldoutResult {
  /** TRAINING is in-sample; HOLDOUT is the post-cutoff evaluation. */
  readonly phase: 'TRAINING' | 'HOLDOUT';
  readonly objectNorad: 527 | 529;
  readonly status: HoldoutAuditStatus;
  readonly points: readonly AuditedHoldoutPoint[];
  readonly levels: readonly RefinementHoldoutLevel[];
  /** Maximum observed change in RMS delta over the last three refinements. */
  readonly recentDeltaSensitivityKm: number | null;
  readonly observationAuthenticity: 'NOT_VERIFIED';
  readonly observationIndependence: 'NOT_VERIFIED';
  readonly historicalCalibration: 'NOT_RUN';
  readonly rigorousErrorEnclosure: false;
  readonly impactInference: 'NOT_SUPPORTED';
}

const normDelta = (a: Vec3, b: Vec3): number =>
  Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

const rms = (squaredErrors: readonly number[]): number =>
  Math.sqrt(squaredErrors.reduce((sum, x) => sum + x, 0) / squaredErrors.length);

const rank = (deltaKm: number): -1 | 0 | 1 =>
  deltaKm < 0 ? -1 : deltaKm > 0 ? 1 : 0;

/**
 * Force every future observation through both independent numerical refinements.
 * The *only* reference positions are withheld inputs supplied by the caller.
 * No future observation enters the already-completed fit.
 *
 * Numerical STABLE only means repeated RK4 steps agree at caller tolerances.
 * The labels APPARENT_* are conditional, never authenticated historical skill:
 * no result here establishes an SGP4 comparison, a proof of accuracy, or impact.
 */
function auditOrbitResiduals(
  fit: PreCutoffOrbitFit,
  heldout: readonly TimedOrbitPosition[],
  controls: ConvergenceControls,
  phase: 'TRAINING' | 'HOLDOUT',
): AuditedHoldoutResult {
  // One strict UTC/frame/object validation boundary for both phases.
  // Unlike a coarse score, this does not propagate before convergence checks.
  validateTimedPositions(heldout, fit.objectNorad, fit.inertialFrame,
    utcMilliseconds(fit.initialEpochUtc), utcMilliseconds(fit.cutoffEpochUtc),
    phase === 'TRAINING' ? 'training' : 'holdout');

  const points = heldout.map(o => ({
    epochUtc: o.epochUtc,
    source: o.source,
    baseline: assessNumericalConvergence(
      fit.initialState, o.elapsedS, fit.stepS,
      fit.terminationAltitudeKm, controls, fit.dynamics),
    fitted: assessNumericalConvergence(
      fit.fittedState, o.elapsedS, fit.stepS,
      fit.terminationAltitudeKm, controls, fit.dynamics),
  }));
  const result = (status: HoldoutAuditStatus, levels: readonly RefinementHoldoutLevel[] = [],
    recentDeltaSensitivityKm: number | null = null): AuditedHoldoutResult => ({
    phase, objectNorad: fit.objectNorad, status, points, levels, recentDeltaSensitivityKm,
    observationAuthenticity: 'NOT_VERIFIED', observationIndependence: 'NOT_VERIFIED',
    historicalCalibration: 'NOT_RUN', rigorousErrorEnclosure: false,
    impactInference: 'NOT_SUPPORTED',
  });

  if (points.some(p => p.baseline.status === 'EVENT_CONFLICT' ||
      p.fitted.status === 'EVENT_CONFLICT')) return result('EVENT_CONFLICT');
  if (points.some(p => p.baseline.status !== 'STABLE' ||
      p.fitted.status !== 'STABLE')) return result('NOT_RESOLVED');
  if (points.some(p => p.baseline.finest.event !== 'elapsed' ||
      p.fitted.finest.event !== 'elapsed')) return result('MODEL_TERMINATED');

  // No score is emitted when either trajectory crossed the termination
  // threshold, even if that numeric event is stable on step halving.
  const levels: RefinementHoldoutLevel[] = [];
  const levelCount = points[0].baseline.levels.length;
  for (let i = 0; i < levelCount; i++) {
    const baselineRmsKm = rms(points.map((p, j) =>
      normDelta(p.baseline.levels[i].result.state.rKm, heldout[j].rKm) ** 2));
    const fittedRmsKm = rms(points.map((p, j) =>
      normDelta(p.fitted.levels[i].result.state.rKm, heldout[j].rKm) ** 2));
    levels.push({
      stepS: points[0].baseline.levels[i].stepS,
      baselineRmsKm, fittedRmsKm, deltaRmsKm: fittedRmsKm - baselineRmsKm,
    });
  }
  const lastThree = levels.slice(-3);
  const delta = lastThree[2].deltaRmsKm;
  const sensitivity = Math.max(
    Math.abs(delta - lastThree[1].deltaRmsKm),
    Math.abs(delta - lastThree[0].deltaRmsKm),
  );

  // Even with individually converged states, the *winner* can change when
  // both models' holdout errors are close. This is a useful negative finding.
  if (lastThree.some(level => rank(level.deltaRmsKm) !== rank(delta)))
    return result('REFINEMENT_RANKING_CONFLICT', levels, sensitivity);
  // This is a heuristic stability margin, NOT a rigorous discretization bound.
  if (Math.abs(delta) <= Math.max(sensitivity, 2 * controls.tolerance.positionKm))
    return result('NUMERICALLY_INDISTINGUISHABLE', levels, sensitivity);
  return result(delta < 0 ? 'APPARENT_FITTED_BETTER' : 'APPARENT_BASELINE_BETTER',
    levels, sensitivity);
}

/** The chronology-only training audit cannot certify independent prediction.
 * It is called AFTER the bounded grid fit, never during optimization.
 * In-sample gain is acceptable only if independently refined r/v trajectories
 * support the ranking; otherwise the caller must preserve a negative result.
 */
export function auditTrainingOrbitScore(
  fit: PreCutoffOrbitFit,
  training: readonly TimedOrbitPosition[],
  controls: ConvergenceControls,
): AuditedHoldoutResult {
  if (!training.length) throw new RangeError('No training observations to audit');
  return auditOrbitResiduals(fit, training, controls, 'TRAINING');
}

/** Withheld-position evaluation. No refit or reuse of training observations. */
export function auditFutureOrbitScore(
  fit: PreCutoffOrbitFit,
  heldout: readonly TimedOrbitPosition[],
  controls: ConvergenceControls,
): AuditedHoldoutResult {
  if (!heldout.length) throw new RangeError('No future observations to score');
  return auditOrbitResiduals(fit, heldout, controls, 'HOLDOUT');
}
