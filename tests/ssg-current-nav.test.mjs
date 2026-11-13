import test from 'node:test';
import assert from 'node:assert/strict';
import { markEditorialNav } from '../scripts/mark-editorial-nav.mjs';

const html = '<html><body><header class="masthead"><nav aria-label="Navegação principal">' +
  '<a href="/conde-incident/">Início</a>' +
  '<a href="/conde-incident/stories/">Histórias</a>' +
  '<a href="/conde-incident/evidencias/">Evidências</a>' +
  '</nav></header><main id="main"><h1>Conde</h1></main></body></html>';
for (const [file, href, value] of [
  ['index.html', '/', 'page'],
  ['stories/index.html', '/stories/', 'page'],
  ['stories/2026-11-13-capitulo/index.html', '/stories/', 'location'],
  ['evidencias/arquivo/familias/exemplo/index.html', '/evidencias/', 'location']
]) test('Marks ' + file + ' as ' + value, () => {
  const first = markEditorialNav(html, file);
  assert.equal(first.found, true);
  assert.equal(first.changed, true);
  assert.ok(first.html.includes('<a href="/conde-incident' + href +
    '" aria-current="' + value + '">'));
  assert.equal((first.html.match(/aria-current=/g) || []).length, 1);
  assert.deepEqual(markEditorialNav(first.html, file), { ...first, changed: false });
  assert.ok(first.html.includes('<main id="main">'));
});
test('Leaves SPA and foreign markup alone', () => {
  assert.deepEqual(markEditorialNav(html, 'lab/index.html'),
    { html, changed: false, found: false });
  assert.deepEqual(markEditorialNav('<main>x</main>', 'stories/index.html'),
    { html: '<main>x</main>', changed: false, found: false });
});
test('Fails closed when a nav link disappears or duplicates', () => {
  assert.throws(() => markEditorialNav(html.replaceAll('/conde-incident/stories/', '/other/'),
    'stories/index.html'), /exactly one/);
  assert.throws(() => markEditorialNav(html.replace('</nav>',
    '<a href="/conde-incident/stories/">again</a></nav>'), 'stories/index.html'), /exactly one/);
});
