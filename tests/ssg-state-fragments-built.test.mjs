import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {archiveStatusAnchor,archiveStatusLink} from '../scripts/archive-status-index.mjs';

const records=JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8')).records;
const root='public/evidencias/arquivo/';
const read=route=>readFileSync(root+route+'index.html','utf8');

function checkStatusTarget(html,code) {
  const fragment=archiveStatusAnchor(code);
  assert.ok(html.includes('id="'+fragment+'"'), 'Estado sem destino HTML: '+code);
  assert.ok(html.includes('href="#'+fragment+'"'), 'Estado sem link de sumário: '+code);
}

test('site SSG real preserva os destinos e o sumário de todos os estados',()=>{
  const html=read('estados/');
  for(const code of new Set(records.map(record=>record.source_status)))
    checkStatusTarget(html,code);
  const code=records[0].source_status;
  const fragment=archiveStatusAnchor(code);
  assert.throws(()=>checkStatusTarget(html.replace('id="'+fragment+'"','id="mutant"'),code),/sem destino HTML/);
});

test('site SSG real liga ocorrência, fonte e obra ao estado canônico',()=>{
  const seen=new Set();
  for(const record of records) {
    const slug=s=>s.toLowerCase().replaceAll('_','-');
    const occurrence=record.occurrence.toLowerCase().replace('#','-');
    const url=archiveStatusLink(record.source_status);
    for(const route of [occurrence+'/', 'fontes/'+slug(record.source_id)+'/', 'obras/'+slug(record.work_id)+'/']) {
      const key=route+'|'+url;
      if(seen.has(key))continue;
      seen.add(key);
      assert.ok(read(route).includes('href="'+url+'"'), 'Link publicado ausente: '+key);
    }
  }
});
