import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// SSG 0.0.75 has one shared navigation bar but no route-aware active state.
// Decorate the built HTML, not its fingerprinted JavaScript or article links.
const opening = '<nav aria-label="Navegação principal">';
const mapLink = '<a href="/conde-incident/mapa/">Mapa</a>';
const simulations = '<a href="/conde-incident/simulacoes/">Simulações</a>';
const sections = new Set(['stories', 'cronologia', 'evidencias', 'hipoteses',
  'mapa', 'simulacoes', 'metodo']);

export function annotateNavigation(html, route) {
  assert.ok(route === 'index.html' || /^[a-z0-9-]+(?:\/[a-z0-9-]+)*\/index\.html$/.test(route),
    'Rota SSG inválida: ' + route);
  if (route.startsWith('lab/')) return {html, found: false, changed: false};
  const start = html.indexOf(opening);
  if (start < 0) return {html, found: false, changed: false};
  assert.equal(html.indexOf(opening, start + opening.length), -1, 'Navegação duplicada');
  const end = html.indexOf('</nav>', start);
  assert.ok(end > start, 'Navegação sem fechamento');
  assert.match(html.slice(0, start), /<html\b[^>]*lang="pt-BR"/i, 'SSG sem pt-BR');
  const oldNav = html.slice(start, end + 6);
  let nav = oldNav;
  if (!nav.includes(mapLink)) {
    assert.equal(nav.split(simulations).length - 1, 1, 'Link de simulações alterado');
    nav = nav.replace(simulations, simulations + '\n' + mapLink);
  }
  assert.equal(nav.split(mapLink).length - 1, 1, 'Link de mapa duplicado');
  const section = route === 'index.html' ? '' : route.split('/')[0];
  if (section === '' || sections.has(section)) {
    const href = '/conde-incident/' + (section ? section + '/' : '');
    const anchor = '<a href="' + href + '"';
    assert.equal(nav.split(anchor).length - 1, 1, 'Destino principal ausente/duplicado: ' + href);
    const selected = anchor + ' aria-current="page"';
    if (!nav.includes(selected)) nav = nav.replace(anchor, selected);
    assert.equal((nav.match(/aria-current="page"/g) || []).length, 1,
      'Mais de uma seção marcada como atual');
  }
  return {html: html.slice(0, start) + nav + html.slice(end + 6),
    found: true, changed: nav !== oldNav};
}

function* pages(dir) {
  for (const ent of readdirSync(dir, {withFileTypes: true})) {
    const file = join(dir, ent.name);
    if (ent.isDirectory() && ent.name !== 'lab') yield* pages(file);
    else if (ent.isFile() && ent.name === 'index.html') yield file;
  }
}

export function annotateGeneratedNavigation({root = resolve('public'), check = false} = {}) {
  assert.ok(existsSync(join(root, 'index.html')), 'SSG build ainda não executado');
  let checked = 0, updated = 0;
  for (const file of pages(root)) {
    const result = annotateNavigation(readFileSync(file, 'utf8'), relative(root, file).replaceAll('\\', '/'));
    if (!result.found) continue;
    checked++;
    if (check) assert.equal(result.changed, false, 'Navegação não tratada: ' + file);
    else if (result.changed) {writeFileSync(file, result.html); updated++;}
  }
  assert.ok(checked >= 3, 'Navegação SSG ausente');
  console.log('SSG navegação acessível: ' + checked + ' páginas, ' + updated + ' atualizadas');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  annotateGeneratedNavigation({check: process.argv.includes('--check')});
