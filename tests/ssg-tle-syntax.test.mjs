import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { auditTlePair, auditTleSyntax, splitTlePairPaste, parseTleClipboard } from '../static/js/ssg-tle-syntax.mjs';

function makeLine(lineNumber, id) {
  // Synthetic bytes, not historical TLEs or complete validated fields.
  const body = (lineNumber + ' ' + String(id).padStart(5, '0')).padEnd(68, ' ');
  const digit = [...body].reduce((sum, c) => sum + (/\d/.test(c) ? Number(c) : c === '-' ? 1 : 0), 0) % 10;
  return body + digit;
}
test('minimal checksum, 69 columns and pair identity', () => {
  const p = auditTlePair(makeLine(1, 528), makeLine(2, 528));
  assert.equal(p.catalogId, 528);
  assert.equal(p.valid, true);
  assert.equal(p.first.computedChecksum, p.first.actualChecksum);
  assert.equal(p.second.computedChecksum, p.second.actualChecksum);
});
test('reject identity divergence, reversed lines and incomplete lines', () => {
  assert.equal(auditTlePair(makeLine(1, 528), makeLine(2, 527)).valid, false);
  assert.equal(auditTlePair(makeLine(2, 528), makeLine(1, 528)).valid, false);
  assert.equal(auditTlePair(makeLine(1, 528), makeLine(2, 528).slice(0, -1)).valid, false);
});
test('reject tampered digit, whitespace padding, newline and non-ASCII digit', () => {
  const line = makeLine(1, 528);
  const changed = line.slice(0, -1) + String((Number(line.at(-1)) + 1) % 10);
  assert.equal(auditTleSyntax(changed, 1, 528).valid, false);
  assert.equal(auditTleSyntax(' ' + line, 1, 528).valid, false);
  assert.equal(auditTleSyntax(line + '\n', 1, 528).valid, false);
  assert.equal(auditTleSyntax(line.slice(0, -1) + '３', 1, 528).valid, false);
});
test('SSG page exposes actual native form, script, non-authenticity warning and no external provider', () => {
  const page = readFileSync('pages/simulacoes/tles/page.md', 'utf8');
  assert.match(page, /<form id="ssg-tle-audit"/);
  assert.match(page, /src="\/conde-incident\/js\/ssg-tle-syntax\.mjs"/);
  assert.match(page, /não autentica TLE histórico/);
  assert.match(page, /\/conde-incident\/lab\/#\/tles/);
  assert.doesNotMatch(page, /maps\.google|tile\.openstreetmap|iframe/);
});
test('audit deliberately remains minimal, not full TLE field validation', () => {
  assert.equal(auditTlePair(makeLine(1, 528), makeLine(2, 528)).valid, true);
  // This synthetic empty payload fails full TLE validation; never claim historical validity.
  const js = readFileSync('static/js/ssg-tle-syntax.mjs', 'utf8');
  assert.match(js, /Não testa campos orbitais completos/);
  assert.match(js, /NÃO autentica os dados/);
});

test('two-line paste splits only terminators, without trimming or repairing bytes', () => {
  const first = makeLine(1, 528);
  const second = makeLine(2, 528);
  assert.deepEqual(splitTlePairPaste(first + '\n' + second), [first, second]);
  assert.deepEqual(splitTlePairPaste(first + '\r\n' + second + '\r\n'), [first, second]);
  assert.equal(splitTlePairPaste(first), null);
  assert.equal(splitTlePairPaste('ISSUED BY UNKNOWN\n' + first + '\n' + second), null);
  assert.equal(splitTlePairPaste(first + '\n' + second + '\nthird line'), null);
  assert.deepEqual(splitTlePairPaste(' ' + first + '\n' + second), [' ' + first, second]);
  assert.equal(auditTlePair(...splitTlePairPaste(' ' + first + '\n' + second)).valid, false);
});


test('three-line TLE clipboard imports an untrusted header without changing orbital columns', () => {
  const first = makeLine(1, 528);
  const second = makeLine(2, 528);
  for (const title of ['0 EXEMPLO NÃO AUTENTICADO', 'NORAD SAMPLE 528']) {
    const block = title + '\r\n' + first + '\r\n' + second + '\r\n';
    assert.deepEqual(parseTleClipboard(block), {lines: [first, second], title});
    assert.equal(auditTlePair(...parseTleClipboard(block).lines).valid, true);
  }
  assert.deepEqual(parseTleClipboard(first + '\n' + second), {lines: [first, second], title: null});
  assert.equal(parseTleClipboard(''), null);
  assert.equal(auditTlePair(...parseTleClipboard('HEADER\n' + first).lines).valid, false,
    'a malformed two-line paste stays visible for diagnosis instead of being silently repaired');
  assert.equal(parseTleClipboard('HEADER\n' + first + '\n' + second + '\nFOURTH'), null);
  assert.equal(parseTleClipboard(first + '\n' + first + '\n' + second), null,
    'a duplicate first orbital line cannot be mistaken for a title');
  assert.equal(parseTleClipboard('LABEL\n' + first + '\n' + second.replace('2 ', '1 ')), null);
  assert.equal(parseTleClipboard('X'.repeat(121) + '\n' + first + '\n' + second), null);
  assert.equal(parseTleClipboard('TAB\tHEADER\n' + first + '\n' + second), null);
  assert.match(readFileSync('pages/simulacoes/tles/page.md', 'utf8'), /não identifica nem autentica a fonte/);
});
