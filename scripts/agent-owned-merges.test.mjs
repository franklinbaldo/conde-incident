import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = (p) => readFileSync(new URL('../' + p, import.meta.url), 'utf8');
const agents = ['polvo', 'castor', 'tartaruga', 'raposa', 'coruja', 'texugo', 'gaviao', 'elefante'];

test('main assigns small PRs, author merge and retrospective review', () => {
  const rules = read('AGENTS.md');
  assert.match(rules, /Each agent owns its own work from issue to merge/);
  assert.match(rules, /Author merge is permitted and expected/);
  assert.match(rules, /retrospective independent auditor/);
  assert.match(rules, /not exclusive merger/);
  assert.match(rules, /exact HEAD SHA/);
  assert.doesNotMatch(rules, /Do not rebase, force-push or merge your own implementation PR/);
});

test('all eight animals own their PRs and may merge without preapproval', () => {
  for (const animal of agents) {
    const card = read('team/' + animal + '.md');
    assert.match(card, /fazer seu próprio merge/);
    assert.match(card, /Não esperar autorização prévia/);
    assert.match(card, /PRs pequenas e independentes/);
    assert.doesNotMatch(card, /abrir ou atualizar PR sem merge próprio/);
  }
});

test('Gaviao reviews all merges since persisted checkpoint, Elefante coordinates', () => {
  const gaviao = read('team/gaviao.md');
  const elefante = read('team/elefante.md');
  assert.match(gaviao, /todas as PRs já integradas na main desde o último checkpoint/);
  assert.match(gaviao, /team\/memory\/gaviao/);
  assert.match(gaviao, /NÃO funcionar como aprovação prévia obrigatória/);
  assert.match(elefante, /autores são responsáveis pelo próprio CI/);
  assert.match(elefante, /NÃO é aprovador ou integrador exclusivo/);
});
