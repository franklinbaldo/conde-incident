import { strict as assert } from 'node:assert';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { selectVisiblePass } from '../src/lib/inversePassSelection.js';

const source = readFileSync('src/components/InversePassInspector.tsx', 'utf8');
const feed = JSON.parse(readFileSync('public/data/conde-source-citations.json', 'utf8'));
const a = { epochMs: 7, closestApproachDistanceKm: 900 };
const b = { epochMs: 8, closestApproachDistanceKm: 150 };
const c = { epochMs: 9, closestApproachDistanceKm: 350 };

test('selection cannot leak a scenario from a different filtered day', () => {
  assert.equal(selectVisiblePass([a, c], 8, false), a);
  assert.equal(selectVisiblePass([a, c], 9, false), c);
  assert.equal(selectVisiblePass([], 8, true), null);
  assert.equal(selectVisiblePass([a, b, c], null, true), b);
  assert.equal(selectVisiblePass([a, b, c], 9, true), c);
});

test('keyboard-accessible native button and filter state are wired to selected epoch', () => {
  assert.match(source, /<button\s+key=\{p\.epochMs\}\s+type="button"/);
  assert.match(source, /onClick=\{\(\) => setSelectedPassEpoch\(p\.epochMs\)\}/);
  assert.match(source, /aria-pressed=\{isSelected\}/);
  assert.match(source, /selectVisiblePass\(filteredPasses, selectedPassEpoch, filterDate === '08'\)/);
  for (const day of ['07','08','09','ALL']) {
    assert.ok(source.includes("aria-pressed={filterDate === '" + day + "'}"));
  }
});

test('documentary context is anchored in original citation feed; no physical proof claim', () => {
  for (const [occurrence, line] of [['C197#1', 905], ['C179#1', 839]]) {
    const record = feed.records.find((entry) => entry.occurrence === occurrence);
    assert.ok(record, occurrence);
    assert.equal(record.matrix_line, line);
    assert.equal(record.not_a_verified_conde_physical_event, true);
    assert.ok(source.includes(occurrence));
    assert.ok(source.includes('matrixOccurrenceUrl(' + line + ')'));
  }
  assert.match(source, /exploratory model outputs, not 1963 observations/);
  assert.match(source, /não comprova admissibilidade física/);
  assert.doesNotMatch(source, /values exatos|compute the exact|fisicamente necessários|demonstrates that the overpass/);
  assert.match(source, /noopener noreferrer/);
});
