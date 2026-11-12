import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const names = ['polvo','castor','tartaruga','coruja','raposa','texugo','gaviao','elefante'];
const read = name => readFileSync(new URL('../.agents/skills/conde-' + name + '/SKILL.md', import.meta.url), 'utf8');

test('all eight animals have their own valid distinct skills', () => {
  for (const n of names) {
    const x=read(n);
    assert.match(x, new RegExp('^---\\nname: conde-' + n + '\\n'));
    assert.match(x, /description: .+/);
    assert.match(x, /AGENTS\.md/);
    assert.match(x, /PRs pequenas|PR pequena/);
    assert.match(x, /OKF/);
    assert.match(x, new RegExp('team/' + n + '\\.md'));
  }
});
test('Elefante owns daily coffee, not exclusive issue or merge powers', () => {
  const x=read('elefante');
  assert.match(x, /America\/Porto_Velho/);
  assert.match(x, /Cafezinho — YYYY-MM-DD/);
  assert.match(x, /Outros agentes também podem abrir suas issues/);
  assert.match(x, /Não duplicar sessões ativas/);
});
test('Gaviao enumerates retrospective merges from durable checkpoint', () => {
  const x=read('gaviao');
  assert.match(x, /team\/memory\/gaviao/);
  assert.match(x, /todos.*merges.*main/i);
  assert.match(x, /base_sha\.\.head_sha/);
  assert.match(x, /após.*merge/);
});
