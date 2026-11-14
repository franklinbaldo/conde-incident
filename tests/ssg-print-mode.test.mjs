import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import test from 'node:test';

const css=readFileSync('static/css/site.css','utf8');
const heading='/* SSG-first print mode:';

function validatePrintStyles(source) {
  const at=source.indexOf(heading);
  assert.ok(at>=0,'modo print ausente');
  const print=source.slice(at);
  assert.match(print,/@media\s+print\s*\{/,'media print real');
  assert.match(print,/:root\s*\{\s*color-scheme:\s*light\s*;/,'papel deve usar cor clara');
  assert.match(print,/html,body\s*\{[^}]*background:\s*#fff!important;[^}]*color:\s*#1b2730!important/,'tinta escura em papel branco');
  assert.match(print,/\.masthead,\.skip-link,#ssg-search-header\s*\{display:none!important\}/,'ocultar apenas cromos de navegação');
  assert.match(print,/\.casefile\s*\{[^}]*background:#fff[^}]*color:#1b2730/,'ficha é imprimível');
  assert.match(print,/\.casefile \.cf-hero,\.casefile \.cf-cards\s*\{grid-template-columns:1fr\}/,'cartões não podem comprimir no papel');
  assert.match(print,/\.casefile :is\(\.cf-card,\.cf-figure,\.cf-trail li\)\s*\{break-inside:avoid-page\}/,'conservar blocos documentais');
  assert.match(print,/\.story-document iframe\s*\{display:none\}/,'PDF incorporado não deve bloquear papel');
  assert.doesNotMatch(print,/\.casefile\s*\{\s*display:none/,'não ocultar conteúdo científico');
}

test('CSS SSG publicado corresponde ao fonte versionado',{skip:process.env.SSG_PRINT_BUILT!=='1'},()=>{
  const built=readFileSync('public/css/site.css','utf8');
  assert.equal(built,css);
  assert.ok(Buffer.byteLength(css,'utf8')<=20000,'regra dos 20 KB');
});

test('dossiê e páginas SSG dispõem de modo de impressão sem JS',{skip:process.env.SSG_PRINT_BUILT!=='1'},()=>{
  validatePrintStyles(css);
  for(const route of ['dossie','stories','evidencias/arquivo']) {
    const html=readFileSync(join('public',route,'index.html'),'utf8');
    assert.match(html,/href="\/conde-incident\/css\/site\.css"/,route+' CSS compartilhado');
    assert.match(html,/<main\b[^>]*id="main"/,route+' landmark principal');
  }
});

test('fonte CSS valida independentemente da compilação SSG',()=>{
  validatePrintStyles(css);
  assert.ok(Buffer.byteLength(css,'utf8')<=20000,'regra dos 20 KB');
});

test('teste negativo: remoção da tinta escura faz o gate reprovar',()=>{
  const broken=css.replace('html,body{background:#fff!important;color:#1b2730!important}',
    'html,body{background:#fff!important;color:#fff!important}');
  assert.notEqual(broken,css);
  assert.throws(()=>validatePrintStyles(broken),/tinta escura/);
});

test('teste negativo: sem modo print o gate reprova',()=>{
  assert.throws(()=>validatePrintStyles(css.replace(heading,'/* sem mídia:')),/modo print/);
});
