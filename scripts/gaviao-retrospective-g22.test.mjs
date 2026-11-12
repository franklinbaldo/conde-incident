import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const audit = JSON.parse(readFileSync(new URL('../research/audits/gaviao-main-window-20261112-g22.json',import.meta.url),'utf8'));
test('G22: thirteen consecutive first-parent integrations and two non-main side-branch commits',()=>{
 const a=audit.first_parent_integrations, g=audit.git_graph;
 assert.equal(a.length,13);
 assert.equal(g.first_parent_integrations,13);
 assert.equal(g.total_reachable_commits,15);
 assert.equal(g.squash_merges,12);
 assert.equal(g.ordinary_merge_commits,1);
 assert.equal(g.main_direct_commits,0);
 let prior=audit.reviewed_from_main_sha;
 for (const row of a) {
   assert.equal(row.first_parent,prior);
   assert.equal(row.parents[0],prior);
   assert.match(row.merge_sha,/^[0-9a-f]{40}$/);
   assert.match(row.pr_head_sha,/^[0-9a-f]{40}$/);
   assert.ok(row.changed_files.length);
   prior=row.merge_sha;
 }
 assert.equal(prior,audit.reviewed_through_main_sha);
 assert.equal(new Set([...a.map(r=>r.merge_sha),...audit.side_branch_commits.map(r=>r.sha)]).size,15);
 const two=a.find(r=>r.pr===185);
 assert.equal(two.merge_mode,'merge');
 assert.equal(two.parents[1],audit.side_branch_commits[1].sha);
 assert.equal(audit.side_branch_commits[0].parent,audit.reviewed_from_main_sha);
 assert.equal(audit.side_branch_commits[1].parent,audit.side_branch_commits[0].sha);
});
test('G22: no canceled workflow is silently counted as a PASS',()=>{
 const rows=audit.first_parent_integrations;
 assert.deepEqual(rows.filter(r=>r.ci.cancelled!==0).map(r=>r.pr),[193,194,195]);
 for(const row of rows){
   assert.equal(row.ci.success+row.ci.cancelled,row.ci.total);
   assert.ok(row.ci.success>=13);
   if(row.ci.cancelled)assert.equal(row.ci.cancelled_workflow,'Publish Conde site');
 }
});
test('G22: documentary and physical conclusions remain separate',()=>{
 assert.equal(audit.verification.conde_impact,'INDETERMINATE');
 assert.equal(audit.verification.numeric_historical_holdout,'NOT_VALIDATED');
 assert.equal(audit.verification.lean_4_35_physical_location,'NOT_PROVED');
 assert.equal(audit.verification.primary_facsims_retrieved_this_round,false);
});
