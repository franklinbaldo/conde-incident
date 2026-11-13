/**
 * A frame *comparison* gate, not a default conversion from TEME to J2000.
 * C179#1 supplies a secondary 528 TLE, not historical Cartesian tracking;
 * C197#1 (NASA SSR 1963-11-15, p.8) supplies a decay DAY, not an epoch.
 *
 * For r_I = R(t) r_T, v_I = R(t) v_T + dR/dt r_T.  Omitting the
 * derivative is a real velocity error even for a perfect position rotation.
 * No historical EOP, nutation, precession, UT1 or frame uncertainty is
 * populated by this module. It refuses absent transformations rather than
 * silently comparing SGP4 TEME with a generic inertial RK4 state.
 */
import { utcMilliseconds } from './orbitPhysics.ts';
import type { State, Vec3 } from './orbitPhysics.ts';
import type { Sgp4ReferenceSample } from './orbitSgp4Baseline.ts';

export type Matrix3 = readonly [number, number, number, number, number, number, number, number, number];
export interface DeclaredFrameKinematics {
  readonly from: 'TEME';
  readonly to: 'ECI_DECLARED';
  readonly epochUtc: string;
  /** Orthogonal, right-handed rotation TEME -> declared inertial axes. */
  readonly rotationRowMajor: Matrix3;
  /** Time derivative of rotation in s^-1, evaluated at the same UTC epoch. */
  readonly rotationRateRowMajorPerS: Matrix3;
  readonly sourceOccurrence: string;
  readonly sourceUrl: string;
  readonly sourceSha256: string;
  /** Uncertainty of the transformation itself, not SGP4/observation error. */
  readonly positionFrameSigmaKm: number;
  readonly velocityFrameSigmaKmS: number;
  /** Synthetic controls cannot be upgraded into a documented transformation. */
  readonly provenance: 'SYNTHETIC_CONTROL' | 'DOCUMENTED_CONDITIONAL';
  /** Needed for any non-synthetic historical frame transformation. */
  readonly eopEpochSourceUrl?: string;
  readonly eopEpochSourceSha256?: string;
}
export interface InertialComparisonState {
  readonly frame: 'ECI_DECLARED';
  readonly epochUtc: string;
  readonly state: State;
}
export interface FrameComparisonAudit {
  readonly status: 'FRAME_NOT_DOCUMENTED' | 'TRANSFORM_INADMISSIBLE' |
    'EPOCH_MISMATCH' | 'SGP4_NOT_AVAILABLE' |
    'SYNTHETIC_DIAGNOSTIC_ONLY' | 'CONDITIONAL_DIAGNOSTIC_ONLY';
  readonly transformed: State | null;
  readonly positionSeparationKm: number | null;
  readonly velocitySeparationKmS: number | null;
  readonly framePositionSigmaKm: number | null;
  readonly frameVelocitySigmaKmS: number | null;
  readonly transformationSourceOccurrence: string | null;
  readonly originalTrackingValidated: false;
  readonly historicalHoldoutValidated: false;
  readonly impactInference: 'NOT_SUPPORTED';
}
const dot = (a: readonly number[], b: readonly number[]): number => a.reduce((s, x, i) => s + x * b[i], 0);
const norm = (a: readonly number[]): number => Math.hypot(...a);
const validVector = (v: readonly number[]) => v?.length === 3 && v.every(Number.isFinite);
const validMatrix = (m: readonly number[]) => m?.length === 9 && m.every(Number.isFinite);
const product = (m: readonly number[], v: Vec3): Vec3 => [
  dot(m.slice(0, 3), v), dot(m.slice(3, 6), v), dot(m.slice(6, 9), v),
];
function isProperDifferentiableRotation(r: Matrix3, dr: Matrix3): boolean {
  if (!validMatrix(r) || !validMatrix(dr)) return false;
  const row = (a: Matrix3, i: number) => a.slice(3 * i, 3 * i + 3);
  // Reject shear, reflection, rate discontinuity and implausible rate units.
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    if (Math.abs(dot(row(r, i), row(r, j)) - (i === j ? 1 : 0)) > 1e-9) return false;
    const symmetry = dot(row(dr, i), row(r, j)) + dot(row(r, i), row(dr, j));
    if (Math.abs(symmetry) > 1e-10) return false;
  }
  const det = r[0] * (r[4] * r[8] - r[5] * r[7]) -
    r[1] * (r[3] * r[8] - r[5] * r[6]) + r[2] * (r[3] * r[7] - r[4] * r[6]);
  return Math.abs(det - 1) < 1e-9 && norm(dr) < 1e-3;
}
const digest = (s: string | undefined): boolean => /^[0-9a-f]{64}$/i.test(s ?? '');
const exactEpoch = (s: string): number | null => {
  try { return utcMilliseconds(s); } catch { return null; }
};
export const isDeclaredFrameKinematics = (k: DeclaredFrameKinematics): boolean =>
  k.from === 'TEME' && k.to === 'ECI_DECLARED' &&
  !!k.sourceOccurrence?.trim() && k.sourceUrl?.startsWith('https://') && digest(k.sourceSha256) &&
  Number.isFinite(k.positionFrameSigmaKm) && k.positionFrameSigmaKm >= 0 &&
  Number.isFinite(k.velocityFrameSigmaKmS) && k.velocityFrameSigmaKmS >= 0 &&
  (k.provenance === 'SYNTHETIC_CONTROL' ||
    (k.provenance === 'DOCUMENTED_CONDITIONAL' &&
      !!k.eopEpochSourceUrl?.startsWith('https://') && digest(k.eopEpochSourceSha256))) &&
  isProperDifferentiableRotation(k.rotationRowMajor, k.rotationRateRowMajorPerS);

