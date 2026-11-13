/**
 * Conditional NRLMSISE-00 driver clock and injection into the coupled (r,v)
 * RK4/J2 drag term. This does NOT implement NRLMSISE-00 or calibrate drag.
 *
 * Data: GFZ 3-hour ap + daily Ap, NRC daily observed F10.7, NOT Kp as ap.
 * A supplied, source-identified inertial->geodetic/solar-time transform and
 * a supplied density solver are mandatory. No 1963 terminal epoch/position
 * or instrumental orbital observations are inferred from these indices.
 */
import { EARTH, utcMilliseconds } from './orbitPhysics.ts';
import type { Atmosphere, State } from './orbitPhysics.ts';
import { validateSourcedGeodeticFrameKm,
  validateSourcedLocalSolarTimeHours } from './orbitGeodeticFrame.ts';

export interface SpaceWeatherSnapshot {
  readonly schema: string;
  readonly source_documents: Readonly<Record<string, {readonly url: string; readonly sha256: string}>>;
  readonly raw_series: {
    readonly F107_observed_daily: Readonly<Record<string, {readonly observed_sfu: number}>>;
    readonly Ap: Readonly<Record<string, number>>;
    readonly ap: Readonly<Record<string, number>>;
    readonly Kp?: Readonly<Record<string, number>>;
  };
}
export interface MsiseDrivers {
  readonly epochUtc: string;
  readonly f107PreviousDayObservedSfu: number;
  readonly f107aCentered81DayObservedSfu: number;
  readonly apDaily: number;
  /** [daily Ap, ap(t), ap(t-3h), ap(t-6h), ap(t-9h),
   *   average ap(t-12h..t-33h), average ap(t-36h..t-57h)]. */
  readonly apHistory: readonly [number, number, number, number, number, number, number];
  readonly inputStatus: 'PLANETARY_DRIVERS_ONLY_NOT_DENSITY_OR_CALIBRATION';
}

const DAY_MS = 86_400_000;
const THREE_HOURS_MS = 10_800_000;
// WGS84-like Earth model used by the Cartesian force. This envelope is a
// necessary geometry check, NOT a substitute for a sourced frame transform.
const POLAR_RADIUS_KM = 6356.752314245;
const WGS84_ECCENTRICITY_SQUARED = 1 - (POLAR_RADIUS_KM / EARTH.radiusKm) ** 2;
const GEODETIC_RADIUS_TOLERANCE_KM = 1e-6;

/** Geocentric radius implied by a WGS84 geodetic (latitude, height) pair.
 * This is invariant under any legitimate inertial↔Earth-fixed rotation.
 * Longitude, frame orientation, EOP and the truth of the reported latitude
 * CANNOT be certified from radius alone.
 */
export function wgs84RadiusForGeodeticKm(latitudeDeg: number, altitudeKm: number): number {
  if (!Number.isFinite(latitudeDeg) || Math.abs(latitudeDeg) > 90 ||
      !Number.isFinite(altitudeKm) || altitudeKm < 0)
    throw new RangeError('Invalid WGS84 latitude or height');
  const phi = latitudeDeg * Math.PI / 180;
  const sinPhi = Math.sin(phi);
  const cosPhi = Math.cos(phi);
  const primeVerticalKm = EARTH.radiusKm /
    Math.sqrt(1 - WGS84_ECCENTRICITY_SQUARED * sinPhi ** 2);
  return Math.hypot((primeVerticalKm + altitudeKm) * cosPhi,
    (primeVerticalKm * (1 - WGS84_ECCENTRICITY_SQUARED) + altitudeKm) * sinPhi);
}
const utcDay = (ms: number) => new Date(Math.floor(ms / DAY_MS) * DAY_MS).toISOString().slice(0, 10);
const dateKey = (ms: number) => new Date(ms).toISOString().replace('.000Z', 'Z');
const validPositive = (x: unknown): x is number => typeof x === 'number' && Number.isFinite(x) && x >= 0;
const provenance = (x: SpaceWeatherSnapshot, k: string): void => {
  const doc = x.source_documents?.[k];
  if (!doc || typeof doc.url !== 'string' || !/^https:\/\//.test(doc.url) ||
      typeof doc.sha256 !== 'string' || !/^[0-9a-f]{64}$/.test(doc.sha256))
    throw new RangeError('Missing source URL or SHA-256 for '+k);
};

