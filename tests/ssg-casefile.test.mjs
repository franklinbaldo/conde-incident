import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {checkPage,AUTHORED_ROUTES} from '../scripts/ssg-authored-pages.mjs';

const src=readFileSync('pages/dossie/page.md','utf8');
const css=readFileSync('static/css/site.css','utf8');

test('o dossiê é uma Page canônica do SSG, não uma SPA',()=>{
  assert.ok(AUTHORED_ROUTES.includes('dossie'));
  assert.equal(checkPage('dossie',src),src);
  assert.doesNotMatch(src,/<script\b|on(click|load|mouseover)\s*=/i);
  for(const term of ['C01#1','C197#1','Rádio Tupi','NASA','não demonstra','Não informa']) {
    assert.ok(src.includes(term),'limite epistemológico ausente: '+term);
  }
  for(const target of [
    '/conde-incident/evidencias/arquivo/c01-1/',
    '/conde-incident/evidencias/arquivo/c197-1/',
    '/conde-incident/hipoteses/',
    '/conde-incident/lab/#/map',
    '/conde-incident/mapa/',
    '/conde-incident/stories/2026-11-11-o-dia-em-que-dois-relatos-se-cruzaram/',
  ]) assert.ok(src.includes('href="'+target+'"'),'elo de jornada ausente: '+target);
});
test('o design system é CSS nativo e reutiliza classes de cartões',()=>{
  for(const token of ['--cf-paper','--cf-ink','--cf-accent','--cf-line','--cf-focus']) {
    assert.ok(css.includes(token),'token ausente '+token);
  }
  for(const cls of ['cf-card','cf-kicker','cf-button','cf-section','cf-trail']) {
    assert.ok(css.includes('.'+cls),'componente ausente '+cls);
  }
  assert.match(css,/@media\(max-width:700px\)/);
  assert.match(css, /@media\(prefers-reduced-motion:reduce\)/);
});

test('a trilha do dossiê é navegação real sem JS, com quatro destinos internos únicos',()=>{
  const trail=src.match(/<nav aria-label="Etapas do dossiê">([\\s\\S]*?)<\\/nav>/)?.[1];
  assert.ok(trail,'falta landmark de navegação de etapas');
  const targets=[...trail.matchAll(/<li><a href="#([a-z]+)">/g)].map(m=>m[1]);
  assert.deepEqual(targets,['relato','fontes','hipoteses','experimentos']);
  for(const id of targets){
    assert.equal([...src.matchAll(new RegExp('\\\\bid="'+id+'"','g'))].length,1,
      'destino da trilha ausente ou duplicado: '+id);
    assert.match(src,new RegExp('id="'+id+'" tabindex="-1"'),
      'destino de fragmento precisa aceitar foco de teclado: '+id);
  }
  assert.doesNotMatch(trail,/<button|onclick|<script/i);
  assert.match(css,/\\.casefile \\.cf-trail a:focus-visible|\\.casefile a:focus-visible/,
    'a trilha precisa de foco de teclado visível');
});
