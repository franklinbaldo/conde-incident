import test from 'node:test';
import assert from 'node:assert/strict';
import { localizeSearchWidget } from '../scripts/localize-ssg-search.mjs';

// Markup copied from the SSG 0.0.75 generated search surface (not the SPA).
const input = `<!doctype html><html lang="pt-BR"><body><p>Search is a research term</p>
<div id="ssg-search-widget">
<button id="ssg-search-btn" type="button" aria-label="Search"><span>Search</span></button>
<div id="ssg-search-overlay" role="dialog" aria-label="Search">
<input id="ssg-search-input" type="search" placeholder="Search documentation..." autocomplete="off" aria-label="Search"/>
<div class="ssg-search-footer"><span><kbd>Esc</kbd> close</span><span><kbd>&uarr;</kbd><kbd>&darr;</kbd> navigate</span><span><kbd>Enter</kbd> open</span></div>
</div></div><script src="/conde-incident/_csp/hash.js" integrity="sha384-test"></script></body></html>`;

test('localizes visible and accessible SSG search strings without touching article or SRI', () => {
  const result = localizeSearchWidget(input);
  assert.equal(result.found, true);
  assert.equal(result.changed, true);
  for (const text of ['aria-label="Pesquisar"', '<span>Pesquisar</span>',
    'placeholder="Pesquisar no acervo..."', 'fechar', 'navegar', 'abrir'])
    assert.ok(result.html.includes(text), text);
  assert.ok(result.html.includes('<p>Search is a research term</p>'));
  assert.ok(result.html.includes('integrity="sha384-test"'));
  assert.deepEqual(localizeSearchWidget(result.html), { ...result, changed: false });
});

test('does not alter the independent laboratory or pages without SSG search', () => {
  const html = '<html lang="en"><body><p>Search</p></body></html>';
  assert.deepEqual(localizeSearchWidget(html), { html, found: false, changed: false });
});

test('fails closed if SSG changes a widget selector or source string', () => {
  assert.throws(() => localizeSearchWidget(input.replace('Search documentation...', 'Find')), /SSG widget markup changed/);
});
