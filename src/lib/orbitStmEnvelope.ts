/**
 * Independent finite-amplitude audit of the local 6D covariance linearization.
 * Uses 12 fully integrated sigma-point controls with the SAME documented
 * RK4/J2/optional-drag model as the G31 state-transition Jacobian.
 *
 * C179#1: the 528 TLE is secondary, not an original covariance.
 * C197#1: NASA/Goddard SSR 1963-11-15 p.8 gives only a decay day:
 * https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
 * Neither provenance chain establishes a NORAD 527/529 historical holdout.
 */
import { propagate, utcMilliseconds } from './orbitPhysics.ts';
import type { Dynamics, State, Vec3 } from './orbitPhysics.ts';
import type { InertialComparisonState } from './orbitFrameKinematics.ts';
import type { CartesianCovariance6, FrameCovarianceAudit } from './orbitFrameCovariance.ts';
import { auditCartesianStateTransition } from './orbitStateTransition.ts';
import type { StmResolutionContract } from './orbitStateTransition.ts';

export interface StmEnvelopeContract {
  /** Explicit sigma radius, in units of the admitted 6x6 covariance. */
  readonly sigmaMultiplier: number;
  /** Maximum absolute nonlinear remainder norm in position, km. */
  readonly maxPositionRemainderKm: number;
  /** Maximum absolute nonlinear remainder norm in velocity, km/s. */
  readonly maxVelocityRemainderKmS: number;
}
export interface StmEnvelopeAudit {
  readonly status: 'BASELINE_NOT_ADMITTED' | 'INVALID_ENVELOPE_CONTRACT' |
    'PROPAGATION_UNRESOLVED' | 'STM_UNRESOLVED' | 'LINEARIZATION_UNRESOLVED' |
    'SYNTHETIC_DIAGNOSTIC_ONLY' | 'CONDITIONAL_DIAGNOSTIC_ONLY';
  readonly positionRemainderKm: number | null;
  readonly velocityRemainderKmS: number | null;
  readonly controlsEvaluated: number;
  readonly frameSystematicsIncluded: false;
  readonly historicalHoldoutValidated: false;
  readonly impactInference: 'NOT_SUPPORTED';
}
const vector = (s: State): number[] => [...s.rKm, ...s.vKmS];
const norm = (v: readonly number[]): number => Math.hypot(...v);
const diagnostic = (status: string): status is 'SYNTHETIC_DIAGNOSTIC_ONLY' |
  'CONDITIONAL_DIAGNOSTIC_ONLY' =>
  status === 'SYNTHETIC_DIAGNOSTIC_ONLY' || status === 'CONDITIONAL_DIAGNOSTIC_ONLY';

/**
 * Form actual covariance sigma directions, not just marginal +/- standard
 * deviations: the off-diagonal position/velocity terms remain represented.
 * Cholesky is done in dimensionless correlation space before restoring units.
 */
function sigmaDirections(c: CartesianCovariance6): number[][] | null {
  if (!Array.isArray(c) || c.length !== 6 ||
      c.some(row => !Array.isArray(row) || row.length !== 6 ||
        !row.every(Number.isFinite))) return null;
  const sigma = c.map((row, i) => Math.sqrt(row[i]));
  if (!sigma.every(x => Number.isFinite(x) && x > 0)) return null;
  const corr = c.map((row, i) => row.map((x, j) => x / sigma[i] / sigma[j]));
  if (corr.some((row, i) => row.some((x, j) =>
      !Number.isFinite(x) || Math.abs(x - corr[j][i]) > 1e-9 ||
      (i === j && Math.abs(x - 1) > 1e-9)))) return null;
  const l = Array.from({length: 6}, () => Array(6).fill(0) as number[]);
  for (let i = 0; i < 6; i++) for (let j = 0; j <= i; j++) {
    let value = corr[i][j];
    for (let k = 0; k < j; k++) value -= l[i][k] * l[j][k];
    if (i === j) {
      if (!(value > 1e-10) || !Number.isFinite(value)) return null;
      l[i][j] = Math.sqrt(value);
    } else {
      l[i][j] = value / l[j][j];
      if (!Number.isFinite(l[i][j])) return null;
    }
  }
  return Array.from({length: 6}, (_, j) =>
    Array.from({length: 6}, (_, i) => l[i][j] * sigma[i]));
}

function integrate(s: State, durationS: number, stepS: number,
  thresholdKm: number, dynamics: Dynamics): number[] | null {
  try {
    const result = propagate(s, durationS, stepS, thresholdKm, dynamics);
    if (result.event !== 'elapsed') return null;
    const v = vector(result.state);
    return v.every(Number.isFinite) ? v : null;
  } catch { return null; }
}

