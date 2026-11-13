import {
  EARTH_RADIUS_EQUATORIAL_KM,
  CONDE_COORDINATES,
  HISTORICAL_ORBITAL_DATA,
} from './constants';
import { MonteCarloRunResult } from '../types/astrodynamics';
import {ballisticFromMassScenario} from './orbitMassConstraints.ts';
import type {MassBudgetScenario, DragGeometryScenario} from './orbitMassConstraints.ts';
import {
  deg2rad,
  rad2deg,
  getGreatCircleDistanceKm,
} from './astrodynamics';

// Box-Muller transform for normal distribution
function randomGaussian(mean = 0, stdev = 1): number {
  let u1 = Math.random();
  let u2 = Math.random();
  while (u1 === 0) u1 = Math.random();
  const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  return mean + z0 * stdev;
}

export interface MonteCarloSummary {
  totalRuns: number;
  runsDecayedOnNov8: number;
  runsWithin50Km: number;
  runsWithin100Km: number;
  runsWithin250Km: number;
  runsWithin500Km: number;
  runsInCondeLatitudeBand: number; // lat in [-12.5, -11.0]
  empiricalProbability100Km: number;
  empiricalProbability500Km: number;
  closestDistanceKm: number;
  closestRun: MonteCarloRunResult | null;
  results: MonteCarloRunResult[];
  /** Null means the existing exploratory sampler, not a mass-calibrated run. */
  conditionalMassScenario: null | {
    sourceOccurrence: 'C61';
    basis: string;
    ballisticCoefficientM2Kg: number;
    historicalProbabilityCertified: false;
  };
}

