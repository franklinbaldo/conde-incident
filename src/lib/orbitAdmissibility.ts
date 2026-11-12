/**
 * Conditional velocity-domain bridge for a future, audited Lean handoff.
 *
 * This module DOES NOT execute Lean or authenticate any matrix occurrence.
 * Each source label denotes a premise, not a verified 1963 measurement.
 * Numeric intersection is exact for the supplied finite intervals; finite
 * sampling and RK4 convergence NEVER certify exhaustive orbital/geographic claims.
 */
import { sampleVelocityBox } from './orbitBoxSampling.ts';
import { assessNumericalConvergence } from './orbitConvergence.ts';
import type { State, Dynamics } from './orbitPhysics.ts';
import type { ConvergenceControls, ConvergenceAssessment } from './orbitConvergence.ts';

export type VelocityAxis = 'vx' | 'vy' | 'vz';
const AXES: readonly VelocityAxis[] = ['vx', 'vy', 'vz'];
export interface ConditionalVelocityBound {
  readonly axis: VelocityAxis;
  readonly lowerKmS: number;
  readonly upperKmS: number;
  /** Matrix ID WITH occurrence if the ID is duplicated. Synthetic tests say SYNTHETIC. */
  readonly evidenceOccurrence: string;
  /** Source or scenario origin; never claim independent observations from shared lineage. */
  readonly sourceLineage: string;
  /** Lean theorem/predicate identifier, or explicitly NOT_AVAILABLE. NOT proof validation. */
  readonly leanPredicate: string;
  readonly premiseStatus: 'SYNTHETIC' | 'CONDITIONAL';
  /** Epoch and frame MUST match the osculating Cartesian initial state. */
  readonly epochUtc: string;
  readonly inertialFrame: string;
}

export interface ConditionalOrbitScenario {
  readonly objectNorad: 527 | 528 | 529;
  readonly epochUtc: string;
  readonly inertialFrame: string;
  /** Fixed r and t; the admissible domain in this slice varies only v. */
  readonly initial: State;
  readonly bounds: readonly ConditionalVelocityBound[];
}
export type VelocityInterval = readonly [number, number];
export type VelocityIntervals = Readonly<Record<VelocityAxis, VelocityInterval | null>>;
export interface DomainAudit {
  readonly status: 'EMPTY' | 'PARTIAL' | 'BOUNDED';
  readonly intervals: VelocityIntervals;
  readonly stillFree: readonly VelocityAxis[];
  readonly sourceCount: number;
  /** No Lean checker, historical source validation or frame conversion here. */
  readonly proofVerification: 'NOT_RUN';
}
const validUtc = (value: string): boolean => {
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/.test(value)) return false;
  const ms = Date.parse(value);
  return Number.isFinite(ms) && new Date(ms).toISOString().slice(0, 19) === value.slice(0, 19);
};

/** Intersection of conditional velocity boxes in km/s, all at the SAME UTC epoch/frame. */
export function auditVelocityDomain(scenario: ConditionalOrbitScenario): DomainAudit {
  if (![527, 528, 529].includes(scenario.objectNorad) ||
      !validUtc(scenario.epochUtc) || !scenario.inertialFrame?.trim() ||
      !Number.isFinite(scenario.initial.tS) ||
      scenario.initial.rKm.length !== 3 || scenario.initial.vKmS.length !== 3 ||
      ![...scenario.initial.rKm, ...scenario.initial.vKmS].every(Number.isFinite)) {
    throw new RangeError('Invalid target, explicit UTC epoch, inertial frame or Cartesian state');
  }
  const intersections: Record<VelocityAxis, [number, number] | null> =
    { vx: null, vy: null, vz: null };
  if (!Array.isArray(scenario.bounds)) throw new RangeError('Expected an array of conditional bounds');
  let empty = false;
  for (const constraint of scenario.bounds) {
    if (!AXES.includes(constraint.axis) ||
        !Number.isFinite(constraint.lowerKmS) || !Number.isFinite(constraint.upperKmS) ||
        constraint.lowerKmS > constraint.upperKmS ||
        !constraint.evidenceOccurrence?.trim() || !constraint.sourceLineage?.trim() ||
        !constraint.leanPredicate?.trim() ||
        !['SYNTHETIC', 'CONDITIONAL'].includes(constraint.premiseStatus) ||
        constraint.epochUtc !== scenario.epochUtc ||
        constraint.inertialFrame !== scenario.inertialFrame) {
      throw new RangeError('Invalid provenance, bounds, units, reference frame or UTC epoch');
    }
    const previous = intersections[constraint.axis];
    const lower = Math.max(previous?.[0] ?? -Infinity, constraint.lowerKmS);
    const upper = Math.min(previous?.[1] ?? Infinity, constraint.upperKmS);
    if (lower > upper) empty = true;
    intersections[constraint.axis] = [lower, upper];
  }
  const stillFree = AXES.filter(axis => intersections[axis] === null);
  return {
    status: empty ? 'EMPTY' : stillFree.length ? 'PARTIAL' : 'BOUNDED',
    intervals: intersections, stillFree, sourceCount: scenario.bounds.length,
    proofVerification: 'NOT_RUN',
  };
}

