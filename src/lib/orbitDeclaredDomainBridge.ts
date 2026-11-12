/**
 * Physics-side bridge from the DECLARED, exact-rational alternative-domain
 * auditor proposed in PR #43. That auditor is not Lean, tracking data, nor a
 * source authenticator. This bridge never promotes its labels into proof.
 *
 * The auditor reports reduced fractions but drops the parameter units and
 * initial-domain source. Callers must explicitly supply both, and neither
 * assertion is verified by this bridge. Only 527/529 Cartesian velocity
 * boxes are supported, NOT TLE mean elements or an orbital fit.
 */
import type { State } from './orbitPhysics.ts';
import type { AlternativeOrbitPremise } from './orbitAlternativeFits.ts';
import type { VelocityAxis, ConditionalVelocityBound } from './orbitAdmissibility.ts';

type RationalString = string;
interface AuditInterval { min: RationalString; max: RationalString }
interface AuditParameter {
  name: string;
  status: 'EMPTY' | 'REDUCED' | 'UNCHANGED';
  /** Original declared rational domain, returned by PR #37 / #43. */
  initial: AuditInterval;
  admissible: AuditInterval | null;
}
interface AuditTrace {
  parameter: string;
  evidence_id: string;
  occurrence: string;
  source_uri: string;
  independence_group_declared: string;
  lean_ref_declared: string;
  lean_status_declared: 'CLAIMED' | 'NOT_RUN';
}
interface AuditBranch {
  id: string;
  domain_status: 'CONTRADICTORY' | 'REDUCED' | 'UNCHANGED';
  declared_evidence: 'SYNTHETIC_ONLY' | 'DECLARED_NOT_AUDITED';
  lean_proofs: 'NOT_VERIFIED';
  numerical_holdout: 'NOT_RUN';
  parameters: readonly AuditParameter[];
  trace: readonly AuditTrace[];
}
export interface DeclaredAlternativesAudit {
  status: 'MULTIPLE_DECLARED_FEASIBLE' | 'ONE_DECLARED_FEASIBLE' | 'NO_DECLARED_FEASIBLE';
  scenarios_declared: number;
  scenarios_with_nonempty_intervals: number;
  scenarios: readonly AuditBranch[];
  scenario_set_exhaustive: 'NOT_VERIFIED';
  matrix_occurrences: 'NOT_VERIFIED';
  source_authenticity: 'NOT_VERIFIED';
  source_independence_between_scenarios: 'NOT_VERIFIED';
  lean_proofs: 'NOT_VERIFIED';
  physical_feasibility: 'NOT_VERIFIED';
  numerical_holdouts: 'NOT_RUN';
  location_and_impact: 'NOT_INFERRED';
}
export interface InitialBranchState {
  id: string;
  initial: State;
  /** Origin of initial velocity box, OMITTED by the declared-domain auditor. */
  initialDomainSource: string;
}
export interface BridgeContext {
  objectNorad: 527 | 529;
  epochUtc: string;
  inertialFrame: string;
  /** Explicit caller assertion; the audit result contains NO units. */
  assumedUnit: 'km/s';
  initials: readonly InitialBranchState[];
}
export interface BridgeRecord {
  id: string;
  status: 'READY_CONDITIONALLY' | 'NOT_RUN_CONTRADICTORY' |
    'NOT_RUN_INCOMPLETE' | 'NOT_RUN_UNTRACED' | 'NOT_RUN_FLOAT64_PRECISION';
  reason: string;
}
export interface BridgeResult {
  alternatives: readonly AlternativeOrbitPremise[];
  records: readonly BridgeRecord[];
  leanProof: 'NOT_VERIFIED';
  sourceAuthenticity: 'NOT_VERIFIED';
  sourceIndependence: 'NOT_VERIFIED';
  unitFromAuditor: 'NOT_PRESENT';
  assumedUnit: 'km/s';
  frameTransformation: 'NOT_RUN';
  geographicInference: 'NOT_SUPPORTED';
  exhaustiveEnclosure: false;
}

