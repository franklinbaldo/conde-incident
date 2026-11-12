/**
 * Raw SGP4 reference from an explicitly sourced TLE pair. This is NOT the
 * coupled osculating RK4/J2 integrator. SGP4 returns TEME coordinates; they
 * cannot be subtracted from a generic ECI/J2000 state without a documented
 * frame/time transformation and its uncertainty.
 *
 * C179#1: the 528 pair is a retrospective SECONDARY mirror. C197#1 provides
 * only the catalogued decay DAY, not a terminal epoch, state or impact.
 */
import * as satellite from 'satellite.js';
import { utcMilliseconds } from './orbitPhysics.ts';
import type { State, Vec3 } from './orbitPhysics.ts';

export interface Sgp4TleInput {
  readonly norad: 527 | 528 | 529;
  readonly line1: string;
  readonly line2: string;
  readonly occurrence: string;
  readonly sourceUrl: string;
  /** Hash declared by custodian; actual byte verification is an external gate. */
  readonly sourceSha256: string;
  readonly sourceClass: 'SECONDARY_LITERAL' | 'SCENARIO_PLACEHOLDER';
}
export interface Sgp4ReferenceSample {
  readonly status: 'SECONDARY_MODEL_ONLY' | 'SOURCE_NOT_ADMISSIBLE' | 'SGP4_UNRESOLVED';
  readonly frame: 'TEME';
  readonly model: 'SGP4';
  readonly tleAgeDays: number | null;
  readonly stateTeme: State | null;
  readonly sourceOccurrence: string;
  readonly custody: 'DECLARED_DIGEST_NOT_AUTHENTICATED';
  readonly independentHistoricalHoldout: 'NOT_RUN';
  readonly impactInference: 'NOT_SUPPORTED';
}

/** NORAD TLE checksum: sum numerals and minus signs over the first 68 bytes. */
export function validTleChecksum(line: string): boolean {
  if (typeof line !== 'string' || line.length !== 69 || !/^\d$/.test(line[68])) return false;
  let sum = 0;
  for (const char of line.slice(0, 68)) {
    if (char >= '0' && char <= '9') sum += Number(char);
    else if (char === '-') sum++;
  }
  return sum % 10 === Number(line[68]);
}

function validatedInput(input: Sgp4TleInput): void {
  if (![527, 528, 529].includes(input.norad) ||
      !input.occurrence?.trim() || !input.sourceUrl?.startsWith('https://') ||
      !/^[0-9a-f]{64}$/i.test(input.sourceSha256) ||
      !['SECONDARY_LITERAL', 'SCENARIO_PLACEHOLDER'].includes(input.sourceClass) ||
      !validTleChecksum(input.line1) || !validTleChecksum(input.line2) ||
      input.line1[0] !== '1' || input.line2[0] !== '2' ||
      input.line1.slice(2, 7) !== input.line2.slice(2, 7) ||
      Number(input.line1.slice(2, 7)) !== input.norad) {
    throw new RangeError('Invalid source, NORAD identity, TLE layout or checksum');
  }
}

/**
 * A direct, unmodified satellite.js SGP4 result. Never inject a decay-time
 * cutoff, longitude shift, altitude correction or fitted drag parameter.
 * `stateTeme` is deliberately named to stop TEME vs ECI silent mixing.
 * A finite model vector is not a measured position or a physical reentry.
 */
export function sgp4ReferenceAtUtc(input: Sgp4TleInput, epochUtc: string): Sgp4ReferenceSample {
  validatedInput(input);
  const milliseconds = utcMilliseconds(epochUtc);
  const result = (status: Sgp4ReferenceSample['status'], tleAgeDays: number | null,
    stateTeme: State | null): Sgp4ReferenceSample => ({
    status, frame: 'TEME', model: 'SGP4', tleAgeDays, stateTeme,
    sourceOccurrence: input.occurrence, custody: 'DECLARED_DIGEST_NOT_AUTHENTICATED',
    independentHistoricalHoldout: 'NOT_RUN', impactInference: 'NOT_SUPPORTED',
  });
  // A fabricated legacy vector must not acquire apparent authority from a
  // successful call to a valid numerical propagator.
  if (input.sourceClass !== 'SECONDARY_LITERAL') return result('SOURCE_NOT_ADMISSIBLE', null, null);
  const satrec = satellite.twoline2satrec(input.line1, input.line2);
  if (!Number.isFinite(satrec.jdsatepoch) || satrec.error !== 0)
    return result('SGP4_UNRESOLVED', null, null);
  // TLE YYDDD.dddddddd UTC epoch is already encoded in the source bytes.
  // Do not reinterpret a bulletin publication or decay DAY as a TLE epoch.
  const yy = Number(input.line1.slice(18, 20));
  const dayOfYear = Number(input.line1.slice(20, 32));
  const year = yy < 57 ? 2000 + yy : 1900 + yy;
  const daysInYear = (Date.UTC(year + 1, 0, 1) - Date.UTC(year, 0, 1)) / 86400000;
  if (!Number.isFinite(dayOfYear) || dayOfYear < 1 || dayOfYear >= daysInYear + 1)
    return result('SGP4_UNRESOLVED', null, null);
  const tleEpochMs = Date.UTC(year, 0, 1) + (dayOfYear - 1) * 86400000;
  const ageDays = (milliseconds - tleEpochMs) / 86400000;
  if (!Number.isFinite(ageDays)) return result('SGP4_UNRESOLVED', null, null);
  const model = satellite.sgp4(satrec, ageDays * 1440);
  const p = model.position, v = model.velocity;
  if (!p || !v || typeof p !== 'object' || typeof v !== 'object' ||
      ![p.x, p.y, p.z, v.x, v.y, v.z].every(Number.isFinite))
    return result('SGP4_UNRESOLVED', ageDays, null);
  const rKm: Vec3 = [p.x, p.y, p.z];
  const vKmS: Vec3 = [v.x, v.y, v.z];
  return result('SECONDARY_MODEL_ONLY', ageDays,
    { rKm, vKmS, tS: ageDays * 86400 });
}