/** Every RK4 substage uses its own actual UTC (no fixed noon evaluation).
 * A three-hour index is held piecewise constant within its published bin.
 * Missing inputs STOP the calculation instead of extrapolating space weather.
 * The 81-day centered mean intentionally uses the following 40 days; it
 * MUST NOT be presented as an operational forecast known at the epoch.
 */
export function deriveMsiseDriversAtUtc(snapshot: SpaceWeatherSnapshot, epochUtc: string): MsiseDrivers {
  if (!snapshot || snapshot.schema !== 'conde.1963-conditional-msise-drivers/v1')
    throw new RangeError('Unsupported historical driver snapshot');
  for (const k of ['F107', 'Ap', 'ap']) provenance(snapshot, k);
  const ms = utcMilliseconds(epochUtc);
  const series = snapshot.raw_series;
  if (!series?.F107_observed_daily || !series.Ap || !series.ap)
    throw new RangeError('Missing planetary series');
  const dayStart = Math.floor(ms / DAY_MS) * DAY_MS;
  const day = utcDay(ms);
  const prev = series.F107_observed_daily[utcDay(dayStart - DAY_MS)]?.observed_sfu;
  if (!validPositive(prev)) throw new RangeError('Missing prior-day observed F10.7 (sfu)');
  let fluxTotal = 0;
  for (let d = -40; d <= 40; d++) {
    const flux = series.F107_observed_daily[utcDay(dayStart + d * DAY_MS)]?.observed_sfu;
    if (!validPositive(flux)) throw new RangeError('Incomplete centered 81-day observed F10.7');
    fluxTotal += flux;
  }
  const apDaily = series.Ap[day + 'T00:00:00Z'];
  if (!validPositive(apDaily)) throw new RangeError('Missing daily planetary Ap');
  const bin = Math.floor(ms / THREE_HOURS_MS) * THREE_HOURS_MS;
  const apAt = (back: number): number => {
    const ap = series.ap[dateKey(bin - back * THREE_HOURS_MS)];
    if (!validPositive(ap)) throw new RangeError('Incomplete three-hour planetary ap history');
    return ap;
  };
  const average = (first: number, last: number): number => {
    let total = 0;
    for (let i = first; i <= last; i++) total += apAt(i);
    return total / (last - first + 1);
  };
  return {
    epochUtc,
    f107PreviousDayObservedSfu: prev,
    f107aCentered81DayObservedSfu: fluxTotal / 81,
    apDaily,
    apHistory: [apDaily, apAt(0), apAt(1), apAt(2), apAt(3),
      average(4, 11), average(12, 19)],
    inputStatus: 'PLANETARY_DRIVERS_ONLY_NOT_DENSITY_OR_CALIBRATION',
  };
}

export interface ConditionalGeodeticPosition {
  readonly latitudeDeg: number;
  readonly longitudeDeg: number;
  readonly altitudeKm: number;
  /** Explicit conversion supplied by caller, not inferred from inertial longitude. */
  readonly localSolarTimeHours: number;
}
export interface ConditionalDensityRequest {
  readonly epochUtc: string;
  readonly drivers: MsiseDrivers;
  readonly geodetic: ConditionalGeodeticPosition;
}
export interface ConditionalMsiseOptions {
  readonly snapshot: SpaceWeatherSnapshot;
  /** UTC corresponding to the provided originStateTS, not a guessed decay time. */
  readonly originEpochUtc: string;
  readonly originStateTS: number;
  readonly inertialFrame: string;
  readonly frameTransformSource: string;
  readonly toGeodetic: (state: State, epochUtc: string) => ConditionalGeodeticPosition;
  /** Optional independent axial check: a sourced unit terrestrial-pole vector
   * expressed in inertialFrame at the *same* UTC. Not an EOP approximation. */
  readonly inertialEarthPoleAtUtc?: (epochUtc: string) => readonly [number, number, number];
  readonly earthPoleSource?: string;
  /** Optional inertial unit ECEF x-axis at each substage UTC (prime meridian).
   * Requires the independently sourced pole above. The resulting right-handed
   * basis validates longitude as well as latitude and height. */
  readonly inertialPrimeMeridianAtUtc?: (epochUtc: string) => readonly [number, number, number];
  readonly primeMeridianSource?: string;
  /** Optional independently sourced inertial unit vector from Earth to Sun
   * at the same UTC as every RK4 substage. Requires pole and meridian axes.
   * Used only to check apparent local solar time, NOT to infer an ephemeris. */
  readonly inertialSunDirectionAtUtc?: (epochUtc: string) => readonly [number, number, number];
  readonly sunDirectionSource?: string;
  readonly densityModelSource: string;
  readonly evaluateDensityKgM3: (request: ConditionalDensityRequest) => number;
  readonly cdAreaOverMassM2Kg: number;
}