/** A conversion *only* when caller supplies documented or synthetic kinematics. */
export function auditTemeInertialComparison(
  sgp4: Sgp4ReferenceSample,
  inertial: InertialComparisonState,
  kinematics: DeclaredFrameKinematics | null,
): FrameComparisonAudit {
  const output = (status: FrameComparisonAudit['status'], transformed: State | null = null,
    positionSeparationKm: number | null = null, velocitySeparationKmS: number | null = null): FrameComparisonAudit => ({
    status, transformed, positionSeparationKm, velocitySeparationKmS,
    framePositionSigmaKm: transformed ? kinematics!.positionFrameSigmaKm : null,
    frameVelocitySigmaKmS: transformed ? kinematics!.velocityFrameSigmaKmS : null,
    transformationSourceOccurrence: transformed ? kinematics!.sourceOccurrence : null,
    originalTrackingValidated: false, historicalHoldoutValidated: false,
    impactInference: 'NOT_SUPPORTED',
  });
  if (!kinematics) return output('FRAME_NOT_DOCUMENTED');
  if (!isDeclaredFrameKinematics(kinematics) || inertial.frame !== 'ECI_DECLARED') return output('TRANSFORM_INADMISSIBLE');
  const sourceEpoch = exactEpoch(sgp4.epochUtc);
  const targetEpoch = exactEpoch(inertial.epochUtc);
  const transformEpoch = exactEpoch(kinematics.epochUtc);
  if (sourceEpoch === null || targetEpoch === null || transformEpoch === null ||
      sourceEpoch !== targetEpoch || targetEpoch !== transformEpoch)
    return output('EPOCH_MISMATCH');
  if (sgp4.status !== 'SECONDARY_MODEL_ONLY' || sgp4.frame !== 'TEME' ||
      !sgp4.stateTeme || !validVector(sgp4.stateTeme.rKm) || !validVector(sgp4.stateTeme.vKmS) ||
      !Number.isFinite(sgp4.stateTeme.tS))
    return output('SGP4_NOT_AVAILABLE');
  if (!validVector(inertial.state.rKm) || !validVector(inertial.state.vKmS) ||
      !Number.isFinite(inertial.state.tS))
    return output('TRANSFORM_INADMISSIBLE');
  const r = product(kinematics.rotationRowMajor, sgp4.stateTeme.rKm);
  const rv = product(kinematics.rotationRowMajor, sgp4.stateTeme.vKmS);
  const dr = product(kinematics.rotationRateRowMajorPerS, sgp4.stateTeme.rKm);
  const v: Vec3 = [rv[0] + dr[0], rv[1] + dr[1], rv[2] + dr[2]];
  if (!validVector(r) || !validVector(v)) return output('TRANSFORM_INADMISSIBLE');
  const transformed: State = { rKm: r, vKmS: v, tS: inertial.state.tS };
  return output(kinematics.provenance === 'SYNTHETIC_CONTROL' ?
    'SYNTHETIC_DIAGNOSTIC_ONLY' : 'CONDITIONAL_DIAGNOSTIC_ONLY', transformed,
    norm(r.map((x, i) => x - inertial.state.rKm[i])),
    norm(v.map((x, i) => x - inertial.state.vKmS[i])));
}
