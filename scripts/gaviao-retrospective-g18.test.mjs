import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const audit = JSON.parse(readFileSync('research/audits/gaviao-main-window-20261112-1041.json','utf8'));
const lineages = JSON.parse(readFileSync('research/provenance/lineages.json','utf8'));

test('G18 window is an exhaustive contiguous 14-merge chain, not a PR search subset', () => {
  assert.equal(audit.reviewed_from_main_sha,'cdc32e402e7dee7378f1a92dabac672635a030cc');
  assert.equal(audit.reviewed_through_main_sha,'dfefa93be7a3e6361c7a0ce35fa196d0ef036a65');
  assert.equal(audit.github_comparison.ahead_by,14);
  assert.equal(audit.github_comparison.behind_by,0);
  assert.equal(audit.commits.length,14);
  assert.deepEqual(audit.commits.map(x=>x.pr),[119,112,121,120,123,124,122,125,126,127,128,129,131,132]);
  assert.equal(new Set(audit.commits.map(x=>x.main_merge_sha)).size,14);
  assert.equal(new Set(audit.commits.map(x=>x.pr)).size,14);
  assert.ok(audit.commits.every((x,i)=>
    x.parent_main_sha===(i?audit.commits[i-1].main_merge_sha:audit.reviewed_from_main_sha)
    && x.files.length>0
    && x.github_actions_pr_head.success===x.github_actions_pr_head.total
    && x.github_actions_pr_head.total>=8));
});
test('G18 notes the source lost in #124 and restored without inventing a physical event',()=>{
  assert.equal(audit.findings.find(x=>x.id==='G18-F1').introduced_by_pr,124);
  const record=lineages.post_matrix_occurrences.find(x=>x.id==='NARA-BB-CONDE-20261112-01');
  assert.ok(record,'later merges must not erase a cumulative occurrence');
  assert.equal(record.journalistic_source_independence,'UNRESOLVED');
  assert.equal(record.physical_constraint,null);
  assert.equal(record.newspaper_publication_time,null);
  assert.ok(lineages.sources.some(x=>x.id===record.source_id));
  assert.ok(lineages.sources.some(x=>x.id===record.quoted_source_id&&x.url===null));
  assert.ok(lineages.dependencies.some(x=>x.from===record.source_id && x.to===record.quoted_source_id && x.kind==='quotes_uninspected_source'));
  assert.equal(audit.editorial.merged_stories_in_window,0);
});
test('G18 excludes location and timing inference from documentary-only work',()=>{
  assert.match(audit.scientific_result,/INDETERMINATE/);
  assert.ok(audit.limitations.some(x=>/NARA telegram/.test(x)));
  assert.equal(audit.first_parent_chain.squash_pr_merges,14);
  assert.equal(audit.first_parent_chain.direct_commits,0);
});
