import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const file = new URL('../research/evidence_matrix_C001-C238_2026-11-11.md', import.meta.url);
const raw = readFileSync(file);
const lines = raw.toString('utf8').split(/\r?\n/);
const rowRe = /^\|\s*(?:\*\*)?(C[0-9]+)(?:\*\*)?\s*\|/;
const ids = lines.map(line => rowRe.exec(line)?.[1]).filter(Boolean);

test('source matrix bytes are exactly the archived research blob', () => {
  const hash = createHash('sha1')
    .update('blob ' + raw.length + '\0')
    .update(raw)
    .digest('hex');
  assert.equal(hash, 'a7978c3a75a153b16ab70118a92c434bba674cb7');
});

test('241 occurrences, 238 labels, duplicate C44-C46 only', () => {
  const counts = new Map();
  for (const id of ids) counts.set(id, (counts.get(id) || 0) + 1);
  assert.equal(ids.length, 241);
  assert.equal(counts.size, 238);
  for (let n = 1; n <= 238; n++) {
    assert.equal(counts.get('C' + String(n).padStart(2, '0')) ??
                 counts.get('C' + n), n >= 44 && n <= 46 ? 2 : 1, 'C' + n);
  }
});

test('NASA date document and mirrored orbital source stay separate', () => {
  const doc = raw.toString('utf8');
  assert.match(doc, /C197/);
  assert.match(doc, /C179/);
  assert.match(doc, /19640001198/);
  assert.match(doc, /198,5261/);
  assert.match(doc, /errata|ERRATA/);
});
