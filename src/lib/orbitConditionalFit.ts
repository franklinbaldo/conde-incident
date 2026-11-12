/**
 * Conditional constrained inverse calibration for the coupled osculating
 * r/v model. Accepts velocity intersections whose premises and source
 * lineage are declared, but NEVER treats those declarations as a checked
 * Lean proof or authenticated historical observations.
 *
 * NOT an SGP4/TLE conversion. No atmosphere defaults, impact inference,
 * posterior probability, or automatic determination of historical sites.
 */
import {
  utcMilliseconds, validateTimedPositions, positionResidualRmsKm,
} from './orbitPhysics.ts';
import { auditVelocityDomain } from './orbitAdmissibility.ts';
import { auditFutureOrbitScore, auditTrainingOrbitScore } from './orbitHoldoutAudit.ts';
import type {
  Dynamics, PreCutoffOrbitFit, State, TimedOrbitPosition, Vec3,
} from './orbitPhysics.ts';
import type { ConditionalOrbitScenario, DomainAudit, VelocityAxis } from './orbitAdmissibility.ts';
import type { ConvergenceControls } from './orbitConvergence.ts';
import type { AuditedHoldoutResult } from './orbitHoldoutAudit.ts';

const AXES: readonly VelocityAxis[] = ['vx', 'vy', 'vz'];

export interface ConditionalFitControls {
  readonly stepS: number;
  readonly terminationAltitudeKm: number;
  readonly gridStepKmS: number;
  /** Finite budget; no unlimited local hill climb. */
  readonly rounds: number;
  readonly convergence: ConvergenceControls;
}
export interface ConditionalFitResult {
  readonly status:
    | 'NOT_RUN_EMPTY'
    | 'NOT_RUN_UNBOUNDED'
    | 'NO_FINITE_TRAINING_SCORE'
    | 'TRAINING_GAIN_UNCONFIRMED'
    | 'CALIBRATED_CONDITIONALLY';
  readonly domain: DomainAudit;
  readonly fit: PreCutoffOrbitFit | null;
  /** Independently refined IN-SAMPLE score; never substitute for future holdout. */
  readonly trainingAudit: AuditedHoldoutResult | null;
  readonly holdout: AuditedHoldoutResult | null;
  /** The original input velocity was outside declared bounds. */
  readonly baselineProjectedIntoDomain: boolean;
  readonly evaluations: number;
  readonly solver: 'BOUNDED_COORDINATE_GRID';
  readonly proofVerification: 'NOT_RUN';
  readonly historicalHoldout: 'NOT_VERIFIED';
  readonly independentObservation: 'NOT_VERIFIED';
  readonly geographicInference: 'NOT_SUPPORTED';
}

const clamp = (value: number, lo: number, hi: number): number =>
  Math.min(hi, Math.max(lo, value));

/**
 * No parameter is silently invented. EMPTY and PARTIAL domains halt before
 * optimization. A bounded domain supplies a finite box, not a probability
 * distribution, unique orbit solution, or certified enclosure.
 *
 * All fit evaluations and holdout predictions use the coupled integrator.
 * A FUTURE observation is never supplied to the optimizer. The independent
 * numerical audit can veto a fitted model's apparent holdout advantage.
 */
