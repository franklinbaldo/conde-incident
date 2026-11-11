import test from 'node:test';
import assert from 'node:assert/strict';
import {collectMatrixClaims, crossBranchConflicts} from '../scripts/audit-matrix-ids.mjs';

const tle = [
  '## C240 — Custódia orbital',
  '| ID | Fonte | Resultado |',
  '|---|---|---|',
  '| **C240** | espelho TLE | RAAN 198.5261, autenticidade não verificada |',
  '| **C241** | confronto numérico | deriva da mesma família |',
  '| **C242** | holdout 529 | uma piora |',
].join('\n');
const nara = [
  '## C239–C241 — localizadores Blue Book',
  '| ID | Fonte | Resultado |',
  '|---|---|---|',
  '| **C239** | NARA NAID 597821 | série oficial, dossiê não recuperado |',
  '| **C240** | NARA T1206 | designação da publicação |',
  '| **C241** | Roll 49 secundário | Conde não identificado |',
].join('\n');

test('reconhece tabelas mesmo quando o título é um intervalo C239–C241', () => {
  assert.deepEqual(collectMatrixClaims(nara,'archive').map(x=>x.id), ['C239','C240','C241']);
});
test('duas afirmações distintas não se tornam a mesma prova porque compartilham um C-ID', () => {
  const findings = crossBranchConflicts([{label:'tle+holdout',markdown:tle},{label:'archive',markdown:nara}]);
  assert.deepEqual(findings.map(x=>x.id),['C240','C241']);
  assert.ok(findings.every(x=>new Set(x.items.map(i=>i.digest)).size===2));
});
test('replicação idêntica de texto não vira duas afirmações incompatíveis', () => {
  assert.deepEqual(crossBranchConflicts([{label:'one',markdown:tle},{label:'two',markdown:tle}]),[]);
});
test('colisões internas são recusadas em vez de sobrescrever a primeira linha', () => {
  assert.throws(()=>collectMatrixClaims(tle+'\n| **C240** | outro | dado oposto |','bad'),/duplicado/);
});
test('texto truncado não passa por matriz auditável', () => {
  assert.throws(()=>collectMatrixClaims('## C240 — sem linhas de tabela','bad'),/Sem linhas/);
});
test('referência C240 no corpo da prosa não cria identidade de afirmação', () => {
  const only = '| **C239** | NARA | série |';
  assert.deepEqual(collectMatrixClaims('C240 foi citado\n'+only,'x').map(x=>x.id),['C239']);
});
test('hashes refletem conteúdo, não ordem ou rótulo de branch', () => {
  const a=collectMatrixClaims(tle,'one')[0], b=collectMatrixClaims(tle,'two')[0];
  assert.equal(a.digest,b.digest);
  assert.notEqual(a.source,b.source);
});
