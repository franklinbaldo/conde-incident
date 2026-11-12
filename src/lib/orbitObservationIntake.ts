/**
 * Admission gate for documented 527/529 Cartesian position observations.
 * A document's publication day, orbital-element epoch, and a measurement
 * epoch are different quantities. This code verifies a declared contract,
 * NOT original-document authenticity, instrument calibration, or covariance.
 *
 * Source C197#1 (NASA/Goddard SSR 15 Nov 1963, printed p.8) reports only
 * the catalogued decay DAY of 1963-003B. It is never a Cartesian holdout.
 * C179-family retrospective TLE mirrors are not original ECI observations.
 */
import type { TimedOrbitPosition, Vec3 } from './orbitPhysics.ts';

export type ObservationKind =
  | 'ORIGINAL_INSTRUMENT_CARTESIAN'
  | 'CATALOG_DECAY_DAY'
  | 'DERIVED_ORBITAL_ELEMENTS';

export interface DocumentaryOrbitDatum {
  readonly kind: ObservationKind;
  readonly objectNorad: number;
  /** Matrix ID and occurrence, not a newly fabricated instrument event. */
  readonly matrixOccurrence: string;
  readonly documentUrl: string;
  /** Shared tracking lineage must not become independent evidence by renaming. */
  readonly lineageRoot: string;
  readonly observationEpochUtc: string | null;
  readonly publicationDateUtc: string | null;
  readonly inertialFrame: string | null;
  readonly rKm: Vec3 | null;
  /** Instrument-reported 1-sigma Cartesian errors, if genuinely documented.
   * Required for admission, but NOT used as likelihood weights by the existing
   * unweighted inverse fit.
   */
  readonly sigmaKm: Vec3 | null;
  readonly instrumentRecordId: string | null;
  readonly calibrationReference: string | null;
  /** Declarative provenance only: never an authentication performed here. */
  readonly custody: 'ORIGINAL_INSTRUMENT' | 'CATALOG' | 'SECONDARY' | 'SYNTHETIC';
}

export interface IntakeContext {
  readonly objectNorad: 527 | 529;
  readonly initialEpochUtc: string;
  readonly cutoffEpochUtc: string;
  readonly inertialFrame: string;
  readonly phase: 'TRAINING' | 'HOLDOUT';
}
export type IntakeRejection =
  | 'NOT_ORIGINAL_CARTESIAN'
  | 'MISSING_DOCUMENTARY_LINEAGE'
  | 'MISSING_OR_INVALID_OBSERVATION_EPOCH'
  | 'INCOMPATIBLE_TARGET_OR_FRAME'
  | 'INVALID_POSITION_OR_UNCERTAINTY'
  | 'MISSING_INSTRUMENT_CALIBRATION'
  | 'OUTSIDE_PREDECLARED_SPLIT'
  | 'DUPLICATE_OR_NONMONOTONE_EPOCH';
export interface IntakeTrace {
  readonly matrixOccurrence: string;
  readonly lineageRoot: string;
  readonly reason: IntakeRejection | null;
}
export interface ConditionalIntake {
  readonly status: 'CONDITIONAL_UNWEIGHTED_INPUTS' | 'CONNECTED_PENDING_CALIBRATION';
  /** All-or-nothing: a blocked batch must not silently lose inconvenient data. */
  readonly positions: readonly TimedOrbitPosition[];
  readonly traces: readonly IntakeTrace[];
  readonly independentInstrumentObservationsVerified: false;
  readonly uncertaintyUsedInFit: false;
  readonly historicalHoldoutValidated: false;
  readonly impactInference: 'NOT_SUPPORTED';
}

const utcMs = (value: string): number => {
  if (typeof value !== 'string' ||
      !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/.test(value))
    throw new RangeError('Require explicit ISO UTC observation epoch');
  const ms = Date.parse(value);
  if (!Number.isFinite(ms) || new Date(ms).toISOString().slice(0, 19) !== value.slice(0, 19))
    throw new RangeError('Invalid UTC calendar epoch');
  return ms;
};
const validVec = (value: unknown): value is Vec3 =>
  Array.isArray(value) && value.length === 3 && value.every(
    x => typeof x === 'number' && Number.isFinite(x));
const hasText = (value: unknown): boolean =>
  typeof value === 'string' && value.trim().length > 0;

/**
 * Convert original Cartesian measurements to the pre-existing numerical
 * TimedOrbitPosition contract only if the source-declared observation epoch,
 * exact frame, Cartesian uncertainty and instrument calibration are present.
 *
 * No TLE conversion or ECI/ECEF transformation is attempted. An accepted
 * synthetic input is only a numerical test; an accepted real-world input
 * still requires external facsimile/custody verification and independent
 * weighted residual analysis before scientific claims.
 */
