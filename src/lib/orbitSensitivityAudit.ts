/**
 * Conditional LOCAL sensitivity of Cartesian positions to the three initial
 * osculating velocity components, at predeclared training epochs only.
 *
 * A finite-difference rank is a property of the assumed model/probe/tolerance,
 * NOT a Lean theorem, empirical calibration, posterior, or a 1963 observation.
 * No holdout position enters this calculation. No SGP4/TEME is converted.
 */
import { auditVelocityDomain } from './orbitAdmissibility.ts';
import { sampleVelocityBox } from './orbitBoxSampling.ts';
import { pivotVelocityResponseRank } from './orbitVelocityRank.ts';
import { assessNumericalConvergence } from './orbitConvergence.ts';
import { NumericalIntegrationBreakdown, utcMilliseconds } from './orbitPhysics.ts';
import type { ConditionalOrbitScenario, VelocityAxis } from './orbitAdmissibility.ts';
import type { Dynamics, Vec3 } from './orbitPhysics.ts';
import type { ConvergenceControls } from './orbitConvergence.ts';

const AXES: readonly VelocityAxis[] = ['vx', 'vy', 'vz'];

export interface ScheduledTrainingEpoch {
  readonly objectNorad: 527 | 529;
  readonly epochUtc: string;
  readonly inertialFrame: string;
  /** An identifier of a traceable source/premise, not authenticity proof. */
  readonly evidenceOccurrence: string;
  readonly sourceLineage: string;
}
export interface SensitivityControls {
  readonly cutoffEpochUtc: string;
  readonly stepS: number;
  readonly terminationAltitudeKm: number;
  /** Maximum symmetric velocity perturbation on each side, km/s. */
  readonly probeKmS: number;
  /** Euclidean displacement of stacked positions required for pivot rank, km. */
  readonly minimumSignalKm: number;
  readonly convergence: ConvergenceControls;
}
export interface SensitivityAxis {
  readonly axis: VelocityAxis;
  readonly kind: 'FIXED_BY_DECLARED_DOMAIN' | 'PROBED';
  /** Actual two finite representable speeds in km/s; null for a singleton. */
  readonly velocitiesKmS: readonly [number, number] | null;
  readonly probeDisplacementKm: number;
  /** Orthogonalized displacement against earlier accepted columns, km. */
  readonly independentDisplacementKm: number;
  readonly entersNumericalBasis: boolean;
}
export interface SensitivityAudit {
  readonly status: 'ASSESSED_CONDITIONALLY' | 'NOT_RUN_EMPTY' |
    'NOT_RUN_UNBOUNDED' | 'NOT_RUN_PROBE_PRECISION' |
    'NOT_RUN_EVENT_CONFLICT' | 'NOT_RUN_NUMERICAL_CONVERGENCE' |
    'NOT_RUN_TERMINATED' | 'NOT_RUN_NUMERICAL_BREAKDOWN';
  readonly axes: readonly SensitivityAxis[];
  readonly localRankAtProbeAndThreshold: number | null;
  /** Dimension not resolved by this local probe. NOT a physical free volume. */
  readonly unresolvedLocalDirections: number | null;
  readonly fixedByPremise: readonly VelocityAxis[];
  readonly freeInPremise: readonly VelocityAxis[];
  readonly epochsUsedUtc: readonly string[];
  readonly cutoffEpochUtc: string;
  readonly proofVerification: 'NOT_RUN';
  readonly historicalHoldout: 'NOT_RUN';
  readonly observationAuthenticity: 'NOT_VERIFIED';
  readonly sensitivityIsLocal: true;
  readonly globalIdentifiability: 'NOT_ESTABLISHED';
  readonly geographicInference: 'NOT_SUPPORTED';
}

const minus = (a: Vec3, b: Vec3): Vec3 =>
  [a[0] - b[0], a[1] - b[1], a[2] - b[2]];

/**
 * Every free axis is perturbed while all others remain fixed at a finite box
 * midpoint. Rank is computed on the resulting position *displacements* (km)
 * by pivoted two-pass Gram-Schmidt with an explicit caller-chosen km threshold.
 * It is not a verified bound on singular values or a proof of observability.
 */
