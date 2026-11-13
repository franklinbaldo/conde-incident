import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {AUTHORED_ROUTES} from './ssg-authored-pages.mjs';

const read=slug=>readFileSync(join('public',slug,'index.html'),'utf8');
const home=readFileSync('public/index.html','utf8');
const sim=read('simulacoes');
assert.ok(home.includes('/conde-incident/mapa/'),
  'Índice SSG sem acesso à página independente do mapa');
assert.ok(sim.includes('/conde-incident/mapa/'),
  'Índice das simulações sem página cartográfica');
for(const slug of AUTHORED_ROUTES){
  const page=read(slug);
  const canonical='https://franklinbaldo.github.io/conde-incident/'+slug+'/';
  assert.ok(page.includes('<link rel="canonical" href="'+canonical+'">'),
    'URL canônica SSG divergente: '+slug);
  assert.match(page,/<h1\b/i,'Página sem título visível: '+slug);
  assert.match(page,/Content-Security-Policy/,'Página sem CSP: '+slug);
  assert.ok(page.includes('/conde-incident/'),
    'Página publicada sem prefixo GitHub Pages: '+slug);
}
const legacy=[
  ['mapa','map'],
  ['simulacoes/inverso','inverse'],
  ['simulacoes/triangulacao','triangulation'],
  ['simulacoes/sensibilidade','sensitivity'],
  ['simulacoes/montecarlo','montecarlo'],
  ['simulacoes/tles','tles'],
];
for(const [slug,id] of legacy){
 assert.ok(read(slug).includes('/conde-incident/lab/#/'+id),
   'Página não preserva ferramenta existente: '+slug);
 if(slug!=='mapa'){
  assert.ok(sim.includes('/conde-incident/'+slug+'/'),
    'Página independente ausente do índice de simulações: '+slug);
 }
}
console.log('PASS: '+AUTHORED_ROUTES.length+' URLs SSG canônicas com navegação e retorno ao laboratório.');
