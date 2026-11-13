/**
 * Conditional topocentric optical holdout for NORAD 527/529.
 *
 * Forward operator ONLY: equatorial direction of satellite minus station,
 * with both vectors supplied in the identical inertial frame and UTC epoch.
 * No Earth rotation/EOP, historical station ephemeris, light-time, refraction,
 * aberration, or instrument authentication is inferred by this module.
 *
 * NASA SSR publication dates / orbital elements and the 528 catalogued decay
 * day are NOT optical measurement epochs or accepted sensor observations.
 */
import type { Vec3 } from './orbitPhysics.ts';

export type OpticalFrame = 'GCRF' | 'EME2000' | 'FK4_B1950' | 'TEME';
export interface OpticalObservation {
  readonly kind: 'INSTRUMENT_ANGULAR' | 'CATALOG_ELEMENT' | 'DECAY_CATALOG';
  readonly custody: 'ORIGINAL_INSTRUMENT' | 'SYNTHETIC' | 'SECONDARY' | 'CATALOG';
  readonly objectNorad: number;
  readonly matrixOccurrence: string;
  readonly sourceUrl: string;
  readonly sourcePdfSha256: string;
  readonly lineageRoot: string;
  readonly instrumentRecordId: string;
  readonly calibrationReference: string;
  /** Actual measurement UTC, NEVER the report publication date. */
  readonly observedEpochUtc: string | null;
  readonly frame: OpticalFrame | null;
  readonly rightAscensionDeg: number | null;
  readonly declinationDeg: number | null;
  /** Isotropic angular dispersion for a conditional diagnostic only. */
  readonly angularSigmaArcsec: number | null;
  /** Documented inertial station vector at precisely observedEpochUtc. */
  readonly stationPositionKm: Vec3 | null;
  readonly stationFrame: OpticalFrame | null;
  readonly stationEpochUtc: string | null;
  readonly stationEphemerisReference: string;
}

export interface OpticalPrediction {
  readonly objectNorad: number;
  readonly epochUtc: string;
  readonly frame: OpticalFrame;
  readonly rKm: Vec3;
}

export interface OpticalControl {
  readonly objectNorad: 527 | 529;
  readonly frame: OpticalFrame;
  readonly cutoffEpochUtc: string;
}

export type OpticalVeto =
  | 'NOT_INSTRUMENT_OBSERVATION'
  | 'MISSING_DOCUMENTARY_CUSTODY'
  | 'INVALID_OR_DUPLICATED_SENSOR_RECORD'
  | 'INVALID_OBSERVATION_EPOCH'
  | 'NOT_FUTURE_HOLDOUT'
  | 'FRAME_OR_EPOCH_MISMATCH'
  | 'MISSING_STATION_EPHEMERIS'
  | 'INVALID_ANGULAR_MEASUREMENT'
  | 'DEGENERATE_LINE_OF_SIGHT';

export interface OpticalTrace {
  readonly matrixOccurrence: string;
  readonly reason: OpticalVeto | null;
}
export interface OpticalPoint {
  readonly observedEpochUtc: string;
  readonly matrixOccurrence: string;
  /** Great-circle angular residual; RA wrap and polar geometry respected. */
  readonly residualArcsec: number;
  /** Descriptive ratio, NOT a calibrated chi-square or likelihood. */
  readonly residualOverDeclaredSigma: number;
}
export interface OpticalAudit {
  readonly status: 'CONDITIONAL_GEOMETRY_ONLY' | 'BLOCKED';
  readonly points: readonly OpticalPoint[];
  readonly traces: readonly OpticalTrace[];
  readonly originalInstrumentAuthenticated: false;
  readonly independentTrackingConfirmed: false;
  readonly stationEphemerisAuthenticated: false;
  readonly dynamicPropagationAuthenticated: false;
  readonly lightTimeAberrationRefraction: 'NOT_MODELED';
  readonly historicalHoldout: 'NOT_VALIDATED';
  readonly impactInference: 'NOT_SUPPORTED';
}

