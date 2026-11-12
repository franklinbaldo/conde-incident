// Exact-interval sensitivity and deletion-minimal contradiction witnesses.
// Epistemic status remains declared/synthetic. This is not orbital inference.
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { analyze } from './audit-admissible-domain.mjs';
import { analyzeAlternatives } from './audit-alternative-domains.mjs';

function trace(record, i) {
  const r = record.restrictions[i];
  return {
    ordinal: i + 1,
    parameter: r.parameter,
    evidence_id: r.trace.evidence_id,
    occurrence: r.trace.occurrence,
    source_uri: r.trace.source_uri,
    independence_group_declared: r.trace.independence_group,
    verification_declared: r.trace.verification,
    assumption: r.assumption,
    lean_ref_declared: r.formal.lean_ref,
    lean_status_declared: r.formal.status,
  };
}

// Reuse the existing rational BigInt interval engine, never round to Number.
function withRestrictions(record, parameter, indices) {
  return analyze({
    ...record,
    parameters: [parameter],
    restrictions: indices.map(i => record.restrictions[i]),
  }).parameters[0];
}

export function auditDomainSensitivity(record) {
  // Validate the ENTIRE record first, including cross-parameter ID/source conflicts.
  const full = analyze(record);
  const parameters = record.parameters.map(parameter => {
    const indices = record.restrictions.flatMap((r, i) =>
      r.parameter === parameter.name ? [i] : []);
    const assessed = withRestrictions(record, parameter, indices);
    if (assessed.admissible === null) {
      // Construct a deletion-minimal core, including the declared INITIAL interval.
      // It is not necessarily the smallest cardinality core or a physical refutation.
      let core = [...indices];
      for (const index of indices) {
        const candidate = core.filter(i => i !== index);
        if (withRestrictions(record, parameter, candidate).admissible === null) {
          core = candidate;
        }
      }
      return {
        name: parameter.name,
        unit: parameter.unit,
        status: 'EMPTY',
        initial_interval: assessed.initial,
        deletion_minimal_conflict: core.map(i => trace(record, i)),
        initial_interval_is_part_of_witness: true,
        conflict_scope: 'DECLARED_INTERVALS_ONLY',
      };
    }
    const pivotal = [];
    const notIndividuallyPivotal = [];
    for (const index of indices) {
      const removed = withRestrictions(record, parameter, indices.filter(i => i !== index));
      const change = JSON.stringify(removed.admissible) !==
        JSON.stringify(assessed.admissible);
      (change ? pivotal : notIndividuallyPivotal).push(trace(record, index));
    }
    return {
      name: parameter.name,
      unit: parameter.unit,
      status: assessed.status,
      initial_interval: assessed.initial,
      admissible_interval: assessed.admissible,
      individually_pivotal: pivotal,
      not_individually_pivotal: notIndividuallyPivotal,
      caution: 'An individually non-pivotal bound can still matter jointly with duplicated bounds.',
    };
  });
  return {
    schema: 'conde.domain-sensitivity-report/v1',
    input_kind: record.kind,
    evidence_label: full.label,
    domain_status: full.domain_status,
    parameters,
    independence: 'DECLARED_NOT_AUDITED',
    matrix_occurrences: 'NOT_VERIFIED',
    lean_proofs: 'NOT_VERIFIED',
    dynamics_and_holdouts: 'NOT_RUN',
    location_and_impact: 'NOT_INFERRED',
  };
}

export function auditAlternativeSensitivity(input) {
  const alternatives = analyzeAlternatives(input);
  const scenarios = input.scenarios.map(scenario => ({
    id: scenario.id,
    result: auditDomainSensitivity({
      ...input.common,
      restrictions: [...input.common.restrictions, ...scenario.restrictions],
    }),
  }));
  return {
    schema: 'conde.alternative-sensitivity-report/v1',
    status: alternatives.status,
    scenarios,
    scenario_set_exhaustive: 'NOT_VERIFIED',
    source_independence_between_scenarios: 'NOT_VERIFIED',
    physical_feasibility: 'NOT_VERIFIED',
    location_and_impact: 'NOT_INFERRED',
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    if (process.argv.length !== 3) throw new Error('usage: node scripts/audit-domain-sensitivity.mjs <record.json>');
    const input = JSON.parse(readFileSync(process.argv[2], 'utf8'));
    const result = input.schema === 'conde.admissible-domain/v1'
      ? auditDomainSensitivity(input)
      : input.schema === 'conde.alternative-domains/v1'
        ? auditAlternativeSensitivity(input)
        : (() => { throw new Error('unsupported schema'); })();
    console.log(JSON.stringify(result, null, 2));
    if (result.domain_status === 'CONTRADICTORY' ||
        result.status === 'NO_DECLARED_FEASIBLE') process.exitCode = 2;
  } catch (e) {
    console.error('Sensitivity audit rejected input: ' + e.message);
    process.exitCode = 1;
  }
}
