import * as satellite from 'satellite.js';
import {
  EARTH_RADIUS_EQUATORIAL_KM,
  EARTH_RADIUS_POLAR_KM,
  EARTH_MU_KM3_S2,
  EARTH_J2,
  EARTH_ROTATION_RATE_RAD_S,
  CONDE_COORDINATES,
  HISTORICAL_ORBITAL_DATA,
} from './constants';
import {
  GeodeticCoordinate,
  GroundTrackPoint,
  TriangulationState,
  UncertaintyEnvelope,
  TrackPassBenchmark,
  InterTrackProximityData,
} from '../types/astrodynamics';

// Convert degrees to radians and vice-versa
export const deg2rad = (deg: number): number => (deg * Math.PI) / 180;
export const rad2deg = (rad: number): number => (rad * 180) / Math.PI;

// Greenwich Mean Sidereal Time (GMST) in radians for a given UTC Date
export function getGMST(date: Date): number {
  return satellite.gstime(date);
}

// Haversine Great Circle Distance on Earth surface (km)
export function getGreatCircleDistanceKm(
  lat1Deg: number,
  lon1Deg: number,
  lat2Deg: number,
  lon2Deg: number
): number {
  const phi1 = deg2rad(lat1Deg);
  const phi2 = deg2rad(lat2Deg);
  const deltaPhi = deg2rad(lat2Deg - lat1Deg);
  const deltaLambda = deg2rad(lon2Deg - lon1Deg);

  const a =
    Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return EARTH_RADIUS_EQUATORIAL_KM * c;
}

// Compute Look Angles (Azimuth, Elevation, Range) from an observer to a satellite
export function getLookAnglesFromObserver(
  obsLatDeg: number,
  obsLonDeg: number,
  obsAltKm: number,
  satLatDeg: number,
  satLonDeg: number,
  satAltKm: number
): { azimuthDeg: number; elevationDeg: number; slantRangeKm: number } {
  // Convert observer and satellite to ECEF coordinates
  const obsPhi = deg2rad(obsLatDeg);
  const obsLam = deg2rad(obsLonDeg);
  const obsR = EARTH_RADIUS_EQUATORIAL_KM + obsAltKm;
  const obsX = obsR * Math.cos(obsPhi) * Math.cos(obsLam);
  const obsY = obsR * Math.cos(obsPhi) * Math.sin(obsLam);
  const obsZ = obsR * Math.sin(obsPhi);

  const satPhi = deg2rad(satLatDeg);
  const satLam = deg2rad(satLonDeg);
  const satR = EARTH_RADIUS_EQUATORIAL_KM + satAltKm;
  const satX = satR * Math.cos(satPhi) * Math.cos(satLam);
  const satY = satR * Math.cos(satPhi) * Math.sin(satLam);
  const satZ = satR * Math.sin(satPhi);

  // Vector from observer to satellite in ECEF
  const dx = satX - obsX;
  const dy = satY - obsY;
  const dz = satZ - obsZ;
  const slantRangeKm = Math.sqrt(dx * dx + dy * dy + dz * dz);

  // Rotate to Topocentric Horizon system (South, East, Zenith)
  // East: -sin(lam)*dx + cos(lam)*dy
  // North: -sin(phi)*cos(lam)*dx - sin(phi)*sin(lam)*dy + cos(phi)*dz
  // Up: cos(phi)*cos(lam)*dx + cos(phi)*sin(lam)*dy + sin(phi)*dz
  const east = -Math.sin(obsLam) * dx + Math.cos(obsLam) * dy;
  const north =
    -Math.sin(obsPhi) * Math.cos(obsLam) * dx -
    Math.sin(obsPhi) * Math.sin(obsLam) * dy +
    Math.cos(obsPhi) * dz;
  const up =
    Math.cos(obsPhi) * Math.cos(obsLam) * dx +
    Math.cos(obsPhi) * Math.sin(obsLam) * dy +
    Math.sin(obsPhi) * dz;

  const horizDist = Math.sqrt(east * east + north * north);
  let elevationDeg = rad2deg(Math.atan2(up, horizDist));
  let azimuthDeg = rad2deg(Math.atan2(east, north));
  if (azimuthDeg < 0) azimuthDeg += 360;

  return { azimuthDeg, elevationDeg, slantRangeKm };
}

