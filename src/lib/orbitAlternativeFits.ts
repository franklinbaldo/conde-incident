/**
 * Evaluate mutually exclusive orbital provenance scenarios without mixing their
 * velocity bounds, changing the fitting model, or selecting a historical winner
 * using withheld observations. All boxes remain ASSUMED until source and Lean
 * custody have been independently audited.
 *
 * This is a physics-side consumer of already-separated conditional branches,
 * NOT the exact-rational alternative-domain solver proposed in PR #43.
 * The "baseline" inside fitConditionalVelocity is unfitted Cartesian r/v,
 * NEVER SGP4. No geographic exclusion or impact inference is supported.
 */
import { fitConditionalVelocity } from './orbitConditionalFit.ts';
import { utcMilliseconds, validateTimedPositions } from './orbitPhysics.ts';
import type { ConditionalOrbitScenario } from './orbitAdmissibility.ts';
import type { ConditionalFitControls, ConditionalFitResult } from './orbitConditionalFit.ts';
import type { Dynamics, TimedOrbitPosition } from './orbitPhysics.ts';

export interface AlternativeOrbitPremise {
  /** Stable identity for ONE alternative documentary/Lean premise branch. */
  readonly alternativeId: string;
  /** Documentary ancestry, NOT a declaration of independent measurements. */
  readonly sourceLineage: string;
  /** Independent Cartesian r/v candidate and conditional velocity intervals. */
  readonly scenario: ConditionalOrbitScenario;
}

export interface AlternativeOrbitEvaluation {
  readonly alternativeId: string;
  readonly sourceLineage: string;
  readonly calibration: ConditionalFitResult;
}

export interface AlternativeOrbitAssessment {
  readonly evaluations: readonly AlternativeOrbitEvaluation[];
  /** Holdout values are reported per branch, never used to elect a branch. */
  readonly selectedAlternativeId: null;
  readonly branchSetExhaustive: false;
  readonly independentObservationsVerified: false;
  readonly leanHistoricalProof: 'NOT_RUN';
  readonly sgp4Baseline: 'NOT_RUN';
  readonly historicLocation: 'INDETERMINATE';
  readonly groundImpact: 'NOT_SUPPORTED';
}

/**
 * One shared, predeclared training/holdout split is applied to ALL branches.
 * Alternative premises are NEVER intersected into one artificial empty box.
 * Each physical propagation starts from its branch's own fixed r and bounded v.
 * Even if only one branch produces a stable fit, the branch set is not proved
 * exhaustive and the result cannot determine where 1963-003B reentered.
 */
export function evaluateAlternativeOrbitFits(
  alternatives: readonly AlternativeOrbitPremise[],
  cutoffEpochUtc: string,
  training: readonly TimedOrbitPosition[],
  withheld: readonly TimedOrbitPosition[],
  controls: ConditionalFitControls,
  dynamics: Dynamics = {},
): AlternativeOrbitAssessment {
  if (!Array.isArray(alternatives) || alternatives.length === 0 || alternatives.length > 12)
    throw new RangeError('Require 1–12 distinct conditional premise branches');
  const first = alternatives[0].scenario;
  if (!first || (first.objectNorad !== 527 && first.objectNorad !== 529) ||
      typeof first.inertialFrame !== 'string' || !first.inertialFrame.trim())
    throw new RangeError('Need a common 527/529 target and explicit inertial frame');
  const initialMs = utcMilliseconds(first.epochUtc);
  const cutoffMs = utcMilliseconds(cutoffEpochUtc);
  if (cutoffMs <= initialMs || training.length < 2 || withheld.length < 1)
    throw new RangeError('Require chronological cutoff, training and future holdout');
  validateTimedPositions(training, first.objectNorad, first.inertialFrame,
    initialMs, cutoffMs, 'training');
  validateTimedPositions(withheld, first.objectNorad, first.inertialFrame,
    initialMs, cutoffMs, 'holdout');

  const ids = new Set<string>();
  for (const alternative of alternatives) {
    if (typeof alternative.alternativeId !== 'string' ||
        !/^[A-Za-z][A-Za-z0-9._:-]{0,79}$/.test(alternative.alternativeId) ||
        ids.has(alternative.alternativeId) ||
        typeof alternative.sourceLineage !== 'string' ||
        !alternative.sourceLineage.trim() || !alternative.scenario ||
        alternative.scenario.objectNorad !== first.objectNorad ||
        alternative.scenario.epochUtc !== first.epochUtc ||
        alternative.scenario.inertialFrame !== first.inertialFrame ||
        alternative.scenario.initial.tS !== 0)
      throw new RangeError('Duplicate/invalid alternative, missing lineage or mixed target/epoch/frame');
    ids.add(alternative.alternativeId);
  }

  const evaluations = alternatives.map(alternative => ({
    alternativeId: alternative.alternativeId,
    sourceLineage: alternative.sourceLineage,
    calibration: fitConditionalVelocity(alternative.scenario, cutoffEpochUtc,
      training, withheld, controls, dynamics),
  }));
  return {
    evaluations, selectedAlternativeId: null, branchSetExhaustive: false,
    independentObservationsVerified: false, leanHistoricalProof: 'NOT_RUN',
    sgp4Baseline: 'NOT_RUN', historicLocation: 'INDETERMINATE',
    groundImpact: 'NOT_SUPPORTED',
  };
}