export function runMonteCarloSimulation(
  sampleSize = 1000,
  options?: {
    customScaleHeight?: number;
    decayWindowDay?: number; // 8 = Nov 8
    /** Explicit four-component accounting and geometry; never historical default. */
    massScenario?: MassBudgetScenario;
    dragGeometry?: DragGeometryScenario;
  }
): MonteCarloSummary {
  const results: MonteCarloRunResult[] = [];
  if (Boolean(options?.massScenario) !== Boolean(options?.dragGeometry))
    throw new RangeError('Mass scenario and Cd/projected area must be provided together');
  const bounded = options?.massScenario && options?.dragGeometry ?
    ballisticFromMassScenario(options.massScenario, options.dragGeometry) : null;
  if (bounded && (!bounded.budgetConsistent || bounded.object !== 528))
    throw new RangeError('Conditional mass budget inconsistent or wrong target for NORAD 528');

  const epochDate = HISTORICAL_ORBITAL_DATA[528].epochDate; // 27 Oct 1963 14:40 UTC
  const epochMs = epochDate.getTime();

  let countDecayedNov8 = 0;
  let countWithin50Km = 0;
  let countWithin100Km = 0;
  let countWithin250Km = 0;
  let countWithin500Km = 0;
  let countLatBand = 0;
  let minDistance = 999999;
  let closestRun: MonteCarloRunResult | null = null;

  const targetLat = CONDE_COORDINATES.latitude; // -11.8139
  const targetLon = CONDE_COORDINATES.longitude; // -37.6108

  // Base parameters for 528
  const baseInclinationDeg = 81.8615;
  const baseNodalRegressionRate = -2.28; // deg/day
  const baseMeanMotion = 15.7490; // rev/day

  for (let i = 1; i <= sampleSize; i++) {
    // 1. Sample physical parameters with uncertainty
    const scaleHeight = options?.customScaleHeight || (45 + randomGaussian(0, 4.0));
    const solarFlux = 76.5 + randomGaussian(0, 3.0);
    // Ballistic coefficient calibrated so decay lands around Nov 8 (12 days ± 1.5 days)
    // A source-declared scenario replaces ONLY the arbitrary B prior, NOT the
    // empirical terminal lifetime law, trajectory phase, or historical evidence.
    const ballisticCoeff = bounded ?
      bounded.cdAreaOverMassM2Kg :
      Math.max(0.005, 0.022 * Math.exp(randomGaussian(0, 0.18)));

    // 2. Sample lifetime to terminal reentry (altitude < 80 km)
    // Nominal lifetime is 12 days (Nov 8), with dispersion representing drag variability
    const lifetimeDays = 12.0 * Math.pow(0.022 / ballisticCoeff, 0.28) * Math.pow(scaleHeight / 45, 0.25) + randomGaussian(0, 0.45);
    const decayMs = epochMs + lifetimeDays * 86400 * 1000;
    const decayDate = new Date(decayMs);

    // Check if decay occurs on Nov 8 (00:00 to 23:59 UTC)
    const decayDay = decayDate.getUTCDate();
    const decayMonth = decayDate.getUTCMonth(); // 10 = November
    const isNov8 = decayMonth === 10 && decayDay === 8;
    if (isNov8) countDecayedNov8++;

    // 3. Compute the orbital geometry at terminal entry:
    // High-inclination polar orbit (81.86°)
    // True anomaly at entry is uniformly distributed around the orbit (or slightly biased towards perigee)
    const entryArgLatitudeRad = Math.random() * 2 * Math.PI; // u = omega + nu
    const incRad = deg2rad(baseInclinationDeg);

    // Geocentric latitude: sin(lat) = sin(i) * sin(u)
    const sinLat = Math.sin(incRad) * Math.sin(entryArgLatitudeRad);
    const reentryLatDeg = rad2deg(Math.asin(Math.max(-1, Math.min(1, sinLat))));

    // Nodal longitude regressed to decay date
    const totalNodalShiftDeg = baseNodalRegressionRate * lifetimeDays;
    const raanAtDecayDeg = (284.152 + totalNodalShiftDeg + 360) % 360;

    // Greenwich sidereal angle theta_g at decay time
    // Approx 24h = 360 deg
    const gmstHours = (decayDate.getUTCHours() + decayDate.getUTCMinutes() / 60 + decayDate.getUTCSeconds() / 3600) * 1.0027379;
    const gmstDeg = ((gmstHours * 15) + (lifetimeDays * 360 / 365.25)) % 360;

    // Sub-satellite longitude: lon = RAAN + arctan2(cos(i)*sin(u), cos(u)) - GMST
    const yTrack = Math.cos(incRad) * Math.sin(entryArgLatitudeRad);
    const xTrack = Math.cos(entryArgLatitudeRad);
    const raTrackDeg = rad2deg(Math.atan2(yTrack, xTrack));

    let reentryLonDeg = ((raanAtDecayDeg + raTrackDeg - gmstDeg + 540) % 360) - 180;
    // Add small random atmospheric wind/drag cross-track dispersion (±0.2°)
    reentryLonDeg += randomGaussian(0, 0.2);
    if (reentryLonDeg > 180) reentryLonDeg -= 360;
    if (reentryLonDeg < -180) reentryLonDeg += 360;

    // 4. Distance to Conde
    const distToConde = getGreatCircleDistanceKm(reentryLatDeg, reentryLonDeg, targetLat, targetLon);

    const isWithin50Km = distToConde <= 50;
    const isWithin100Km = distToConde <= 100;
    const isWithin250Km = distToConde <= 250;
    const isWithin500Km = distToConde <= 500;
    const inLatBand = reentryLatDeg >= -12.5 && reentryLatDeg <= -11.0;

    if (isWithin50Km) countWithin50Km++;
    if (isWithin100Km) countWithin100Km++;
    if (isWithin250Km) countWithin250Km++;
    if (isWithin500Km) countWithin500Km++;
    if (inLatBand) countLatBand++;

    const runResult: MonteCarloRunResult = {
      runId: i,
      decayTimestampMs: decayMs,
      decayUtcString: decayDate.toISOString().replace('T', ' ').substring(0, 19) + ' UTC',
      reentryLat: Math.round(reentryLatDeg * 100) / 100,
      reentryLon: Math.round(reentryLonDeg * 100) / 100,
      ballisticCoeff: Math.round(ballisticCoeff * 10000) / 10000,
      scaleHeightKm: Math.round(scaleHeight * 10) / 10,
      solarFluxF107: Math.round(solarFlux * 10) / 10,
      distanceToCondeKm: Math.round(distToConde * 10) / 10,
      isWithinConde100Km: isWithin100Km,
      isWithinConde500Km: isWithin500Km,
      latitudePassesCondeBand: inLatBand,
    };

    if (distToConde < minDistance) {
      minDistance = distToConde;
      closestRun = runResult;
    }

    results.push(runResult);
  }

  return {
    totalRuns: sampleSize,
    conditionalMassScenario: bounded && options?.massScenario ? {
      sourceOccurrence:'C61',
      basis:options.massScenario.basis,
      ballisticCoefficientM2Kg:bounded.cdAreaOverMassM2Kg,
      historicalProbabilityCertified:false,
    } : null,
    runsDecayedOnNov8: countDecayedNov8,
    runsWithin50Km: countWithin50Km,
    runsWithin100Km: countWithin100Km,
    runsWithin250Km: countWithin250Km,
    runsWithin500Km: countWithin500Km,
    runsInCondeLatitudeBand: countLatBand,
    empiricalProbability100Km: countWithin100Km / sampleSize,
    empiricalProbability500Km: countWithin500Km / sampleSize,
    closestDistanceKm: Math.round(minDistance * 10) / 10,
    closestRun,
    results,
  };
}
