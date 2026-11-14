import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { checkPage } from '../scripts/ssg-authored-pages.mjs';

const page = readFileSync('pages/mapa/page.md', 'utf8');
const map = readFileSync('static/img/conde-bahia-context.svg', 'utf8');

test('página Mapa é autônoma, acessível e preserva o laboratório', () => {
  assert.equal(checkPage('mapa', page), page);
  assert.match(page, /<figure class="context-map">[\s\S]*?<img\s+src="\/conde-incident\/img\/conde-bahia-context\.svg"/);
  assert.match(page, /alt="[^"]*Conde[^"]*Nenhum ponto de queda/);
  assert.match(page, /<figcaption>[\s\S]*?Natural Earth 1:110m[\s\S]*?<\/figcaption>/);
  assert.match(page, /href="\/conde-incident\/img\/conde-bahia-context\.svg"/);
  assert.match(page, /\/conde-incident\/lab\/#\/map/);
  assert.doesNotMatch(page, /<iframe\b|maps\.googleapis\.com|www\.openstreetmap\.org|tile\.openstreetmap/);
});

test('SVG local mantém fonte, escala e distinção sede ≠ queda', () => {
  assert.match(map, /^<svg\b[^>]*viewBox="0 0 800 500"/);
  assert.match(map, /<title[^>]*>Conde, Bahia:/);
  assert.match(map, /<desc[^>]*>[\s\S]*Não representa local de queda/);
  assert.match(map, /Natural Earth 1:110m \(domínio público\)/);
  assert.doesNotMatch(map, /<script\b|<foreignObject\b|(?:href|src)=\"https?:\/\//i);
});
