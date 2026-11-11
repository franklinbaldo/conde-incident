import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validate} from '../scripts/check-editorial-source-audit.mjs';
const base=JSON.parse(readFileSync(new URL('../research/gaviao_editorial_source_audit_2026-11-11.json',import.meta.url),'utf8'));
const fresh=()=>structuredClone(base);

test('ledger real tem quatro fontes e tres cadeias documentais',()=>assert.deepEqual(validate(fresh()),{sources:4,findings:7,independent_chains:3}));
test('OCR não se torna imagem conferida por troca de rótulo',()=>{
  const x=fresh();x.findings[3].status='VERIFIED_DOCUMENT';
  assert.throws(()=>validate(x),/OCR promoted/);
});
test('publicações repetidas não aumentam cadeias independentes',()=>{
  const x=fresh();x.findings[6].independent_groups=4;
  assert.throws(()=>validate(x),/independence inflation/);
});
test('ID de achado não é reutilizado',()=>{
  const x=fresh();x.findings[0].id=x.findings[1].id;
  assert.throws(()=>validate(x),/duplicate finding/);
});
test('fonte precisa estar identificada',()=>{
  const x=fresh();x.findings[0].support=['INEXISTENTE'];
  assert.throws(()=>validate(x),/unknown source/);
});
test('cronologia não admite direção causal invertida',()=>{
  const x=fresh();x.findings[5].chronology.earlier='FBIS-03';
  x.findings[5].chronology.later='EOP-UAP-D002';
  assert.throws(()=>validate(x),/chronology reversed/);
});
test('data administrativa não comprova impacto físico',()=>{
  const x=fresh();x.findings[5].effect='SPECIFIC_IMPACT';
  assert.throws(()=>validate(x),/finding type\/effect/);
});
test('sem hash não é permitido dizer bytes verificados',()=>{
  const x=fresh();x.sources[2].hash_status='VERIFIED_BYTES';x.sources[2].sha256=null;
  assert.throws(()=>validate(x),/hash proof missing/);
});
test('resultado físico permanece indeterminado',()=>{
  const x=fresh();x.scientific_gates.impact_conde='ESTABLISHED';
  assert.throws(()=>validate(x),/unsupported physical assertion/);
});
test('cada matéria precisa de SHA e CI auditável',()=>{
  const x=fresh();x.reviewed_heads[0].ci_run=null;
  assert.throws(()=>validate(x),/missing head\/CI/);
});
