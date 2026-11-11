import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const ledger = JSON.parse(readFileSync(new URL('../research/gaviao_source_ledger_2026-11-11.json', import.meta.url), 'utf8'));
const index = new Map(ledger.claims.map(claim => [claim.id, claim]));

function audit(data) {
  const errors = [];
  const ids = new Set();
  const mandatory = ['GAV-NASA-01', 'GAV-FBIS-02', 'GAV-TV-03', 'GAV-RV-04', 'GAV-RAAN-05', 'GAV-BB-06', 'GAV-PRESS-07'];
  for (const claim of data.claims ?? []) {
    if (ids.has(claim.id)) errors.push(`Duplicate claim ID: ${claim.id}`);
    ids.add(claim.id);
    if (!/^https:\/\//.test(claim.source_url ?? '')) errors.push(`Missing HTTPS source: ${claim.id}`);
    if (!(claim.matrix_ids?.length > 0)) errors.push(`Missing cumulative-matrix identifiers: ${claim.id}`);
    if (!(claim.supports?.length > 0) || !(claim.does_not_support?.length > 0)) errors.push(`Missing evidence limits: ${claim.id}`);
    if (!claim.verification || !claim.source_family || !claim.source_kind) errors.push(`Missing provenance classification: ${claim.id}`);
    for (const forbidden of ['physical_impact_conde', 'reentry_coordinates', 'impact_probability', 'independent_witness', 'hoax_physical_proof']) {
      if (claim.supports?.includes(forbidden)) errors.push(`Unjustified physical conclusion: ${claim.id} / ${forbidden}`);
    }
  }
  for (const id of mandatory) if (!ids.has(id)) errors.push(`Missing required claim ${id}`);
  const get = id => data.claims.find(c => c.id === id) ?? {};
  const has = (id, key, value) => {
    if (!(get(id)[key] ?? []).includes(value)) errors.push(`Missing caveat: ${id} / ${value}`);
  };
  has('GAV-NASA-01', 'supports', 'historically_reported_decay_day');
  has('GAV-NASA-01', 'does_not_support', 'decay_time');
  has('GAV-NASA-01', 'does_not_support', 'reentry_coordinates');
  has('GAV-NASA-01', 'does_not_support', 'physical_impact_conde');
  has('GAV-FBIS-02', 'does_not_support', 'crater_observed');
  has('GAV-FBIS-02', 'does_not_support', 'narrative_added_later');
  has('GAV-FBIS-02', 'does_not_support', 'clock_zone_2330');
  has('GAV-TV-03', 'does_not_support', 'new_original_discovery_in_pr8');
  has('GAV-TV-03', 'does_not_support', 'radio_tupi_rio_silence');
  has('GAV-RV-04', 'does_not_support', 'real_527_529_holdout');
  has('GAV-RV-04', 'does_not_support', 'impact_probability');
  has('GAV-RAAN-05', 'does_not_support', 'correct_raan_selection');
  has('GAV-BB-06', 'does_not_support', 'hoax_physical_proof');
  has('GAV-BB-06', 'does_not_support', 'authenticated_case_file');
  has('GAV-PRESS-07', 'does_not_support', 'identical_original_dispatch');
  if (get('GAV-NASA-01').source_family === get('GAV-FBIS-02').source_family)
    errors.push('Orbital and journalism lineages mistakenly conflated');
  if (get('GAV-BB-06').verification !== 'prior_matrix_text_extraction_no_visual_facsimile')
    errors.push('Blue Book index improperly promoted to direct visual verification');
  if (get('GAV-TV-03').verification !== 'matrix_prior_visual_inspection_not_repeated')
    errors.push('TV script falsely reported as newly read in this review');
  if (!/^https:\/\//.test(data.source_matrix ?? '')) errors.push('Missing cumulative matrix source');
  return errors;
}

const clone = () => structuredClone(ledger);

test('every ledger claim has provenance, stable original matrix IDs and explicit limits', () => {
  assert.equal(ledger.schema_version, 1);
  assert.equal(index.size, ledger.claims.length);
  assert.deepEqual(audit(ledger), []);
});

test('reject a fictional terminal coordinate promoted from the NASA decay date', () => {
  const changed = clone();
  changed.claims[0].supports.push('reentry_coordinates');
  assert.match(audit(changed).join('; '), /Unjustified physical conclusion/);
});

test('reject omission of the missing time in NASA date-only evidence', () => {
  const changed = clone();
  changed.claims[0].does_not_support = changed.claims[0].does_not_support.filter(x => x !== 'decay_time');
  assert.match(audit(changed).join('; '), /Missing caveat/);
});

test('reject an FBIS transcript being treated as observed crater or later narrative embellishment', () => {
  const changed = clone();
  changed.claims[1].supports.push('physical_impact_conde');
  changed.claims[1].does_not_support = changed.claims[1].does_not_support.filter(x => x !== 'narrative_added_later');
  assert.ok(audit(changed).length >= 2);
});

test('reject relabeling already recorded TV-script inspection as a new independent discovery', () => {
  const changed = clone();
  changed.claims[2].verification = 'direct_visual_page';
  assert.match(audit(changed).join('; '), /falsely reported as newly read/);
});

test('reject turning synthetic orbit tests into a real blind holdout', () => {
  const changed = clone();
  changed.claims[3].does_not_support = changed.claims[3].does_not_support.filter(x => x !== 'real_527_529_holdout');
  assert.match(audit(changed).join('; '), /Missing caveat/);
});

test('reject promoting Blue Book index text into authenticated case-file inspection', () => {
  const changed = clone();
  changed.claims[5].verification = 'direct_visual_page';
  assert.match(audit(changed).join('; '), /improperly promoted/);
});

test('reject broken source lineage and missing provenance link', () => {
  const changed = clone();
  changed.claims[6].source_url = 'not-a-source';
  changed.claims[6].matrix_ids = [];
  assert.ok(audit(changed).some(e => e.includes('Missing HTTPS source')));
  assert.ok(audit(changed).some(e => e.includes('Missing cumulative-matrix')));
});