const AXES: readonly VelocityAxis[] = ['vx', 'vy', 'vz'];
function must(ok: unknown, message: string): asserts ok {
  if (!ok) throw new RangeError(message);
}
interface Fraction { n: bigint; d: bigint }
function rational(raw: string): Fraction {
  must(typeof raw === 'string' && /^-?(?:0|[1-9]\d*)(?:\/[1-9]\d*)?$/.test(raw),
    'Expected an exact integer/fraction from declared-domain auditor');
  const [numerator, denominator = '1'] = raw.split('/');
  const n = BigInt(numerator), d = BigInt(denominator);
  must(d > 0n, 'Invalid rational denominator');
  return { n, d };
}
const compare = (a: Fraction, b: Fraction): number =>
  a.n * b.d < b.n * a.d ? -1 : a.n * b.d > b.n * a.d ? 1 : 0;

const buffer = new DataView(new ArrayBuffer(8));
const MASK = (1n << 52n) - 1n;
function exactFloat(x: number): Fraction {
  must(Number.isFinite(x), 'Finite Float64 required');
  buffer.setFloat64(0, x);
  const bits = buffer.getBigUint64(0);
  const sign = bits >> 63n ? -1n : 1n;
  const exp = Number((bits >> 52n) & 2047n);
  const mantissa = (bits & MASK) + (exp === 0 ? 0n : 1n << 52n);
  const power = exp === 0 ? -1074 : exp - 1075;
  return power >= 0
    ? { n: sign * mantissa * (1n << BigInt(power)), d: 1n }
    : { n: sign * mantissa, d: 1n << BigInt(-power) };
}
// Monotone keys enumerate *all and only* finite IEEE-754 binary64 values.
// Negative keys invert the bits; nonnegative keys flip the sign bit.
// This avoids Number(BigInt) overflow/underflow or double rounding when
// the exact rational numerator and denominator are individually enormous.
const SIGN64 = 1n << 63n;
const ALL64 = (1n << 64n) - 1n;
const MIN_FINITE_KEY = 0x0010000000000000n; // -Number.MAX_VALUE
const MAX_FINITE_KEY = 0xffefffffffffffffn; // +Number.MAX_VALUE
function floatAtKey(key: bigint): number {
  buffer.setBigUint64(0, (key & SIGN64) ? (key & ~SIGN64) : (ALL64 ^ key));
  return buffer.getFloat64(0);
}

/** Find the first finite Float64 >= bound (inclusive), or > bound (exclusive).
 * A sentinel one past +MAX_VALUE means that no such float exists.
 * Every comparison is exact rational arithmetic, including subnormals.
 */
function firstFiniteKey(bound: Fraction, inclusive: boolean): bigint {
  let low = MIN_FINITE_KEY, high = MAX_FINITE_KEY + 1n;
  while (low < high) {
    const mid = (low + high) >> 1n;
    const relation = compare(exactFloat(floatAtKey(mid)), bound);
    if (relation > 0 || (inclusive && relation === 0)) high = mid;
    else low = mid + 1n;
  }
  return low;
}

/** Intersect the exact rational box with finite Float64, rounding INWARDS.
 * This is an exact *representable subset*, not an enclosure of the whole
 * rational interval or of physical trajectories.
 */
function exactInterval(box: AuditInterval): { lo: Fraction; hi: Fraction } {
  must(box && typeof box === 'object', 'Missing exact rational interval');
  const lo = rational(box.min), hi = rational(box.max);
  must(compare(lo, hi) <= 0, 'Inverted exact rational interval');
  return { lo, hi };
}

/** Independently check the producer's serialized domain arithmetic metadata.
 * This is NOT a proof that the source restrictions or traces are genuine.
 */
function checkedParameters(branch: AuditBranch): void {
  const seen = new Set<string>();
  let empty = false, reduced = false;
  for (const param of branch.parameters) {
    must(param && typeof param.name === 'string' && !seen.has(param.name) &&
      AXES.includes(param.name as VelocityAxis), 'Duplicate or unsupported audit parameter');
    seen.add(param.name);
    const start = exactInterval(param.initial);
    if (param.admissible === null) {
      must(param.status === 'EMPTY', 'Inconsistent empty rational parameter status');
      empty = true;
      continue;
    }
    const end = exactInterval(param.admissible);
    must(compare(start.lo, end.lo) <= 0 && compare(end.hi, start.hi) <= 0,
      'Declared admissible interval expands its original exact domain');
    const narrowed = compare(start.lo, end.lo) !== 0 || compare(start.hi, end.hi) !== 0;
    must(param.status === (narrowed ? 'REDUCED' : 'UNCHANGED'),
      'Inconsistent declared rational parameter status');
    if (narrowed) reduced = true;
  }
  // Missing axes are reported as NOT_RUN_INCOMPLETE by the caller below,
  // rather than throwing or fabricating an unconstrained velocity.
  const expected = empty ? 'CONTRADICTORY' : reduced ? 'REDUCED' : 'UNCHANGED';
  must(branch.domain_status === expected, 'Inconsistent declared scenario domain status');
}

