/**
 * C241: conditional mass-budget contract shared across physical and statistical
 * models. These constants come from a SECONDARY GCAT/C61 classification, NOT
 * a measurement of the 1963 separated fragments.
 *
 * A conditional scenario must be supplied explicitly. No historical bound on
 * m527/m528/m529, area, Cd, X, pre-separation losses or epsilon is activated.
 */
import type { Atmosphere } from './orbitPhysics.ts';

export type NoradObject = 527 | 528 | 529;
export type MassBasis =
  | 'GCAT_TOTMASS_1176'
  | 'PAYLOAD_PLUS_STAGE_DRY_1176'
  | 'PAYLOAD_PLUS_STAGE_AT_INSERTION_1206';

export const GCAT_MASS_FIELDS = Object.freeze({
  occurrence: 'C61',
  sourceFamily: 'GCAT_SECONDARY_NOT_ENGINEERING_BREAKUP_INVENTORY',
  payloadOPS0180MassKg: 306,
  payloadOPS0180DryMassKg: 306,
  agenaBMassKg: 900,
  agenaBDryMassKg: 870,
  totalMassAssociatedKg: 1176,
  originalComponentSumKg: 1206,
  referenceEpochUtc: null,
  massOf528Kg: null,
  massOf529Kg: null,
  referenceUncertaintyKg: null,
  completeThreeObjectPartitionAuthenticated: false,
  historicallyCalibrated: false,
} as const);

const BASE_MASS: Readonly<Record<MassBasis, number>> = {
  GCAT_TOTMASS_1176: 1176,
  PAYLOAD_PLUS_STAGE_DRY_1176: 1176,
  PAYLOAD_PLUS_STAGE_AT_INSERTION_1206: 1206,
};

export interface MassBudgetScenario {
  readonly schema: 'conde.conditional-three-object-mass/v1';
  readonly sourceOccurrence: 'C61';
  /** Explicitly hypothetical mass basis, never silently selected. */
  readonly basis: MassBasis;
  /** User/model declared accounting convention; not authenticated UTC. */
  readonly referenceEpochDescription: string;
  /** Physical mass assigned to each tracked object AT THAT SAME reference. */
  readonly massesKg: Readonly<Record<NoradObject, number>>;
  /** Separate components outside 527/528/529 at the chosen reference epoch. */
  readonly untrackedKg: number;
  /** Matter lost between a prior inventory and this accounting instant. */
  readonly priorLossKg: number;
  /** Signed discrepancy with the source's approximate inventory. */
  readonly catalogErrorKg: number;
  /** Optional retained OPS mass, when a physical scenario supplies it. */
  readonly opsPayloadRetainedBy527Kg?: number;
}

export interface MassScenarioAudit {
  readonly basis: MassBasis;
  readonly nominalKg: number;
  readonly accountedKg: number;
  readonly catalogCorrectedKg: number;
  readonly arithmeticResidualKg: number;
  readonly mathematicallyConsistent: boolean;
  readonly historicalConstraintActive: false;
  readonly classification: 'CONDITIONAL_NOT_HISTORICALLY_CALIBRATED';
  readonly sourceOccurrence: 'C61';
  readonly requires: readonly string[];
}

const assertFinite = (value: number, context: string): number => {
  if (typeof value !== 'number' || !Number.isFinite(value))
    throw new RangeError('Finite number required: ' + context);
  return value;
};
const nonnegative = (value: number, context: string): number => {
  if (assertFinite(value, context) < 0)
    throw new RangeError('Nonnegative value required: ' + context);
  return value;
};
const positive = (value: number, context: string): number => {
  if (assertFinite(value, context) <= 0)
    throw new RangeError('Positive value required: ' + context);
  return value;
};

/** Conservation in ONE conditional accounting system. Tolerances here are
 * floating point numerical roundoff, NOT historical instrumental error.
 */
