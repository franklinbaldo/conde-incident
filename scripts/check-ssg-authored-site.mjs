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
const lookupPage=read('evidencias/fontes');
assert.match(lookupPage,/id="source-lookup-form"/, 'Consulta documental SSG ausente');
// Fail the Pages build if a reverse-index source would lead to a missing or
// foreign profile. This checks all profiles, not only one smoke-test click.
const sourcePointer=JSON.parse(readFileSync('public/data/conde-source-lookup-manifest.json'));
const sourceShard=readFileSync(sourcePointer.source_index.path);
assert.equal(sourceShard.length,sourcePointer.source_index.bytes);
const sourceIndex=JSON.parse(sourceShard);
const sourceRoutes=new Set();
for(const source of sourceIndex.sources){
  assert.match(source.source_id,/^[A-Z][A-Z0-9_]{1,95}$/);
  const slug=source.source_id.toLowerCase().replaceAll('_','-');
  assert.ok(!sourceRoutes.has(slug),'Colisão de slug na consulta reversa: '+slug);
  sourceRoutes.add(slug);
  const html=read('evidencias/arquivo/fontes/'+slug);
  assert.ok(html.includes(source.source_id),'Ficha sem identificador: '+slug);
  for(const ref of source.references){
    assert.ok(html.includes(ref.occurrence),'Ficha sem ocorrência: '+slug+' / '+ref.occurrence);
    assert.ok(html.includes(ref.row_sha256),'Ficha sem digest de linha: '+slug);
    assert.ok(html.includes(ref.archive_path),'Ficha sem link de ocorrência: '+slug);
  }
}
assert.ok(read('evidencias/arquivo/fontes').includes('Identificadores de fontes'),
  'Índice estático de fontes ausente');
assert.ok(lookupPage.includes('/conde-incident/evidencias/arquivo/fontes/'),
  'Consulta reversa sem fallback direto para fichas estáticas');
assert.match(lookupPage,/js\/ssg-source-lookup-ui\.mjs/, 'Módulo de consulta não publicado');
assert.match(lookupPage,/evidencias\/arquivo\//, 'Fallback sem JS não publicado');
// The SSG Map page is useful offline, without the React lab or tile-provider quota.
const editorialMap=read('mapa');
assert.match(editorialMap,/<figure class="context-map">[\s\S]*?<img\b[^>]*src="\/conde-incident\/img\/conde-bahia-context\.svg"/,
  'Página Mapa perdeu a cartografia SVG local');
assert.match(editorialMap,/<img\b[^>]*alt="[^"]*Conde[^"]*queda[^"]*"/,
  'Mapa sem descrição textual distinguindo sede e local de queda');
assert.match(editorialMap,/Natural Earth 1:110m/,
  'Mapa SSG sem fonte cartográfica e escala');
assert.match(editorialMap,/href="\/conde-incident\/img\/conde-bahia-context\.svg"/,
  'Mapa SSG sem acesso ao original independente de JavaScript');
assert.doesNotMatch(editorialMap, /<iframe\b|www\.openstreetmap\.org\/export\/embed|maps\.googleapis\.com/i,
  'Mapa SSG contém serviço externo de tiles');
assert.ok(readFileSync('public/img/conde-bahia-context.svg','utf8').includes('Natural Earth 1:110m'),
  'Mapa local não foi incluído no site publicado');
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
const custody=read('simulacoes/tles/custodia');
assert.ok(custody.includes('https://franklinbaldo.github.io/conde-incident/simulacoes/tles/custodia/'),
 'Custódia TLE sem URL canônica independente');
for(const marker of ['63300.61129783','198.5261','18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd','C179#1'])
 assert.ok(custody.includes(marker),'Custódia TLE ausente no HTML publicado: '+marker);
assert.ok(read('simulacoes/tles').includes('/conde-incident/simulacoes/tles/custodia/'),
 'Auditoria TLE sem acesso à custódia SSG');
// Static pages expose the quota-free map without opening legacy Google SDK hosts.
// The React /lab/ is separate and is not mutated by this check.
for (const file of ['index.html','stories/index.html',
  'stories/2026-11-12-a-resposta-que-veio-de-salvador/index.html',
  'evidencias/arquivo/index.html',
  'evidencias/arquivo/c197-1/index.html',
  ...AUTHORED_ROUTES.map(route => route + '/index.html')]) {
  const html = readFileSync(join('public', file), 'utf8');
  const nav = /<nav aria-label="Navegação principal">([\s\S]*?)<\/nav>/.exec(html)?.[1];
  assert.ok(nav, 'Navegação SSG ausente: '+file);
  assert.equal((nav.match(/href="\/conde-incident\/mapa\/"/g) || []).length, 1,
    'Link Mapa não encontrado exatamente uma vez: '+file);
  const policy = /<meta http-equiv="Content-Security-Policy" content="([^"]+)">/.exec(html)?.[1];
  assert.ok(policy, 'CSP SSG ausente: '+file);
  assert.match(policy, /script-src 'self'/, 'Script local não permitido: '+file);
  assert.doesNotMatch(policy, /maps\.googleapis\.com|\*\.googleapis\.com|\*\.gstatic\.com/,
    'CSP ainda autoriza SDK Google Maps sem necessidade: '+file);
}
console.log('PASS: '+AUTHORED_ROUTES.length+' URLs SSG canônicas com navegação e retorno ao laboratório.');
