import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { analyze } from '../scripts/audit-admissible-domain.mjs';

const source=(id='SYN1',group='synthetic-group')=>({
  evidence_id:id,occurrence:'synthetic fixture',source_uri:'synthetic:test',
  independence_group:group,verification:'synthetic'
});
const constraint=(min,max,parameter='x',overrides={})=>({
  parameter,interval:{min,max},trace:source(),
  formal:{lean_ref:'Synthetic.conditional',status:'NOT_RUN'},
  assumption:'synthetic interval restriction',...overrides
});
const input=()=>({
  schema:'conde.admissible-domain/v1',kind:'synthetic',
  parameters:[{name:'x',unit:'synthetic',initial:{min:'0',max:'10'}}],
  restrictions:[constraint('2','8')]
});
test('strict contraction is recorded, without orbital inference',()=>{
  const x=analyze(input());
  assert.equal(x.domain_status,'REDUCED');
  assert.deepEqual(x.parameters[0].admissible,{min:'2',max:'8'});
  assert.equal(x.reentry_and_impact_location,'NOT_INFERRED');
  assert.equal(x.numerical_holdout,'NOT_RUN');
  assert.equal(x.lean_proofs,'NOT_VERIFIED');
});
test('wider constraint cannot expand the initial interval',()=>{
  const x=input();x.restrictions[0].interval={min:'-5',max:'25'};
  assert.equal(analyze(x).domain_status,'UNCHANGED');
});
test('disjoint restrictions reveal contradiction, not location',()=>{
  const x=input();x.restrictions.push(constraint('9','10','x',{trace:{...source('SYN2'),source_uri:'synthetic:second'}}));
  const y=analyze(x);assert.equal(y.domain_status,'CONTRADICTORY');assert.equal(y.parameters[0].admissible,null);
});
test('single point is a nonempty contracted domain',()=>{
  const x=input();x.restrictions[0].interval={min:'5',max:'5'};
  assert.deepEqual(analyze(x).parameters[0].admissible,{min:'5',max:'5'});
});
test('long decimals have exact, non-float comparisons',()=>{
  const x=input();x.restrictions[0].interval={min:'0.10000000000000000000001',max:'0.10000000000000000000002'};
  const y=analyze(x);assert.notEqual(y.parameters[0].admissible.min,y.parameters[0].admissible.max);
});
test('inverted intervals rejected',()=>{
  const x=input();x.restrictions[0].interval={min:'9',max:'2'};
  assert.throws(()=>analyze(x),/inverted interval/);
});
test('NaN rejected, never rounded silently',()=>{
  const x=input();x.parameters[0].initial.min='NaN';
  assert.throws(()=>analyze(x),/decimal strings/);
});
test('missing occurrence rejected',()=>{
  const x=input();delete x.restrictions[0].trace.occurrence;
  assert.throws(()=>analyze(x),/occurrence/);
});
test('synthetic input cannot masquerade as inspected evidence',()=>{
  const x=input();x.restrictions[0].trace.verification='directly_inspected';
  assert.throws(()=>analyze(x),/stay synthetic/);
});
test('same source URL cannot be counted independent',()=>{
  const x=input();x.restrictions.push(constraint('3','7','x',{trace:source('SYN2','other-group')}));
  assert.throws(()=>analyze(x),/same source claimed as independent/);
});
test('same evidence ID with conflicting independence groups rejected',()=>{
  const x=input();x.restrictions.push(constraint('3','7','x',{trace:{...source('SYN1','other-group'),source_uri:'synthetic:other'}}));
  assert.throws(()=>analyze(x),/conflicting independence groups/);
});
test('unverified Lean assertion cannot be called PASS',()=>{
  const x=input();x.restrictions[0].formal.status='PASS';
  assert.throws(()=>analyze(x),/only NOT_RUN\/CLAIMED/);
});
test('declared historical evidence remains unaudited',()=>{
  const x=input();x.kind='declared-evidence';
  x.restrictions[0].trace={evidence_id:'C197',
    occurrence:'NASA bulletin printed p. 8, catalog entry',
    source_uri:'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf',
    independence_group:'nasa-norad-catalog',verification:'directly_inspected'};
  assert.equal(analyze(x).label,'DECLARED_NOT_AUDITED');
});
test('two parameters preserve separate contractions',()=>{
  const x=input();x.parameters.push({name:'y',unit:'synthetic',initial:{min:'-3',max:'3'}});
  x.restrictions.push(constraint('-2','2','y',{trace:{...source('SYN2'),source_uri:'synthetic:second'}}));
  const y=analyze(x);
  assert.equal(y.parameters[1].status,'REDUCED');
  assert.deepEqual(y.parameters[1].admissible,{min:'-2',max:'2'});
});
test('unknown parameters rejected, not invented',()=>{
  const x=input();x.restrictions[0].parameter='unobserved';
  assert.throws(()=>analyze(x),/unknown parameter/);
});