export interface DomainRunControls {
  readonly seed: number;
  /** Interior draws in addition to midpoint and up to eight corners. Not a posterior. */
  readonly interiorDraws: number;
  readonly durationS: number;
  readonly stepS: number;
  readonly terminationAltitudeKm: number;
  readonly convergence: ConvergenceControls;
}
export interface ConditionalSample {
  readonly vKmS: readonly [number, number, number];
  readonly numerical: ConvergenceAssessment;
}
export interface DomainRun {
  readonly domain: DomainAudit;
  readonly status: 'NOT_RUN_EMPTY' | 'NOT_RUN_UNBOUNDED' | 'SAMPLED_CONDITIONALLY';
  readonly samples: readonly ConditionalSample[];
  readonly seed: number;
  readonly method: 'MIDPOINT_CORNERS_SEEDED_INTERIOR';
  readonly historicalHoldout: 'NOT_RUN';
  readonly proofVerification: 'NOT_RUN';
  readonly exhaustivePhysicalEnclosure: false;
  readonly geographicInference: 'NOT_SUPPORTED';
}

/**
 * Propagate only samples from a *bounded* assumed domain. Every sample runs
 * full coupled r/v numerical refinement, not SGP4 and not a position shortcut.
 * If the domain is empty/unbounded, DO NOT invent a witness or silently clamp it.
 */
export function runConditionalVelocityDomain(
  scenario: ConditionalOrbitScenario, controls: DomainRunControls,
  dynamics: Dynamics = {},
): DomainRun {
  const domain = auditVelocityDomain(scenario);
  if (!Number.isSafeInteger(controls.seed) || controls.seed < 1 || controls.seed > 0xffffffff ||
      !Number.isInteger(controls.interiorDraws) ||
      controls.interiorDraws < 0 || controls.interiorDraws > 100) {
    throw new RangeError('Require uint32 seed and 0–100 conditional interior draws');
  }
  const header = {
    domain, seed: controls.seed, method: 'MIDPOINT_CORNERS_SEEDED_INTERIOR' as const,
    historicalHoldout: 'NOT_RUN' as const, proofVerification: 'NOT_RUN' as const,
    exhaustivePhysicalEnclosure: false as const, geographicInference: 'NOT_SUPPORTED' as const,
  };
  if (domain.status !== 'BOUNDED') {
    return {
      ...header, status: domain.status === 'EMPTY' ? 'NOT_RUN_EMPTY' : 'NOT_RUN_UNBOUNDED',
      samples: [],
    };
  }
  const intervals = AXES.map(axis => domain.intervals[axis]!);
  // Samples are exact finite witnesses inside the declared Float64 box.
  // Convex interpolation handles opposite-sign extremes without overflow.
  const samples: ConditionalSample[] = [];
  for (const vKmS of sampleVelocityBox(intervals, controls.seed, controls.interiorDraws)) {
    const initial = { ...scenario.initial, vKmS };
    samples.push({
      vKmS,
      numerical: assessNumericalConvergence(initial, controls.durationS, controls.stepS,
        controls.terminationAltitudeKm, controls.convergence, dynamics),
    });
  }
  return { ...header, status: 'SAMPLED_CONDITIONALLY', samples };
}
