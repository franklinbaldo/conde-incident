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

test('every agent may create issues and Elefante organizes without monopoly', () => {
  const rules = read('AGENTS.md');
  const elefante = read('team/elefante.md');
  assert.match(rules, /Issue creation is shared by everyone/);
  assert.match(rules, /Any agent may open an issue/);
  assert.match(elefante, /Todos os animais também podem abrir issues novas/);
  assert.match(elefante, /atribui responsáveis e ordena a fila/);
});

test('daily Elefante coffee has date, expiry, no concurrent duplicate', () => {
  const rules = read('AGENTS.md');
  const elefante = read('team/elefante.md');
  assert.match(rules, /America\/Porto_Velho/);
  assert.match(rules, /new numbered session/);
  assert.match(elefante, /☕ cafezinho/);
  assert.match(elefante, /Não criar duas sessões simultaneamente/);
});

test('every animal keeps its own skill by stable path', () => {
  const rules = read('AGENTS.md');
  assert.match(rules, /Each animal maintains its own skill/);
  for (const animal of agents) {
    assert.match(rules, /\.agents\/skills\/conde-<animal>\/SKILL\.md/);
  }
});
