import assert from 'node:assert/strict';
import {existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync} from 'node:fs';
import {join, relative, resolve, sep} from 'node:path';
import {pathToFileURL} from 'node:url';

export const BASE = 'https://franklinbaldo.github.io/conde-incident/';
export const SITEMAP_URL = BASE + 'sitemap.xml';

// Inventory the deployed artifact, never the source Markdown or an assumed route list.
// The SSG and Vite both emit directory/index.html routes under this same root.
export function generateSitemap(outputDir = 'public') {
  const root = resolve(outputDir);
  assert.ok(existsSync(root), 'Pasta do site não existe: ' + root);
  const routes = [];
  function visit(dir) {
    for (const entry of readdirSync(dir, {withFileTypes: true}).sort((a, b) => a.name.localeCompare(b.name, 'en'))) {
      const path = join(dir, entry.name);
      assert.ok(!entry.isSymbolicLink(), 'Symlink não autorizado no artefato: ' + path);
      if (entry.isDirectory()) {
        visit(path);
      } else if (entry.name === 'index.html') {
        assert.ok(entry.isFile(), 'Rota não é arquivo: ' + path);
        const html = readFileSync(path, 'utf8');
        assert.match(html, /<html\b[^>]*>/i, 'Destino não contém HTML: ' + path);
        const directory = relative(root, dir);
        const segments = directory ? directory.split(sep) : [];
        for (const segment of segments) {
          assert.match(segment, /^[a-zA-Z0-9._~-]+$/, 'Slug inseguro no site: ' + segment);
          assert.notEqual(segment, '..');
        }
        routes.push(BASE + (segments.length ? segments.join('/') + '/' : ''));
      }
    }
  }
  visit(root);
  routes.sort();
  assert.ok(routes.length > 0, 'Sitemap vazio: nenhum index.html real no artefato');
  assert.equal(new Set(routes).size, routes.length, 'Rotas duplicadas');

  const robots = readFileSync(join(root, 'robots.txt'), 'utf8');
  const advertised = [...robots.matchAll(/^Sitemap:\s*(\S+)\s*$/gim)].map(match => match[1]);
  assert.deepEqual(advertised, [SITEMAP_URL], 'robots.txt não anuncia apenas o sitemap canônico');

  const xml = ['<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...routes.map(url => '  <url><loc>' + url + '</loc></url>'),
    '</urlset>', ''].join('\n');
  mkdirSync(root, {recursive: true});
  writeFileSync(join(root, 'sitemap.xml'), xml, 'utf8');
  return routes;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  console.log('Sitemap do artefato Pages: ' + generateSitemap(process.argv[2] || 'public').length + ' rotas reais.');
}
