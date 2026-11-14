import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const read = path => readFileSync('public/'+path+'/index.html','utf8');
const chapter='stories/2026-11-12-a-resposta-que-veio-de-salvador';
const story=read(chapter);
for (const [slug,anchor] of [['c01-1','contexto-fbis'],['c197-1','contexto-nasa']]) {
  const target='/conde-incident/evidencias/arquivo/'+slug+'/';
  const back='/conde-incident/'+chapter+'/#'+anchor;
  assert.ok(story.includes('id="'+anchor+'"'),'Âncora no HTML final ausente: '+anchor);
  assert.ok(story.includes('href="'+target+'"'),'Saída HTML para ocorrência ausente: '+slug);
  const occurrence=read('evidencias/arquivo/'+slug);
  assert.ok(occurrence.includes('href="'+back+'"'),'Retorno à reportagem ausente: '+slug);
  assert.ok(occurrence.includes('Abrir documento original'),'Original ausente: '+slug);
}
console.log('Jornada editorial ↔ arquivo C01#1 / C197#1 presente no HTML gerado.');