/**
 * G32: before interpreting a first-order covariance pushforward, check the
 * six correlated Cholesky directions with both signs at finite amplitude.
 * A tiny Jacobian finite-difference drift (G31) does NOT guarantee that the
 * admitted covariance is small enough for a linear approximation.
 *
 * These directions are deterministic diagnostics, not a probabilistic
 * confidence region; 12 successful controls never establish a global bound.
 */
export function auditStmNonlinearEnvelope(
  initial: InertialComparisonState, admitted: FrameCovarianceAudit,
  durationS: number, stepS: number, thresholdKm: number,
  dynamics: Dynamics, resolution: StmResolutionContract, contract: StmEnvelopeContract,
): StmEnvelopeAudit {
  const report = (status: StmEnvelopeAudit['status'], dr: number | null = null,
    dv: number | null = null, n = 0): StmEnvelopeAudit => ({
    status, positionRemainderKm: dr, velocityRemainderKmS: dv,
    controlsEvaluated: n, frameSystematicsIncluded: false,
    historicalHoldoutValidated: false, impactInference: 'NOT_SUPPORTED',
  });
  if (![durationS,stepS,thresholdKm,contract?.sigmaMultiplier,
    contract?.maxPositionRemainderKm,contract?.maxVelocityRemainderKmS]
    .every(Number.isFinite) || durationS < 0 || stepS <= 0 || thresholdKm < 0 ||
    contract.sigmaMultiplier <= 0 ||
    contract.maxPositionRemainderKm <= 0 ||
    contract.maxVelocityRemainderKmS <= 0)
    return report('INVALID_ENVELOPE_CONTRACT');
  if (!initial || initial.frame !== 'ECI_DECLARED' ||
    !admitted || !diagnostic(admitted.status) ||
    !admitted.transformedCovariance || !initial.state ||
    vector(initial.state).length !== 6 ||
    !vector(initial.state).every(Number.isFinite) ||
    !Number.isFinite(initial.state.tS))
    return report('BASELINE_NOT_ADMITTED');
  try {
    if (!admitted.epochUtc ||
      utcMilliseconds(initial.epochUtc) !== utcMilliseconds(admitted.epochUtc))
      return report('BASELINE_NOT_ADMITTED');
  } catch { return report('BASELINE_NOT_ADMITTED'); }
  // Recompute G31 with identical force, epoch, step and event contract. Never
  // accept a caller-provided STM computed for different dynamics or duration.
  const stm = auditCartesianStateTransition(initial, admitted, durationS, stepS,
    thresholdKm, dynamics, resolution);
  if (!diagnostic(stm.status) || stm.status !== admitted.status ||
      !stm.transitionMatrix || !stm.propagatedCovariance)
    return report('STM_UNRESOLVED');
  const f = stm.transitionMatrix;
  if (f.length !== 6 || f.some(row => row.length !== 6 || !row.every(Number.isFinite)))
    return report('BASELINE_NOT_ADMITTED');
  const cols = sigmaDirections(admitted.transformedCovariance);
  if (!cols) return report('BASELINE_NOT_ADMITTED');
  const base = integrate(initial.state, durationS, stepS, thresholdKm, dynamics);
  if (!base) return report('PROPAGATION_UNRESOLVED');
  const start = vector(initial.state);
  let maxDr = 0, maxDv = 0, count = 0;
  for (const col of cols) {
    for (const sign of [-1,1]) {
      const delta = col.map(x => x * sign * contract.sigmaMultiplier);
      const shifted = start.map((x,i) => x + delta[i]);
      if (!shifted.every(Number.isFinite) ||
        shifted.some((x,i) => x === start[i] && delta[i] !== 0))
        return report('LINEARIZATION_UNRESOLVED',maxDr,maxDv,count);
      const state: State = {tS:initial.state.tS,
        rKm: shifted.slice(0,3) as unknown as Vec3,
        vKmS: shifted.slice(3,6) as unknown as Vec3};
      const actual = integrate(state,durationS,stepS,thresholdKm,dynamics);
      if (!actual) return report('PROPAGATION_UNRESOLVED',maxDr,maxDv,count);
      const remainder = actual.map((x,i) => x-base[i]-
        f[i].reduce((sum,a,j) => sum+a*delta[j],0));
      const dr = norm(remainder.slice(0,3)), dv = norm(remainder.slice(3,6));
      if (!Number.isFinite(dr) || !Number.isFinite(dv))
        return report('LINEARIZATION_UNRESOLVED',maxDr,maxDv,count);
      maxDr = Math.max(maxDr,dr); maxDv = Math.max(maxDv,dv);
      count++;
    }
  }
  if (maxDr > contract.maxPositionRemainderKm ||
    maxDv > contract.maxVelocityRemainderKmS)
    return report('LINEARIZATION_UNRESOLVED',maxDr,maxDv,count);
  return report(stm.status,maxDr,maxDv,count);
}
