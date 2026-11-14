import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';

const component = readFileSync(
  fileURLToPath(new URL('../src/components/AtmosphereSensitivity.tsx', import.meta.url)),
  'utf8',
);

function assertAccessibleSliders(source) {
  const ids = ['scaleHeightId', 'solarFluxId', 'ballisticCoeffId'];
  assert.equal((source.match(/type="range"/g) ?? []).length, ids.length);
  assert.equal((source.match(/<label htmlFor=/g) ?? []).length, ids.length);
  for (const id of ids) {
    assert.ok(source.includes(`const ${id} = useId();`), `${id}: stable React ID`);
    assert.ok(source.includes(`<label htmlFor={${id}}`), `${id}: visible associated label`);
    assert.match(source, new RegExp(`<input\\s+id=\\{${id}\\}\\s+type="range"`), `${id}: labeled slider input`);
  }
  assert.ok(!source.includes('text-zinc-500'), 'low-contrast labels must not return');
}

test('all three sensitivity sliders have stable visible programmatic labels', () => {
  assertAccessibleSliders(component);
});

test('negative: deleting an input association causes the audit to fail', () => {
  const mutant = component.replace('id={solarFluxId}', 'id={brokenSolarId}');
  assert.notEqual(mutant, component, 'mutant must change the source');
  assert.throws(() => assertAccessibleSliders(mutant));
});

test('negative: removing one visible label causes the audit to fail', () => {
  const mutant = component.replace('htmlFor={ballisticCoeffId}', 'data-broken={ballisticCoeffId}');
  assert.notEqual(mutant, component, 'mutant must change the source');
  assert.throws(() => assertAccessibleSliders(mutant));
});
