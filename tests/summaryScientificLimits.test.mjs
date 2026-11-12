import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { evidenceRecordFromHash, resolveLabHash } from '../src/lib/labRoutes.ts';

const file = path => readFileSync(new URL(path, import.meta.url), 'utf8');
const summary = file('../src/components/ExecutiveSummary.tsx');
const app = file('../src/App.tsx');
const html = file('../index.html');

test('initial summary cannot resurrect unsupported terminal time or posterior', () => {
  assert.doesNotMatch(summary, /19:48 UTC|16:48 hora local|0,006%|probabilidade a priori|VEREDITO ASTRODINÂMICO|N=5000/);
  assert.match(summary, /Resultado: indeterminado/);
  assert.match(summary, /Nenhuma hora, posição terminal, probabilidade de impacto ou intervalo físico validado/);
  assert.match(summary, /coincidência cronológica/);
});

test('documentary IDs and conditional formal sources are linked', () => {
  for (const id of ['c01', 'c197', 'raan', 'holdout529']) {
    assert.match(summary, new RegExp('#/research/' + id));
    assert.equal(evidenceRecordFromHash('#/research/' + id), id);
    assert.equal(resolveLabHash('#/research/' + id), 'research');
  }
  for (const name of ['evidence_matrix_C001-C238_2026-11-11.md','formal/Conde1963/Core.lean','ADMISSIBLE_DOMAIN_GATE.md','ALTERNATIVE_DOMAINS.md']) {
    assert.ok(summary.includes(name), name);
  }
  assert.match(summary, /propostas ainda não integradas/);
  assert.match(summary, /testes sintéticos/);
});

test('lab metadata describes an exploratory site with canonical subpath', () => {
  assert.match(html, /<html lang="pt-BR">/);
  assert.match(html, /rel="canonical" href="https:\/\/franklinbaldo\.github\.io\/conde-incident\/lab\/"/);
  assert.match(html, /Sem trajetória terminal ou impacto comprovado/);
  assert.doesNotMatch(html, /Reconstrução Orbital e Falsificação|Reconstrução orbital histórica quantitativa/);
});

test('skip-to-content never hijacks the hash router', () => {
  assert.match(app, /id="conteudo-lab" tabIndex=\{-1\}/);
  assert.match(app, /document\.getElementById\('conteudo-lab'\)\?\.focus\(\)/);
  assert.match(app, /focus:not-sr-only/);
  assert.doesNotMatch(app, /href="#conteudo-lab"/);
  assert.equal(resolveLabHash('#conteudo-lab'), null);
});
