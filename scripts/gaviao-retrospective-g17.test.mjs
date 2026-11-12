import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkRefinementTrend} from '../src/lib/orbitEnergyAudit.ts';
import {matrixOccurrenceUrl} from '../src/lib/sourceCitationAudit.ts';

const load = path => readFileSync(new URL('../'+path, import.meta.url),'utf8');
const audit = JSON.parse(load('research/audits/gaviao-main-window-20261112-0942.json'));
const feed = JSON.parse(load('public/data/conde-source-citations.json'));
const support = JSON.parse(load('research/constraints/norad_1963_epoch_availability_C241-L3.json'));
const expectedPRs = [99,100,103,104,106,107,109,108,111,113,115,117];

test('G17 exhausts 12 unique main first-parent squash integrations including after #113', () => {
  assert.equal(audit.schema,'conde.gaviao.retrospective-window/v3');
  assert.deepEqual(audit.github_comparison,{status:'ahead',ahead_by:12,behind_by:0,total_commits:12,first_parent_chain_complete:true,method:audit.github_comparison.method});
  assert.equal(audit.entries.length,12);
  assert.deepEqual(audit.entries.map(x=>x.pr),expectedPRs);
  assert.equal(audit.entries[0].parent_main_sha,audit.reviewed_from_main_sha);
  for(let i=1;i<audit.entries.length;i++){
    assert.equal(audit.entries[i].parent_main_sha,audit.entries[i-1].main_sha);
  }
  assert.equal(audit.entries.at(-1).main_sha,audit.reviewed_through_main_sha);
  assert.equal(new Set(audit.entries.map(x=>x.main_sha)).size,12);
  assert.equal(new Set(audit.entries.map(x=>x.pr_head_sha)).size,12);
  assert.ok(audit.entries.every(x=>x.main_sha.length===40 && x.pr_head_sha.length===40 && x.changed_files.length>0 && x.completed_successful_workflows_on_pr_head>=7));
  assert.deepEqual(audit.direct_commits_in_window,[]);
  assert.deepEqual(audit.closed_without_merge_in_window,[]);
});

test('G17 independently preserves source families and immutable documentary links', () => {
  assert.equal(feed.total_matrix_occurrences,241);
  // G17 historically audited 24 rows. Later verified curation is additive;
  // do not freeze a current, regenerable feed to the G17-era count.
  assert.ok(feed.curated_occurrences >= 24);
  assert.equal(feed.curated_occurrences + feed.unmapped_occurrences,241);
  assert.ok(feed.records.length >= feed.curated_occurrences);
  assert.equal(feed.matrix_git_blob_sha1,'a7978c3a75a153b16ab70118a92c434bba674cb7');
  assert.ok(matrixOccurrenceUrl(100).includes('/blob/faf4dd0fd8dfbdd825e4e934b3b30ebd81bf61df/'));
  assert.ok(!matrixOccurrenceUrl(100).includes('/blob/main/'));
  assert.equal(audit.findings.find(x=>x.id==='G17-F1')?.status,'FIX_IN_G17_PR');
  const science=audit.science;
  assert.match(science.documentary,/O Globo.*original not recovered/);
  assert.match(science.lean,/no original ZIP/i);
  assert.equal(audit.conclusion,'INDETERMINATE');
});

test('G17 temporal proximity is not an authenticated measurement or reduced domain', () => {
  assert.equal(support.id,'C241-L3');
  assert.equal(support.observable.unit,'microseconds');
  assert.equal(support.observable.uncertainty,null);
  assert.equal(support.candidate_forward_dependency.target,'joint 527/528/529 orbital fitting');
  assert.match(audit.entries.find(x=>x.pr===117).scope_and_epistemic_verdict,/secondary|calendar/i);
  assert.equal(audit.notable_workflow_log_evidence.pr117.exact_shared_both,0);
  assert.deepEqual(audit.notable_workflow_log_evidence.pr117.observed_overlap_both_6h_24h_72h,[1,2,15]);
  assert.equal(audit.notable_workflow_log_evidence.pr113.python_unittest_pass,76);
  assert.equal(audit.notable_workflow_log_evidence.pr113.node_test_pass,71);
  assert.match(audit.science.editorial,/#85.*#98.*#116/);
  assert.match(audit.science.editorial,/No stories merged/i);
});

test('G16 9000x Jacobi growth counterexample is now detected, not mistaken for certification', () => {
  const prev={positionKm:0.0001,velocityKmS:0,epochS:0,jacobiKm2S2:0,modeledWorkKm2S2:0};
  const final={...prev,positionKm:0.9};
  const allowance={...prev,positionKm:64*Number.EPSILON*7000};
  assert.ok(final.positionKm<=1);
  assert.ok(final.positionKm<=Math.max(1,1.25*prev.positionKm));
  assert.equal(checkRefinementTrend(prev,final,allowance).status,'GROWTH_BEYOND_ROUNDOFF');
  assert.equal(audit.findings.find(x=>x.id==='G17-F3')?.status,'PR111_FIXED');
  assert.equal(audit.no_blog_publication,true);
});
