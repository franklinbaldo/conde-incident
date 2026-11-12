import assert from 'node:assert/strict';
import {readFileSync,readdirSync,existsSync} from 'node:fs';
import {join} from 'node:path';
const root='public';
const read=path=>readFileSync(join(root,path),'utf8');
const index=read('index.html'), listing=read('stories/index.html'), lab=read('lab/index.html');
for(const [name,html] of [['home',index],['stories',listing]]) {
  assert.match(html,/\/conde-incident\/stories\//,name+' sem rota Caderno');
  assert.match(html,/\/conde-incident\/lab\//,name+' sem rota laboratório');
  assert.match(html,/<html[^>]+lang=["']?pt-BR/i,name+' sem idioma pt-BR');
  assert.doesNotMatch(html,/(?:src|href)=["']\/(?:assets|css)\//i,name+' referencia assets da raiz');
}
assert.match(lab,/\/conde-incident\/lab\/assets\//,'Assets Vite fora de /lab/');
assert.doesNotMatch(lab,/(?:src|href)=["']\/assets\//,'Assets relativos à raiz, 404 no Pages');
assert.ok(existsSync('public/lab/assets'),'Assets de laboratório ausentes');
assert.ok(existsSync('public/css/site.css'),'CSS do Caderno ausente');
assert.ok(existsSync('public/img/caderno.svg'),'Arte editorial ausente');
for(const page of ['index.html','stories/index.html','lab/index.html']) assert.match(read(page),/Content-Security-Policy/,'CSP ausente em '+page);
let chapters=0;
for(const name of readdirSync('stories').filter(s=>/^\d{4}-\d{2}-\d{2}-.+\.md$/.test(s))){
  const slug=name.slice(0,-3);
  const source=readFileSync(join('stories',name),'utf8');
  const article=read(join('stories',slug,'index.html'));
  assert.ok(listing.includes('/conde-incident/stories/'+slug+'/'),'Capítulo omitido: '+slug);
  assert.match(article,/<article\b/i,'Sem artigo HTML: '+slug);
  assert.match(article,/Content-Security-Policy/,'Artigo sem CSP: '+slug);
  assert.ok(article.includes('/conde-incident/lab/'),'Artigo sem retorno ao laboratório: '+slug);
  assert.ok(article.includes('https://github.com/franklinbaldo/conde-incident/blob/main/stories/'+name),'Fonte canônica ausente: '+slug);
  assert.ok(article.includes('https://') && source.includes('https://'),'Sem referência externa: '+slug);
  chapters++;
}

const chapter03=read('stories/2026-11-12-a-resposta-que-veio-de-salvador/index.html');
assert.match(chapter03,/<figure\\b/i,'Capítulo 03 sem figuras incorporadas');
assert.match(chapter03,/<iframe\\b[^>]*src=[\"']https:\/\/www\\.openstreetmap\\.org\/export\/embed/i,'Mapa ausente no HTML final');
assert.match(chapter03,/<iframe\\b[^>]*src=[\"']https:\/\/media\\.ondisclosure\\.org\/[^\\s\"']+\\.pdf/i,'Documento PDF não incorporado');
assert.match(chapter03,/cadeia-documental-conde\\.svg/,'Diagrama ausente');
assert.match(chapter03,/frame-src[^<]*www\\.openstreetmap\\.org/,'CSP impede mapa incorporado');
assert.match(chapter03,/frame-src[^<]*media\\.ondisclosure\\.org/,'CSP impede documento incorporado');
assert.ok(existsSync('public/img/cadeia-documental-conde.svg'),'Asset do diagrama não copiado');

assert.ok(chapters>0,'Nenhuma reportagem renderizada');
console.log('PASS: '+chapters+' capítulos, índice, CSS, laboratório e rotas GitHub Pages.');
