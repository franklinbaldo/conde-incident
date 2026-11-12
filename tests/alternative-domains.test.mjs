import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { analyzeAlternatives } from '../scripts/audit-alternative-domains.mjs';
import { analyze } from '../scripts/audit-admissible-domain.mjs';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const trace=(id,source='synthetic:'+id)=>({
  evidence_id:id,occurrence:'synthetic fixture '+id,source_uri:source,
  independence_group:'synthetic-'+id,verification:'synthetic',
});
const bound=(id,min,max)=>({
  parameter:'x',interval:{min,max},trace:trace(id),
  formal:{lean_ref:'Synthetic.conditional_'+id,status:'NOT_RUN'},
  assumption:'synthetic mutually exclusive case '+id,
});
const input=()=>({
  schema:'conde.alternative-domains/v1',
  common:{
    schema:'conde.admissible-domain/v1',kind:'synthetic',
    parameters:[{name:'x',unit:'synthetic',initial:{min:'0',max:'10'}}],
    restrictions:[],
  },
  scenarios:[
    {id:'first',reason:'source lineage A not yet reconciled',restrictions:[bound('SYN1','0','4')]},
    {id:'second',reason:'source lineage B not yet reconciled',restrictions:[bound('SYN2','6','10')]},
  ],
});
test('two alternatives remain feasible instead of an invented joint contradiction',()=>{
  const x=input(); const result=analyzeAlternatives(x);
  assert.equal(result.status,'MULTIPLE_DECLARED_FEASIBLE');
  assert.equal(result.scenarios_with_nonempty_intervals,2);
  assert.deepEqual(result.scenarios[0].parameters[0].admissible,{min:'0',max:'4'});
  assert.deepEqual(result.scenarios[1].parameters[0].admissible,{min:'6',max:'10'});
  assert.equal(result.location_and_impact,'NOT_INFERRED');
  assert.equal(result.scenario_set_exhaustive,'NOT_VERIFIED');
  assert.equal(result.physical_feasibility,'NOT_VERIFIED');
  assert.equal(analyze({...x.common,restrictions:x.scenarios.flatMap(s=>s.restrictions)}).domain_status,
    'CONTRADICTORY','naive intersection of incompatible source variants is invalid');
});
test('verified-looking source labels do not become proof',()=>{
  const x=input();
  x.common.kind='declared-evidence';
  for(let i=0;i<2;i++){
    const r=x.scenarios[i].restrictions[0];
    r.trace={evidence_id:'C'+(240+i),occurrence:'declared historical document, occurrence '+(i+1),
      source_uri:'https://example.org/archival/'+(i+1),independence_group:'lineage-'+i,
      verification:'directly_inspected'};
  }
  const result=analyzeAlternatives(x);
  assert.equal(result.scenarios[0].declared_evidence,'DECLARED_NOT_AUDITED');
  assert.equal(result.source_authenticity,'NOT_VERIFIED');
  assert.equal(result.matrix_occurrences,'NOT_VERIFIED');
  assert.equal(result.source_independence_between_scenarios,'NOT_VERIFIED');
  assert.equal(result.scenarios[1].trace[0].evidence_id,'C241');
  assert.equal(result.scenarios[1].trace[0].lean_status_declared,'NOT_RUN');
});
test('shared restrictions are applied within every separate scenario',()=>{
  const x=input();
  x.common.restrictions.push(bound('BASE','2','8'));
  const result=analyzeAlternatives(x);
  assert.deepEqual(result.scenarios[0].parameters[0].admissible,{min:'2',max:'4'});
  assert.deepEqual(result.scenarios[1].parameters[0].admissible,{min:'6',max:'8'});
  assert.equal(result.scenarios[0].trace.length,2);
});
test('only one declared feasible alternative is NOT a unique historical orbit',()=>{
  const x=input();
  x.common.parameters[0].initial={min:'0',max:'3'};
  const result=analyzeAlternatives(x);
  assert.equal(result.status,'ONE_DECLARED_FEASIBLE');
  assert.equal(result.scenarios_with_nonempty_intervals,1);
  assert.equal(result.scenario_set_exhaustive,'NOT_VERIFIED');
  assert.equal(result.location_and_impact,'NOT_INFERRED');
});
test('all empty is an inconsistency of declared assumptions, never proof of geography',()=>{
  const x=input();
  x.common.parameters[0].initial={min:'4.5',max:'5.5'};
  const result=analyzeAlternatives(x);
  assert.equal(result.status,'NO_DECLARED_FEASIBLE');
  assert.equal(result.scenarios_with_nonempty_intervals,0);
  assert.equal(result.location_and_impact,'NOT_INFERRED');
});
test('exact rationals preserve distinct feasible intervals',()=>{
  const x=input();
  x.common.parameters[0].initial={min:'0.100000000000000000001',max:'0.100000000000000000009'};
  x.scenarios[0].restrictions[0].interval={min:'0.100000000000000000002',max:'0.100000000000000000003'};
  x.scenarios[1].restrictions[0].interval={min:'0.100000000000000000007',max:'0.100000000000000000008'};
  const result=analyzeAlternatives(x);
  assert.equal(result.status,'MULTIPLE_DECLARED_FEASIBLE');
  assert.notEqual(result.scenarios[0].parameters[0].admissible.min,
    result.scenarios[1].parameters[0].admissible.min);
});
test('duplicate scenario ids are rejected',()=>{
  const x=input();x.scenarios[1].id='first';
  assert.throws(()=>analyzeAlternatives(x),/duplicate scenario id/);
});
test('scenario names must be stable lowercase slugs',()=>{
  const x=input();x.scenarios[1].id='../escape';
  assert.throws(()=>analyzeAlternatives(x),/stable lowercase slug/);
});
test('alternatives must have declared, nonempty reasons',()=>{
  const x=input();x.scenarios[0].reason=' ';
  assert.throws(()=>analyzeAlternatives(x),/documented reason/);
});
test('at least two alternatives required',()=>{
  const x=input();x.scenarios.pop();
  assert.throws(()=>analyzeAlternatives(x),/at least two alternatives/);
});
test('an empty alternative cannot masquerade as tested',()=>{
  const x=input();x.scenarios[0].restrictions=[];
  assert.throws(()=>analyzeAlternatives(x),/distinguishing restriction/);
});
test('declaring the alternatives exhaustive is refused',()=>{
  const x=input();x.exhaustive=true;
  assert.throws(()=>analyzeAlternatives(x),/exhaustive coverage cannot be certified/);
});
test('independence claims within a scenario still pass through provenance validation',()=>{
  const x=input();
  x.scenarios[0].restrictions.push({
    ...bound('SYN3','1','3'),
    trace:{...trace('SYN3','synthetic:SYN1'),independence_group:'other-chain'},
  });
  assert.throws(()=>analyzeAlternatives(x),/same source claimed as independent/);
});
test('unrecognized parameter is never silently created in a variant',()=>{
  const x=input();x.scenarios[0].restrictions[0].parameter='unknown';
  assert.throws(()=>analyzeAlternatives(x),/unknown parameter/);
});
test('a fake Lean PASS status is rejected before any interval narrowing',()=>{
  const x=input();x.scenarios[0].restrictions[0].formal.status='PASS';
  assert.throws(()=>analyzeAlternatives(x),/only NOT_RUN\/CLAIMED/);
});
test('CLI exits 2 for no declared feasible scenario and 1 on invalid input',()=>{
  const x=input();x.common.parameters[0].initial={min:'4.5',max:'5.5'};
  const temp=mkdtempSync(join(tmpdir(),'conde-alternatives-'));
  try{
    const filename=join(temp,'input.json');writeFileSync(filename,JSON.stringify(x));
    const script=new URL('../scripts/audit-alternative-domains.mjs',import.meta.url);
    let run=spawnSync(process.execPath,[script.pathname,filename],{encoding:'utf8'});
    assert.equal(run.status,2);assert.match(run.stdout,/"NO_DECLARED_FEASIBLE"/);
    writeFileSync(filename,'{"schema":"invalid"}');
    run=spawnSync(process.execPath,[script.pathname,filename],{encoding:'utf8'});
    assert.equal(run.status,1);assert.match(run.stderr,/rejected input/);
  }finally{rmSync(temp,{recursive:true,force:true});}
});
