/**
 * Resolution-budget gate for DOCUMENTED Cartesian 527/529 holdouts.
 * C197#1 (NASA/Goddard SSR, 15 Nov 1963, printed p.8) gives only
 * a catalogued decay DAY for 1963-003B, not a Cartesian measurement.
 * C179-family TLE mirrors share AFSPC lineage and are NOT independent
 * instrumental Cartesian positions.
 *
 * This is a numerical diagnostic only. A reported 1-sigma component
 * does not establish a covariance, a likelihood, source authenticity
 * or historical predictive skill. SGP4 is a separate baseline.
 */
import { auditFutureOrbitScore } from './orbitHoldoutAudit.ts';
import { stageDocumentedChronologicalSplit } from './orbitObservationIntake.ts';
import type { DocumentaryOrbitDatum, ChronologicalCartesianSplit } from './orbitObservationIntake.ts';
import type { PreCutoffOrbitFit } from './orbitPhysics.ts';
import type { ConvergenceControls } from './orbitConvergence.ts';
import type { AuditedHoldoutResult } from './orbitHoldoutAudit.ts';

export type DocumentedResolutionStatus =
  | 'BLOCKED_DOCUMENTATION'
  | 'BLOCKED_NUMERICAL_AUDIT'
  | 'INSUFFICIENT_NUMERICAL_RESOLUTION'
  | 'CONDITIONAL_RESOLUTION_ONLY';

export interface DocumentedResolutionAudit {
  readonly status: DocumentedResolutionStatus;
  readonly intake: ChronologicalCartesianSplit;
  readonly numericalHoldout: AuditedHoldoutResult | null;
  readonly minimumDeclaredSigmaKm: number | null;
  /** Largest of last two adjacent position differences for BOTH hypotheses. */
  readonly worstRecentRefinementKm: number | null;
  /** Conservative diagnostic scale, NOT a rigorous discretization bound. */
  readonly resolutionScaleKm: number | null;
  readonly maxFractionOfSigma: number;
  readonly verifiedInstrumentIndependence: false;
  readonly covarianceOrLikelihoodCalibrated: false;
  readonly historicalHoldoutValidated: false;
  readonly impactInference: 'NOT_SUPPORTED';
}

/**
 * Gate an apparent numerical prediction against declared instrumental
 * component-wise 1-sigma resolution. The fraction is PREDECLARED by caller.
 *
 * All historical measurement claims remain blocked until independently
 * authenticated records with epochs, frames, lineage and calibration exist.
 * Even a compatible resolution is only an internal numerical check, and
 * cannot certify a physical prediction, covariance or reentry location.
 *
 * The fit must have been constructed before seeing the future observations;
 * this contract can check training count, NOT independently prove its
 * creation chronology. No inverse refit occurs here.
 */
export function auditDocumentedHoldoutResolution(
  fit: PreCutoffOrbitFit,
  training: readonly DocumentaryOrbitDatum[],
  holdout: readonly DocumentaryOrbitDatum[],
  controls: ConvergenceControls,
  maxFractionOfSigma: number,
): DocumentedResolutionAudit {
  if (!Number.isFinite(maxFractionOfSigma) ||
      !(maxFractionOfSigma > 0 && maxFractionOfSigma <= 1))
    throw new RangeError('Require a predeclared fraction in (0, 1] of reported 1-sigma');
  const intake = stageDocumentedChronologicalSplit(training, holdout, {
    objectNorad: fit.objectNorad,
    initialEpochUtc: fit.initialEpochUtc,
    cutoffEpochUtc: fit.cutoffEpochUtc,
    inertialFrame: fit.inertialFrame,
  });
  const report = (
    status: DocumentedResolutionStatus,
    numericalHoldout: AuditedHoldoutResult | null = null,
    minimumDeclaredSigmaKm: number | null = null,
    worstRecentRefinementKm: number | null = null,
    resolutionScaleKm: number | null = null,
  ): DocumentedResolutionAudit => ({
    status, intake, numericalHoldout, minimumDeclaredSigmaKm,
    worstRecentRefinementKm, resolutionScaleKm, maxFractionOfSigma,
    verifiedInstrumentIndependence: false,
    covarianceOrLikelihoodCalibrated: false,
    historicalHoldoutValidated: false,
    impactInference: 'NOT_SUPPORTED',
  });

  if (intake.status !== 'CONDITIONAL_UNWEIGHTED_INPUTS' ||
      !Number.isSafeInteger(fit.trainingCount) ||
      fit.trainingCount !== intake.trainingPositions.length)
    return report('BLOCKED_DOCUMENTATION');

  // The intake gate checked every sigma element for finiteness/positivity.
  // Min component sigma is a strict guard: a loose numerical tolerance
  // must not be portrayed as sufficient for a much sharper observation.
  const sigma = Math.min(...holdout.flatMap(datum => datum.sigmaKm ?? []));
  if (!Number.isFinite(sigma) || !(sigma > 0))
    return report('BLOCKED_DOCUMENTATION');

  const numerical = auditFutureOrbitScore(fit, intake.holdoutPositions, controls);
  if (numerical.status === 'EVENT_CONFLICT' ||
      numerical.status === 'MODEL_TERMINATED' ||
      numerical.status === 'NOT_RESOLVED' ||
      numerical.status === 'REFINEMENT_RANKING_CONFLICT')
    return report('BLOCKED_NUMERICAL_AUDIT', numerical, sigma);

  const adjacent = numerical.points.flatMap(point =>
    [point.baseline, point.fitted].flatMap(assessment =>
      assessment.levels.slice(-2).map(level => level.difference?.positionKm ?? NaN)));
  const worst = Math.max(...adjacent);
  const scale = Math.max(worst, controls.tolerance.positionKm);
  if (!Number.isFinite(worst) || !Number.isFinite(scale))
    return report('BLOCKED_NUMERICAL_AUDIT', numerical, sigma);
  if (scale > maxFractionOfSigma * sigma)
    return report('INSUFFICIENT_NUMERICAL_RESOLUTION', numerical, sigma, worst, scale);
  return report('CONDITIONAL_RESOLUTION_ONLY', numerical, sigma, worst, scale);
}
