/**
 * Conditional propagation of a declared TEME r/v covariance into the same
 * ECI_DECLARED frame as orbitFrameKinematics.ts. This is a pushforward of
 * measurement/model covariance, NOT an Earth-orientation solution.
 *
 * Source lineage: C179#1 secondary 528 TLE is NOT an instrument covariance;
 * C197#1 NASA/Goddard SSR 1963-11-15 p.8 supplies only a catalog decay DAY:
 * https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
 * Original NORAD 527/529 Cartesian states and their covariance are absent.
 */
import { isDeclaredFrameKinematics } from './orbitFrameKinematics.ts';
import { utcMilliseconds } from './orbitPhysics.ts';
import type { DeclaredFrameKinematics } from './orbitFrameKinematics.ts';

/** Covariance ordering: [rx,ry,rz (km), vx,vy,vz (km/s)]. */
export type CartesianCovariance6 = readonly (readonly number[])[];
export interface DeclaredTemeCovariance {
  readonly epochUtc: string;
  readonly sourceOccurrence: string;
  readonly sourceUrl: string;
  readonly sourceSha256: string;
  readonly provenance: 'SYNTHETIC_CONTROL' | 'DOCUMENTED_CONDITIONAL';
  readonly covariance: CartesianCovariance6;
}
export interface FrameCovarianceAudit {
  readonly status: 'FRAME_NOT_DOCUMENTED' | 'TRANSFORM_INADMISSIBLE' |
    'COVARIANCE_INADMISSIBLE' | 'EPOCH_MISMATCH' |
    'SYNTHETIC_DIAGNOSTIC_ONLY' | 'CONDITIONAL_DIAGNOSTIC_ONLY';
  readonly transformedCovariance: CartesianCovariance6 | null;
  /** Rdot couples TEME position errors to ECI velocity errors. */
  readonly rateCouplingIncluded: boolean;
  readonly sourceOccurrence: string | null;
  /** The frame's own uncertain R and Rdot require a separate joint covariance. */
  readonly frameSystematicsIncluded: false;
  readonly measurementCovarianceAuthenticated: false;
  readonly historicalHoldoutValidated: false;
  readonly impactInference: 'NOT_SUPPORTED';
}
const digest = (s: string): boolean => /^[0-9a-f]{64}$/i.test(s ?? '');
const epoch = (s: string): number | null => {
  try { return utcMilliseconds(s); } catch { return null; }
};
const near = (a: number, b: number): boolean =>
  Math.abs(a-b) <= 1e-9 * Math.max(1, Math.abs(a), Math.abs(b));

/**
 * Cholesky on a dimensionless correlation matrix checks admissibility before
 * changing units. Refuse poorly conditioned, non-SPD and non-finite inputs.
 */
function admissibleCovariance(c: CartesianCovariance6): boolean {
  if (!Array.isArray(c) || c.length !== 6 ||
      c.some(row => !Array.isArray(row) || row.length !== 6 ||
        !row.every(Number.isFinite))) return false;
  const sigma = c.map((row, i) => Math.sqrt(row[i]));
  if (!sigma.every(s => Number.isFinite(s) && s > 0)) return false;
  const corr = c.map((row, i) => row.map((value, j) => value / sigma[i] / sigma[j]));
  if (corr.some((row, i) => row.some((x, j) => !Number.isFinite(x) ||
      (i === j && !near(x, 1)) || (i > j && !near(x, corr[j][i]))))) return false;
  const l = Array.from({length: 6}, () => Array(6).fill(0) as number[]);
  for (let i = 0; i < 6; i++) for (let j = 0; j <= i; j++) {
    let v = corr[i][j];
    for (let k = 0; k < j; k++) v -= l[i][k] * l[j][k];
    if (i === j) {
      if (!(v > 1e-10) || !Number.isFinite(v)) return false;
      l[i][j] = Math.sqrt(v);
    } else {
      l[i][j] = v / l[j][j];
      if (!Number.isFinite(l[i][j])) return false;
    }
  }
  return true;
}

/**
 * J = [[R, 0], [Rdot, R]] and C_ECI = J C_TEME J^T.
 * This operation never adds an invented frame-uncertainty covariance.
 */
export function auditTemeInertialCovariance(
  source: DeclaredTemeCovariance,
  frame: DeclaredFrameKinematics | null,
): FrameCovarianceAudit {
  const report = (status: FrameCovarianceAudit['status'],
    transformedCovariance: CartesianCovariance6 | null = null): FrameCovarianceAudit => ({
    status, transformedCovariance, rateCouplingIncluded: transformedCovariance !== null,
    sourceOccurrence: transformedCovariance ? source.sourceOccurrence : null,
    frameSystematicsIncluded: false, measurementCovarianceAuthenticated: false,
    historicalHoldoutValidated: false, impactInference: 'NOT_SUPPORTED',
  });
  if (!frame) return report('FRAME_NOT_DOCUMENTED');
  if (!isDeclaredFrameKinematics(frame)) return report('TRANSFORM_INADMISSIBLE');
  const srcEpoch = epoch(source?.epochUtc), frameEpoch = epoch(frame.epochUtc);
  if (srcEpoch === null || frameEpoch === null || srcEpoch !== frameEpoch)
    return report('EPOCH_MISMATCH');
  if (!source.sourceOccurrence?.trim() || !source.sourceUrl?.startsWith('https://') ||
      !digest(source.sourceSha256) ||
      !['SYNTHETIC_CONTROL','DOCUMENTED_CONDITIONAL'].includes(source.provenance) ||
      !admissibleCovariance(source.covariance))
    return report('COVARIANCE_INADMISSIBLE');
  const r = frame.rotationRowMajor, dr = frame.rotationRateRowMajorPerS;
  const jacobian = Array.from({length: 6}, (_, i) =>
    Array.from({length: 6}, (_, j) => i < 3 ? (j < 3 ? r[3*i+j] : 0) :
      (j < 3 ? dr[3*(i-3)+j] : r[3*(i-3)+j-3])));
  const c = source.covariance;
  const out = Array.from({length: 6}, (_, i) =>
    Array.from({length: 6}, (_, j) => {
      let sum = 0;
      for (let a = 0; a < 6; a++) for (let b = 0; b < 6; b++)
        sum += jacobian[i][a] * c[a][b] * jacobian[j][b];
      return sum;
    }));
  if (!admissibleCovariance(out)) return report('COVARIANCE_INADMISSIBLE');
  return report(frame.provenance === 'SYNTHETIC_CONTROL' ||
    source.provenance === 'SYNTHETIC_CONTROL' ?
    'SYNTHETIC_DIAGNOSTIC_ONLY' : 'CONDITIONAL_DIAGNOSTIC_ONLY', out);
}
