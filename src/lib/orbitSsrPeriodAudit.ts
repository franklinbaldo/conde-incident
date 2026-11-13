/**
 * C241-P11: documentary two-body consistency check for printed NASA SSR
 * periods and apo/perigee heights. A publication day is NOT a tracking epoch.
 * The ledger's *_km fields are deliberately stored in HALF-kilometre units;
 * period_min is in 1/100 minute. This module refuses silent unit mixing.
 *
 * A two-body Kepler period is a baseline dimensional sanity check, NOT an
 * SGP4/J2/anomalistic-period prediction, historical likelihood or measurement.
 */
import { EARTH } from './orbitPhysics.ts';

export interface SsrPrintedElements {
  readonly sourceOccurrence: string;
  readonly sourcePdfSha256: string;
  readonly reportDateUtc: string;
  readonly designator: '1963-003A' | '1963-003C';
  readonly perigeeHalfKm: number;
  readonly apogeeHalfKm: number;
  readonly periodCentimin: number;
}

export interface SsrPeriodDiagnostic {
  readonly classification: 'DOCUMENTARY_UNIT_AND_KEPLER_DIAGNOSTIC';
  readonly sourceOccurrence: string;
  readonly sourcePdfSha256: string;
  readonly reportDateUtc: string;
  readonly designator: SsrPrintedElements['designator'];
  readonly semiMajorAxisKm: number;
  readonly printedPeriodMin: number;
  readonly twoBodyKeplerPeriodMin: number;
  /** Printed minus 2-body prediction; no J2, tracking, epoch or sensor model. */
  readonly printedMinusKeplerSec: number;
  /** Only the table's declared decimal rounding: NOT an instrumental sigma. */
  readonly printRoundingResidualSec: readonly [number, number];
  /** Incorrect interpretation of the ledger's half-km values as whole km. */
  readonly wrongUnitResidualSec: number;
  readonly originalObservationEpochUtc: null;
  readonly originalInstrumentCovariance: null;
  readonly independentValidation: false;
  readonly historicalHoldout: 'NOT_RUN';
  readonly impactInference: 'NOT_SUPPORTED';
}

const keplerMinutes = (semiMajorKm: number): number =>
  2 * Math.PI * Math.sqrt(semiMajorKm ** 3 / EARTH.muKm3S2) / 60;

/**
 * Printed heights are rounded to whole km, represented as integer *2 in the
 * C241-P11 ledger; periods are rounded to the nearest 0.1 minute. Bound only
 * this printing error. Never use the bounds as historical physical tolerance.
 */
export function auditSsrPrintedPeriod(row: SsrPrintedElements): SsrPeriodDiagnostic {
  if (!row || !row.sourceOccurrence?.trim() ||
      !/^[a-f0-9]{64}$/.test(row.sourcePdfSha256) ||
      !/^1963-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/.test(row.reportDateUtc) ||
      !Number.isFinite(Date.parse(row.reportDateUtc + 'T00:00:00Z')) ||
      new Date(row.reportDateUtc + 'T00:00:00Z').toISOString().slice(0, 10) !== row.reportDateUtc ||
      !['1963-003A', '1963-003C'].includes(row.designator) ||
      ![row.perigeeHalfKm, row.apogeeHalfKm, row.periodCentimin].every(Number.isSafeInteger) ||
      row.perigeeHalfKm < 0 || row.apogeeHalfKm < row.perigeeHalfKm ||
      row.apogeeHalfKm > 200000 || row.periodCentimin <= 0) {
    throw new RangeError('Missing or invalid NASA SSR documentary units/provenance');
  }
  const midAltitudeKm = (row.perigeeHalfKm + row.apogeeHalfKm) / 4;
  const aKm = EARTH.radiusKm + midAltitudeKm;
  const printedMin = row.periodCentimin / 100;
  const predictedMin = keplerMinutes(aKm);
  // Each printed height can differ by ±0.5 km from its unrounded source;
  // so their mean also differs by at most ±0.5 km.
  const minPredMin = keplerMinutes(aKm - 0.5);
  const maxPredMin = keplerMinutes(aKm + 0.5);
  return {
    classification: 'DOCUMENTARY_UNIT_AND_KEPLER_DIAGNOSTIC',
    sourceOccurrence: row.sourceOccurrence,
    sourcePdfSha256: row.sourcePdfSha256,
    reportDateUtc: row.reportDateUtc,
    designator: row.designator,
    semiMajorAxisKm: aKm,
    printedPeriodMin: printedMin,
    twoBodyKeplerPeriodMin: predictedMin,
    printedMinusKeplerSec: 60 * (printedMin - predictedMin),
    printRoundingResidualSec: [
      60 * (printedMin - 0.05 - maxPredMin),
      60 * (printedMin + 0.05 - minPredMin),
    ],
    wrongUnitResidualSec: 60 * (printedMin - keplerMinutes(EARTH.radiusKm + 2 * midAltitudeKm)),
    originalObservationEpochUtc: null,
    originalInstrumentCovariance: null,
    independentValidation: false,
    historicalHoldout: 'NOT_RUN',
    impactInference: 'NOT_SUPPORTED',
  };
}
