import {
  EARTH_RADIUS_EQUATORIAL_KM,
  CONDE_COORDINATES,
  HISTORICAL_ORBITAL_DATA,
  SPACE_ENVIRONMENT_NOV_1963,
} from './constants';
import { CandidatePass } from '../types/astrodynamics';
import {
  deg2rad,
  rad2deg,
  getGreatCircleDistanceKm,
  getLookAnglesFromObserver,
  propagateState,
  getThermosphericDensity,
} from './astrodynamics';

// Find all candidate passes of NORAD 528 across the latitude of Conde on Nov 7-9, 1963
export function computeInversePasses(
  startDateStr = '1963-11-07T00:00:00Z',
  endDateStr = '1963-11-09T23:59:59Z',
  customScaleHeightKm = 45
): CandidatePass[] {
  const passes: CandidatePass[] = [];
  const epochDate528 = HISTORICAL_ORBITAL_DATA[528].epochDate;
  const targetLat = CONDE_COORDINATES.latitude; // -11.8139
  const targetLon = CONDE_COORDINATES.longitude; // -37.6108

  const startMs = new Date(startDateStr).getTime();
  const endMs = new Date(endDateStr).getTime();

  // Orbital period is ~91.4 minutes (~5486 seconds)
  // Step through time in small increments (30 seconds) to find local distance minima to Conde
  const stepMs = 30 * 1000;
  let revCounter = 1;

  let prevDistance = 999999;
  let isDecreasing = false;
  let localMinPoint: any = null;
  let localMinDate: Date | null = null;

  for (let t = startMs; t <= endMs; t += stepMs) {
    const curDate = new Date(t);
    const pt = propagateState(528, curDate, { customScaleHeight: customScaleHeightKm });
    if (!pt) continue;

    const dist = pt.distanceToCondeKm;

    if (dist < prevDistance) {
      isDecreasing = true;
      localMinPoint = pt;
      localMinDate = curDate;
    } else if (isDecreasing && localMinPoint) {
      // Local minimum detected! Check if this pass is within 2500 km (regional ground track pass)
      if (localMinPoint.distanceToCondeKm <= 2600) {
        // Refine exact minimum distance with 5-second sub-stepping
        let bestDist = localMinPoint.distanceToCondeKm;
        let bestDate = localMinDate!;
        let bestPt = localMinPoint;

        const subStart = bestDate.getTime() - 60000;
        const subEnd = bestDate.getTime() + 60000;
        for (let subT = subStart; subT <= subEnd; subT += 5000) {
          const sDate = new Date(subT);
          const sPt = propagateState(528, sDate, { customScaleHeight: customScaleHeightKm });
          if (sPt && sPt.distanceToCondeKm < bestDist) {
            bestDist = sPt.distanceToCondeKm;
            bestDate = sDate;
            bestPt = sPt;
          }
        }

        // Determine ascending vs descending from latitude gradient
        const nextPt = propagateState(528, new Date(bestDate.getTime() + 30000), { customScaleHeight: customScaleHeightKm });
        const passType: 'ASCENDING' | 'DESCENDING' = (nextPt && nextPt.latitude > bestPt.latitude) ? 'ASCENDING' : 'DESCENDING';

        // Look angles
        const look = getLookAnglesFromObserver(
          CONDE_COORDINATES.latitude,
          CONDE_COORDINATES.longitude,
          CONDE_COORDINATES.altitudeKm,
          bestPt.latitude,
          bestPt.longitude,
          bestPt.altitudeKm
        );

        // Compute Required Inverse Parameters:
        // How much would the along-track phase have to shift for this pass to directly overfly Conde (dist = 0)?
        // Ground speed of 81.8° orbit ~ 7.4 km/s. Longitudinal distance in km = earth_radius * cos(lat) * delta_lon_rad
        const deltaLonDeg = bestPt.longitude - targetLon;
        // 1 deg lon at -11.8 deg lat = ~109 km
        const lonKm = deltaLonDeg * 111.32 * Math.cos(deg2rad(targetLat));
        const requiredAlongTrackKm = lonKm; // Projection onto orbital track
        const orbitCircumferenceKm = 2 * Math.PI * (EARTH_RADIUS_EQUATORIAL_KM + bestPt.altitudeKm);
        const requiredPhaseDeltaDeg = (requiredAlongTrackKm / orbitCircumferenceKm) * 360;

        // Elapsed time from epoch (27 Oct 14:40) to this pass in days
        const deltaTDays = (bestDate.getTime() - epochDate528.getTime()) / (1000 * 86400);

        // Required dn/dt (rev/day^2) to accumulate that phase delta
        // Delta M (revs) = 0.5 * (dn/dt) * (deltaTDays)^2
        const requiredPhaseDeltaRevs = requiredPhaseDeltaDeg / 360;
        const requiredDndt = (2 * requiredPhaseDeltaRevs) / (deltaTDays * deltaTDays);

        // Required effective Ballistic Coefficient B = C_D * A / m (m^2 / kg)
        // dn/dt = 1.5 * n * rho * v * B
        const nRevS = (15.75) / 86400; // rev/s
        const vM_S = bestPt.velocityKmS * 1000;
        const rho = getThermosphericDensity(bestPt.altitudeKm, customScaleHeightKm);
        // Required B in m^2 / kg
        const requiredB = (requiredDndt / 86400) / (1.5 * nRevS * Math.max(rho, 1e-12) * vM_S);

        // Physical Feasibility Assessment
        let feasibility: 'ALTA' | 'MODERADA' | 'EXTREMA' | 'INCOMPATIVEL' = 'MODERADA';
        let notes = '';

        if (bestDist < 120) {
          feasibility = 'ALTA';
          notes = 'Geometria nominal quase direta sobre o litoral norte baiano. Requer ajuste de fase mínimo (<0,5°).';
        } else if (bestDist < 600) {
          feasibility = 'MODERADA';
          notes = 'Passagem dentro do horizonte visual de alta altitude (>150 km). Fase sintonizável com pequena variação de arrasto.';
        } else if (bestDist < 1500) {
          feasibility = 'EXTREMA';
          notes = 'Passagem regional distante (Atlântico ou interior do Brasil). Exigiria desvio balístico acumulado de 3° a 10°.';
        } else {
          feasibility = 'INCOMPATIVEL';
          notes = 'Fora de qualquer raio de observação ou reentrada terminal local (>1500 km de Conde).';
        }

        // Check if altitude corresponds to atmospheric breakup
        if (bestPt.altitudeKm > 200) {
          notes += ' Altura orbital ainda em vácuo (>200 km); não é ponto de queda.';
        } else if (bestPt.altitudeKm <= 120 && bestPt.altitudeKm >= 70) {
          notes += ' CORREDOR DE REENTRADA TÉRMICA (120-70 km).';
        }

        // Local time in Bahia (UTC - 3h)
        const localDate = new Date(bestDate.getTime() - 3 * 3600 * 1000);
        const pad = (n: number) => n.toString().padStart(2, '0');
        const localTimeString = `${pad(localDate.getUTCHours())}:${pad(localDate.getUTCMinutes())}:${pad(localDate.getUTCSeconds())} (Horário da Bahia / UTC-3)`;

        passes.push({
          revolutionNumber: revCounter++,
          epochMs: bestDate.getTime(),
          utcString: bestDate.toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
          localTimeString,
          closestApproachDistanceKm: Math.round(bestDist * 10) / 10,
          subSatelliteLat: Math.round(bestPt.latitude * 1000) / 1000,
          subSatelliteLon: Math.round(bestPt.longitude * 1000) / 1000,
          altitudeKm: Math.round(bestPt.altitudeKm * 10) / 10,
          velocityKmS: Math.round(bestPt.velocityKmS * 100) / 100,
          elevationDeg: Math.round(look.elevationDeg * 10) / 10,
          azimuthDeg: Math.round(look.azimuthDeg * 10) / 10,
          passType,
          requiredMeanAnomalyDeltaDeg: Math.round(requiredPhaseDeltaDeg * 100) / 100,
          requiredMeanMotionDerivative: Math.round(requiredDndt * 1e6) / 1e6,
          requiredBallisticCoeff: Math.abs(Math.round(requiredB * 10000) / 10000),
          physicalFeasibility: feasibility,
          notes,
        });
      }
      isDecreasing = false;
    }

    prevDistance = dist;
  }

  return passes;
}
