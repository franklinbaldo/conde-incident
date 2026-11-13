import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// ssg 0.0.75's CLI registers SearchPlugin with English labels, even when
// ssg.toml declares language="pt-BR". Patch only its generated HTML UI text.
// Do not touch the fingerprinted JS or its SRI/CSP integrity metadata.
const translations = [
  ['<button id="ssg-search-btn" type="button" aria-label="Search">',
   '<button id="ssg-search-btn" type="button" aria-label="Pesquisar">'],
  ['<span>Search</span>', '<span>Pesquisar</span>'],
  ['<div id="ssg-search-overlay" role="dialog" aria-label="Search">',
   '<div id="ssg-search-overlay" role="dialog" aria-label="Pesquisar">'],
  ['<input id="ssg-search-input" type="search" placeholder="Search documentation..." autocomplete="off" aria-label="Search"/>',
   '<input id="ssg-search-input" type="search" placeholder="Pesquisar no acervo..." autocomplete="off" aria-label="Pesquisar"/>'],
  ['<span><kbd>Esc</kbd> close</span>', '<span><kbd>Esc</kbd> fechar</span>'],
  ['<span><kbd>&uarr;</kbd><kbd>&darr;</kbd> navigate</span>',
   '<span><kbd>&uarr;</kbd><kbd>&darr;</kbd> navegar</span>'],
  ['<span><kbd>Enter</kbd> open</span>', '<span><kbd>Enter</kbd> abrir</span>'],
];

export function localizeSearchWidget(html) {
  const start = html.indexOf('id="ssg-search-widget"');
  if (start < 0) return { html, found: false, changed: false };
  assert.match(html.slice(0, start), /<html\b[^>]*lang="pt-BR"/i,
    'SSG search localization expects a pt-BR page');
  const end = html.lastIndexOf('</body>');
  assert.ok(end > start, 'SSG search widget must precede </body>');
  let widget = html.slice(start, end);
  let changed = false;
  for (const [original, translated] of translations) {
    const count = widget.split(original).length - 1;
    if (count === 1) {
      widget = widget.replace(original, translated);
      changed = true;
    } else {
      assert.equal(count, 0, 'Unexpected duplicate SSG widget copy: ' + original);
      assert.equal(widget.split(translated).length - 1, 1,
        'SSG widget markup changed; review localization: ' + original);
    }
  }
  return { html: html.slice(0, start) + widget + html.slice(end), found: true, changed };
}

function* htmlFiles(path) {
  for (const ent of readdirSync(path, { withFileTypes: true })) {
    const file = join(path, ent.name);
    if (ent.isDirectory()) yield* htmlFiles(file);
    else if (ent.isFile() && ent.name.endsWith('.html')) yield file;
  }
}

export function localizeGeneratedPages({ check = false, root = resolve('public') } = {}) {
  assert.ok(existsSync(join(root, 'index.html')), 'Run after ssg build');
  let checked = 0, updated = 0;
  for (const file of htmlFiles(root)) {
    const source = readFileSync(file, 'utf8');
    const result = localizeSearchWidget(source);
    if (!result.found) continue; // SPA /lab/ is a separate bilingual application.
    checked++;
    if (check) assert.equal(result.changed, false, 'SSG widget remains untranslated: ' + file);
    else if (result.changed) { writeFileSync(file, result.html); updated++; }
  }
  assert.ok(checked >= 3, 'SSG search widget absent from generated pages');
  console.log('SSG pt-BR search: ' + checked + ' pages checked, ' + updated + ' updated');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  localizeGeneratedPages({ check: process.argv.includes('--check') });
