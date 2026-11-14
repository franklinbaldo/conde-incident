import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const html = readFileSync(resolve('design/casefile-prototype.html'), 'utf8');
const proposal = readFileSync(resolve('design/CASEFILE_UX_ARCHITECTURE.md'), 'utf8');
const existing = new Set(['', 'stories/', 'evidencias/', 'simulacoes/', 'hipoteses/', 'metodo/', 'cronologia/', 'mapa/', 'lab/']);
const base = '/conde-incident/';

function anchors(markup) {
  return [...markup.matchAll(/<a\s+([^>]*?)>/gi)].map(([, attributes]) => {
    const href = attributes.match(/\bhref="([^"]+)"/i);
    return href?.[1] ?? '';
  });
}

test('the prototype is a no-JS, accessible exploration of the REAL routes', () => {
  assert.match(html, /<html lang="pt-BR">/);
  assert.match(html, /<meta name="viewport" content="width=device-width, initial-scale=1">/);
  assert.equal((html.match(/<h1\b/g) ?? []).length, 1);
  assert.equal((html.match(/<main\b/g) ?? []).length, 1);
  assert.match(html, /<a class="skip" href="#conteudo">Pular para conteúdo<\/a>/);
  assert.match(html, /<main id="conteudo" tabindex="-1">/);
  assert.match(html, /:focus-visible\{/);
  assert.match(html, /@media\(max-width:370px\)/);
  assert.match(html, /prefers-reduced-motion/);
  assert.doesNotMatch(html, /<script\b|on(?:click|load|mouseover)=|https?:\/\//i);
  for (const href of anchors(html)) {
    if (href === '#conteudo') continue;
    assert.ok(href.startsWith(base), `unexpected route: ${href}`);
    assert.ok(existing.has(href.slice(base.length)), `unrecognized destination: ${href}`);
  }
});

test('four primary choices lead to existing canonical destinations', () => {
  const nav = html.match(/<nav\s[^>]*>([\s\S]*?)<\/nav>/i)?.[1] ?? '';
  assert.deepEqual(anchors(nav), ['/', 'stories/', 'evidencias/', 'simulacoes/'].map(s => base + (s === '/' ? '' : s)));
  assert.equal((nav.match(/aria-current="page"/g) ?? []).length, 1);
  assert.match(html, /Protótipo de arquitetura visual/);
  assert.match(html, /sem registro histórico preenchido/);
});

test('architecture proposal retains the tradeoffs, provenance and acceptance gates', () => {
  assert.match(proposal, /^---\ntype: Guide\n/m);
  for (const term of ['SSG Rust', 'React', 'WASM', 'OKF', 'paridade', 'NOT_RUN', 'rollback', 'Raposa', 'Morcego']) {
    assert.ok(proposal.includes(term), `missing decision topic ${term}`);
  }
});
