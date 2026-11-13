import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {AUTHORED_ROUTES,checkPage} from '../scripts/ssg-authored-pages.mjs';

test('todas as páginas canônicas têm URL própria, tipo e acesso à ferramenta',()=>{
  assert.equal(AUTHORED_ROUTES.length,9);
  for(const slug of AUTHORED_ROUTES){
    const page=readFileSync('pages/'+slug+'/index.md','utf8');
    assert.equal(checkPage(slug,page),page);
    assert.match(page,/^---\ntype: Page\n/);
    assert.ok(page.includes('canonical_route: "/conde-incident/'+slug+'/"'));
  }
});
test('índice preserva todas as oito URLs anteriores do laboratório',()=>{
  const content=readFileSync('pages/simulacoes/index.md','utf8');
  for(const id of ['summary','map','inverse','triangulation','sensitivity','montecarlo','tles','documents'])
    assert.ok(content.includes('/conde-incident/lab/#/'+id),'Deep link legado perdido: '+id);
});
test('rota divergente, tipo errado, metadado repetido e ferramenta sem retorno falham',()=>{
  const slug='mapa';
  const valid=readFileSync('pages/mapa/index.md','utf8');
  assert.throws(()=>checkPage(slug,valid.replace('type: Page','type: Story')));
  assert.throws(()=>checkPage(slug,valid.replace('/conde-incident/mapa/','/conde-incident/outra/')));
  assert.throws(()=>checkPage(slug,valid.replace('type: Page','type: Page\ntype: Page')));
  assert.throws(()=>checkPage(slug,valid.replace('/conde-incident/lab/#/map','/desconhecido')));
  assert.throws(()=>checkPage('../unsafe',valid));
});
