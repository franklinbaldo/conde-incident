import test from 'node:test';
import assert from 'node:assert/strict';
import {annotateNavigation} from '../scripts/ssg-navigation.mjs';

const nav = `<nav aria-label="Navegação principal">
<a href="/conde-incident/">Início</a>
<a href="/conde-incident/stories/">Histórias</a>
<a href="/conde-incident/evidencias/">Evidências</a>
<a href="/conde-incident/simulacoes/">Simulações</a>
<a href="/conde-incident/lab/">Laboratório</a></nav>`;
const html = `<html lang="pt-BR"><body>${nav}<main><a href="/conde-incident/mapa/">Veja a fonte</a></main></body></html>`;
const selected = (content) => content.match(/<a [^>]*aria-current="page"[^>]*>/g) || [];

test('indica uma única seção ativa no acervo e nos capítulos, sem alterar links editoriais', () => {
  for (const [route, section] of [
    ['index.html', ''], ['stories/index.html', 'stories'],
    ['stories/2026-11-13-a-fonte/index.html', 'stories'],
    ['evidencias/arquivo/c197-1/index.html', 'evidencias'],
    ['simulacoes/tles/custodia/index.html', 'simulacoes']
  ]) {
    const result = annotateNavigation(html, route);
    assert.equal(result.found, true);
    assert.equal(selected(result.html).length, 1);
    const expected = '/conde-incident/' + (section ? section + '/' : '');
    assert.ok(selected(result.html)[0].includes('href="' + expected + '"'));
    assert.ok(result.html.includes('href="/conde-incident/mapa/">Veja a fonte</a>'));
    assert.ok(result.html.includes('href="/conde-incident/mapa/">Mapa</a>'));
    assert.deepEqual(annotateNavigation(result.html, route), {...result, changed: false});
  }
});

test('identifica o mapa diretamente e não altera a aplicação React', () => {
  assert.equal(selected(annotateNavigation(html, 'mapa/index.html').html)[0].includes('/mapa/'), true);
  assert.deepEqual(annotateNavigation(html, 'lab/index.html'),
    {html, found: false, changed: false});
});

test('falha fechado em duplicação, troca de template ou rotas não confiáveis', () => {
  assert.throws(() => annotateNavigation(html + nav, 'index.html'), /duplicada/);
  assert.throws(() => annotateNavigation(html.replace('Simulações</a>', 'Calculadora</a>'), 'index.html'), /simulações alterado/);
  assert.throws(() => annotateNavigation(html, '../index.html'), /Rota SSG inválida/);
  assert.throws(() => annotateNavigation(html.replace('lang="pt-BR"', 'lang="en"'), 'index.html'), /pt-BR/);
  assert.throws(() => annotateNavigation(html.replace('>Histórias</a>', ' aria-current="page">Histórias</a>'), 'index.html'), /Mais de uma seção/);
});