export function stageDocumentedCartesianPositions(
  documents: readonly DocumentaryOrbitDatum[], context: IntakeContext,
): ConditionalIntake {
  if (!Array.isArray(documents) || (context.objectNorad !== 527 && context.objectNorad !== 529) ||
      !hasText(context.inertialFrame) || !['TRAINING', 'HOLDOUT'].includes(context.phase))
    throw new RangeError('Invalid holdout intake context');
  const origin = utcMs(context.initialEpochUtc);
  const cutoff = utcMs(context.cutoffEpochUtc);
  if (cutoff <= origin) throw new RangeError('Cutoff must follow initial epoch');
  let previousEpoch = origin;
  const traces: IntakeTrace[] = [];
  const positions: TimedOrbitPosition[] = [];
  for (const datum of documents) {
    let reason: IntakeRejection | null = null;
    if (!datum || datum.kind !== 'ORIGINAL_INSTRUMENT_CARTESIAN' ||
        !['ORIGINAL_INSTRUMENT', 'SYNTHETIC'].includes(datum.custody)) {
      reason = 'NOT_ORIGINAL_CARTESIAN';
    } else if (!hasText(datum.matrixOccurrence) || !hasText(datum.lineageRoot) ||
        typeof datum.documentUrl !== 'string' || !/^https:\/\//.test(datum.documentUrl)) {
      reason = 'MISSING_DOCUMENTARY_LINEAGE';
    } else if (!datum.observationEpochUtc) {
      reason = 'MISSING_OR_INVALID_OBSERVATION_EPOCH';
    } else if (datum.objectNorad !== context.objectNorad ||
        datum.inertialFrame !== context.inertialFrame) {
      reason = 'INCOMPATIBLE_TARGET_OR_FRAME';
    } else if (!validVec(datum.rKm) || !validVec(datum.sigmaKm) ||
        !datum.sigmaKm.every((x: number) => x > 0)) {
      reason = 'INVALID_POSITION_OR_UNCERTAINTY';
    } else if (!hasText(datum.instrumentRecordId) ||
        !hasText(datum.calibrationReference)) {
      reason = 'MISSING_INSTRUMENT_CALIBRATION';
    } else {
      let ms: number | null = null;
      try { ms = utcMs(datum.observationEpochUtc); }
      catch { reason = 'MISSING_OR_INVALID_OBSERVATION_EPOCH'; }
      if (ms !== null) {
        if (ms <= previousEpoch) reason = 'DUPLICATE_OR_NONMONOTONE_EPOCH';
        else if (context.phase === 'TRAINING' ? ms > cutoff : ms <= cutoff)
          reason = 'OUTSIDE_PREDECLARED_SPLIT';
        if (reason === null) {
          positions.push({
            objectNorad: context.objectNorad,
            inertialFrame: context.inertialFrame,
            epochUtc: datum.observationEpochUtc!,
            elapsedS: (ms - origin) / 1000,
            rKm: datum.rKm!,
            source: datum.matrixOccurrence + ' | ' + datum.documentUrl +
              ' | lineage=' + datum.lineageRoot +
              ' | record=' + datum.instrumentRecordId,
          });
          previousEpoch = ms;
        }
      }
    }
    traces.push({
      matrixOccurrence: datum?.matrixOccurrence ?? 'UNKNOWN',
      lineageRoot: datum?.lineageRoot ?? 'UNKNOWN',
      reason,
    });
  }
  const accepted = documents.length > 0 && traces.every(t => t.reason === null);
  return {
    status: accepted ? 'CONDITIONAL_UNWEIGHTED_INPUTS' : 'CONNECTED_PENDING_CALIBRATION',
    positions: accepted ? positions : [],
    traces,
    independentInstrumentObservationsVerified: false,
    uncertaintyUsedInFit: false,
    historicalHoldoutValidated: false,
    impactInference: 'NOT_SUPPORTED',
  };
}


/**
 * A declared instrument *record* can occur in only one chronological sample.
 * A shared station/tracking lineage is NOT itself a duplicate: it may contain
 * many distinct measurements and still does not establish independence.
 */
