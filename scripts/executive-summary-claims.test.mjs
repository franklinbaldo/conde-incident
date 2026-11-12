import { strict as assert } from 'node:assert';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const summary = readFileSync('src/components/ExecutiveSummary.tsx', 'utf8');
const navigation = readFileSync('src/lib/tabRoutes.ts', 'utf8');
const citations = JSON.parse(readFileSync('public/data/conde-source-citations.json', 'utf8'));
const graph = JSON.parse(readFileSync('research/constraints/ssr_1963_observable_graph.json', 'utf8'));

test('summary contains only source-backed matrix occurrences', () => {
  for (const [occurrence, line] of [['C01#1', 19], ['C02#1', 20], ['C197#1', 905], ['C198#1', 906], ['C179#1', 839]]) {
    const record = citations.records.find(item => item.occurrence === occurrence);
    assert.ok(record, occurrence + ' is missing from pinned citation feed');
    assert.equal(record.matrix_line, line);
    assert.ok(summary.includes(occurrence));
    assert.ok(summary.includes((occurrence === 'C02#1' || occurrence === 'C198#1' ? 'otherMatrixLine: ' : 'matrixLine: ') + line));
  }
  assert.ok(summary.includes('matrixOccurrenceUrl(claim.matrixLine)'));
  assert.ok(summary.includes('matrixOccurrenceUrl(claim.otherMatrixLine)'));
  assert.ok(summary.includes('same documentary work') || summary.includes('mesma obra documental'));
});

test('summary does not promote synthetic timing or odds to historical observations', () => {
  for (const unsupported of [
    '19:48', '0,0062%', '0.0062%', 'Boato Fabricado', 'Fabricated Hoax',
    'VEREDITO ASTRODINÂMICO', 'ASTRODYNAMIC & DOCUMENTARY VERDICT',
    'CONDE_IMPACT_PASS_MS', '120-80 km exatamente',
  ]) assert.equal(summary.includes(unsupported), false, unsupported);
  assert.match(summary, /Resultado: indeterminado/);
  assert.match(summary, /Outcome: undetermined/);
  assert.match(summary, /Lean proofs depend on their premises/);
});

test('all summary navigation targets exist in deployed lab router, not draft Evidence', () => {
  for (const tab of ['documents', 'map']) {
    assert.match(summary, new RegExp("onJumpToTab\\('" + tab + "'\\)"));
    assert.ok(navigation.includes("'" + tab + "'"));
  }
  assert.equal(summary.includes("onJumpToTab('research')"), false);
  assert.match(summary, /focus-visible:outline/);
  assert.match(summary, /aria-labelledby="summary-title"/);
  assert.match(summary, /rel="noopener noreferrer"/);
});

test('cumulative scientific graph is linked without calibrated-domain overclaim', () => {
  assert.ok(JSON.stringify(graph).includes('CONNECTED_PENDING_CALIBRATION'));
  assert.match(summary, /ssr_1963_observable_graph\.json/);
  assert.match(summary, /CONNECTED_PENDING_CALIBRATION/);
});