export function auditMassBudgetScenario(s: MassBudgetScenario): MassScenarioAudit {
  if (!s || s.schema !== 'conde.conditional-three-object-mass/v1' ||
      s.sourceOccurrence !== GCAT_MASS_FIELDS.occurrence ||
      !(s.basis in BASE_MASS) ||
      !s.referenceEpochDescription?.trim())
    throw new RangeError('Explicit mass scenario, source and reference convention required');
  const exactIds = Object.keys(s.massesKg ?? {}).sort();
  if (exactIds.join(',') !== '527,528,529')
    throw new RangeError('All three individual object masses required');
  for (const id of [527, 528, 529] as const)
    positive(s.massesKg[id], 'm'+id);
  nonnegative(s.untrackedKg, 'untracked X');
  nonnegative(s.priorLossKg, 'pre-separation losses');
  assertFinite(s.catalogErrorKg, 'catalog signed epsilon');
  const nominalKg = BASE_MASS[s.basis];
  const accountedKg = s.massesKg[527] + s.massesKg[528] + s.massesKg[529] +
    s.untrackedKg + s.priorLossKg;
  const catalogCorrectedKg = nominalKg + s.catalogErrorKg;
  if (catalogCorrectedKg <= 0)
    throw new RangeError('Catalog-corrected total must be positive');
  if (s.opsPayloadRetainedBy527Kg !== undefined) {
    const retained = nonnegative(s.opsPayloadRetainedBy527Kg, 'OPS retained mass');
    if (retained > GCAT_MASS_FIELDS.payloadOPS0180MassKg ||
        retained > s.massesKg[527])
      throw new RangeError('Retained payload exceeds source OPS or assigned 527 mass');
  }
  const arithmeticResidualKg = accountedKg - catalogCorrectedKg;
  return {
    basis: s.basis, nominalKg, accountedKg, catalogCorrectedKg, arithmeticResidualKg,
    mathematicallyConsistent:
      Math.abs(arithmeticResidualKg) <= 1e-10 * Math.max(1, catalogCorrectedKg),
    historicalConstraintActive: false,
    classification: 'CONDITIONAL_NOT_HISTORICALLY_CALIBRATED',
    sourceOccurrence: 'C61',
    requires: [
      'source semantics at separation epoch',
      'physical identity of separated components',
      'independent bound on X and prior losses',
      'instrument/catlog mass uncertainty and drag/geometry provenance',
    ],
  };
}

/** No physical upper bound follows from the approximate GCAT total until
 * a maximum absolute catalog error is independently supplied. Caps for X and
 * prior loss are optional; omitted caps imply NO positive lower tracked sum.
 */
export function conditionalTrackedMassEnvelope(input: {
  readonly basis: MassBasis;
  readonly maxAbsCatalogErrorKg: number | null;
  readonly maxUntrackedKg: number | null;
  readonly maxPriorLossKg: number | null;
  readonly minRetainedPayloadIn527Kg?: number | null;
}) {
  if (!input || !(input.basis in BASE_MASS))
    throw new RangeError('Explicit mass basis required');
  const E = input.maxAbsCatalogErrorKg;
  const X = input.maxUntrackedKg;
  const L = input.maxPriorLossKg;
  if (E !== null) nonnegative(E, 'catalog error cap');
  if (X !== null) nonnegative(X, 'X cap');
  if (L !== null) nonnegative(L, 'prior loss cap');
  if (input.minRetainedPayloadIn527Kg != null)
    nonnegative(input.minRetainedPayloadIn527Kg, 'OPS retained lower bound');
  const upper = E === null ? null : BASE_MASS[input.basis] + E;
  const lower = (E === null || X === null || L === null) ? 0 :
    Math.max(0, BASE_MASS[input.basis] - E - X - L);
  const retained = input.minRetainedPayloadIn527Kg ?? null;
  if (retained !== null && retained > GCAT_MASS_FIELDS.payloadOPS0180MassKg)
    throw new RangeError('Retained payload lower bound exceeds nominal OPS mass');
  const remainingUpper = (retained !== null && upper !== null) ?
    Math.max(0, upper - retained) : null;
  return {
    trackedTotalInfimumKg: upper === null ? null : lower,
    trackedTotalSupremumKg: upper,
    individualMassUpperExclusiveKg: upper,
    othersPlusXAndLossUpperKgIfPayloadRetained: remainingUpper,
    massLowerBoundForAnyIndividualKg: null,
    historicalConstraintActive: false as const,
    requiresSourceCalibratedCaps: true as const,
  };
}

export interface DragGeometryScenario {
  readonly object: NoradObject;
  readonly projectedAreaM2: number;
  readonly dragCoefficient: number;
  readonly geometrySource: string;
  /** Physically sourced geometry? false for all current 1963 cases. */
  readonly historicalGeometryAuthenticated: boolean;
}

/** A/m and B = Cd A/m are identified in a *scenario* only; the GCAT mass
 * budget alone neither measures Cd nor constrains projected area.
 */
export function ballisticFromMassScenario(
  scenario: MassBudgetScenario, geometry: DragGeometryScenario,
): {object: NoradObject; areaOverMassM2Kg: number;
    cdAreaOverMassM2Kg: number; historicalConstraintActive: false;
    budgetConsistent: boolean; provenance: string} {
  const audit = auditMassBudgetScenario(scenario);
  if (![527,528,529].includes(geometry.object))
    throw new RangeError('Invalid NORAD for drag geometry');
  const area = positive(geometry.projectedAreaM2, 'projected area');
  const cd = positive(geometry.dragCoefficient, 'drag coefficient');
  if (!geometry.geometrySource?.trim())
    throw new RangeError('Geometry source/assumption required');
  if (geometry.historicalGeometryAuthenticated)
    throw new RangeError('Cannot claim authenticated 1963 projected area from this scenario');
  const m = scenario.massesKg[geometry.object];
  return {
    object: geometry.object, areaOverMassM2Kg: area / m,
    cdAreaOverMassM2Kg: cd * area / m,
    historicalConstraintActive: false,
    budgetConsistent: audit.mathematicallyConsistent,
    provenance: geometry.geometrySource + ' | GCAT C61 conditional '+scenario.basis,
  };
}

