import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {AUTHORED_ROUTES,checkPage} from '../scripts/ssg-authored-pages.mjs';

test('todas as páginas canônicas têm URL própria, tipo e acesso à ferramenta',()=>{
  assert.equal(AUTHORED_ROUTES.length,11);
  for(const slug of AUTHORED_ROUTES){
    const page=readFileSync('pages/'+slug+'/page.md','utf8');
    assert.equal(checkPage(slug,page),page);
    assert.match(page,/^---\ntype: Page\n/);
    assert.ok(page.includes('canonical_route: "/conde-incident/'+slug+'/"'));
  }
});
test('oito perguntas conectam contexto SSG e instrumento real, sem links órfãos',()=>{
  const content=readFileSync('pages/simulacoes/page.md','utf8');
  const routes={
    summary:'/',map:'/mapa/',inverse:'/simulacoes/inverso/',
    triangulation:'/simulacoes/triangulacao/',sensitivity:'/simulacoes/sensibilidade/',
    montecarlo:'/simulacoes/montecarlo/',tles:'/simulacoes/tles/custodia/',
    documents:'/evidencias/arquivo/',
  };
  const cards=content.split('<li data-lab-tab="').slice(1).map(fragment=>{
    const tab=fragment.slice(0,fragment.indexOf('"'));
    const body=fragment.slice(fragment.indexOf('">')+2,fragment.indexOf('</li>'));
    return {tab,body};
  });
  assert.equal(cards.length,8,'não publicar um índice incompleto/duplicado');
  assert.deepEqual(new Set(cards.map(card=>card.tab)),new Set(Object.keys(routes)));
  for(const {tab,body} of cards){
    const links=[...body.matchAll(/<a href="([^"]+)"/g)].map(match=>match[1]);
    assert.deepEqual(links,[
      '/conde-incident'+routes[tab],
      '/conde-incident/lab/#/'+tab,
    ],'par de rotas divergente: '+tab);
    assert.ok(body.includes('<h3>') && body.includes('</h3>'));
    assert.ok(body.includes('Ler contexto:'));
    assert.ok(body.includes('Abrir instrumento:'));
  }
  assert.match(content,/cálculos ainda dependem do laboratório React/);
  assert.match(content,/não comprova sobrevoo de Conde/);
  assert.ok(content.includes('[Visão geral de TLEs](/conde-incident/simulacoes/tles/)'));
});
test('rota divergente, tipo errado, metadado repetido e ferramenta sem retorno falham',()=>{
  const slug='mapa';
  const valid=readFileSync('pages/mapa/page.md','utf8');
  assert.throws(()=>checkPage(slug,valid.replace('type: Page','type: Story')));
  assert.throws(()=>checkPage(slug,valid.replace('/conde-incident/mapa/','/conde-incident/outra/')));
  assert.throws(()=>checkPage(slug,valid.replace('type: Page','type: Page\ntype: Page')));
  assert.throws(()=>checkPage(slug,valid.replace('/conde-incident/lab/#/map','/desconhecido')));
  assert.throws(()=>checkPage('../unsafe',valid));
});
