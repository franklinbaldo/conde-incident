import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { auditDomainSensitivity, auditAlternativeSensitivity } from '../scripts/audit-domain-sensitivity.mjs';
import { analyze } from '../scripts/audit-admissible-domain.mjs';

const trace = (id) => ({
  evidence_id: id, occurrence: 'Synthetic case ' + id,
  source_uri: 'synthetic:' + id, independence_group: 'synthetic-' + id,
  verification: 'synthetic',
});
const bound = (id, min, max, parameter='x') => ({
  parameter, interval: { min, max }, trace: trace(id),
  formal: { lean_ref: 'Synthetic.conditional_' + id, status: 'NOT_RUN' },
  assumption: 'Synthetic constraint ' + id,
});
const record = (restrictions) => ({
  schema: 'conde.admissible-domain/v1', kind: 'synthetic',
  parameters: [{ name:'x', unit:'test', initial:{min:'0',max:'10'} }],
  restrictions,
});

test('reports actual individually pivotal bounds without numerical rounding', () => {
  const r = auditDomainSensitivity(record([bound('A','1','9'),bound('B','2','8')]));
  assert.equal(r.domain_status,'REDUCED');
  assert.deepEqual(r.parameters[0].admissible_interval,{min:'2',max:'8'});
  assert.deepEqual(r.parameters[0].individually_pivotal.map(x=>x.evidence_id),['B']);
  assert.deepEqual(r.parameters[0].not_individually_pivotal.map(x=>x.evidence_id),['A']);
  assert.equal(r.location_and_impact,'NOT_INFERRED');
});

test('coincident tight bounds are not mislabeled as useless', () => {
  const r=auditDomainSensitivity(record([bound('A','2','8'),bound('B','2','8')]));
  assert.equal(r.parameters[0].individually_pivotal.length,0);
  assert.equal(r.parameters[0].not_individually_pivotal.length,2);
  assert.match(r.parameters[0].caution,/matter jointly/);
  assert.equal(r.parameters[0].status,'REDUCED');
});

test('two incompatible bounds produce a deletion-minimal pair, not a location', () => {
  const source=record([bound('A','0','4'),bound('B','6','10'),bound('C','0','10')]);
  const r=auditDomainSensitivity(source);
  assert.equal(r.domain_status,'CONTRADICTORY');
  const witness=r.parameters[0].deletion_minimal_conflict;
  assert.equal(witness.length,2);
  assert.deepEqual(witness.map(x=>x.evidence_id),['A','B']);
  for(const item of witness) {
    const remaining=witness.filter(x=>x.ordinal!==item.ordinal);
    const subset=record(remaining.map(x=>source.restrictions[x.ordinal-1]));
    assert.notEqual(analyze(subset).domain_status,'CONTRADICTORY');
  }
  assert.equal(r.parameters[0].initial_interval_is_part_of_witness,true);
  assert.equal(r.parameters[0].conflict_scope,'DECLARED_INTERVALS_ONLY');
});

test('a single interval outside declared initial range is sufficient witness', () => {
  const r=auditDomainSensitivity(record([bound('A','-10','-1'),bound('B','0','10')]));
  assert.deepEqual(r.parameters[0].deletion_minimal_conflict.map(x=>x.evidence_id),['A']);
});

test('different parameter contradictions remain independently attributed', () => {
  const x=record([bound('A','2','8'),bound('B','5','9','y'),bound('C','11','12','y')]);
  x.parameters.push({name:'y',unit:'test',initial:{min:'0',max:'10'}});
  const r=auditDomainSensitivity(x);
  assert.equal(r.parameters[0].status,'REDUCED');
  assert.equal(r.parameters[1].status,'EMPTY');
  assert.deepEqual(r.parameters[1].deletion_minimal_conflict.map(x=>x.evidence_id),['C']);
});

test('unconstrained parameter stays unchanged and has no invented source', () => {
  const r=auditDomainSensitivity(record([]));
  assert.equal(r.domain_status,'UNCHANGED');
  assert.deepEqual(r.parameters[0].individually_pivotal,[]);
  assert.deepEqual(r.parameters[0].admissible_interval,{min:'0',max:'10'});
});

test('long decimal rational comparison remains exact', () => {
  const r=record([bound('A','0.100000000000000000000001','0.100000000000000000000003'),
    bound('B','0.100000000000000000000002','0.100000000000000000000003')]);
  const out=auditDomainSensitivity(r);
  assert.deepEqual(out.parameters[0].individually_pivotal.map(x=>x.evidence_id),['B']);
  assert.match(out.parameters[0].admissible_interval.min,/^\d+\/\d+$/);
});

test('mixed independence groups for the same source are rejected by reused auditor', () => {
  const x=record([bound('A','1','9'),bound('B','2','8')]);
  x.restrictions[1].trace.source_uri='synthetic:A';
  assert.throws(()=>auditDomainSensitivity(x),/same source claimed as independent/);
});

test('unsupported Lean PASS is never promoted by sensitivity analysis', () => {
  const x=record([bound('A','1','9')]);x.restrictions[0].formal.status='PASS';
  assert.throws(()=>auditDomainSensitivity(x),/only NOT_RUN\/CLAIMED/);
});

test('historical labels remain DECLARED_NOT_AUDITED rather than scientific proof', () => {
  const x=record([bound('A','1','9')]);x.kind='declared-evidence';
  x.restrictions[0].trace={
    evidence_id:'C197',occurrence:'NASA 15 Nov 1963 printed p.8',
    source_uri:'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf',
    independence_group:'nasa-norad-catalog',verification:'directly_inspected',
  };
  const r=auditDomainSensitivity(x);
  assert.equal(r.evidence_label,'DECLARED_NOT_AUDITED');
  assert.equal(r.matrix_occurrences,'NOT_VERIFIED');
  assert.equal(r.lean_proofs,'NOT_VERIFIED');
});

test('alternatives are diagnosed independently and are NOT claimed exhaustive', () => {
  const common=record([]);
  const input={
    schema:'conde.alternative-domains/v1',common,
    scenarios:[
      {id:'lineage-a',reason:'unresolved source A',restrictions:[bound('A','0','4')]},
      {id:'lineage-b',reason:'unresolved source B',restrictions:[bound('B','6','10')]},
    ],
  };
  const r=auditAlternativeSensitivity(input);
  assert.equal(r.status,'MULTIPLE_DECLARED_FEASIBLE');
  assert.equal(r.scenarios[0].result.domain_status,'REDUCED');
  assert.equal(r.scenarios[1].result.domain_status,'REDUCED');
  assert.equal(r.scenario_set_exhaustive,'NOT_VERIFIED');
  assert.equal(r.physical_feasibility,'NOT_VERIFIED');
});

test('CLI emits explicit contradiction exit status 2 and invalid input status 1', () => {
  const dir=mkdtempSync(join(tmpdir(),'conde-sensitivity-'));
  try {
    const file=join(dir,'input.json');
    writeFileSync(file,JSON.stringify(record([bound('A','0','4'),bound('B','6','10')])));
    const cli=new URL('../scripts/audit-domain-sensitivity.mjs',import.meta.url);
    const run=spawnSync(process.execPath,[cli.pathname,file],{encoding:'utf8'});
    assert.equal(run.status,2);
    assert.match(run.stdout,/"CONTRADICTORY"/);
    writeFileSync(file,'{"schema":"unknown"}');
    const bad=spawnSync(process.execPath,[cli.pathname,file],{encoding:'utf8'});
    assert.equal(bad.status,1);
    assert.match(bad.stderr,/unsupported schema/);
  } finally {rmSync(dir,{recursive:true,force:true});}
});