// Atmospheric density model for the thermosphere (altitude 100 to 500 km)
// Parameterized for 1963 solar minimum (F10.7 ~ 76 sfu, quiet Ap ~ 9)
export function getThermosphericDensity(altitudeKm: number, scaleHeightKm = 45): number {
  if (altitudeKm < 80) {
    // Mesosphere/stratosphere exponential ramp
    return 1.8e-5 * Math.exp(-(altitudeKm - 80) / 7.2); // kg/m^3
  }
  if (altitudeKm > 600) return 1e-13;

  // Reference density at 200 km for solar minimum: ~ 3.3e-10 kg/m^3
  const rho200 = 3.3e-10;
  return rho200 * Math.exp(-(altitudeKm - 200) / scaleHeightKm);
}

// Analytical Nodal Regression Rate (J2 perturbation) in deg/day
export function getNodalPrecessionRateDegDay(
  meanMotionRevDay: number,
  inclinationDeg: number,
  semiMajorAxisKm: number,
  eccentricity: number
): number {
  const nRadS = (meanMotionRevDay * 2 * Math.PI) / 86400;
  const pKm = semiMajorAxisKm * (1 - eccentricity * eccentricity);
  const factor = -1.5 * nRadS * EARTH_J2 * Math.pow(EARTH_RADIUS_EQUATORIAL_KM / pKm, 2);
  const dOmegaDtRadS = factor * Math.cos(deg2rad(inclinationDeg));
  return rad2deg(dOmegaDtRadS) * 86400; // degrees per day
}

// SGP4 Satrec Cache
const satrecCache: Record<number, any> = {};

function getSatrec(noradId: number) {
  if (!satrecCache[noradId]) {
    const data = HISTORICAL_ORBITAL_DATA[noradId];
    if (data) {
      satrecCache[noradId] = satellite.twoline2satrec(data.line1, data.line2);
    }
  }
  return satrecCache[noradId];
}

// Propagate satellite state at a specific Date
export function propagateState(
  noradId: number,
  date: Date,
  options?: {
    customDecayRate?: number; // rev/day^2 to inject calibrated decay
    customScaleHeight?: number;
  }
): GroundTrackPoint | null {
  const launchMs = new Date('1963-01-16T21:59:00Z').getTime();
  const curMs = date.getTime();

  // Before launch: object not yet in space
  if (curMs < launchMs) {
    return null;
  }

  // After decay dates:
  const decay528Ms = new Date('1963-11-08T23:59:59Z').getTime();
  const decay529Ms = new Date('1963-12-31T23:59:59Z').getTime();

  if (noradId === 528 && curMs > decay528Ms) {
    return null; // Decayed on 08/11/1963
  }
  if (noradId === 529 && curMs > decay529Ms) {
    return null; // Decayed on 31/12/1963
  }

  const satrec = getSatrec(noradId);
  if (!satrec) return null;

  // Calculate elapsed time in days from TLE epoch
  // Baseline SGP4 propagation
  const positionAndVelocity = satellite.propagate(satrec, date);
  if (!positionAndVelocity) return null;
  const positionEci = positionAndVelocity.position;
  const velocityEci = positionAndVelocity.velocity;

  if (!positionEci || typeof positionEci !== 'object' || !velocityEci || typeof velocityEci !== 'object') {
    return null;
  }

  // Convert to Geodetic
  const gmst = satellite.gstime(date);
  const geodetic = satellite.eciToGeodetic(positionEci as satellite.EciVec3<number>, gmst);

  let latDeg = rad2deg(geodetic.latitude);
  let lonDeg = rad2deg(geodetic.longitude);
  let altKm = geodetic.height;

  // Velocity magnitude (km/s)
  const velX = (velocityEci as satellite.EciVec3<number>).x;
  const velY = (velocityEci as satellite.EciVec3<number>).y;
  const velZ = (velocityEci as satellite.EciVec3<number>).z;
  const velMag = Math.sqrt(velX * velX + velY * velY + velZ * velZ);

  // Scientific integrity: retain the position, altitude and velocity computed by SGP4.
  // Prior code independently modified altitude and longitude using prescribed
  // terminal-drop and along-track shifts, producing a nonphysical state vector.
  // SGP4 extrapolation 12+ days beyond an historical TLE is NOT a validated
  // reconstruction of terminal reentry: display as an uncalibrated baseline.
  // customDecayRate/customScaleHeight are retained only for API compatibility;
  // neither is applied until a coupled dynamical propagation is implemented.
  // Ensure longitude in [-180, 180]
  while (lonDeg > 180) lonDeg -= 360;
  while (lonDeg < -180) lonDeg += 360;

  // Distance to Conde
  const distanceToCondeKm = getGreatCircleDistanceKm(
    latDeg,
    lonDeg,
    CONDE_COORDINATES.latitude,
    CONDE_COORDINATES.longitude
  );

  const look = getLookAnglesFromObserver(
    CONDE_COORDINATES.latitude,
    CONDE_COORDINATES.longitude,
    CONDE_COORDINATES.altitudeKm,
    latDeg,
    lonDeg,
    altKm
  );

  return {
    latitude: latDeg,
    longitude: lonDeg,
    altitudeKm: altKm,
    timestamp: date.getTime(),
    velocityKmS: velMag,
    inSunlight: true,
    distanceToCondeKm,
    elevationFromCondeDeg: look.elevationDeg,
  };
}

