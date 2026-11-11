import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const statuses=new Set(['VERIFIED_DOCUMENT','OCR_PROVISIONAL','CONDITIONAL_CHRONOLOGY','UNRESOLVED']);
const effects=new Set(['REPORT_ONLY','DAY_ONLY','ADMIN_ONLY','NO_PHYSICAL_INFERENCE']);
export function validate(a) {
  if(a?.schema!=='gaviao-editorial-v1'||!Array.isArray(a.sources)||!Array.isArray(a.findings)) throw Error('schema/collections');
  const ids=new Set();
  for(const s of a.sources){
    if(!s.id||ids.has(s.id)) throw Error('duplicate source ID');
    ids.add(s.id);
    if(!s.url?.startsWith('https://')||!s.locator||!s.independence_chain||!s.limit) throw Error('incomplete source provenance');
    if(!['FACSIMILE_VISUAL','OCR_ONLY'].includes(s.access)) throw Error('unknown verification method');
    if(!['NOT_COMPUTED','REPORTED_NOT_RECOMPUTED','VERIFIED_BYTES'].includes(s.hash_status)) throw Error('hash status');
    if(s.sha256!==null && !/^[a-f0-9]{64}$/.test(s.sha256)) throw Error('malformed SHA256');
    if(s.hash_status==='VERIFIED_BYTES' && !s.sha256) throw Error('hash proof missing');
    if(Number.isNaN(Date.parse(s.date+'T00:00:00Z'))) throw Error('invalid date');
  }
  const byId=new Map(a.sources.map(s=>[s.id,s]));
  const fIds=new Set();
  for(const f of a.findings){
    if(!f.id||fIds.has(f.id)) throw Error('duplicate finding ID');
    fIds.add(f.id);
    if(!statuses.has(f.status)||!effects.has(f.effect)||!f.summary||!f.support?.length) throw Error('finding type/effect');
    const sources=f.support.map(id=>{if(!byId.has(id)) throw Error('unknown source');return byId.get(id)});
    if(new Set(sources.map(s=>s.independence_chain)).size!==f.independent_groups) throw Error('independence inflation');
    if(f.status==='VERIFIED_DOCUMENT'&&sources.some(s=>s.access!=='FACSIMILE_VISUAL')) throw Error('OCR promoted to visual verification');
    if(f.status==='OCR_PROVISIONAL'&&!sources.some(s=>s.access==='OCR_ONLY')) throw Error('missing OCR source');
    if(f.status==='CONDITIONAL_CHRONOLOGY'){
      if(!f.chronology||!f.support.includes(f.chronology.earlier)||!f.support.includes(f.chronology.later)) throw Error('chronology support');
      if(!(byId.get(f.chronology.earlier).date<byId.get(f.chronology.later).date)) throw Error('chronology reversed');
      if(f.effect!=='ADMIN_ONLY') throw Error('chronology cannot locate impact');
    }
  }
  if(a.reviewed_heads?.length!==5||new Set(a.reviewed_heads.map(x=>x.pr)).size!==5) throw Error('reviewed heads');
  for(const h of a.reviewed_heads){
    if(!/^[a-f0-9]{40}$/.test(h.sha)|| (h.chapter!==null&&!Number.isInteger(h.ci_run))) throw Error('missing head/CI');
  }
  if(a.reviewed_heads.filter(h=>h.chapter!==null).map(h=>h.chapter).join(',')!=='1,2,3,4') throw Error('chapter sequence');
  const g=a.scientific_gates;
  if(g?.lean_new_constraints!=='NOT_JUSTIFIED'||g.reduced_numerical_domain!==false||g.simulator_new_data!=='NOT_RUN'||g.impact_conde!=='UNDETERMINED'||g.exact_reentry_time!=='NOT_ESTABLISHED'||g.exact_reentry_place!=='NOT_ESTABLISHED') throw Error('unsupported physical assertion');
  return {sources:a.sources.length,findings:a.findings.length,independent_chains:new Set(a.sources.map(s=>s.independence_chain)).size};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
  const a=JSON.parse(readFileSync(new URL('../research/gaviao_editorial_source_audit_2026-11-11.json',import.meta.url),'utf8'));
  console.log('EDITORIAL_LEDGER_PASS',JSON.stringify(validate(a)));
}
