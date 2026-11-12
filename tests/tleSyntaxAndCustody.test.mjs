import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { auditTleSyntax } from '../src/lib/tleChecksum.ts';

const source = readFileSync(new URL('../src/components/TleAuditViewer.tsx', import.meta.url), 'utf8');
const first = '1 00528U 63003B   63300.61111111  .00000000  00000-0  00000-0 0  9992';
const second = '2 00528  81.8615 284.1520 0084200 142.3150 218.4210 15.74900000 45124';

test('TLE check digit math checks both example strings, without authenticating their source', () => {
  assert.deepEqual([first.length, second.length], [69, 69]);
  assert.equal(auditTleSyntax(first, 1, 528).computedChecksum, 2);
  assert.equal(auditTleSyntax(second, 2, 528).computedChecksum, 4);
  assert.equal(auditTleSyntax(first, 1, 528).valid, true);
  assert.equal(auditTleSyntax(second, 2, 528).valid, true);
});

test('corrupt digits, missing columns and wrong NORAD IDs fail the limited audit', () => {
  assert.equal(auditTleSyntax(first.slice(0, -1) + '9', 1, 528).valid, false);
  assert.equal(auditTleSyntax(first.slice(0, -1), 1, 528).valid, false);
  assert.equal(auditTleSyntax(first, 1, 527).valid, false);
  assert.equal(auditTleSyntax(first, 2, 528).valid, false);
});

test('a synthetic TLE with a newly computed valid checksum is still only syntactically valid', () => {
  const changed = first.slice(0, 20) + '9' + first.slice(21, 68);
  const check = [...changed].reduce((sum, c) => sum + (/\d/.test(c) ? Number(c) : c === '-' ? 1 : 0), 0) % 10;
  assert.equal(auditTleSyntax(changed + String(check), 1, 528).valid, true);
});

test('TLE interface distinguishes embedded inputs, checksum and documentary custody, in PT/EN', () => {
  assert.match(source, /não autenticação de elementos orbitais/);
  assert.match(source, /not authentication of 1963 orbital elements/);
  assert.match(source, /Checksums válidos podem ser gerados/);
  assert.match(source, /entirely hypothetical values can carry valid checksums/);
  assert.match(source, /aria-pressed=\{selectedId === id\}/);
  assert.match(source, /aria-live="polite"/);
  assert.match(source, /overflow-x-auto/);
  assert.match(source, /navigator\.clipboard\.writeText/);
  assert.match(source, /catch \{/);
  assert.doesNotMatch(source, /INTEGRIDADE CONFIRMADA|Rigorosa.*proveniência|Último TLE autenticado|convenção manual|SPADATS.*BMEWS/);
});

test('source and individual Evidence/Map links exist without claiming ground impact', () => {
  for (const fragment of ['#/research/raan', '#/research/c197', '#/research/holdout529', '#/map', '/pull/14', 'evidence_matrix_C001-C238_2026-11-11.md', '19640001198.pdf']) {
    assert.ok(source.includes(fragment), fragment);
  }
  assert.match(source, /Reentrada não comprova impacto/);
  assert.match(source, /Scientific outcome: undetermined/);
  assert.match(source, /Não há domínio admissível não vazio e reduzido/);
});
