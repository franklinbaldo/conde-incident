/** Structural return paths for deep SSG pages, never for React hash routes. */
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const prefix = '/conde-incident/';
const sections = new Map([
  ['stories', 'Histórias'], ['cronologia', 'Cronologia'],
  ['evidencias', 'Evidências'], ['hipoteses', 'Hipóteses'],
  ['mapa', 'Mapa'], ['simulacoes', 'Simulações'], ['metodo', 'Método'],
]);
const names = new Map([
  ['arquivo', 'Arquivo documental'], ['estados', 'Estados documentais'],
  ['tles', 'TLEs'], ['custodia', 'Custódia documental'],
]);
const main = '<main id="main" class="wrap" tabindex="-1">';

function label(segment) {
  return names.get(segment) || sections.get(segment) ||
    (segment.charAt(0).toLocaleUpperCase('pt-BR') + segment.slice(1).replaceAll('-', ' '));
}
function fileParts(path) {
  const normalized = path.replaceAll('\\', '/');
  if (!normalized.endsWith('/index.html')) return [];
  const parts = normalized.split('/').slice(0, -1);
  if (parts.length < 2 || !sections.has(parts[0])) return [];
  assert.ok(parts.every(s => /^[a-z0-9-]+$/.test(s)), 'Rota SSG insegura: ' + path);
  return parts;
}
export function addBreadcrumbs(html, path, hasPage = () => true) {
  const parts = fileParts(path);
  if (!parts.length) return { html, eligible: false, changed: false };
  // Preserve offsets while excluding inert markup: an exact breadcrumb string
  // in a comment, script, template or textarea is not a navigable DOM node.
  const activeHtml = html
    .replace(/<!--[\s\S]*?(?:-->|$)/g, text => ' '.repeat(text.length))
    .replace(/<(script|style|template|textarea)\b[^>]*>[\s\S]*?<\/\1\s*>/gi,
      text => ' '.repeat(text.length));
  const mainAt = activeHtml.indexOf(main);
  assert.ok(mainAt >= 0, 'Main canônico ausente: ' + path);
  const match = /<title>([^<>\r\n]{1,320})<\/title>/i.exec(activeHtml);
  assert.ok(match && match[1].trim(), 'Título textual seguro ausente: ' + path);
  const items = ['<li><a href="' + prefix + '">Início</a></li>'];
  for (let i = 1; i < parts.length; i++) {
    const ancestor = parts.slice(0, i).join('/');
    if (!hasPage(ancestor)) continue; // No dead links to intermediate routes.
    items.push('<li><a href="' + prefix + ancestor + '/">' + label(parts[i - 1]) + '</a></li>');
  }
  items.push('<li><span aria-current="page">' + match[1] + '</span></li>');
  const trail = '<nav aria-label="Trilha de navegação" class="breadcrumbs"><ol>' +
    items.join('') + '</ol></nav>';
  // A bare aria-label anywhere in the HTML is not proof of a usable trail.
  // Validate the exact static navigation *inside* the canonical main, including
  // the ancestor links and the title; do not trust a stale or empty breadcrumb.
  const markers = activeHtml.split('aria-label="Trilha de navegação"').length - 1;
  if (markers > 0) {
    assert.equal(markers, 1, 'Trilha preexistente duplicada: ' + path);
    assert.equal(activeHtml.indexOf(main + trail), mainAt,
      'Trilha preexistente não corresponde ao contrato: ' + path);
    return { html, eligible: true, changed: false };
  }
  const insertion = mainAt + main.length;
  return { html: html.slice(0, insertion) + trail + html.slice(insertion),
    eligible: true, changed: true };
}
function* pages(root) {
  for (const entry of readdirSync(root, { withFileTypes: true })) {
    const target = join(root, entry.name);
    if (entry.isDirectory()) yield* pages(target);
    else if (entry.isFile() && entry.name === 'index.html') yield target;
  }
}
export function applyBreadcrumbs(root = resolve('public'), check = false) {
  assert.ok(existsSync(join(root, 'index.html')), 'Artefato SSG não construído');
  let eligible = 0, changed = 0;
  for (const file of pages(root)) {
    const path = relative(root, file);
    const old = readFileSync(file, 'utf8');
    const result = addBreadcrumbs(old, path,
      ancestor => existsSync(join(root, ancestor, 'index.html')));
    if (!result.eligible) continue;
    eligible++;
    if (check) assert.equal(result.changed, false, 'Trilha ausente em ' + path);
    else if (result.changed) { writeFileSync(file, result.html); changed++; }
  }
  assert.ok(eligible >= 2, 'Nenhuma jornada documental profunda foi encontrada');
  return { eligible, changed };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const report = applyBreadcrumbs(resolve(process.argv[2] || 'public'),
    process.argv.includes('--check'));
  console.log('SSG breadcrumbs:', report);
}

