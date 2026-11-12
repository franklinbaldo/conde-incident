/**
 * Independent step-halving for each member of a seeded velocity-sensitivity
 * ensemble. NOT a posterior, a 1963 observation, or an SGP4/TLE propagation.
 *
 * Source lineage: NASA/Goddard SSR 15 Nov 1963, printed p. 8, C197#1
 * https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
 * gives 8 Nov as a decay DAY, not a terminal epoch, site or covariance.
 * C179/C180 are secondary element mirrors, not original Cartesian holdouts.
 */
import { NumericalIntegrationBreakdown, seededUniform } from './orbitPhysics.ts';
import { assessNumericalConvergence } from './orbitConvergence.ts';
import type { State, Vec3, Dynamics } from './orbitPhysics.ts';
import type { ConvergenceAssessment, ConvergenceControls } from './orbitConvergence.ts';

export interface EnsembleRefinementMember {
  readonly index: number;
  /** Cartesian velocity perturbation, km/s. The same draw is used at every step. */
  readonly deltaVKmS: Vec3;
  readonly convergence: ConvergenceAssessment | null;
  readonly numericalBreakdown: boolean;
}

export type EnsembleRefinementStatus =
  | 'STABLE_ELAPSED_ONLY'
  | 'TERMINATION_PRESENT'
  | 'EVENT_CONFLICT'
  | 'NOT_RESOLVED';

export interface EnsembleRefinementAudit {
  readonly status: EnsembleRefinementStatus;
  readonly seed: number;
  readonly members: readonly EnsembleRefinementMember[];
  readonly worstRecentPositionDifferenceKm: number | null;
  readonly worstRecentVelocityDifferenceKmS: number | null;
  readonly worstRecentEpochDifferenceS: number | null;
  readonly samplingContract: 'SEEDED_UNIFORM_CARTESIAN_VELOCITY_CUBE';
  readonly distributionCalibrated: false;
  readonly historicalHoldoutValidated: false;
  readonly likelihoodComputed: false;
  readonly impactInference: 'NOT_SUPPORTED';
}

/**
 * Sample each velocity ONCE with the existing xorshift32 sequence and
 * reintegrate full r/v at h, h/2, ... for that SAME state. Rerolling at
 * each refinement would confound sampling spread with integration error.
 *
 * A single unresolved member blocks an ensemble-wide stability claim. A
 * consistent numerical threshold crossing is still not an observed reentry,
 * much less an impact. No fraction of members is a probability.
 */
export function auditSeededEnsembleRefinement(
  initial: State, seed: number, count: number, velocityPerturbationKmS: number,
  durationS: number, stepS: number, terminationAltitudeKm: number,
  controls: ConvergenceControls, dynamics: Dynamics = {},
): EnsembleRefinementAudit {
  if (!Number.isSafeInteger(count) || count < 1 || count > 128 ||
      !Number.isFinite(velocityPerturbationKmS) || velocityPerturbationKmS < 0)
    throw new RangeError('Require 1–128 members and finite nonnegative velocity spread');
  // The shared physical kernel validates duration, threshold and step limits.
  // Validate the seed via the same generator used by propagateEnsemble.
  const rng = seededUniform(seed);
  const members: EnsembleRefinementMember[] = [];
  for (let index = 0; index < count; index++) {
    const deltaVKmS: Vec3 = [
      (2 * rng() - 1) * velocityPerturbationKmS,
      (2 * rng() - 1) * velocityPerturbationKmS,
      (2 * rng() - 1) * velocityPerturbationKmS,
    ];
    const state: State = {
      ...initial,
      vKmS: [
        initial.vKmS[0] + deltaVKmS[0],
        initial.vKmS[1] + deltaVKmS[1],
        initial.vKmS[2] + deltaVKmS[2],
      ],
    };
    try {
      members.push({
        index, deltaVKmS, numericalBreakdown: false,
        convergence: assessNumericalConvergence(
          state, durationS, stepS, terminationAltitudeKm, controls, dynamics),
      });
    } catch (error) {
      // Preserve representability failure rather than silently discarding
      // inconvenient samples or treating them as physical exclusions.
      if (!(error instanceof NumericalIntegrationBreakdown)) throw error;
      members.push({ index, deltaVKmS, numericalBreakdown: true, convergence: null });
    }
  }
  const differences = members.flatMap(member =>
    member.convergence?.levels.slice(-2).map(level => level.difference!) ?? []);
  const worst = (key: 'positionKm' | 'velocityKmS' | 'epochS'): number | null => {
    if (!differences.length || members.some(member => member.numericalBreakdown))
      return null;
    const value = Math.max(...differences.map(difference => difference[key]));
    return Number.isFinite(value) ? value : null;
  };
  const eventConflict = members.some(member =>
    member.convergence?.status === 'EVENT_CONFLICT');
  const notResolved = members.some(member => member.numericalBreakdown ||
    member.convergence?.status === 'NOT_RESOLVED');
  const terminated = members.some(member =>
    member.convergence?.finest.event === 'reentry-threshold');
  const status: EnsembleRefinementStatus =
    eventConflict ? 'EVENT_CONFLICT' :
    notResolved ? 'NOT_RESOLVED' :
    terminated ? 'TERMINATION_PRESENT' : 'STABLE_ELAPSED_ONLY';
  return {
    status, seed, members,
    worstRecentPositionDifferenceKm: worst('positionKm'),
    worstRecentVelocityDifferenceKmS: worst('velocityKmS'),
    worstRecentEpochDifferenceS: worst('epochS'),
    samplingContract: 'SEEDED_UNIFORM_CARTESIAN_VELOCITY_CUBE',
    distributionCalibrated: false,
    historicalHoldoutValidated: false,
    likelihoodComputed: false,
    impactInference: 'NOT_SUPPORTED',
  };
}