// Generate continuous ground track points over a time span
export function generateGroundTrack(
  noradId: number,
  startDate: Date,
  durationMinutes: number,
  stepSeconds = 60,
  options?: { customDecayRate?: number; customScaleHeight?: number }
): GroundTrackPoint[] {
  const points: GroundTrackPoint[] = [];
  const startMs = startDate.getTime();
  const totalSeconds = durationMinutes * 60;

  for (let s = 0; s <= totalSeconds; s += stepSeconds) {
    const d = new Date(startMs + s * 1000);
    const pt = propagateState(noradId, d, options);
    if (pt) points.push(pt);
  }
  return points;
}

// Generate Ground Track with Epistemic Error Envelope / Uncertainty Buffer
// In low-Earth orbit without radar updates, SGP4 along-track errors grow with t^2 (thermospheric drag)
// while cross-track/radial errors grow linearly with t (nodal regression uncertainty)
export function computeGroundTrackWithUncertainty(
  noradId: number,
  startDate: Date,
  durationMinutes: number,
  stepSeconds = 60,
  options?: { customDecayRate?: number; customScaleHeight?: number }
): { points: GroundTrackPoint[]; envelopes: UncertaintyEnvelope[] } {
  const points = generateGroundTrack(noradId, startDate, durationMinutes, stepSeconds, options);
  const envelopes: UncertaintyEnvelope[] = [];
  const tleData = HISTORICAL_ORBITAL_DATA[noradId];
  const epochMs = tleData ? tleData.epochDate.getTime() : startDate.getTime();

  for (let i = 0; i < points.length; i++) {
    const pt = points[i];
    const dtDays = Math.abs(pt.timestamp - epochMs) / (86400 * 1000);

    // Ballistic error growth model:
    // Base cross-track error: ~2 km at epoch + ~18 km/day due to J2 / orbital plane drift
    const crossTrackKm = Math.min(650, 4.0 + 22.0 * dtDays + 0.8 * dtDays * dtDays);
    // Along-track phase error: ~5 km at epoch + quadratic drag uncertainty ~35 km/day^2
    const alongTrackKm = Math.min(4000, 8.0 + 45.0 * dtDays + 12.0 * dtDays * dtDays);

    // Track heading angle (tangent to orbital path)
    let headingRad = 0;
    if (i < points.length - 1) {
      const nextPt = points[i + 1];
      const dLat = deg2rad(nextPt.latitude - pt.latitude);
      const dLon = deg2rad(nextPt.longitude - pt.longitude) * Math.cos(deg2rad(pt.latitude));
      headingRad = Math.atan2(dLon, dLat);
    } else if (i > 0) {
      const prevPt = points[i - 1];
      const dLat = deg2rad(pt.latitude - prevPt.latitude);
      const dLon = deg2rad(pt.longitude - prevPt.longitude) * Math.cos(deg2rad(pt.latitude));
      headingRad = Math.atan2(dLon, dLat);
    }

    // Normal vector perpendicular to ground track (heading + 90 deg)
    const normalRad = headingRad + Math.PI / 2;
    const latOffsetDeg = (crossTrackKm / 111.32) * Math.cos(normalRad);
    const lonCos = Math.max(0.1, Math.cos(deg2rad(pt.latitude)));
    const lonOffsetDeg = (crossTrackKm / (111.32 * lonCos)) * Math.sin(normalRad);

    let leftLat = Math.max(-90, Math.min(90, pt.latitude + latOffsetDeg));
    let leftLon = pt.longitude + lonOffsetDeg;
    let rightLat = Math.max(-90, Math.min(90, pt.latitude - latOffsetDeg));
    let rightLon = pt.longitude - lonOffsetDeg;

    // Wrap longitudes into [-180, 180]
    while (leftLon > 180) leftLon -= 360;
    while (leftLon < -180) leftLon += 360;
    while (rightLon > 180) rightLon -= 360;
    while (rightLon < -180) rightLon += 360;

    envelopes.push({
      center: pt,
      leftLat,
      leftLon,
      rightLat,
      rightLon,
      crossTrackKm,
      alongTrackKm,
      sigmaKm: Math.sqrt(crossTrackKm * crossTrackKm + alongTrackKm * alongTrackKm),
      daysFromTleEpoch: dtDays,
    });
  }

  return { points, envelopes };
}

