import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const html=readFileSync('public/dossie/index.html','utf8');

test('o SSG publicou um dossiê acessível e recuperável sem hidratação',()=>{
  assert.match(html,/<link rel="canonical" href="https:\/\/franklinbaldo.github.io\/conde-incident\/dossie\/">/);
  assert.match(html,/<main id="main"/);
  assert.equal((html.match(/<h1\b/g)??[]).length,1);
  for(const id of ['fontes','pergunta']) assert.ok(html.includes('id="'+id+'"'));
  assert.match(html,/casefile/);
  assert.match(html,/"@type":"WebPage"/);
  assert.doesNotMatch(html,/"@type":"Article"/,"Page SSG não deve exigir autoria ou data de artigo");
  for(const marker of ['C01#1','C197#1']) assert.ok(html.includes(marker));
  assert.doesNotMatch(html,/<script[^>]*src="[^"]*(react|vite|index-[^"]+\.js)"/i);
});