const supported = (frame: unknown): frame is OpticalFrame =>
  frame === 'GCRF' || frame === 'EME2000' || frame === 'FK4_B1950' || frame === 'TEME';
const nonempty = (s: unknown): s is string => typeof s === 'string' && s.trim().length > 0;
const vec = (v: unknown): v is Vec3 =>
  Array.isArray(v) && v.length === 3 &&
  v.every(x => typeof x === 'number' && Number.isFinite(x));
const epochMs = (s: unknown): number => {
  if (typeof s !== 'string' ||
      !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/.test(s))
    throw new RangeError('Explicit UTC measurement epoch required');
  const ms = Date.parse(s);
  if (!Number.isFinite(ms) || new Date(ms).toISOString().slice(0, 19) !== s.slice(0, 19))
    throw new RangeError('Invalid UTC calendar timestamp');
  return ms;
};
const unit = (v: Vec3): Vec3 | null => {
  const n = Math.hypot(...v);
  return n > 0 && Number.isFinite(n) ?
    [v[0] / n, v[1] / n, v[2] / n] : null;
};

/** Stable great-circle separation, including 0/360° and near-pole cases. */
export function opticalAngularSeparationArcsec(
  rightAscensionDeg: number, declinationDeg: number, direction: Vec3,
): number {
  if (!Number.isFinite(rightAscensionDeg) || rightAscensionDeg < 0 ||
      rightAscensionDeg >= 360 || !Number.isFinite(declinationDeg) ||
      Math.abs(declinationDeg) > 90 || !vec(direction))
    throw new RangeError('Invalid equatorial measurement or model direction');
  const u = unit(direction);
  if (u === null) throw new RangeError('Zero line-of-sight');
  const a = rightAscensionDeg * Math.PI / 180;
  const d = declinationDeg * Math.PI / 180;
  const observed: Vec3 = [Math.cos(d) * Math.cos(a), Math.cos(d) * Math.sin(a), Math.sin(d)];
  const cross: Vec3 = [
    observed[1] * u[2] - observed[2] * u[1],
    observed[2] * u[0] - observed[0] * u[2],
    observed[0] * u[1] - observed[1] * u[0],
  ];
  const dot = Math.max(-1, Math.min(1,
    observed[0] * u[0] + observed[1] * u[1] + observed[2] * u[2]));
  return Math.atan2(Math.hypot(...cross), dot) * 180 / Math.PI * 3600;
}

/**
 * Predeclared post-cutoff holdout: predictions must be computed independently,
 * before consulting withheld angular observations. Every point is vetted and
 * the entire batch is blocked if a single row fails.
 *
 * Numeric residuals are conditional diagnostics, NOT observational proof:
 * metadata and station vectors are only declarations, not authenticated here.
 */