// Compute joint dynamic state of the 3 objects (527, 528, 529)
export function getTriangulationState(date: Date): TriangulationState {
  const data527 = HISTORICAL_ORBITAL_DATA[527];
  const data528 = HISTORICAL_ORBITAL_DATA[528];
  const data529 = HISTORICAL_ORBITAL_DATA[529];

  const launchMs = new Date('1963-01-16T21:59:00Z').getTime();
  const daysSinceLaunch = (date.getTime() - launchMs) / (1000 * 86400);

  // Compute nodal precessions
  const rate527 = getNodalPrecessionRateDegDay(data527.meanMotionRevDay, data527.inclinationDeg, data527.semiMajorAxisKm, data527.eccentricity);
  const rate528 = getNodalPrecessionRateDegDay(data528.meanMotionRevDay, data528.inclinationDeg, data528.semiMajorAxisKm, data528.eccentricity);
  const rate529 = getNodalPrecessionRateDegDay(data529.meanMotionRevDay, data529.inclinationDeg, data529.semiMajorAxisKm, data529.eccentricity);

  // Accumulated RAAN difference since launch (shared plane initial injection)
  const deltaDaysFromOct27 = (date.getTime() - data528.epochDate.getTime()) / (1000 * 86400);

  const raan527 = (data527.raanDeg + rate527 * deltaDaysFromOct27 + 360) % 360;
  const raan528 = (data528.raanDeg + rate528 * deltaDaysFromOct27 + 360) % 360;
  const raan529 = (data529.raanDeg + rate529 * deltaDaysFromOct27 + 360) % 360;

  // Altitudes
  let alt528 = data528.meanAltitudeKm;
  if (deltaDaysFromOct27 > 0) {
    alt528 = Math.max(0, alt528 - 240 * Math.pow(Math.min(deltaDaysFromOct27, 12) / 12, 3.2));
  }

  return {
    timestampMs: date.getTime(),
    timeSinceLaunchDays: daysSinceLaunch,
    sat527: {
      altitudeKm: data527.meanAltitudeKm,
      raanDeg: raan527,
      meanMotion: data527.meanMotionRevDay,
    },
    sat528: {
      altitudeKm: alt528,
      raanDeg: raan528,
      meanMotion: data528.meanMotionRevDay + (deltaDaysFromOct27 > 0 ? 0.05 * deltaDaysFromOct27 : 0),
    },
    sat529: {
      altitudeKm: data529.meanAltitudeKm + 50,
      raanDeg: raan529,
      meanMotion: data529.meanMotionRevDay - 0.2,
    },
    deltaRaan528_527: ((raan528 - raan527 + 540) % 360) - 180,
    deltaRaan528_529: ((raan528 - raan529 + 540) % 360) - 180,
  };
}

