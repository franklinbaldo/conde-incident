import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import test from 'node:test';

// Check the generated SSG artifact, not a handcrafted HTML fixture.
// The laboratory has its own React layout and is intentionally excluded.
const routes = [
  'index.html',
  'stories/index.html',
  'cronologia/index.html',
  'evidencias/arquivo/index.html',
  'stories/2026-11-12-o-mapa-que-conhecia-conde/index.html',
];

function siteFooter(html) {
  const match = html.match(/<footer class="site-footer">\s*<div class="wrap">([\s\S]*?)<\/div>\s*<\/footer>/i);
  return match?.[1] || null;
}

test('negative controls reject the published unstyled footer and incomplete fix', () => {
  assert.equal(siteFooter('<main></main><footer><p>Nota</p></footer>'), null);
  assert.equal(siteFooter('<main></main><footer class="site-footer"><p>Nota</p></footer>'), null);
  assert.equal(siteFooter('<main></main><footer><div class="wrap"><p>Nota</p></div></footer>'), null);
});

test('production CSS declares both the footer treatment and centered grid', () => {
  const css = readFileSync('public/css/site.css', 'utf8');
  assert.match(css, /\.site-footer\s*\{[^}]*border-top:/);
  assert.match(css, /\.wrap\s*\{[^}]*margin-inline:auto/);
});

for (const route of routes) {
  test('built SSG footer uses the same centered grid as the article: ' + route, () => {
    const html = readFileSync(join('public', route), 'utf8');
    const block = siteFooter(html);
    assert.ok(block, 'missing styled centered global footer in ' + route);
    assert.match(block, /Documento, relato, hipótese e simulação são categorias diferentes\./);
    assert.match(block, /href="https:\/\/github\.com\/franklinbaldo\/conde-incident"/);
    assert.ok(html.lastIndexOf('<main') < html.lastIndexOf('<footer class="site-footer">'),
      'footer must come after the main landmark in ' + route);
  });
}