export function fitConditionalVelocity(
  scenario: ConditionalOrbitScenario,
  cutoffEpochUtc: string,
  training: readonly TimedOrbitPosition[],
  future: readonly TimedOrbitPosition[],
  controls: ConditionalFitControls,
  dynamics: Dynamics = {},
): ConditionalFitResult {
  const domain = auditVelocityDomain(scenario);
  if (scenario.objectNorad === 528)
    throw new RangeError('Blind holdout protocol requires 527 or 529, not decayed 528');
  if (!Number.isFinite(controls.stepS) || controls.stepS <= 0 ||
      !Number.isFinite(controls.terminationAltitudeKm) || controls.terminationAltitudeKm < 0 ||
      !Number.isFinite(controls.gridStepKmS) || controls.gridStepKmS <= 0 ||
      !Number.isInteger(controls.rounds) || controls.rounds < 1 || controls.rounds > 20)
    throw new RangeError('Invalid finite step, threshold, velocity grid or iteration budget');
  const header = {
    domain, solver: 'BOUNDED_COORDINATE_GRID' as const,
    proofVerification: 'NOT_RUN' as const, historicalHoldout: 'NOT_VERIFIED' as const,
    independentObservation: 'NOT_VERIFIED' as const,
    geographicInference: 'NOT_SUPPORTED' as const,
  };
  if (domain.status !== 'BOUNDED')
    return { ...header, status: domain.status === 'EMPTY' ? 'NOT_RUN_EMPTY' as const :
      'NOT_RUN_UNBOUNDED' as const, fit: null, trainingAudit: null, holdout: null,
      baselineProjectedIntoDomain: false, evaluations: 0 };

  if (scenario.initial.tS !== 0)
    throw new RangeError('The osculating initial state must use tS=0 at declared UTC epoch');
  const epochMs = utcMilliseconds(scenario.epochUtc);
  const cutoffMs = utcMilliseconds(cutoffEpochUtc);
  if (cutoffMs <= epochMs)
    throw new RangeError('Cutoff must be later than initial UTC epoch');
  if (training.length < 2 || future.length < 1)
    throw new RangeError('Require at least two pre-cutoff and one withheld position');
  validateTimedPositions(training, scenario.objectNorad, scenario.inertialFrame,
    epochMs, cutoffMs, 'training');
  validateTimedPositions(future, scenario.objectNorad, scenario.inertialFrame,
    epochMs, cutoffMs, 'holdout');

  const intervals = AXES.map(axis => domain.intervals[axis]!);
  const projected = scenario.initial.vKmS.map((x, i) =>
    clamp(x, intervals[i][0], intervals[i][1])) as [number, number, number];
  const baselineProjectedIntoDomain = projected.some((x, i) =>
    x !== scenario.initial.vKmS[i]);
  const baselineState: State = { ...scenario.initial, vKmS: projected };
  let evaluations = 0;
  const evaluate = (vKmS: Vec3): number => {
    evaluations++;
    return positionResidualRmsKm(
      { ...scenario.initial, vKmS }, training, controls.stepS,
      controls.terminationAltitudeKm, dynamics);
  };
  let best = evaluate(projected);
  if (!Number.isFinite(best))
    return { ...header, status: 'NO_FINITE_TRAINING_SCORE', fit: null,
      trainingAudit: null, holdout: null, baselineProjectedIntoDomain, evaluations };

  let velocity: Vec3 = projected;
  let delta = controls.gridStepKmS;
  for (let round = 0; round < controls.rounds; round++) {
    for (let axis = 0; axis < 3; axis++) {
      const [lo, hi] = intervals[axis];
      // Test the faces, too: the optimum may lie exactly at a conditional
      // bound even if local +/-delta proposals never reach it.
      const candidates = new Set([lo, hi, clamp(velocity[axis] - delta, lo, hi),
        clamp(velocity[axis] + delta, lo, hi)]);
      candidates.delete(velocity[axis]);
      for (const value of candidates) {
        const v = [...velocity] as [number, number, number];
        v[axis] = value;
        const rms = evaluate(v);
        if (rms + 1e-12 < best) {
          best = rms;
          velocity = v;
        }
      }
    }
    delta /= 2;
  }
  const fittedState: State = { ...scenario.initial, vKmS: velocity };
  const fit: PreCutoffOrbitFit = {
    objectNorad: scenario.objectNorad, initialEpochUtc: scenario.epochUtc,
    cutoffEpochUtc, inertialFrame: scenario.inertialFrame,
    initialState: baselineState, fittedState,
    trainingBaselineRmsKm: positionResidualRmsKm(baselineState, training,
      controls.stepS, controls.terminationAltitudeKm, dynamics),
    trainingFittedRmsKm: best, evaluations, trainingCount: training.length,
    stepS: controls.stepS, terminationAltitudeKm: controls.terminationAltitudeKm,
    dynamics,
  };
  // Crucial numerical falsification: the optimizer ranks a coarse RK4
  // training score. A separate step-halving audit must corroborate that gain.
  // Any event conflict, nonconvergence, near tie, or reversed winner blocks
  // CALIBRATED_CONDITIONALLY, without discarding the fitted candidate.
  const trainingAudit = auditTrainingOrbitScore(fit, training, controls.convergence);
  const holdout = auditFutureOrbitScore(fit, future, controls.convergence);
  return { ...header,
    status: trainingAudit.status === 'APPARENT_FITTED_BETTER'
      ? 'CALIBRATED_CONDITIONALLY' : 'TRAINING_GAIN_UNCONFIRMED',
    fit, trainingAudit, holdout, baselineProjectedIntoDomain, evaluations };
}
