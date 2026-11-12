import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const audit = JSON.parse(readFileSync('research/audits/gaviao-main-window-20261112-1136.json', 'utf8'));
const provenance = JSON.parse(readFileSync('research/provenance/lineages.json', 'utf8'));

test('G19 covers the exact thirteen contiguous squash merges after G18', () => {
  assert.equal(audit.reviewed_from_main_sha, 'dfefa93be7a3e6361c7a0ce35fa196d0ef036a65');
  assert.equal(audit.reviewed_through_main_sha, '9e6596c679985b2cc886e31d88969fd9eab16b18');
  assert.equal(audit.github_comparison.ahead_by, 13);
  assert.equal(audit.github_comparison.behind_by, 0);
  assert.equal(audit.commits.length, 13);
  assert.equal(audit.first_parent_chain.direct_commits, 0);
  assert.deepEqual(audit.commits.map(c => c.pr), [134, 135, 138, 137, 139, 140, 141, 143, 142, 144, 145, 146, 147]);
  assert.equal(new Set(audit.commits.map(c => c.main_merge_sha)).size, 13);
  assert.equal(new Set(audit.commits.map(c => c.pr)).size, 13);
  assert.ok(audit.commits.every((c,i) =>
    c.parent_main_sha === (i ? audit.commits[i-1].main_merge_sha : audit.reviewed_from_main_sha) &&
    /^[a-f0-9]{40}$/.test(c.pr_final_head_sha) && c.files.length > 0 &&
    c.github_actions_pr_head.total >= 9 &&
    c.github_actions_pr_head.total === c.github_actions_pr_head.success));
  assert.equal(audit.commits.flatMap(c => c.files).length, 58);
});

test('G19 preserves the NARA occurrence and does not convert reporting to observation', () => {
  const row = provenance.post_matrix_occurrences.find(o => o.id === 'NARA-BB-CONDE-20261112-01');
  assert.ok(row, 'G18 NARA restoration must survive G19 changes');
  assert.equal(row.journalistic_source_independence, 'UNRESOLVED');
  assert.equal(row.physical_constraint, null);
  assert.equal(row.newspaper_publication_time, null);
  assert.equal(audit.source_integrity.NARA_addendum, row.id);
  assert.equal(audit.editorial.merged_stories, 0);
  assert.match(audit.scientific_result, /INDETERMINATE/);
});

test('G19 identifies a control-plane race but never claims a physical or Pages deployment proof', () => {
  const bug = audit.findings.find(x => x.id === 'G19-F1');
  assert.equal(bug.introduced_by_pr, 143);
  assert.match(bug.counterexample, /run_attempt/);
  assert.match(bug.counterexample, /status id/);
  assert.equal(audit.editorial.site_published_verified, false);
  assert.equal(audit.editorial.repo_has_pages, false);
});
