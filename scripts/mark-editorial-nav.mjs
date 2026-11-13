import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { resolve, relative, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const prefix = '/conde-incident/';
const sections = new Set(['', 'stories', 'cronologia', 'evidencias', 'hipoteses',
  'mapa', 'simulacoes', 'metodo']);

// Only postprocess generated SSG HTML. Never alter fingerprinted JS or CSP/SRI.
export function markEditorialNav(html, file) {
  if (!file.endsWith('index.html')) return { html, changed: false, found: false };
  const route = file.replaceAll('\\', '/').replace(/index\.html$/, '').replace(/\/$/, '');
  const section = route ? route.split('/')[0] : '';
  if (!sections.has(section)) return { html, changed: false, found: false };
  const header = html.indexOf('<header class="masthead">');
  if (header < 0) return { html, changed: false, found: false };
  const start = html.indexOf('<nav', header), end = html.indexOf('</nav>', start);
  assert(start > header && end > start, 'Missing editorial navigation: ' + file);
  const nav = html.slice(start, end);
  const href = prefix + (section ? section + '/' : '');
  const anchor = '<a href="' + href + '">';
  assert.equal(nav.split(anchor).length - 1, 1,
    'Expected exactly one section link: ' + JSON.stringify({ file, route, section, href, anchor, nav }));
  const state = route === '' || route === section ? 'page' : 'location';
  const marked = '<a href="' + href + '" aria-current="' + state + '">';
  if (nav.includes(marked)) {
    assert.equal((nav.match(/aria-current=/g) || []).length, 1,
      'Conflicting current links: ' + file);
    return { html, changed: false, found: true };
  }
  assert.doesNotMatch(nav, /aria-current=/, 'Unexpected active marker: ' + file);
  return { html: html.slice(0, start) + nav.replace(anchor, marked) + html.slice(end),
    changed: true, found: true };
}
function* htmlFiles(path) {
  for (const ent of readdirSync(path, { withFileTypes: true })) {
    const file = join(path, ent.name);
    if (ent.isDirectory()) yield* htmlFiles(file);
    else if (ent.isFile() && ent.name === 'index.html') yield file;
  }
}
export function markGeneratedNavigation({ root = resolve('public'), check = false } = {}) {
  assert.ok(existsSync(join(root, 'index.html')), 'Run after SSG build');
  let inspected = 0, updated = 0;
  for (const file of htmlFiles(root)) {
    const source = readFileSync(file, 'utf8');
    const result = markEditorialNav(source, relative(root, file));
    if (!result.found) continue; // /lab is a separate SPA.
    inspected++;
    if (check) assert.equal(result.changed, false, 'Missing current nav: ' + file);
    else if (result.changed) { writeFileSync(file, result.html); updated++; }
  }
  assert.ok(inspected >= 7, 'Expected at least seven editorial SSG pages');
  console.log('SSG current section: ' + inspected + ' checked, ' + updated + ' updated');
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  markGeneratedNavigation({ check: process.argv.includes('--check') });