export function auditFutureOpticalDirections(
  observations: readonly OpticalObservation[],
  predictions: readonly OpticalPrediction[],
  control: OpticalControl,
): OpticalAudit {
  if (![527, 529].includes(control.objectNorad) || !supported(control.frame) ||
      !Array.isArray(observations) || !Array.isArray(predictions) ||
      observations.length !== predictions.length || !observations.length)
    throw new RangeError('A nonempty one-to-one predeclared optical holdout is required');
  const cutoffMs = epochMs(control.cutoffEpochUtc);
  const seen = new Set<string>();
  const points: OpticalPoint[] = [];
  const traces: OpticalTrace[] = [];
  for (let i = 0; i < observations.length; i++) {
    const o = observations[i];
    const p = predictions[i];
    let reason: OpticalVeto | null = null;
    if (!o || o.kind !== 'INSTRUMENT_ANGULAR' ||
        !['ORIGINAL_INSTRUMENT', 'SYNTHETIC'].includes(o.custody)) {
      reason = 'NOT_INSTRUMENT_OBSERVATION';
    } else if (!nonempty(o.matrixOccurrence) || !nonempty(o.lineageRoot) ||
        !nonempty(o.instrumentRecordId) || !nonempty(o.calibrationReference) ||
        !nonempty(o.sourceUrl) || !o.sourceUrl.startsWith('https://') ||
        !/^[0-9a-f]{64}$/i.test(o.sourcePdfSha256)) {
      reason = 'MISSING_DOCUMENTARY_CUSTODY';
    } else {
      const key = o.lineageRoot.trim() + '\u0000' + o.instrumentRecordId.trim();
      if (seen.has(key)) reason = 'INVALID_OR_DUPLICATED_SENSOR_RECORD';
      seen.add(key);
      let measuredMs: number | null = null;
      let stationMs: number | null = null;
      let predictedMs: number | null = null;
      try {
        measuredMs = epochMs(o.observedEpochUtc);
        stationMs = epochMs(o.stationEpochUtc);
        predictedMs = epochMs(p?.epochUtc);
      } catch { reason ??= 'INVALID_OBSERVATION_EPOCH'; }
      if (reason === null && measuredMs !== null) {
        if (measuredMs <= cutoffMs) reason = 'NOT_FUTURE_HOLDOUT';
        else if (!supported(o.frame) || o.frame !== control.frame ||
          o.stationFrame !== control.frame ||
          p?.frame !== control.frame || p?.objectNorad !== control.objectNorad ||
          o.objectNorad !== control.objectNorad ||
          measuredMs !== stationMs || measuredMs !== predictedMs)
          reason = 'FRAME_OR_EPOCH_MISMATCH';
        else if (!vec(o.stationPositionKm) || !nonempty(o.stationEphemerisReference) ||
          Math.hypot(...o.stationPositionKm) < 6300 ||
          Math.hypot(...o.stationPositionKm) > 6450)
          reason = 'MISSING_STATION_EPHEMERIS';
        else if (typeof o.rightAscensionDeg !== 'number' ||
          typeof o.declinationDeg !== 'number' ||
          typeof o.angularSigmaArcsec !== 'number' ||
          !Number.isFinite(o.angularSigmaArcsec) || o.angularSigmaArcsec <= 0 ||
          !Number.isFinite(o.rightAscensionDeg) || o.rightAscensionDeg < 0 ||
          o.rightAscensionDeg >= 360 || !Number.isFinite(o.declinationDeg) ||
          Math.abs(o.declinationDeg) > 90 || !vec(p?.rKm))
          reason = 'INVALID_ANGULAR_MEASUREMENT';
        else {
          const direction: Vec3 = [
            p.rKm[0] - o.stationPositionKm[0],
            p.rKm[1] - o.stationPositionKm[1],
            p.rKm[2] - o.stationPositionKm[2],
          ];
          if (unit(direction) === null)
            reason = 'DEGENERATE_LINE_OF_SIGHT';
          else {
            const residual = opticalAngularSeparationArcsec(
              o.rightAscensionDeg, o.declinationDeg, direction);
            points.push({
              observedEpochUtc: o.observedEpochUtc!,
              matrixOccurrence: o.matrixOccurrence,
              residualArcsec: residual,
              residualOverDeclaredSigma: residual / o.angularSigmaArcsec,
            });
          }
        }
      }
    }
    traces.push({ matrixOccurrence: o?.matrixOccurrence ?? 'UNKNOWN', reason });
  }
  const accepted = traces.every(t => t.reason === null);
  return {
    status: accepted ? 'CONDITIONAL_GEOMETRY_ONLY' : 'BLOCKED',
    points: accepted ? points : [],
    traces,
    originalInstrumentAuthenticated: false,
    independentTrackingConfirmed: false,
    stationEphemerisAuthenticated: false,
    dynamicPropagationAuthenticated: false,
    lightTimeAberrationRefraction: 'NOT_MODELED',
    historicalHoldout: 'NOT_VALIDATED',
    impactInference: 'NOT_SUPPORTED',
  };
}
