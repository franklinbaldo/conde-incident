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
assert.match(chapter03,/<figure\b/i,'Capítulo 03 sem figuras incorporadas');
assert.match(chapter03,/<iframe\b[^>]*src=[\"']https:\/\/www\.openstreetmap\.org\/export\/embed/i,'Mapa ausente no HTML final');
assert.match(chapter03,/<iframe\b[^>]*src=[\"']https:\/\/media\.ondisclosure\.org\/[^\s\"']+\.pdf/i,'Documento PDF não incorporado');
assert.match(chapter03,/cadeia-documental-conde\.svg/,'Diagrama ausente');
assert.match(chapter03,/frame-src[^<]*www\.openstreetmap\.org/,'CSP impede mapa incorporado');
assert.match(chapter03,/frame-src[^<]*media\.ondisclosure\.org/,'CSP impede documento incorporado');
assert.ok(existsSync('public/img/cadeia-documental-conde.svg'),'Asset do diagrama não copiado');

assert.match(chapter03,/<picture>[\s\S]*?<source\s+media=["']\(max-width:\s*620px\)["']\s+srcset=["']\/conde-incident\/img\/cadeia-documental-conde-mobile\.svg["']/,
  'Genealogia documental não possui variante móvel');
assert.ok(existsSync('public/img/cadeia-documental-conde-mobile.svg'),'SVG móvel ausente na publicação');
const diagramMobile=read('img/cadeia-documental-conde-mobile.svg');
assert.match(diagramMobile,/viewBox="0 0 340 616"/,'Diagrama móvel não é vertical');
for(const stamp of ['8 NOV 1963','14 NOV 1963','20 NOV 1963','testemunhas independentes'])
  assert.ok(diagramMobile.includes(stamp),'Etapa documental ausente no diagrama móvel: '+stamp);
const fontSizes=[...diagramMobile.matchAll(/font-size="([0-9.]+)"/g)].map(match=>Number(match[1]));
assert.ok(fontSizes.length>0 && Math.min(...fontSizes)>=13,'Texto SVG móvel ilegível por redução excessiva');



const stanislaw=read('stories/2026-11-12-o-humorista-que-encontrou-um-satelite-na-redacao/index.html');
assert.match(stanislaw,/<figure\b/i,'Capitulo Stanislaw sem documento visual');
assert.ok(stanislaw.includes('https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00477.pdf#page=7'),'Original de Ultima Hora nao foi incorporado');
assert.ok(stanislaw.includes('frame-src https://hemeroteca-pdf.bn.gov.br'),'CSP impede fac-simile de Ultima Hora');
assert.ok(stanislaw.includes('stanislaw-escalada.svg') && stanislaw.includes('stanislaw-escalada-mobile.svg'),'Diagrama comparativo sem variantes responsivas');
assert.ok(existsSync('public/img/stanislaw-escalada.svg'),'SVG da crônica nao publicado');
assert.ok(existsSync('public/img/stanislaw-escalada-mobile.svg'),'SVG vertical da crônica nao publicado');
for(const name of ['stanislaw-escalada.svg','stanislaw-escalada-mobile.svg']) {
 const svg=read('img/'+name);
 for(const word of ['Stanislaw','FBIS','satélite']) assert.ok(svg.toLowerCase().includes(word.toLowerCase()),'Diagrama sem contexto: '+word);
}

assert.ok(chapters>0,'Nenhuma reportagem renderizada');
console.log('PASS: '+chapters+' capítulos, índice, CSS, laboratório e rotas GitHub Pages.');
