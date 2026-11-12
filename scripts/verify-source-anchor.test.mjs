import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { verifyNASAAnchor } from './verify-source-anchor.mjs';

const matrix = readFileSync(new URL('../research/evidence_matrix_C001-C238_2026-11-11.md', import.meta.url), 'utf8');
const anchor = JSON.parse(readFileSync(new URL('../research/source_anchors/nasa-1963-11-15-decay-3b.json', import.meta.url), 'utf8'));

test('C197 identifies the actual NASA facsimile page and limitation', () => {
  assert.deepEqual(verifyNASAAnchor(matrix, anchor), []);
});

test('rejects historically wrong zero-based PDF index 8', () => {
  const bad = matrix.replace('PDF índice 9 (página 10 do visor)', 'PDF índice 8');
  assert.ok(verifyNASAAnchor(bad, anchor).some(e => e.includes('locator')));
});

test('rejects removal of exact NASA primary URL', () => {
  const bad = matrix.replace(anchor.url, 'https://example.invalid/secondary');
  assert.ok(verifyNASAAnchor(bad, anchor).some(e => e.includes('facsimile')));
});

test('rejects duplicate C197 provenance rows', () => {
  const row = matrix.split('\n').find(line => line.startsWith('| **C197** |'));
  assert.ok(row);
  assert.ok(verifyNASAAnchor(matrix + '\n' + row, anchor).some(e => e.includes('exactly one')));
});

test('rejects treating catalogue entry C198 as independent tracking', () => {
  const bad = matrix.replace('não duas fontes independentes', 'duas fontes independentes');
  assert.ok(verifyNASAAnchor(bad, anchor).some(e => e.includes('independence')));
});

test('rejects suppression of the unknown terminal time and place', () => {
  const bad = matrix.replace('Não contém hora nem coordenadas.', 'Hora e local registrados.');
  assert.ok(verifyNASAAnchor(bad, anchor).some(e => e.includes('no-time')));
});

test('rejects invented precision in the machine-readable anchor', () => {
  const bad = { ...anchor, pdf_index_zero_based: 8 };
  assert.ok(verifyNASAAnchor(matrix, bad).some(e => e.includes('mapping')));
  const bad2 = { ...anchor, uncertainty: 'A landing in Conde was observed' };
  assert.ok(verifyNASAAnchor(matrix, bad2).some(e => e.includes('uncertainty')));
});
