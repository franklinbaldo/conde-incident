import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkRefinementTrend} from '../src/lib/orbitEnergyAudit.ts';
const read = path => readFileSync(new URL('../'+path, import.meta.url), 'utf8');
const m=JSON.parse(read('research/audits/gaviao-main-window-20261112-0838.json'));
const graph=JSON.parse(read('research/constraints/ssr_1963_observable_graph.json'));
const weather=JSON.parse(read('research/constraints/igra_bahia_1963_coverage.json'));
test('G16 window exhausts eight consecutive main first-parent squash merges',()=>{
 assert.equal(m.ahead_by,8); assert.equal(m.behind_by,0);
 assert.equal(m.entries.length,8);
 assert.deepEqual(m.entries.map(e=>e.pr),[90,92,91,78,94,95,96,97]);
 assert.equal(m.entries[0].parent_main_sha,m.base_sha);
 for(let i=1;i<m.entries.length;i++) assert.equal(m.entries[i].parent_main_sha,m.entries[i-1].main_sha);
 assert.equal(m.entries.at(-1).main_sha,m.observed_main_head_sha);
 assert.equal(new Set(m.entries.map(e=>e.main_sha)).size,8);
 assert.deepEqual(m.direct_commits_in_interval,[]);
 assert.deepEqual(m.closed_without_merge_in_interval,[]);
 assert.ok(m.entries.every(e=>e.changed_files.length && e.pr_head_sha.length===40 && e.all_reported_workflows_success && e.reported_successful_workflows>=6));
});
test('G16 does not promote secondary TLE or NASA publication epoch into an observation',()=>{
 const tle=graph.observations.filter(o=>o.object_id===528);
 assert.equal(tle.length,6);
 assert.equal(new Set(tle.map(o=>o.source_id)).size,1);
 assert.ok(tle.every(o=>o.observed_at_utc===null && o.measurement_error===null && o.constraint_status==='CANDIDATE_NOT_ACTIVATED'));
 assert.ok(graph.observations.filter(o=>[527,529].includes(o.object_id)).every(o=>o.observed_at_utc===null));
 assert.equal(new Set(graph.sources.map(s=>s.upstream_tracking_family)).size,1);
 assert.ok(graph.physical_bridges.every(b=>b.physical_domain==='NOT_NARROWED_UNCALIBRATED_SOURCE'));
});
test('G16 NOAA archive gaps are not evidence of no historical balloon',()=>{
 assert.equal(weather.evidence.length,4);
 assert.equal(weather.dependencies.length,4);
 const entries=new Map(weather.evidence.map(e=>[e.station_name??e.archive_id,e]));
 for(const [station,year] of [['SALVADOR',1970],['ARACAJU',1974]]){
   const e=entries.get(station);
   assert.equal(e.record_first_year,year);
   assert.equal(e.value,false);
   assert.equal(e.type,'ARCHIVE_COVERAGE_NOT_BALLOON_EXISTENCE');
   assert.equal(e.physical_constraint_status,'NOT_APPLICABLE');
 }
 assert.equal(entries.get('RECIFE').value,true);
 assert.equal(entries.get('d394001').value,null);
 assert.equal(weather.connectivity_delta.hard_physical_constraints_added,0);
 assert.match(weather.physical_domain_status,/NOT_YET_EVALUABLE/);
});
test('G16 preserves historical finding and tests Castor corrective trend guard',()=>{
 // The G16 audit is an immutable historical snapshot: finding status was OPEN.
 // Do not require the bug to remain in current HEAD after a corrective PR.
 const energy=read('src/lib/orbitEnergyAudit.ts');
 assert.ok(!energy.includes('final[k] <= Math.max(limits[k], 1.25 * previous[k])'));
 const previous=0.0001, final=0.9, limit=1;
 assert.ok(final<=limit);
 assert.ok(final<=Math.max(limit,1.25*previous));
 assert.ok(final>1000*previous);
 const earlier={positionKm:previous,velocityKmS:0,epochS:0,jacobiKm2S2:0,modeledWorkKm2S2:0};
 const latest={...earlier,positionKm:final};
 const allowance={...earlier,positionKm:64*Number.EPSILON*7000};
 assert.equal(checkRefinementTrend(earlier,latest,allowance).status,'GROWTH_BEYOND_ROUNDOFF');
 assert.equal(m.findings.find(f=>f.id==='G16-N1')?.status,'OPEN_TO_CASTOR_ISSUE_4');
 assert.equal(m.geographic_conclusion,'INDETERMINATE');
});
