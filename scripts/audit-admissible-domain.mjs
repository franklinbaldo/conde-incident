// Conservative exact-rational audit: no claim of source authenticity, Lean proof or orbital physics.
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

function requireThat(ok, msg) { if (!ok) throw new Error(msg); }
function gcd(a,b) { a=a<0n?-a:a; while(b!==0n) [a,b]=[b,a%b]; return a; }
function rational(s) {
  requireThat(typeof s==='string' && /^-?(?:0|[1-9]\d*)(?:\.\d+)?$/.test(s), 'bounds must be exact decimal strings');
  const [whole,frac='']=s.split('.');
  const d=10n**BigInt(frac.length);
  const n=BigInt(whole.startsWith('-')?'-'+whole.slice(1)+frac:whole+frac);
  const factor=gcd(n,d);
  return { n:n/factor,d:d/factor };
}
const cmp=(a,b)=>{const delta=a.n*b.d-b.n*a.d;return delta<0n?-1:delta>0n?1:0;};
const show=x=>x.d===1n?x.n.toString():`${x.n}/${x.d}`;
function interval(data,where) {
  requireThat(data && typeof data==='object', `${where}: interval required`);
  const min=rational(data.min),max=rational(data.max);
  requireThat(cmp(min,max)<=0,`${where}: inverted interval`);
  return {min,max};
}
const nonempty=x=>cmp(x.min,x.max)<=0;
const printable=x=>x && nonempty(x)?{min:show(x.min),max:show(x.max)}:null;
const intersect=(a,b)=>({
  min:cmp(a.min,b.min)>=0?a.min:b.min,
  max:cmp(a.max,b.max)<=0?a.max:b.max,
});
function required(s,where) {
  requireThat(typeof s==='string'&&s.trim().length>0,`${where} is required`);
  return s;
}
export function analyze(record) {
  requireThat(record && typeof record==='object' && !Array.isArray(record),'record object required');
  requireThat(record.schema==='conde.admissible-domain/v1','unsupported schema');
  requireThat(['synthetic','declared-evidence'].includes(record.kind),'kind must be synthetic or declared-evidence');
  requireThat(Array.isArray(record.parameters)&&record.parameters.length>0,'parameters required');
  requireThat(Array.isArray(record.restrictions),'restrictions array required');
  const current=new Map(),original=new Map();
  for(const p of record.parameters) {
    const name=required(p?.name,'parameter name');
    required(p?.unit,`${name}: unit`);
    requireThat(!current.has(name),`duplicate parameter ${name}`);
    const start=interval(p.initial,`${name}: initial`);
    current.set(name,start);original.set(name,start);
  }
  const ids=new Map(),urls=new Map(),chains=new Set();
  let contradiction=false;
  for(const [i,r] of record.restrictions.entries()) {
    const where=`restriction ${i+1}`;
    const name=required(r?.parameter,`${where}: parameter`);
    requireThat(current.has(name),`${where}: unknown parameter ${name}`);
    const bound=interval(r.interval,where);
    const t=r.trace;
    requireThat(t&&typeof t==='object',`${where}: trace required`);
    const id=required(t.evidence_id,`${where}: evidence_id`);
    required(t.occurrence,`${where}: occurrence`);
    const url=required(t.source_uri,`${where}: source_uri`);
    requireThat(/^https:\/\/[^\s/]+\//.test(url)||url.startsWith('synthetic:'),`${where}: source_uri must be HTTPS or synthetic:`);
    const group=required(t.independence_group,`${where}: independence_group`);
    const verification=required(t.verification,`${where}: verification`);
    if(record.kind==='synthetic') {
      requireThat(verification==='synthetic'&&url.startsWith('synthetic:'),`${where}: synthetic records must stay synthetic`);
    } else {
      requireThat(['directly_inspected','contemporary_secondhand','modern_catalog','quantitative_inference','hypothesis','unknown'].includes(verification),`${where}: invalid verification label`);
      requireThat(url.startsWith('https://'),`${where}: evidence URI must be HTTPS`);
      requireThat(/^C\d{1,4}(?:-[A-Za-z0-9]+)?$/.test(id),`${where}: evidence ID must refer to matrix-style C record`);
    }
    requireThat(r.formal&&typeof r.formal==='object',`${where}: formal reference required`);
    required(r.formal.lean_ref,`${where}: lean_ref`);
    requireThat(['NOT_RUN','CLAIMED'].includes(r.formal.status),`${where}: only NOT_RUN/CLAIMED allowed without independent Lean verification`);
    required(r.assumption,`${where}: assumption`);
    if(ids.has(id)) requireThat(ids.get(id)===group,`${where}: ID ${id} assigned conflicting independence groups`);
    if(urls.has(url)) requireThat(urls.get(url)===group,`${where}: same source claimed as independent`);
    ids.set(id,group);urls.set(url,group);chains.add(group);
    const next=intersect(current.get(name),bound);
    current.set(name,next);
    if(!nonempty(next)) contradiction=true;
  }
  const parameters=[...current].map(([name,value])=>{
    const start=original.get(name),valid=nonempty(value);
    return {name,initial:printable(start),admissible:printable(value),
      status:!valid?'EMPTY':cmp(start.min,value.min)!==0||cmp(start.max,value.max)!==0?'REDUCED':'UNCHANGED'};
  });
  return {
    label:record.kind==='synthetic'?'SYNTHETIC_ONLY':'DECLARED_NOT_AUDITED',
    domain_status:contradiction?'CONTRADICTORY':parameters.some(p=>p.status==='REDUCED')?'REDUCED':'UNCHANGED',
    parameters,restrictions:record.restrictions.length,independent_chains_declared:chains.size,
    lean_proofs:'NOT_VERIFIED',numerical_holdout:'NOT_RUN',reentry_and_impact_location:'NOT_INFERRED'
  };
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href) {
  try {
    requireThat(process.argv.length===3,'usage: node scripts/audit-admissible-domain.mjs <record.json>');
    const result=analyze(JSON.parse(readFileSync(process.argv[2],'utf8')));
    console.log(JSON.stringify(result,null,2));
    if(result.domain_status==='CONTRADICTORY')process.exitCode=2;
  } catch(error) {
    console.error(`Domain audit rejected input: ${error.message}`);
    process.exitCode=1;
  }
}