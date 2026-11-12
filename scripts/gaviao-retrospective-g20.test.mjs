import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { isDeclaredDependenceFeed, declaredLineageContext, citationContext } from '../src/lib/sourceCitationAudit.ts';

const audit = JSON.parse(readFileSync(new URL('../research/audits/gaviao-main-window-20261112-1244.json', import.meta.url)));
const dependence = JSON.parse(readFileSync(new URL('../public/data/conde-declared-dependence.json', import.meta.url)));
const citations = JSON.parse(readFileSync(new URL('../public/data/conde-source-citations.json', import.meta.url)));
const provenance = JSON.parse(readFileSync(new URL('../research/provenance/lineages.json', import.meta.url)));
const clone = value => JSON.parse(JSON.stringify(value));

test('G20 enumerates every one of fourteen consecutive main merges since G19', () => {
  assert.equal(audit.reviewed_from_main_sha, '9e6596c679985b2cc886e31d88969fd9eab16b18');
  assert.equal(audit.reviewed_through_main_sha, '5c2f610d624a79dab9b4b181851d8fe2883868f5');
  assert.equal(audit.github_comparison.ahead_by, 14);
  assert.equal(audit.github_comparison.behind_by, 0);
  assert.equal(audit.first_parent_chain.squash_pr_merges, 14);
  assert.equal(audit.first_parent_chain.direct_commits, 0);
  assert.deepEqual(audit.commits.map(c => c.pr),
    [150,151,152,153,154,155,160,157,159,161,163,162,164,166]);
  assert.equal(audit.commits.length, 14);
  assert.ok(audit.commits.every((c, i) =>
    c.parent_main_sha === (i ? audit.commits[i-1].main_merge_sha : audit.reviewed_from_main_sha) &&
    /^[a-f0-9]{40}$/.test(c.pr_final_head_sha) &&
    c.github_actions_pr_head.total === c.github_actions_pr_head.success &&
    c.files.length > 0));
  assert.equal(audit.commits.flatMap(c => c.files).length, 62);
  assert.equal(new Set(audit.commits.flatMap(c => c.files.map(f => f.path))).size, 60);
  assert.deepEqual(audit.closed_unmerged_in_window.map(x => x.pr), [22]);
  assert.equal(audit.scientific_axes.inference, 'CONDE_INDETERMINATE_NO_TERMINAL_HOUR_COORDINATE_OR_IMPACT_EVIDENCE');
});

test('G20 retains previously integrated NARA occurrence and declared family limits', () => {
  const nara = provenance.post_matrix_occurrences.find(x => x.id === 'NARA-BB-CONDE-20261112-01');
  assert.ok(nara, 'NARA row lost from cumulative provenance');
  assert.equal(nara.physical_constraint, null);
  assert.equal(nara.journalistic_source_independence, 'UNRESOLVED');
  assert.equal(isDeclaredDependenceFeed(dependence), true);
  assert.equal(dependence.epistemic_limits.independent_physical_observation_count, null);
});

test('G20-F1 rejects an ancestry edge beginning at a different document', () => {
  const malformed = clone(dependence);
  const row = malformed.citation_lineages.find(x => x.source_id === 'FBIS_EOP_UAP_D001');
  assert.ok(row);
  row.declared_upstream_paths[0].edges[0].from = 'NASA_SSR_19631115';
  assert.equal(isDeclaredDependenceFeed(malformed), false);
  const original = citationContext(citations, 'C01#1');
  assert.equal(original.state, 'mapped');
  assert.equal(declaredLineageContext(dependence, citations, original.record).state, 'declared');
});

test('G20-F1 rejects disconnected chains, fake terminal ancestry and cycles', () => {
  const change = fn => {
    const malformed = clone(dependence);
    const row = malformed.citation_lineages.find(x => x.source_id === 'FBIS_EOP_UAP_D001');
    fn(row.declared_upstream_paths[0]);
    assert.equal(isDeclaredDependenceFeed(malformed), false);
  };
  change(path => path.upstream_source_id = 'NTRS_19640001198');
  change(path => path.edges.push({from:'UNRELATED',to:'SECOND',kind:'copies'}));
  change(path => path.edges.push({from:'RADIO_TUPI_19631108',to:'FBIS_EOP_UAP_D001',kind:'cycle'}));
  change(path => path.edges = []);
});

test('G20-F1 rejects duplicate or wrongly qualified snapshot rows', () => {
  const duplicate = clone(dependence);
  duplicate.citation_lineages.push(clone(duplicate.citation_lineages[0]));
  assert.equal(isDeclaredDependenceFeed(duplicate), false);
  const stale = clone(dependence);
  stale.citation_lineages[0].snapshot_ref =
    'matrix:0000000000000000000000000000000000000000:C01#1';
  assert.equal(isDeclaredDependenceFeed(stale), false);
  const invalid = clone(dependence);
  invalid.citation_lineages[0].snapshot_ref =
    'matrix:' + invalid.matrix_git_blob_sha1 + ':C01';
  assert.equal(isDeclaredDependenceFeed(invalid), false);
});

test('G20 keeps legitimate zero-edge rows without claiming physical independence', () => {
  const nasa = citationContext(citations, 'C197#1');
  assert.equal(nasa.state, 'mapped');
  const lineage = declaredLineageContext(dependence, citations, nasa.record);
  assert.equal(lineage.state, 'declared');
  assert.equal(lineage.paths.length, 0);
  assert.equal(isDeclaredDependenceFeed(dependence), true);
});