/** Adapter used by orbitPhysics propagation and source-declared MSISE density
 * models, preventing an unrelated B coefficient from silently bypassing mass
 * conservation. Explicit caller opt-in; old unconstrained paths stay labelled.
 */
export function atmosphereForMassScenario(
  atmosphere: Atmosphere, scenario: MassBudgetScenario,
  geometry: DragGeometryScenario,
): Atmosphere {
  if (!atmosphere?.source?.trim() || typeof atmosphere.densityKgM3 !== 'function')
    throw new RangeError('Sourced atmosphere and density callback required');
  const b = ballisticFromMassScenario(scenario, geometry);
  if (!b.budgetConsistent)
    throw new RangeError('Mass partition fails conditional conservation');
  return {
    densityKgM3: atmosphere.densityKgM3,
    cdAreaOverMassM2Kg: b.cdAreaOverMassM2Kg,
    source: atmosphere.source+'; '+b.provenance+'; SCENARIO_ONLY_NOT_HISTORICAL_CALIBRATION',
  };
}

/** Geometric area may be bounded only when MASS, aerodynamic Cd, and the
 * independently calibrated B interval all have sourced finite bounds.
 * No one of them follows solely from C61, even if total 1176 is assumed.
 */
export function conditionalProjectedAreaEnvelope(input: {
  readonly massMinKg: number | null;
  readonly massMaxKg: number | null;
  readonly bMinM2Kg: number | null;
  readonly bMaxM2Kg: number | null;
  readonly cdMin: number | null;
  readonly cdMax: number | null;
}) {
  const vals = Object.values(input);
  if (vals.some(v => v === null))
    return {areaMinM2:null,areaMaxM2:null,
      historicalConstraintActive:false as const,
      reason:'Mass, B and Cd are not jointly calibrated'};
  const [mLo,mHi,bLo,bHi,cdLo,cdHi] = vals as number[];
  positive(mLo,'lower mass');positive(mHi,'upper mass');
  nonnegative(bLo,'lower B');nonnegative(bHi,'upper B');
  positive(cdLo,'lower Cd');positive(cdHi,'upper Cd');
  if (mLo>mHi || bLo>bHi || cdLo>cdHi)
    throw new RangeError('Ordered mass, B and Cd ranges required');
  return {
    areaMinM2:bLo*mLo/cdHi,
    areaMaxM2:bHi*mHi/cdLo,
    historicalConstraintActive:false as const,
    reason:'Conditioned on separately sourced masses, B and Cd',
  };
}

/** Equivalent circular projected diameter only if the analyst explicitly
 * selects that shape; it is not a measured maximum dimension or breakup size.
 */
export function conditionalCircularProjectedDiameter(
  areaMinM2: number | null, areaMaxM2: number | null,
  geometryModel: 'EXPLICIT_EQUIVALENT_CIRCULAR_PROJECTION',
) {
  if (geometryModel !== 'EXPLICIT_EQUIVALENT_CIRCULAR_PROJECTION')
    throw new RangeError('Projected shape must be explicitly declared');
  if (areaMinM2 === null || areaMaxM2 === null)
    return {minDiameterM:null,maxDiameterM:null,historicalConstraintActive:false as const};
  nonnegative(areaMinM2,'lower projected area');
  nonnegative(areaMaxM2,'upper projected area');
  if (areaMinM2>areaMaxM2)
    throw new RangeError('Inverted projected-area bounds');
  return {
    minDiameterM:Math.sqrt(4*areaMinM2/Math.PI),
    maxDiameterM:Math.sqrt(4*areaMaxM2/Math.PI),
    historicalConstraintActive:false as const,
  };
}

/** Inverse feasibility can compare required B with explicit A,Cd,m scenario;
 * without independently constrained area/Cd this MUST NOT reject a historic
 * orbit. A Boolean match here is only numeric compatibility with the scenario.
 */
export function conditionalBallisticCompatibility(
  requiredB: number, scenario: MassBudgetScenario,
  geometry: DragGeometryScenario, allowedRelativeDeviation: number,
) {
  nonnegative(requiredB, 'inverse required B');
  nonnegative(allowedRelativeDeviation, 'assumed scenario B relative tolerance');
  const b = ballisticFromMassScenario(scenario, geometry);
  return {
    compatibleWithChosenScenario: b.budgetConsistent &&
      Math.abs(b.cdAreaOverMassM2Kg - requiredB) <=
        allowedRelativeDeviation * Math.max(b.cdAreaOverMassM2Kg,requiredB,1e-15),
    historicalExclusion: false as const,
    historicalErrorBound: null,
    scenarioB: b.cdAreaOverMassM2Kg,
  };
}
