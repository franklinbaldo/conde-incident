/**
 * Finite-difference state-transition matrix (STM) for the same Cartesian
 * osculating RK4 dynamics used by orbitPhysics.ts. Its frame is ECI_DECLARED;
 * it does not turn a secondary TEME TLE into an original measurement.
 *
 * C179#1: secondary 528 TLE, no instrumental covariance.
 * C197#1: NASA/Goddard SSR 15 Nov 1963 p.8 records only a decay day:
 * https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
 * No historical NORAD 527/529 holdout or EOP calibration is claimed here.
 */
import { propagate, utcMilliseconds } from './orbitPhysics.ts';
import type { State, Dynamics, Vec3 } from './orbitPhysics.ts';
import type { InertialComparisonState } from './orbitFrameKinematics.ts';
import type { FrameCovarianceAudit, CartesianCovariance6 } from './orbitFrameCovariance.ts';

export interface StmResolutionContract {
  /** Finite-difference perturbations of each initial Cartesian component. */
  readonly positionPerturbationKm: number;
  readonly velocityPerturbationKmS: number;
  /** Max absolute component drift in a dimensionless, unit-scaled STM. */
  readonly maxScaledJacobianDrift: number;
  /** Independent RK4 step-halving limits for unperturbed predicted state. */
  readonly maxStateDifferenceKm: number;
  readonly maxVelocityDifferenceKmS: number;
}

export interface CartesianStmAudit {
  readonly status: 'INITIAL_COVARIANCE_UNAVAILABLE' | 'EPOCH_OR_FRAME_MISMATCH' |
    'INVALID_RESOLUTION_CONTRACT' | 'PROPAGATION_UNRESOLVED' |
    'NUMERICAL_UNRESOLVED' | 'SYNTHETIC_DIAGNOSTIC_ONLY' |
    'CONDITIONAL_DIAGNOSTIC_ONLY';
  readonly transitionMatrix: CartesianCovariance6 | null;
  readonly propagatedCovariance: CartesianCovariance6 | null;
  readonly jacobianTimeDrift: number | null;
  readonly jacobianPerturbationDrift: number | null;
  readonly stateDifferenceKm: number | null;
  readonly velocityDifferenceKmS: number | null;
  readonly frameSystematicsIncluded: false;
  readonly historicalHoldoutValidated: false;
  readonly impactInference: 'NOT_SUPPORTED';
}

const finiteState = (s: State): boolean => Number.isFinite(s.tS) &&
  [...s.rKm, ...s.vKmS].every(Number.isFinite) &&
  s.rKm.length === 3 && s.vKmS.length === 3;
const vector = (s: State): number[] => [...s.rKm, ...s.vKmS];
const norm3 = (x: readonly number[]): number => Math.hypot(...x);

function integrated(s: State, duration: number, step: number,
  threshold: number, dynamics: Dynamics): State | null {
  try {
    const result = propagate(s, duration, step, threshold, dynamics);
    return result.event === 'elapsed' && finiteState(result.state) ? result.state : null;
  } catch { return null; }
}

/** Central differences for all six initial coordinates, retaining full coupling. */
function finiteDifferenceMatrix(s: State, duration: number, step: number,
  threshold: number, dynamics: Dynamics, perturbations: readonly number[]): number[][] | null {
  const cols: number[][] = [];
  const start = vector(s);
  for (let j = 0; j < 6; j++) {
    const plus = start.slice(), minus = start.slice(), h = perturbations[j];
    plus[j] += h;
    minus[j] -= h;
    if (plus[j] === start[j] || minus[j] === start[j]) return null;
    const state = (v: number[]): State => ({
      rKm: v.slice(0, 3) as unknown as Vec3,
      vKmS: v.slice(3, 6) as unknown as Vec3, tS: s.tS,
    });
    const p = integrated(state(plus), duration, step, threshold, dynamics);
    const m = integrated(state(minus), duration, step, threshold, dynamics);
    if (!p || !m) return null;
    const vp = vector(p), vm = vector(m);
    cols.push(vp.map((x, i) => (x - vm[i]) / (2 * h)));
  }
  const f = Array.from({length: 6}, (_, i) =>
    Array.from({length: 6}, (_, j) => cols[j][i]));
  return f.every(row => row.every(Number.isFinite)) ? f : null;
}

function covariancePushforward(f: readonly (readonly number[])[],
  c: CartesianCovariance6): number[][] {
  return Array.from({length: 6}, (_, i) =>
    Array.from({length: 6}, (_, j) => {
      let sum = 0;
      for (let a = 0; a < 6; a++) for (let b = 0; b < 6; b++)
        sum += f[i][a] * c[a][b] * f[j][b];
      return sum;
    }));
}

/**
 * Compare separate errors rather than allowing perturbation-step and RK4-step
 * errors to cancel. Normalize each Jacobian component by the ratio of
 * explicitly dimensioned initial perturbations h[j]/h[i]; the numeric drift
 * threshold is dimensionless, not an arbitrary mix of km and km/s.
 */
