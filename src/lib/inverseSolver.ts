import { CONDE_COORDINATES } from './constants';
import { CandidatePass } from '../types/astrodynamics';
import {
  getLookAnglesFromObserver,
  propagateState,
} from './astrodynamics';

// Find all candidate passes of NORAD 528 across the latitude of Conde on Nov 7-9, 1963
export function computeInversePasses(
  startDateStr = '1963-11-07T00:00:00Z',
  endDateStr = '1963-11-09T23:59:59Z',
  _customScaleHeightKm = 45
): CandidatePass[] {
  const passes: CandidatePass[] = [];

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
    const pt = propagateState(528, curDate);
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
          const sPt = propagateState(528, sDate);
          if (sPt && sPt.distanceToCondeKm < bestDist) {
            bestDist = sPt.distanceToCondeKm;
            bestDate = sDate;
            bestPt = sPt;
          }
        }

        // Determine ascending vs descending from latitude gradient
        const nextPt = propagateState(528, new Date(bestDate.getTime() + 30000));
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

        // Geometric closest approach only. No adjustment of mean anomaly,
        // mean-motion derivative or ballistic coefficient can be deduced from
        // longitude alone. In particular, there is no inverse-fit result here.
        const notes = 'Unvalidated historical-TLE extrapolation (SGP4 baseline), not an observed terminal pass.';

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
          notes,
        });
      }
      isDecreasing = false;
    }

    prevDistance = dist;
  }

  return passes;
}
