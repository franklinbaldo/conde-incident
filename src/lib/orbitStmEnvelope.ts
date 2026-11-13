/**
 * Independent finite-amplitude audit of the local 6D covariance linearization.
 * Uses 72 fully integrated sigma-point controls with the SAME documented
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
  /** Separate maxima distinguish axial and cross-direction failures. */
  readonly axialPositionRemainderKm: number | null;
  readonly axialVelocityRemainderKmS: number | null;
  readonly mixedPositionRemainderKm: number | null;
  readonly mixedVelocityRemainderKmS: number | null;
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
  const sigma: number[] = c.map((row: readonly number[], i: number) => Math.sqrt(row[i]));
  if (!sigma.every(x => Number.isFinite(x) && x > 0)) return null;
  const corr: number[][] = c.map((row: readonly number[], i: number) =>
    row.map((x: number, j: number) => x / sigma[i] / sigma[j]));
  if (corr.some((row: number[], i: number) => row.some((x: number, j: number) =>
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
 * G33: use 12 axial +/- and 60 two-axis +/- combinations (6 choose 2 x 4).
 * Pair vectors are divided by sqrt(2), keeping the SAME Mahalanobis radius
 * as an axial displacement. Under x -> x_i*x_j, every axial control misses
 * the nonlinear term, while a mixed control detects it: a falsifiable blind
 * spot of G32, not a new historical observation.
 * 72 directions still DO NOT certify a whole ellipsoid or likelihood.
 */
export function correlatedSigmaControls(c: CartesianCovariance6,
  multiplier: number): readonly {kind: 'AXIAL' | 'MIXED'; delta: readonly number[]}[] | null {
  if (!Number.isFinite(multiplier) || multiplier <= 0) return null;
  const cols = sigmaDirections(c);
  if (!cols) return null;
  const controls: {kind: 'AXIAL' | 'MIXED'; delta: number[]}[] = [];
  for (const col of cols) for (const sign of [-1,1])
    controls.push({kind: 'AXIAL', delta: col.map(x => multiplier * sign * x)});
  for (let i = 0; i < 6; i++) for (let j = i+1; j < 6; j++)
    for (const a of [-1,1]) for (const b of [-1,1])
      controls.push({kind: 'MIXED', delta: cols[i].map((x,k) =>
        multiplier * (a*x + b*cols[j][k]) / Math.SQRT2)});
  return controls.every(control => control.delta.every(Number.isFinite)) ? controls : null;
}

/**
 * G33: test finite-amplitude off-axis cross couplings missed by G32.
 * Controls are deterministic probes, not a probabilistic confidence region.
 * G31 Jacobian convergence does not certify linearity at covariance scale.
 */
export function auditStmNonlinearEnvelope(
  initial: InertialComparisonState, admitted: FrameCovarianceAudit,
  durationS: number, stepS: number, thresholdKm: number,
  dynamics: Dynamics, resolution: StmResolutionContract, contract: StmEnvelopeContract,
): StmEnvelopeAudit {
  const report = (status: StmEnvelopeAudit['status'], dr: number | null = null,
    dv: number | null = null, n = 0,
    aDr: number | null = null, aDv: number | null = null,
    mDr: number | null = null, mDv: number | null = null): StmEnvelopeAudit => ({
    status, positionRemainderKm: dr, velocityRemainderKmS: dv,
    controlsEvaluated: n, axialPositionRemainderKm: aDr,
    axialVelocityRemainderKmS: aDv, mixedPositionRemainderKm: mDr,
    mixedVelocityRemainderKmS: mDv, frameSystematicsIncluded: false,
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
  const controls = correlatedSigmaControls(
    admitted.transformedCovariance, contract.sigmaMultiplier);
  if (!controls) return report('BASELINE_NOT_ADMITTED');
  // G31 returns the step-halved Jacobian; use that same integration
  // resolution for all finite-amplitude controls to avoid a mixed-step bias.
  const controlStepS = stepS / 2;
  const base = integrate(initial.state, durationS, controlStepS, thresholdKm, dynamics);
  if (!base) return report('PROPAGATION_UNRESOLVED');
  const start = vector(initial.state);
  let maxDr = 0, maxDv = 0, count = 0;
  let aDr = 0, aDv = 0, mDr = 0, mDv = 0;
  const fail = (status: StmEnvelopeAudit['status']): StmEnvelopeAudit =>
    report(status,maxDr,maxDv,count,
      count ? aDr : null,count ? aDv : null,
      count > 12 ? mDr : null,count > 12 ? mDv : null);
  for (const control of controls) {
    const delta = control.delta;
    const shifted = start.map((x,i) => x + delta[i]);
    if (!shifted.every(Number.isFinite) ||
      shifted.some((x,i) => x === start[i] && delta[i] !== 0))
      return fail('LINEARIZATION_UNRESOLVED');
    const state: State = {tS:initial.state.tS,
      rKm: shifted.slice(0,3) as unknown as Vec3,
      vKmS: shifted.slice(3,6) as unknown as Vec3};
    const actual = integrate(state,durationS,controlStepS,thresholdKm,dynamics);
    if (!actual) return fail('PROPAGATION_UNRESOLVED');
    const remainder = actual.map((x,i) => x-base[i]-
      f[i].reduce((sum,a,j) => sum+a*delta[j],0));
    const dr = norm(remainder.slice(0,3)), dv = norm(remainder.slice(3,6));
    if (!Number.isFinite(dr) || !Number.isFinite(dv))
      return fail('LINEARIZATION_UNRESOLVED');
    maxDr = Math.max(maxDr,dr); maxDv = Math.max(maxDv,dv);
    if (control.kind === 'AXIAL') {
      aDr = Math.max(aDr,dr); aDv = Math.max(aDv,dv);
    } else {
      mDr = Math.max(mDr,dr); mDv = Math.max(mDv,dv);
    }
    count++;
  }
  if (maxDr > contract.maxPositionRemainderKm ||
    maxDv > contract.maxVelocityRemainderKmS)
    return fail('LINEARIZATION_UNRESOLVED');
  return report(stm.status,maxDr,maxDv,count,aDr,aDv,mDr,mDv);
}