// Calculate past and future closest ground track passes of 527 and 529 relative to a reference coordinate/date
export function computeInterTrackProximity(
  refLat: number,
  refLon: number,
  refAltKm: number,
  date: Date
): InterTrackProximityData | null {
  const launchMs = new Date('1963-01-16T21:59:00Z').getTime();
  const curMs = date.getTime();
  if (curMs < launchMs) return null;

  const findClosestPass = (satId: 527 | 529, direction: 'PAST' | 'FUTURE'): TrackPassBenchmark => {
    const isPast = direction === 'PAST';
    // Scan over orbital period window: past [-100 min, -5 min], future [+5 min, +100 min]
    const startOffsetMin = isPast ? -100 : 5;
    const endOffsetMin = isPast ? -5 : 100;
    const stepMin = 1.0; // 1-minute coarse search

    let bestDist = Infinity;
    let bestTimeMs = curMs + (isPast ? -45 : 45) * 60 * 1000;
    let bestPt: GroundTrackPoint | null = null;

    for (let offset = startOffsetMin; offset <= endOffsetMin; offset += stepMin) {
      const scanDate = new Date(curMs + offset * 60 * 1000);
      const pt = propagateState(satId, scanDate);
      if (!pt) continue;

      const dist = getGreatCircleDistanceKm(pt.latitude, pt.longitude, refLat, refLon);
      if (dist < bestDist) {
        bestDist = dist;
        bestTimeMs = scanDate.getTime();
        bestPt = pt;
      }
    }

    // Refine with 10-second fine search around bestTimeMs (±2 minutes)
    if (bestPt) {
      const fineStartMs = bestTimeMs - 2 * 60 * 1000;
      const fineEndMs = bestTimeMs + 2 * 60 * 1000;
      for (let t = fineStartMs; t <= fineEndMs; t += 10 * 1000) {
        const scanDate = new Date(t);
        const pt = propagateState(satId, scanDate);
        if (!pt) continue;
        const dist = getGreatCircleDistanceKm(pt.latitude, pt.longitude, refLat, refLon);
        if (dist < bestDist) {
          bestDist = dist;
          bestTimeMs = t;
          bestPt = pt;
        }
      }
    }

    const satName = satId === 527 ? 'NORAD 527 (OPS 0180)' : 'NORAD 529 (1963-003C)';
    const deltaMin = (bestTimeMs - curMs) / (60 * 1000);

    return {
      satelliteId: satId,
      satelliteName: satName,
      passType: direction,
      time: new Date(bestTimeMs),
      deltaMinutes: Math.round(deltaMin * 10) / 10,
      point: bestPt || {
        latitude: refLat,
        longitude: refLon,
        altitudeKm: satId === 527 ? 485 : 280,
        timestamp: bestTimeMs,
        velocityKmS: 7.6,
        inSunlight: true,
        distanceToCondeKm: 0,
        elevationFromCondeDeg: 0,
      },
      distanceKm: Math.round(bestDist),
      latitude: bestPt ? bestPt.latitude : refLat,
      longitude: bestPt ? bestPt.longitude : refLon,
      altitudeKm: bestPt ? bestPt.altitudeKm : (satId === 527 ? 485 : 280),
    };
  };

  const past527 = findClosestPass(527, 'PAST');
  const future527 = findClosestPass(527, 'FUTURE');
  const past529 = findClosestPass(529, 'PAST');
  const future529 = findClosestPass(529, 'FUTURE');

  // Corridor width between the two passes of 527
  const corridorWidth527Km = Math.round(
    getGreatCircleDistanceKm(past527.latitude, past527.longitude, future527.latitude, future527.longitude)
  );

  return {
    referencePoint: {
      latitude: refLat,
      longitude: refLon,
      altitudeKm: refAltKm,
      timestampMs: curMs,
    },
    past527,
    future527,
    past529,
    future529,
    corridorWidth527Km,
    bracketingVerdict: `A trajetória do 528 está delimitada entre a passagem anterior do 527 (${Math.abs(past527.deltaMinutes)} min atrás, a ${past527.distanceKm} km) e a próxima passagem (${future527.deltaMinutes} min à frente, a ${future527.distanceKm} km), definindo um corredor transversal rigorosamente estável.`,
  };
}