export function auditLocalVelocitySensitivity(
  scenario: ConditionalOrbitScenario,
  scheduledEpochs: readonly ScheduledTrainingEpoch[],
  controls: SensitivityControls,
  dynamics: Dynamics = {},
): SensitivityAudit {
  const domain = auditVelocityDomain(scenario);
  if (scenario.objectNorad !== 527 && scenario.objectNorad !== 529)
    throw new RangeError('Sensitivity is restricted to NORAD 527 or 529');
  const startMs = utcMilliseconds(scenario.epochUtc);
  const cutoffMs = utcMilliseconds(controls.cutoffEpochUtc);
  if (!(cutoffMs > startMs)) throw new RangeError('Training cutoff must follow initial UTC epoch');
  if (!Array.isArray(scheduledEpochs) || scheduledEpochs.length < 1 ||
      scheduledEpochs.length > 12)
    throw new RangeError('Require 1–12 predeclared training epochs');
  let previousMs = -Infinity;
  const elapsedS: number[] = [];
  for (const entry of scheduledEpochs) {
    const ms = utcMilliseconds(entry.epochUtc);
    if (entry.objectNorad !== scenario.objectNorad ||
        entry.inertialFrame !== scenario.inertialFrame ||
        !entry.evidenceOccurrence?.trim() || !entry.sourceLineage?.trim())
      throw new RangeError('Mixed object/frame or absent source lineage in sensitivity schedule');
    if (ms < startMs || ms >= cutoffMs || ms <= previousMs)
      throw new RangeError('Training epoch leakage, invalid order or duplicate UTC epoch');
    previousMs = ms;
    elapsedS.push((ms - startMs) / 1000);
  }
  const { probeKmS, minimumSignalKm, stepS, terminationAltitudeKm, convergence } = controls;
  if (!Number.isFinite(probeKmS) || probeKmS <= 0 ||
      !Number.isFinite(minimumSignalKm) || minimumSignalKm <= 0 ||
      !(minimumSignalKm > 2 * convergence.tolerance.positionKm) ||
      !Number.isFinite(stepS) || stepS <= 0 ||
      !Number.isFinite(terminationAltitudeKm) || terminationAltitudeKm < 0)
    throw new RangeError('Require positive finite probe, step, threshold and resolvable signal');
  const freeInPremise = AXES.filter(axis => {
    const x = domain.intervals[axis];
    return x !== null && x[0] !== x[1];
  });
  const fixedByPremise = AXES.filter(axis => {
    const x = domain.intervals[axis];
    return x !== null && x[0] === x[1];
  });
  const header = {
    cutoffEpochUtc: controls.cutoffEpochUtc,
    epochsUsedUtc: scheduledEpochs.map(e => e.epochUtc),
    proofVerification: 'NOT_RUN' as const,
    historicalHoldout: 'NOT_RUN' as const,
    observationAuthenticity: 'NOT_VERIFIED' as const,
    sensitivityIsLocal: true as const,
    globalIdentifiability: 'NOT_ESTABLISHED' as const,
    geographicInference: 'NOT_SUPPORTED' as const,
    fixedByPremise, freeInPremise,
  };
  const noScore = (status: SensitivityAudit['status'], axes: readonly SensitivityAxis[] = []):
    SensitivityAudit =>
    ({ ...header, status, axes, localRankAtProbeAndThreshold: null,
      unresolvedLocalDirections: null });
  if (domain.status !== 'BOUNDED')
    return noScore(domain.status === 'EMPTY' ? 'NOT_RUN_EMPTY' : 'NOT_RUN_UNBOUNDED');

  const ranges = AXES.map(axis => domain.intervals[axis]!);
  const midpoint = sampleVelocityBox(ranges, 1, 0)[0];
  const columns: number[][] = [];
  const axisPairs: Array<readonly [number, number] | null> = [];
  for (let axis = 0; axis < 3; axis++) {
    const [lo, hi] = ranges[axis];
    if (lo === hi) { axisPairs.push(null); columns.push([]); continue; }
    const left = Math.max(lo, midpoint[axis] - probeKmS);
    const right = Math.min(hi, midpoint[axis] + probeKmS);
    // A rational/Float64 box may be non-singleton while a requested probe
    // cannot resolve two distinct speeds near its chosen midpoint.
    if (!(left < right) || right - left <= Number.EPSILON * Math.max(1, Math.abs(midpoint[axis])))
      return noScore('NOT_RUN_PROBE_PRECISION');
    axisPairs.push([left, right]);
    const observations: number[][] = [[], []];
    for (const [side, speed] of [left, right].entries()) {
      const vKmS = [...midpoint] as [number, number, number];
      vKmS[axis] = speed;
      for (const durationS of elapsedS) {
        let assessment;
        try {
          assessment = assessNumericalConvergence(
            { ...scenario.initial, vKmS }, durationS, stepS,
            terminationAltitudeKm, convergence, dynamics);
        } catch (error) {
          if (error instanceof NumericalIntegrationBreakdown)
            return noScore('NOT_RUN_NUMERICAL_BREAKDOWN');
          throw error;
        }
        if (assessment.status === 'EVENT_CONFLICT')
          return noScore('NOT_RUN_EVENT_CONFLICT');
        if (assessment.status !== 'STABLE')
          return noScore('NOT_RUN_NUMERICAL_CONVERGENCE');
        if (assessment.finest.event !== 'elapsed')
          return noScore('NOT_RUN_TERMINATED');
        observations[side].push(...assessment.finest.state.rKm);
      }
    }
    columns.push(observations[1].map((v, i) => v - observations[0][i]));
  }
  // Pivot on the strongest remaining displacement, not an arbitrary
  // vx→vy→vz ordering. Almost parallel columns can give different ranks
  // with an unpivoted km-threshold Gram-Schmidt.
  const freeIndices = axisPairs.flatMap((pair, index) => pair === null ? [] : [index]);
  const rankResult = pivotVelocityResponseRank(
    freeIndices.map(index => columns[index]), minimumSignalKm);
  if (rankResult === null) return noScore('NOT_RUN_NUMERICAL_BREAKDOWN');
  const rankByAxis = new Map(freeIndices.map((index, j) =>
    [index, rankResult.columns[j]] as const));
  const axes: SensitivityAxis[] = AXES.map((axis, index) => {
    const pair = axisPairs[index];
    if (pair === null) return {
      axis, kind: 'FIXED_BY_DECLARED_DOMAIN' as const, velocitiesKmS: null,
      probeDisplacementKm: 0, independentDisplacementKm: 0,
      entersNumericalBasis: false,
    };
    const response = rankByAxis.get(index)!;
    return {
      axis, kind: 'PROBED' as const, velocitiesKmS: pair,
      probeDisplacementKm: response.rawNormKm,
      independentDisplacementKm: response.independentNormKm,
      entersNumericalBasis: response.entersBasis,
    };
  });
  return { ...header, status: 'ASSESSED_CONDITIONALLY', axes,
    localRankAtProbeAndThreshold: rankResult.rankAtThreshold,
    unresolvedLocalDirections: freeInPremise.length - rankResult.rankAtThreshold };
}
