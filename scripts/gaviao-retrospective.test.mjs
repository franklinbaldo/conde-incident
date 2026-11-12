import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const src = readFileSync(new URL('../src/lib/constants.ts', import.meta.url), 'utf8');
const window = JSON.parse(readFileSync(
  new URL('../research/audits/gaviao-main-window-20261112-0740.json', import.meta.url), 'utf8'
));
const block = (start, next) => {
  const i = src.indexOf("id: '" + start + "'");
  const j = src.indexOf("id: '" + next + "'", i + 1);
  assert.ok(i >= 0 && j > i, 'missing audit/timeline record ' + start);
  return src.slice(i, j);
};

test('initial retrospective window is contiguous and enumerates EVERY main commit', () => {
  assert.equal(window.schema, 'conde.gaviao.retrospective-main-window/v1');
  const entries = window.window_entries;
  assert.equal(entries.length, 16);
  assert.equal(window.post_base_changes, entries.length - 1);
  assert.equal(entries[0].sha, window.reviewed_base_sha);
  assert.equal(entries.at(-1).sha, window.reviewed_through_sha);
  assert.equal(window.reviewed_through_sha, '006c7d08b64956aeeabed7162b5604bba77de85b');
  assert.equal(entries[0].kind, 'initial-root');
  for (let index = 0; index < entries.length; index++) {
    const item = entries[index];
    assert.match(item.sha, /^[a-f0-9]{40}$/);
    assert.equal(item.order, index);
    assert.equal(item.parent_sha, index === 0 ? null : entries[index - 1].sha);
    assert.ok(item.source_url.endsWith(item.sha));
    if (index > 0) assert.ok(item.changed_files.length > 0, 'missing file enumeration');
  }
  assert.equal(new Set(entries.map(e => e.sha)).size, entries.length);
  assert.deepEqual(entries.filter(e => e.kind === 'direct-commit').map(e => e.sha),
    ['807a118939fac50b48d649b1045461bfcc79b140']);
  const merges = entries.filter(e => e.kind === 'squash-merge-pr').map(e => e.pr_number);
  assert.deepEqual(merges, [2, 58, 69, 73, 75, 76, 79, 77, 80, 81, 83, 82, 84, 87]);
  assert.deepEqual(merges, window.merged_prs);
  assert.ok(!merges.includes(74), 'closed unmerged PR must not masquerade as main commit');
  assert.ok(entries.every(e => e.changed_files.every(path => !/^stories\//.test(path))),
    'no story was merged in this interval; change coverage if that becomes false');
});

test('NASA 528 is PRESENT in 15-Nov-1963 decayed-object list, without terminal position', () => {
  const note = block('EPIST-03', 'EPIST-04');
  assert.match(note, /1963 3B/);
  assert.match(note, /08\/11\/1963/);
  assert.match(note, /C197#1/);
  assert.match(note, /sem hora ou local/);
  assert.doesNotMatch(note, /não consta no boletim/);
  const timeline = block('OBS-09', 'OBS-10');
  assert.match(timeline, /lista de objetos decaídos/);
  assert.match(timeline, /PDF índice 9/);
  assert.match(timeline, /hora do evento não informada/);
  assert.doesNotMatch(timeline, /15T12:00:00Z/);
  assert.doesNotMatch(timeline, /Confirmação de Ausência do 528/);
});

test('A-628 contemporary diplomatic NEGATIVE REPORT is not field proof of no impact', () => {
  const note = block('EPIST-05', 'EPIST-06');
  assert.match(note, /A-628/);
  assert.match(note, /telegrama 157/);
  assert.match(note, /14\/11/);
  assert.match(note, /não contém laudo de campo/);
  assert.doesNotMatch(note, /investigaram e concluíram/);
  assert.doesNotMatch(note, /verificaram ausência de cratera/);
  assert.doesNotMatch(note, /não houve queda física em Conde/);
});

test('NASA catalog date is not treated as observed reentry time or impact', () => {
  const timeline = block('OBS-08', 'OBS-09');
  assert.match(timeline, /calendar-day UI anchor only/);
  assert.match(timeline, /sem hora ou local terminal/);
  assert.doesNotMatch(timeline, /Fim da Trajetória/);
});
