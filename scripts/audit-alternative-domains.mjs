// Conditional partition of declared interval domains. Does not validate archival sources, Lean, or orbits.
import { analyze } from './audit-admissible-domain.mjs';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

function must(value, message) {
  if (!value) throw new Error(message);
}

function plain(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

export function analyzeAlternatives(input) {
  must(plain(input), 'alternative record object required');
  must(input.schema === 'conde.alternative-domains/v1', 'unsupported alternative schema');
  must(plain(input.common), 'common domain is required');
  must(input.common.schema === 'conde.admissible-domain/v1', 'common must use admissible-domain/v1');
  must(Array.isArray(input.common.restrictions), 'common restrictions array required');
  must(Array.isArray(input.scenarios) && input.scenarios.length >= 2, 'at least two alternatives required');
  must(input.exhaustive !== true, 'exhaustive coverage cannot be certified from declared scenarios');

  const ids = new Set();
  const results = [];
  for (const scenario of input.scenarios) {
    must(plain(scenario), 'each scenario must be an object');
    const id = scenario.id;
    must(typeof id === 'string' && /^[a-z0-9][a-z0-9-]{1,63}$/.test(id),
      'scenario id must be a stable lowercase slug');
    must(!ids.has(id), 'duplicate scenario id ' + id);
    ids.add(id);
    must(typeof scenario.reason === 'string' && scenario.reason.trim().length > 0,
      'scenario ' + id + ': documented reason required');
    must(Array.isArray(scenario.restrictions) && scenario.restrictions.length > 0,
      'scenario ' + id + ': at least one distinguishing restriction required');
    // Deliberately analyze each source-dependent alternative separately.
    // Intersecting all competing TLEs in one box would invent a contradiction.
    const result = analyze({
      ...input.common,
      restrictions: [...input.common.restrictions, ...scenario.restrictions],
    });
    results.push({
      id,
      reason: scenario.reason,
      trace: [...input.common.restrictions, ...scenario.restrictions].map(r => ({
        parameter: r.parameter,
        evidence_id: r.trace.evidence_id,
        occurrence: r.trace.occurrence,
        source_uri: r.trace.source_uri,
        independence_group_declared: r.trace.independence_group,
        lean_ref_declared: r.formal.lean_ref,
        lean_status_declared: r.formal.status,
      })),
      domain_status: result.domain_status,
      parameters: result.parameters,
      declared_evidence: result.label,
      lean_proofs: result.lean_proofs,
      numerical_holdout: result.numerical_holdout,
    });
  }

  const feasible = results.filter(x => x.domain_status !== 'CONTRADICTORY');
  const status = feasible.length === 0 ? 'NO_DECLARED_FEASIBLE' :
    feasible.length === 1 ? 'ONE_DECLARED_FEASIBLE' : 'MULTIPLE_DECLARED_FEASIBLE';

  return {
    status,
    scenarios_declared: results.length,
    scenarios_with_nonempty_intervals: feasible.length,
    scenarios: results,
    scenario_set_exhaustive: 'NOT_VERIFIED',
    matrix_occurrences: 'NOT_VERIFIED',
    source_authenticity: 'NOT_VERIFIED',
    source_independence_between_scenarios: 'NOT_VERIFIED',
    lean_proofs: 'NOT_VERIFIED',
    physical_feasibility: 'NOT_VERIFIED',
    numerical_holdouts: 'NOT_RUN',
    location_and_impact: 'NOT_INFERRED',
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    must(process.argv.length === 3, 'usage: node scripts/audit-alternative-domains.mjs <record.json>');
    const result = analyzeAlternatives(JSON.parse(readFileSync(process.argv[2], 'utf8')));
    console.log(JSON.stringify(result, null, 2));
    if (result.status === 'NO_DECLARED_FEASIBLE') process.exitCode = 2;
  } catch (error) {
    console.error('Alternative audit rejected input: ' + error.message);
    process.exitCode = 1;
  }
}
