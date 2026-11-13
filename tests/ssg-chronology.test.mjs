import test from 'node:test';
import assert from 'node:assert/strict';
import { editorialChronology } from '../scripts/ssg-chronology.mjs';

const stories=[
  {date:'2026-11-11',chapter:'01',slug:'first',title:'Uma esfera',summary:'Relato sem prova de queda.'},
  {date:'2026-11-11',chapter:'02',slug:'second',title:'Uma órbita',summary:'Decaimento sem posição.'},
  {date:'2026-11-12',chapter:'03',slug:'third',title:'Outro documento',summary:'Origem distinta.'},
];
test('separa datas editoriais por cabeçalhos navegáveis e mantém a ordem',()=>{
  const page=editorialChronology(stories);
  assert.deepEqual(page.match(/^## Publicação: .*$/gm),[
    '## Publicação: 2026-11-11','## Publicação: 2026-11-12']);
  assert.equal((page.match(/^- \[Capítulo/gm)||[]).length,3);
  assert.ok(page.indexOf('/first/')<page.indexOf('/second/'));
  assert.ok(page.indexOf('/second/')<page.indexOf('/third/'));
  assert.match(page,/Relato sem prova de queda/);
  assert.match(page,/Decaimento sem posição/);
  assert.doesNotMatch(page, /data de queda|data de observação/);
});
test('cronologia vazia não inventa datas',()=>{
  assert.equal(editorialChronology([]),'');
});
