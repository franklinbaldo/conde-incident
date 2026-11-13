/**
 * C241-P11: first-order averaged J2 nodal-rate ranges from NASA SSR PRINTED
 * elements (527/529, Oct-Nov 1963). These ranges cover decimal printing
 * precision only; they are NOT physical error bars, observational fits,
 * posterior intervals, or estimates of historical RAAN/impact.
 *
 * The SSR data ledger uses half-km counts and centidegrees. Rates require an
 * osculating interpretation of the published elements, which is unverified.
 * Report dates must never be used as tracking epochs or propagation times.
 */
import { EARTH } from './orbitPhysics.ts';
import { auditSsrPrintedPeriod } from './orbitSsrPeriodAudit.ts';
import type { SsrPrintedElements } from './orbitSsrPeriodAudit.ts';

export interface SsrJ2PrintedElements extends SsrPrintedElements {
  readonly inclinationCentideg: number;
}

export interface SsrJ2RateInterval {
  readonly classification: 'CONDITIONAL_PRINT_QUANTIZATION_J2_RATE';
  readonly sourceOccurrence: string;
  readonly sourcePdfSha256: string;
  readonly reportDateUtc: string;
  readonly designator: SsrPrintedElements['designator'];
  /** Signed averaged regression, degrees per model day (86400 s). */
  readonly nominalDegPerDay: number;
  /** Conservative bounds from all eight printing-box corners. */
  readonly printOnlyRangeDegPerDay: readonly [number, number];
  readonly osculatingElementIdentification: 'UNVERIFIED';
  readonly observedEpochUtc: null;
  readonly raanDeg: null;
  readonly originalSensorSigma: null;
  readonly historicalHoldout: 'NOT_RUN';
  readonly historicalDomainReduction: false;
  readonly impactInference: 'NOT_SUPPORTED';
}

const rad = (deg: number): number => deg * Math.PI / 180;
const deg = (radians: number): number => radians * 180 / Math.PI;

/** Pure first-order, orbit-averaged nodal rate. No time propagation. */
export function firstOrderJ2RateDegDay(hpKm: number, haKm: number, inclinationDeg: number): number {
  if (![hpKm, haKm, inclinationDeg].every(Number.isFinite) ||
      hpKm < 80 || haKm < hpKm || haKm > 50000 ||
      inclinationDeg <= 0 || inclinationDeg >= 90) {
    throw new RangeError('J2 print diagnostic requires finite prograde non-equatorial altitudes');
  }
  const rp = EARTH.radiusKm + hpKm;
  const ra = EARTH.radiusKm + haKm;
  const a = (rp + ra) / 2;
  const p = 2 * rp * ra / (rp + ra);
  return deg(-1.5 * Math.sqrt(EARTH.muKm3S2 / a ** 3) * EARTH.j2 *
    (EARTH.radiusKm / p) ** 2 * Math.cos(rad(inclinationDeg))) * 86400;
}

/** Each printed altitude is rounded to 1 km, inclination to 0.01 deg. */
export function auditSsrJ2PrintInterval(row: SsrJ2PrintedElements): SsrJ2RateInterval {
  // Reuse the source/ledger validation of the adjacent Kepler diagnostic.
  auditSsrPrintedPeriod(row);
  if (!Number.isSafeInteger(row.inclinationCentideg) ||
      row.inclinationCentideg < 1 || row.inclinationCentideg >= 9000) {
    throw new RangeError('NASA SSR inclination must be a centidegree integer');
  }
  const hp = row.perigeeHalfKm / 2;
  const ha = row.apogeeHalfKm / 2;
  const i = row.inclinationCentideg / 100;
  const nominal = firstOrderJ2RateDegDay(hp, ha, i);
  const corners: number[] = [];
  for (const hpBound of [hp - 0.5, hp + 0.5])
    for (const haBound of [ha - 0.5, ha + 0.5])
      for (const iBound of [i - 0.005, i + 0.005])
        corners.push(firstOrderJ2RateDegDay(hpBound, haBound, iBound));
  return {
    classification: 'CONDITIONAL_PRINT_QUANTIZATION_J2_RATE',
    sourceOccurrence: row.sourceOccurrence,
    sourcePdfSha256: row.sourcePdfSha256,
    reportDateUtc: row.reportDateUtc,
    designator: row.designator,
    nominalDegPerDay: nominal,
    printOnlyRangeDegPerDay: [Math.min(...corners), Math.max(...corners)],
    osculatingElementIdentification: 'UNVERIFIED',
    observedEpochUtc: null,
    raanDeg: null,
    originalSensorSigma: null,
    historicalHoldout: 'NOT_RUN',
    historicalDomainReduction: false,
    impactInference: 'NOT_SUPPORTED',
  };
}

/** Same-edition relative *model* rates. A positive A-C rate difference
 * says A regresses less quickly, NOT that A passed any longitude at a date. */
export function compareSameEditionSsrJ2Rates(
  a: SsrJ2RateInterval, c: SsrJ2RateInterval,
): {
  readonly classification: 'CONDITIONAL_SAME_EDITION_J2_CONTRAST';
  readonly aMinusCDegPerDay: readonly [number, number];
  readonly disjointPrintRanges: boolean;
  readonly historicalConstraintActivated: false;
} {
  if (a.designator !== '1963-003A' || c.designator !== '1963-003C' ||
      a.reportDateUtc !== c.reportDateUtc ||
      a.sourceOccurrence !== c.sourceOccurrence ||
      a.sourcePdfSha256 !== c.sourcePdfSha256) {
    throw new RangeError('Compare only 527/529 printed in the same sourced SSR edition');
  }
  const [aLo, aHi] = a.printOnlyRangeDegPerDay;
  const [cLo, cHi] = c.printOnlyRangeDegPerDay;
  return {
    classification: 'CONDITIONAL_SAME_EDITION_J2_CONTRAST',
    aMinusCDegPerDay: [aLo - cHi, aHi - cLo],
    disjointPrintRanges: aLo > cHi || cLo > aHi,
    historicalConstraintActivated: false,
  };
}