export function auditCartesianStateTransition(
  initial: InertialComparisonState,
  admittedCovariance: FrameCovarianceAudit,
  durationS: number, stepS: number, terminationAltitudeKm: number,
  dynamics: Dynamics, resolution: StmResolutionContract,
): CartesianStmAudit {
  const result = (status: CartesianStmAudit['status'], f: number[][] | null = null,
    c: number[][] | null = null, time: number | null = null,
    perturb: number | null = null, dr: number | null = null,
    dv: number | null = null): CartesianStmAudit => ({
    status, transitionMatrix: f, propagatedCovariance: c,
    jacobianTimeDrift: time, jacobianPerturbationDrift: perturb,
    stateDifferenceKm: dr, velocityDifferenceKmS: dv,
    frameSystematicsIncluded: false, historicalHoldoutValidated: false,
    impactInference: 'NOT_SUPPORTED',
  });
  const admitted = admittedCovariance?.status === 'SYNTHETIC_DIAGNOSTIC_ONLY' ||
    admittedCovariance?.status === 'CONDITIONAL_DIAGNOSTIC_ONLY';
  if (!admitted || !admittedCovariance.transformedCovariance ||
      !admittedCovariance.epochUtc) return result('INITIAL_COVARIANCE_UNAVAILABLE');
  let t: number, cEpoch: number;
  try { t = utcMilliseconds(initial.epochUtc); cEpoch = utcMilliseconds(admittedCovariance.epochUtc); }
  catch { return result('EPOCH_OR_FRAME_MISMATCH'); }
  if (initial.frame !== 'ECI_DECLARED' || t !== cEpoch || !finiteState(initial.state))
    return result('EPOCH_OR_FRAME_MISMATCH');
  const params = [durationS, stepS, terminationAltitudeKm, resolution?.positionPerturbationKm,
    resolution?.velocityPerturbationKmS, resolution?.maxScaledJacobianDrift,
    resolution?.maxStateDifferenceKm, resolution?.maxVelocityDifferenceKmS];
  if (!params.every(Number.isFinite) || durationS < 0 || stepS <= 0 ||
      terminationAltitudeKm < 0 || params.slice(3).some(x => x <= 0))
    return result('INVALID_RESOLUTION_CONTRACT');
  const covariance = admittedCovariance.transformedCovariance;
  if (durationS === 0) {
    const identity = Array.from({length: 6}, (_, i) =>
      Array.from({length: 6}, (_, j) => i === j ? 1 : 0));
    return result(admittedCovariance.status, identity, covariance.map(row => [...row]), 0, 0, 0, 0);
  }
  const coarse = integrated(initial.state, durationS, stepS, terminationAltitudeKm, dynamics);
  const fine = integrated(initial.state, durationS, stepS / 2, terminationAltitudeKm, dynamics);
  if (!coarse || !fine) return result('PROPAGATION_UNRESOLVED');
  const dc = vector(coarse), df = vector(fine);
  const dr = norm3(dc.slice(0, 3).map((x, i) => x - df[i]));
  const dv = norm3(dc.slice(3, 6).map((x, i) => x - df[i + 3]));
  const h = [resolution.positionPerturbationKm, resolution.positionPerturbationKm,
    resolution.positionPerturbationKm, resolution.velocityPerturbationKmS,
    resolution.velocityPerturbationKmS, resolution.velocityPerturbationKmS];
  const f0 = finiteDifferenceMatrix(initial.state, durationS, stepS, terminationAltitudeKm, dynamics, h);
  const f1 = finiteDifferenceMatrix(initial.state, durationS, stepS / 2, terminationAltitudeKm, dynamics, h);
  const f2 = finiteDifferenceMatrix(initial.state, durationS, stepS / 2, terminationAltitudeKm,
    dynamics, h.map(x => x / 2));
  if (!f0 || !f1 || !f2) return result('PROPAGATION_UNRESOLVED');
  const drift = (a: number[][], b: number[][]): number =>
    Math.max(...a.flatMap((row, i) => row.map((v, j) =>
      Math.abs((v - b[i][j]) * h[j] / h[i]))));
  const timeDrift = drift(f0, f1), perturbDrift = drift(f1, f2);
  if (![dr, dv, timeDrift, perturbDrift].every(Number.isFinite) ||
      dr > resolution.maxStateDifferenceKm ||
      dv > resolution.maxVelocityDifferenceKmS ||
      timeDrift > resolution.maxScaledJacobianDrift ||
      perturbDrift > resolution.maxScaledJacobianDrift)
    return result('NUMERICAL_UNRESOLVED', null, null, timeDrift, perturbDrift, dr, dv);
  const pushed = covariancePushforward(f2, covariance);
  if (!pushed.every(row => row.every(Number.isFinite)))
    return result('NUMERICAL_UNRESOLVED', null, null, timeDrift, perturbDrift, dr, dv);
  return result(admittedCovariance.status, f2, pushed, timeDrift, perturbDrift, dr, dv);
}
