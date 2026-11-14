import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {TLE_SHA256,TLE_SOURCE,checkTleLine,renderTleCustody} from '../scripts/ssg-tle-custody.mjs';
const raw = readFileSync(TLE_SOURCE,'utf8');
const [first,second] = raw.trimEnd().split('\n');

test('Custódia em SSG com SHA imutável, checksum, RAAN e limites explícitos',()=>{
  assert.equal(createHash('sha256').update(raw).digest('hex'),TLE_SHA256);
  assert.equal(checkTleLine(first,1).valid,true);
  assert.equal(checkTleLine(second,2).valid,true);
  const page=renderTleCustody(raw);
  for (const item of ['C179#1','63300.61129783','198.5261°','NORAD 527','NORAD 528','NORAD 529',
    'não observação instrumental primária','hora, a posição terminal','/conde-incident/lab/#/tles'])
    assert.ok(page.includes(item),`Informação estática ausente: ${item}`);
  assert.doesNotMatch(page,/<script|onload=|onclick=/i);
  assert.match(page, /<pre class="tle-source-lines" tabindex="0" role="region" aria-label="[^"]+"><code>/);
  assert.ok(page.includes('<code>'+first+'\n'+second+'</code>'), 'Preservar as duas linhas TLE de 69 colunas sem reflow textual');
});

test('Checksum rejeita alteração, prefixo, tamanho e linha trocada',()=>{
  assert.equal(checkTleLine(second,2).valid,true, 'Controle positivo com segundo checksum original');
  assert.equal(checkTleLine(first.slice(0,68)+'9',1).valid,false);
  assert.equal(checkTleLine(second,1).valid,false);
  assert.equal(checkTleLine(second.slice(1),2).valid,false);
  assert.equal(checkTleLine(second.replace('00528','00527'),2).valid,false);
});

test('Publicação falha fechada se os bytes custodiados mudarem',()=>{
  assert.throws(()=>renderTleCustody(raw.replace('198.5261','198.5262')),/SHA-256/);
  assert.throws(()=>renderTleCustody(raw+'\n'),/SHA-256/);
  assert.throws(()=>renderTleCustody(raw.slice(0,-1)),/SHA-256/);
});