function finiteInside(box: AuditInterval): [number, number] | null {
  const { lo, hi } = exactInterval(box);
  const first = firstFiniteKey(lo, true);
  const last = firstFiniteKey(hi, false) - 1n;
  if (first > last || first > MAX_FINITE_KEY || last < MIN_FINITE_KEY) return null;
  const a = floatAtKey(first), b = floatAtKey(last);
  return [Object.is(a, -0) ? 0 : a, Object.is(b, -0) ? 0 : b];
}

/**
 * Consumes PR #43's audit RESULT, not its primary declarations or Lean proof.
 * Each branch is kept separate. A tiny exact interval with no Float64 member
 * is NOT silently rounded into a false orbital witness.
 */
export function bridgeDeclaredAlternatives(
  audit: DeclaredAlternativesAudit, context: BridgeContext,
): BridgeResult {
  must(audit && Array.isArray(audit.scenarios) && audit.scenarios.length > 0 &&
    audit.scenarios.length <= 12 &&
    Number.isSafeInteger(audit.scenarios_declared) &&
    audit.scenarios_declared === audit.scenarios.length &&
    Number.isSafeInteger(audit.scenarios_with_nonempty_intervals) &&
    audit.scenarios_with_nonempty_intervals === audit.scenarios.filter(s =>
      s && s.domain_status !== 'CONTRADICTORY').length &&
    audit.status === (audit.scenarios_with_nonempty_intervals === 0
      ? 'NO_DECLARED_FEASIBLE' : audit.scenarios_with_nonempty_intervals === 1
        ? 'ONE_DECLARED_FEASIBLE' : 'MULTIPLE_DECLARED_FEASIBLE') &&
    audit.scenario_set_exhaustive === 'NOT_VERIFIED' &&
    audit.matrix_occurrences === 'NOT_VERIFIED' &&
    audit.source_authenticity === 'NOT_VERIFIED' &&
    audit.source_independence_between_scenarios === 'NOT_VERIFIED' &&
    audit.lean_proofs === 'NOT_VERIFIED' &&
    audit.physical_feasibility === 'NOT_VERIFIED' &&
    audit.numerical_holdouts === 'NOT_RUN' &&
    audit.location_and_impact === 'NOT_INFERRED',
  'Unsupported or falsely certified declared-domain audit');
  must(context.assumedUnit === 'km/s' &&
    (context.objectNorad === 527 || context.objectNorad === 529) &&
    typeof context.epochUtc === 'string' && context.epochUtc.endsWith('Z') &&
    typeof context.inertialFrame === 'string' && context.inertialFrame.trim() &&
    Array.isArray(context.initials), 'Explicit Cartesian unit, epoch, target and frame required');
  const ids = new Set<string>();
  const initials = new Map(context.initials.map(s => [s.id, s]));
  must(initials.size === context.initials.length, 'Duplicate initial-state IDs');
  must(initials.size === audit.scenarios.length, 'Exactly one initial state per alternative required');

  const alternatives: AlternativeOrbitPremise[] = [], records: BridgeRecord[] = [];
  for (const branch of audit.scenarios) {
    must(branch && /^[a-z0-9][a-z0-9-]{1,63}$/.test(branch.id) && !ids.has(branch.id) &&
      ['SYNTHETIC_ONLY', 'DECLARED_NOT_AUDITED'].includes(branch.declared_evidence) &&
      branch.lean_proofs === 'NOT_VERIFIED' && branch.numerical_holdout === 'NOT_RUN' &&
      ['CONTRADICTORY', 'REDUCED', 'UNCHANGED'].includes(branch.domain_status) &&
      Array.isArray(branch.parameters) && Array.isArray(branch.trace),
    'Invalid branch identity, status or trace');
    checkedParameters(branch);
    must(branch.trace.every(t => t && AXES.includes(t.parameter as VelocityAxis)),
      'Trace cites unsupported velocity parameter');
    ids.add(branch.id);
    const original = initials.get(branch.id);
    must(original && original.initialDomainSource.trim() &&
      original.initial.tS === 0 && original.initial.rKm?.length === 3 &&
      original.initial.vKmS?.length === 3 &&
      [...original.initial.rKm, ...original.initial.vKmS].every(Number.isFinite),
    'Missing explicit finite initial Cartesian state or initial-domain lineage');
    const stop = (status: BridgeRecord['status'], reason: string) =>
      records.push({ id: branch.id, status, reason });
    if (branch.domain_status === 'CONTRADICTORY') {
      stop('NOT_RUN_CONTRADICTORY', 'Contradiction among declared premises only');
      continue;
    }
    const bounds: ConditionalVelocityBound[] = [];
    let failure: BridgeRecord | null = null;
    for (const axis of AXES) {
      const param = branch.parameters.find(p => p.name === axis);
      if (!param?.admissible || param.status === 'EMPTY') {
        failure = { id: branch.id, status: 'NOT_RUN_INCOMPLETE', reason: 'Missing rational interval for ' + axis };
        break;
      }
      const lineage = branch.trace.filter(t => t.parameter === axis);
      if (lineage.length === 0) {
        failure = { id: branch.id, status: 'NOT_RUN_UNTRACED', reason: 'No declared restriction trace for ' + axis };
        break;
      }
      for (const trace of lineage) {
        must(trace.evidence_id?.trim() && trace.occurrence?.trim() &&
          trace.source_uri?.trim() && trace.independence_group_declared?.trim() &&
          trace.lean_ref_declared?.trim() &&
          ['NOT_RUN', 'CLAIMED'].includes(trace.lean_status_declared) &&
          (branch.declared_evidence === 'SYNTHETIC_ONLY'
            ? trace.source_uri.startsWith('synthetic:')
            : trace.source_uri.startsWith('https://') && /^C\d{1,4}(?:-[A-Za-z0-9]+)?$/.test(trace.evidence_id)),
        'Invalid or falsely certified restriction trace');
      }
      const inside = finiteInside(param.admissible);
      if (!inside) {
        failure = { id: branch.id, status: 'NOT_RUN_FLOAT64_PRECISION',
          reason: 'Exact interval has no representable finite Float64 velocity on ' + axis };
        break;
      }
      bounds.push({
        axis, lowerKmS: inside[0], upperKmS: inside[1],
        evidenceOccurrence: lineage.map(t => t.evidence_id + '@' + t.occurrence).join('; '),
        sourceLineage: 'Declared initial box: ' + original.initialDomainSource +
          '; restrictions: ' + lineage.map(t => t.source_uri + ' [' + t.independence_group_declared + ']').join('; '),
        leanPredicate: lineage.map(t => t.lean_ref_declared + ':' + t.lean_status_declared).join('; '),
        premiseStatus: branch.declared_evidence === 'SYNTHETIC_ONLY' ? 'SYNTHETIC' : 'CONDITIONAL',
        epochUtc: context.epochUtc, inertialFrame: context.inertialFrame,
      });
    }
    if (failure) { records.push(failure); continue; }
    alternatives.push({
      alternativeId: branch.id, sourceLineage: 'Declared domain, not audited: ' + original.initialDomainSource,
      scenario: { objectNorad: context.objectNorad, epochUtc: context.epochUtc,
        inertialFrame: context.inertialFrame, initial: original.initial, bounds },
    });
    stop('READY_CONDITIONALLY', 'Finite representable subset only; no proof, physical enclosure or 1963 inference');
  }
  return {
    alternatives, records, leanProof: 'NOT_VERIFIED', sourceAuthenticity: 'NOT_VERIFIED',
    sourceIndependence: 'NOT_VERIFIED', unitFromAuditor: 'NOT_PRESENT',
    assumedUnit: 'km/s', frameTransformation: 'NOT_RUN',
    geographicInference: 'NOT_SUPPORTED', exhaustiveEnclosure: false,
  };
}
