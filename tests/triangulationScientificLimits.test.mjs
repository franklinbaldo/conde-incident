import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../src/components/TriangulationDashboard.tsx', import.meta.url), 'utf8');

test('triangulation cannot turn a hypothetical clock or bracketing width into a historical measurement', () => {
  assert.doesNotMatch(source, /1963-11-08T19:48|19:48|19h48|19h48|19h48|19:48:00/);
  assert.doesNotMatch(source, /condeProximity|condeDate|computeInterTrackProximity|bracketingVerdict|corridorWidth527Km/);
  assert.doesNotMatch(source, /certeza absoluta|inquestionável|balizas geográficas|rigorosamente balizada|Passagem Conde/);
  assert.doesNotMatch(source, /propagateState|getTriangulationState|~91 km|0,022 m²\/kg/);
});

test('the three related objects are compared without asserting that their tracks fix a corridor', () => {
  for (const id of ['527', '528', '529']) {
    assert.match(source, new RegExp("id: '" + id + "'"));
  }
  assert.match(source, /Não há ajuste dinâmico conjunto validado/);
  assert.match(source, /Não há hora, coordenadas, largura de corredor, probabilidade ou intervalo físico de impacto validado/);
  assert.match(source, /Resultado: indeterminado/);
});

test('auditable evidence links distinguish records, uncertain RAAN and 529 holdout', () => {
  for (const fragment of ['#/research/c197', '#/research/raan', '#/research/holdout529', '#/research/c44-orbital', '#/map']) {
    assert.ok(source.includes(fragment), fragment);
  }
  assert.match(source, /evidence_matrix_C001-C238_2026-11-11\.md/);
  assert.match(source, /19640001198\.pdf/);
  assert.match(source, /Lean 4\.35\.0/);
  assert.match(source, /PR #43/);
});

test('object selection is keyboard-native, announced and bilingual', () => {
  assert.match(source, /type="button"/);
  assert.match(source, /aria-pressed=\{selectedId === object\.id\}/);
  assert.match(source, /aria-controls="triangulation-object-detail"/);
  assert.match(source, /aria-live="polite"/);
  assert.match(source, /focus-visible:outline/);
  assert.match(source, /lang: Language/);
  assert.match(source, /pt: 'Objeto investigado', en: 'Object under investigation'/);
  assert.doesNotMatch(source, /<input[^>]+type="range"/);
});