export interface ReusedOrbitRecord {
  readonly firstPhase: 'TRAINING' | 'HOLDOUT';
  readonly repeatedPhase: 'TRAINING' | 'HOLDOUT';
  readonly firstOccurrence: string;
  readonly repeatedOccurrence: string;
  readonly matchingKey: 'LINEAGE_RECORD' | 'DOCUMENT_RECORD';
}
export interface ChronologicalCartesianSplit {
  readonly status: ConditionalIntake['status'];
  /** Both arrays are emptied if either side is inadmissible or reused. */
  readonly trainingPositions: readonly TimedOrbitPosition[];
  readonly holdoutPositions: readonly TimedOrbitPosition[];
  readonly trainingTraces: readonly IntakeTrace[];
  readonly holdoutTraces: readonly IntakeTrace[];
  readonly reusedRecords: readonly ReusedOrbitRecord[];
  readonly independentInstrumentObservationsVerified: false;
  readonly historicalHoldoutValidated: false;
  readonly uncertaintyUsedInFit: false;
  readonly impactInference: 'NOT_SUPPORTED';
}

/**
 * Joint admission for a predeclared split. Running two independent per-phase
 * admission gates alone would miss the *same instrument record* being replayed
 * across training and holdout with a different timestamp.
 *
 * Compare (lineage root, instrument record ID) and (document URL, record ID);
 * different records from the same lineage are allowed, but NOT asserted
 * statistically independent. This cannot detect a disguised copy when all
 * documentary identifiers are changed. External source authentication and
 * any covariance modelling remain separate obligations.
 *
 * Primary C197#1 (NASA/Goddard SSR 15 Nov 1963, p.8, NTRS 19640001198)
 * supplies only a decay day for 528. C179/C180 historical TLE reproductions
 * share AFSPC tracking lineage and supply no original Cartesian holdout.
 */
export function stageDocumentedChronologicalSplit(
  trainingDocuments: readonly DocumentaryOrbitDatum[],
  holdoutDocuments: readonly DocumentaryOrbitDatum[],
  context: Omit<IntakeContext, 'phase'>,
): ChronologicalCartesianSplit {
  const training = stageDocumentedCartesianPositions(trainingDocuments, { ...context, phase: 'TRAINING' });
  const holdout = stageDocumentedCartesianPositions(holdoutDocuments, { ...context, phase: 'HOLDOUT' });

  type Ref = { phase: 'TRAINING' | 'HOLDOUT'; occurrence: string };
  const seen = new Map<string, Ref>();
  const reusedRecords: ReusedOrbitRecord[] = [];
  for (const [phase, batch] of [
    ['TRAINING', trainingDocuments], ['HOLDOUT', holdoutDocuments],
  ] as const) {
    for (const datum of batch) {
      if (!datum || datum.kind !== 'ORIGINAL_INSTRUMENT_CARTESIAN' ||
          !hasText(datum.instrumentRecordId)) continue;
      const recordId = datum.instrumentRecordId!.trim();
          // Only compare fully identified records; missing metadata is rejected
      // by the ordinary intake gate rather than guessed into a false match.
      const candidateKeys: [ReusedOrbitRecord['matchingKey'], string][] = [];
      if (hasText(datum.lineageRoot))
        candidateKeys.push(['LINEAGE_RECORD', 'L\u0000' + datum.lineageRoot.trim() + '\u0000' + recordId]);
      if (hasText(datum.documentUrl))
        candidateKeys.push(['DOCUMENT_RECORD', 'D\u0000' + datum.documentUrl.trim() + '\u0000' + recordId]);
      const match = candidateKeys
        .map(([kind, key]) => ({ kind, previous: seen.get(key) }))
        .find(entry => entry.previous !== undefined);
      if (match) reusedRecords.push({
        firstPhase: match.previous!.phase,
        repeatedPhase: phase,
        firstOccurrence: match.previous!.occurrence,
        repeatedOccurrence: datum.matrixOccurrence ?? 'UNKNOWN',
        matchingKey: match.kind,
      });
      else for (const [, key] of candidateKeys)
        seen.set(key, { phase, occurrence: datum.matrixOccurrence ?? 'UNKNOWN' });
    }
  }

  const accepted = training.status === 'CONDITIONAL_UNWEIGHTED_INPUTS' &&
    holdout.status === 'CONDITIONAL_UNWEIGHTED_INPUTS' &&
    reusedRecords.length === 0;
  return {
    status: accepted ? 'CONDITIONAL_UNWEIGHTED_INPUTS' : 'CONNECTED_PENDING_CALIBRATION',
    trainingPositions: accepted ? training.positions : [],
    holdoutPositions: accepted ? holdout.positions : [],
    trainingTraces: training.traces,
    holdoutTraces: holdout.traces,
    reusedRecords,
    independentInstrumentObservationsVerified: false,
    historicalHoldoutValidated: false,
    uncertaintyUsedInFit: false,
    impactInference: 'NOT_SUPPORTED',
  };
}