/** Connect historical *drivers* to force evaluations, with the missing
 * geodetic transform and NRLMSISE solver explicitly injected by the caller.
 * The actual density is a conditional model output, never measured here.
 */
export function makeConditionalMsiseAtmosphere(options: ConditionalMsiseOptions): Atmosphere {
  const {snapshot, originEpochUtc, originStateTS, inertialFrame, frameTransformSource,
    toGeodetic, inertialEarthPoleAtUtc, earthPoleSource,
    inertialPrimeMeridianAtUtc, primeMeridianSource,
    inertialSunDirectionAtUtc, sunDirectionSource,
    densityModelSource, evaluateDensityKgM3, cdAreaOverMassM2Kg} = options;
  const originMs = utcMilliseconds(originEpochUtc);
  if (!Number.isFinite(originStateTS) || !inertialFrame?.trim() ||
      !frameTransformSource?.trim() || !densityModelSource?.trim() ||
      typeof toGeodetic !== 'function' || typeof evaluateDensityKgM3 !== 'function' ||
      !validPositive(cdAreaOverMassM2Kg) ||
      (inertialEarthPoleAtUtc !== undefined && typeof inertialEarthPoleAtUtc !== 'function') ||
      Boolean(inertialEarthPoleAtUtc) !== Boolean(earthPoleSource?.trim()) ||
      (inertialPrimeMeridianAtUtc !== undefined &&
        typeof inertialPrimeMeridianAtUtc !== 'function') ||
      Boolean(inertialPrimeMeridianAtUtc) !== Boolean(primeMeridianSource?.trim()) ||
      (Boolean(inertialPrimeMeridianAtUtc) && !inertialEarthPoleAtUtc) ||
      (inertialSunDirectionAtUtc !== undefined &&
        typeof inertialSunDirectionAtUtc !== 'function') ||
      Boolean(inertialSunDirectionAtUtc) !== Boolean(sunDirectionSource?.trim()) ||
      (Boolean(inertialSunDirectionAtUtc) && !inertialPrimeMeridianAtUtc))
    throw new RangeError('Requires explicit inertial frame, sourced transform, density model and Cd*A/m');
  // Preflight source and required series without inventing any density.
  deriveMsiseDriversAtUtc(snapshot, originEpochUtc);
  return {
    cdAreaOverMassM2Kg,
    source: 'CONDITIONAL_NRLMSISE: '+densityModelSource+'; frame='+inertialFrame+
      '; transform='+frameTransformSource+
      (earthPoleSource ? '; axial-pole='+earthPoleSource+' (CHECK_ONLY)' : '; axial-pole=NOT_CHECKED')+
      (primeMeridianSource ? '; full-geodesy='+primeMeridianSource+' (CHECK_ONLY)' :
        '; full-geodesy=NOT_CHECKED')+
      (sunDirectionSource ? '; local-solar-time='+sunDirectionSource+' (CHECK_ONLY)' :
        '; local-solar-time=NOT_CHECKED')+
      '; GFZ/NRC declared provenance; NOT_CALIBRATED',
    densityKgM3: (radialAltitudeKm: number, tS: number, state: State): number => {
      if (!state || !Number.isFinite(tS) || state.tS !== tS ||
          !Array.isArray(state.rKm) || state.rKm.length !== 3 ||
          !state.rKm.every(Number.isFinite))
        throw new RangeError('Missing or inconsistent coupled r/v state for atmosphere');
      // Do not trust the independently supplied altitude argument: a caller
      // might supply a self-consistent geodetic pair for a *different* state.
      const stateRadiusKm = Math.hypot(...state.rKm);
      if (!Number.isFinite(radialAltitudeKm) ||
          Math.abs(stateRadiusKm - EARTH.radiusKm - radialAltitudeKm) >
            GEODETIC_RADIUS_TOLERANCE_KM)
        throw new RangeError('Atmosphere radius argument disagrees with Cartesian state (km)');
      const epochMs = originMs + (tS - originStateTS) * 1000;
      if (!Number.isFinite(epochMs) || !Number.isSafeInteger(Math.round(epochMs)))
        throw new RangeError('Atmosphere UTC overflow');
      const epochUtc = new Date(epochMs).toISOString();
      const drivers = deriveMsiseDriversAtUtc(snapshot, epochUtc);
      const geo = toGeodetic(state, epochUtc);
      if (!geo || !Number.isFinite(geo.latitudeDeg) || Math.abs(geo.latitudeDeg) > 90 ||
          !Number.isFinite(geo.longitudeDeg) || Math.abs(geo.longitudeDeg) > 180 ||
          !Number.isFinite(geo.altitudeKm) || geo.altitudeKm < 0 ||
          !Number.isFinite(geo.localSolarTimeHours) ||
          geo.localSolarTimeHours < 0 || geo.localSolarTimeHours >= 24)
        throw new RangeError('Missing sourced geodetic state or local solar time');
      // For a WGS84 ellipsoidal height h>=0, the inertial distance r must
      // satisfy b+h <= r <= a+h (a/b are equatorial/polar radii). Reject
      // meter-vs-km mistakes and stale positions before invoking density.
      // This NECESSARY bound cannot authenticate EOP/UT1 or the geodetic frame.
      const maxAltitudeKm = radialAltitudeKm + EARTH.radiusKm - POLAR_RADIUS_KM;
      if (!Number.isFinite(radialAltitudeKm) ||
          geo.altitudeKm < radialAltitudeKm - GEODETIC_RADIUS_TOLERANCE_KM ||
          geo.altitudeKm > maxAltitudeKm + GEODETIC_RADIUS_TOLERANCE_KM)
        throw new RangeError('Geodetic altitude inconsistent with inertial radius (km)');
      // The broad a/b envelope above cannot catch an inconsistent geodetic
      // latitude: a polar height can masquerade as an equatorial height.
      // The exact WGS84 latitude-height pair must reproduce |r|, which is
      // invariant under rotation. This remains NECESSARY, not sufficient:
      // a jointly fabricated latitude/height or incorrect longitude may pass.
      const modelRadiusKm = wgs84RadiusForGeodeticKm(geo.latitudeDeg, geo.altitudeKm);
      if (Math.abs(modelRadiusKm - stateRadiusKm) > GEODETIC_RADIUS_TOLERANCE_KM)
        throw new RangeError('WGS84 latitude-height pair inconsistent with inertial radius (km)');
      if (inertialEarthPoleAtUtc) {
        const pole = inertialEarthPoleAtUtc(epochUtc);
        if (!Array.isArray(pole) || pole.length !== 3 ||
            !pole.every(Number.isFinite) ||
            Math.abs(Math.hypot(...pole) - 1) > 1e-10)
          throw new RangeError('Invalid sourced unit Earth pole at atmosphere UTC');
        // Earth rotation about this axis preserves the axial coordinate. A
        // wrong geodetic latitude can have exactly the right geocentric radius
        // (G42), but it cannot have the wrong axial projection as well.
        const phi = geo.latitudeDeg * Math.PI / 180;
        const sinPhi = Math.sin(phi);
        const N = EARTH.radiusKm / Math.sqrt(1 - WGS84_ECCENTRICITY_SQUARED * sinPhi ** 2);
        const expectedAxialKm = (N * (1 - WGS84_ECCENTRICITY_SQUARED) +
          geo.altitudeKm) * sinPhi;
        const inertialAxialKm = state.rKm[0] * pole[0] +
          state.rKm[1] * pole[1] + state.rKm[2] * pole[2];
        if (Math.abs(expectedAxialKm - inertialAxialKm) > GEODETIC_RADIUS_TOLERANCE_KM)
          throw new RangeError('Geodetic latitude inconsistent with sourced Earth pole (km)');
        if (inertialPrimeMeridianAtUtc) {
          const primeMeridian = inertialPrimeMeridianAtUtc(epochUtc);
          validateSourcedGeodeticFrameKm(state.rKm, geo, pole, primeMeridian);
          if (inertialSunDirectionAtUtc) {
            const sun = inertialSunDirectionAtUtc(epochUtc);
            validateSourcedLocalSolarTimeHours(geo.longitudeDeg,
              geo.localSolarTimeHours, pole, primeMeridian, sun);
          }
        }
      }
      const rho = evaluateDensityKgM3({epochUtc, drivers, geodetic: geo});
      if (!validPositive(rho)) throw new RangeError('Conditional density model returned invalid kg/m^3');
      return rho;
    },
  };
}
