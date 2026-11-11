import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { auditGraph, genealogicalRoots, summarize } from '../scripts/check-document-genealogy.mjs';

const original = JSON.parse(readFileSync(new URL('../research/gaviao_document_genealogy_2026-11-11.json', import.meta.url),'utf8'));
const copy = () => structuredClone(original);

test('ledger pins matrix, document URLs, classifications and uncertainty without empirical claims', () => {
  assert.deepEqual(auditGraph(original), []);
  assert.equal(summarize(original).impact_in_conde.status, 'not_verified');
  assert.equal(summarize(original).reentry_coordinates.status, 'not_verified');
});

test('Tupi attribution and FBIS transcription share one documentary origin', () => {
  assert.deepEqual(genealogicalRoots(original, ['TUPI_RIO','FBIS03']), ['TUPI_RIO']);
});

test('reprinting an FBIS transcription cannot create an independent report origin', () => {
  const g=copy();
  g.nodes.push({id:'FBIS_REPRINT',url:'https://example.org/reprint',inspection:'secondary_copy',family:'TUPI_FBIS',supports:[],matrix_ids:['C76']});
  g.relations.push({from:'FBIS03',to:'FBIS_REPRINT',kind:'documented_transcription',verification:'test_fixture',note:'Synthetic derivative for falsification'});
  assert.deepEqual(genealogicalRoots(g,['FBIS03','FBIS_REPRINT']), ['TUPI_RIO']);
  assert.deepEqual(auditGraph(g),[]);
});

test('a physical impact cannot be promoted from press documents', () => {
  const g=copy();
  const c=g.claims.find(x=>x.id==='impact_in_conde');
  c.status='documented_text';
  c.sources=['FBIS03'];
  assert.ok(auditGraph(g).some(s=>s.includes('Unverified empirical claim was promoted')));
  assert.ok(auditGraph(g).some(s=>s.includes('Source does not support')));
});

test('NASA catalog day cannot be converted into terminal location evidence', () => {
  const g=copy();
  g.claims.find(x=>x.id==='reentry_coordinates').status='documented_text';
  g.claims.find(x=>x.id==='reentry_coordinates').sources=['NASA_SSR_19631115'];
  assert.ok(auditGraph(g).some(s=>s.includes('Unverified empirical claim was promoted')));
});

test('GMT convention cannot become a confirmed time for 1963 merely from FBIS header W', () => {
  const g=copy();
  const c=g.claims.find(x=>x.id==='broadcast_clock_zone_GMT');
  c.status='documented_text';
  c.sources=['FBIS03'];
  assert.ok(auditGraph(g).some(s=>s.includes('Unverified empirical claim was promoted')));
});

test('hypothetical Blue Book dependence cannot be rewritten as observed quotation', () => {
  const g=copy();
  const rel=g.relations.find(x=>x.to==='BLUEBOOK_INDEX');
  rel.verification='directly_verified';
  assert.ok(auditGraph(g).some(s=>s.includes('Possible link presented as verified')));
});

test('Blue Book text extraction cannot pretend to be visual inspection of case file', () => {
  const g=copy();
  g.nodes.find(x=>x.id==='BLUEBOOK_INDEX').inspection='direct_visual_facsimile';
  assert.ok(auditGraph(g).some(s=>s.includes('Blue Book index promoted')));
});

test('prior TV script inspection cannot become a new first original reading', () => {
  const g=copy();
  g.nodes.find(x=>x.id==='TUPI_SP_SCRIPT_09').inspection='direct_visual_facsimile';
  assert.ok(auditGraph(g).some(s=>s.includes('TV script promoted')));
});

test('documented transcriptions with cycles cannot be treated as independent roots', () => {
  const g=copy();
  g.relations.push({from:'FBIS03',to:'TUPI_RIO',kind:'documented_transcription',verification:'test_fixture',note:'Synthetic erroneous cycle'});
  assert.match(auditGraph(g).join(' | '), /Cycle in documented genealogy/);
});

test('broken document IDs and unsupported sources fail before publication', () => {
  const g=copy();
  g.nodes.find(x=>x.id==='NASA_SSR_19631115').url='missing';
  g.claims.find(x=>x.id==='nasa_records_decay_date').sources=['UNINSPECTED_UNKNOWN'];
  const errors=auditGraph(g);
  assert.ok(errors.some(s=>s.includes('Missing source URL')));
  assert.ok(errors.some(s=>s.includes('Source does not support')));
});
