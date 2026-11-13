/**
 * Conditional WGS84 forward geodesy in a caller-sourced inertial Earth-fixed
 * basis. No Earth orientation, UT1, ephemeris or observations are inferred.
 * The basis must refer to the SAME UTC and inertial frame as the state.
 */
import { EARTH } from './orbitPhysics.ts';
import type { Vec3 } from './orbitPhysics.ts';

export interface GeodeticFramePoint {
  readonly latitudeDeg: number;
  readonly longitudeDeg: number;
  readonly altitudeKm: number;
}

const B_KM = 6356.752314245;
const E2 = 1 - (B_KM / EARTH.radiusKm) ** 2;
const norm = (v: Vec3) => Math.hypot(...v);
const dot = (a: Vec3, b: Vec3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: Vec3, b: Vec3): Vec3 => [
  a[1] * b[2] - a[2] * b[1],
  a[2] * b[0] - a[0] * b[2],
  a[0] * b[1] - a[1] * b[0],
];

/**
 * A unit pole and a unit direction toward the ECEF x-axis (prime meridian)
 * determine a right-handed basis: y = pole × x. Reconstruct the WGS84
 * Cartesian position and compare it to the inertial r vector to 1 mm.
 * This detects wrong longitude even if radius and pole projection agree.
 *
 * Passing this check proves only INTERNAL geometric consistency of the
 * provided frame; it does not authenticate its epoch, provenance or EOP.
 */
export function validateSourcedGeodeticFrameKm(
  rKm: Vec3, point: GeodeticFramePoint,
  pole: Vec3, primeMeridian: Vec3,
): void {
  const validVec = (v: Vec3) => Array.isArray(v) && v.length === 3 &&
    v.every(Number.isFinite);
  if (!validVec(rKm) || !validVec(pole) || !validVec(primeMeridian) ||
      !Number.isFinite(point.latitudeDeg) || Math.abs(point.latitudeDeg) > 90 ||
      !Number.isFinite(point.longitudeDeg) || Math.abs(point.longitudeDeg) > 180 ||
      !Number.isFinite(point.altitudeKm) || point.altitudeKm < 0)
    throw new RangeError('Invalid sourced WGS84 frame inputs');
  if (Math.abs(norm(pole) - 1) > 1e-10 ||
      Math.abs(norm(primeMeridian) - 1) > 1e-10 ||
      Math.abs(dot(pole, primeMeridian)) > 1e-10)
    throw new RangeError('Sourced Earth-fixed axes must be unit and perpendicular');
  const phi = point.latitudeDeg * Math.PI / 180;
  const lambda = point.longitudeDeg * Math.PI / 180;
  const sinPhi = Math.sin(phi);
  const N = EARTH.radiusKm / Math.sqrt(1 - E2 * sinPhi ** 2);
  const horizontal = (N + point.altitudeKm) * Math.cos(phi);
  const vertical = (N * (1 - E2) + point.altitudeKm) * sinPhi;
  const east = cross(pole, primeMeridian);
  const x = horizontal * Math.cos(lambda);
  const y = horizontal * Math.sin(lambda);
  const reconstructed: Vec3 = [
    primeMeridian[0] * x + east[0] * y + pole[0] * vertical,
    primeMeridian[1] * x + east[1] * y + pole[1] * vertical,
    primeMeridian[2] * x + east[2] * y + pole[2] * vertical,
  ];
  if (Math.hypot(rKm[0] - reconstructed[0],
    rKm[1] - reconstructed[1], rKm[2] - reconstructed[2]) > 1e-6)
    throw new RangeError('WGS84 longitude/latitude/height inconsistent with sourced frame (km)');
}

/**
 * Optional independent check of the apparent local solar hour. A sourced
 * inertial Sun direction and a sourced Earth-fixed basis must share the
 * state's UTC and inertial frame. The Sun vector is projected onto the
 * equatorial plane; it is not derived from UTC or an invented UT1 offset.
 *
 * Longitude is EAST-positive. Local apparent solar time is noon when the
 * Sun crosses the local meridian; 24h and 0h represent the same instant.
 * This validates only internal consistency, not historical authenticity.
 */
export function validateSourcedLocalSolarTimeHours(
  longitudeDeg: number, localSolarTimeHours: number,
  pole: Vec3, primeMeridian: Vec3, sunDirection: Vec3,
): void {
  const validUnit = (v: Vec3) => Array.isArray(v) && v.length === 3 &&
    v.every(Number.isFinite) && Math.abs(norm(v) - 1) <= 1e-10;
  if (!Number.isFinite(longitudeDeg) || Math.abs(longitudeDeg) > 180 ||
      !Number.isFinite(localSolarTimeHours) ||
      localSolarTimeHours < 0 || localSolarTimeHours >= 24 ||
      !validUnit(pole) || !validUnit(primeMeridian) ||
      !validUnit(sunDirection) || Math.abs(dot(pole, primeMeridian)) > 1e-10)
    throw new RangeError('Invalid sourced Sun/Earth axes or local solar time');
  const east = cross(pole, primeMeridian);
  const sunX = dot(sunDirection, primeMeridian);
  const sunY = dot(sunDirection, east);
  if (Math.hypot(sunX, sunY) < 1e-8)
    throw new RangeError('Sourced Sun direction has undefined equatorial hour angle');
  const subsolarLongitudeRad = Math.atan2(sunY, sunX);
  const wrap24 = (h: number) => ((h % 24) + 24) % 24;
  const expected = wrap24(12 + longitudeDeg / 15 - subsolarLongitudeRad * 12 / Math.PI);
  const wrappedError = Math.abs(wrap24(localSolarTimeHours - expected + 12) - 12);
  // 1 second of local solar time. This is a numerical consistency tolerance,
  // NOT an uncertainty bound for 1963 Sun ephemerides or the Earth orientation.
  if (wrappedError > 1 / 3600)
    throw new RangeError('Local solar time inconsistent with sourced Sun and Earth frame');
}
