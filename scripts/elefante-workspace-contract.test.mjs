import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

// Prevent stale public team cards from sending private memories or cafe conversations
// to the scientific project after the owner's 2026-11-12 custody decision.
const paths = [
  'team/elefante.md',
  '.agents/skills/conde-elefante/SKILL.md',
  'docs/AGENT_WORKSPACES.md',
];
const documents = paths.map((path) => [path, readFileSync(path, 'utf8')]);

test('Elefante cards point to private personal workspace and cafe, not project issues', () => {
  for (const [path, content] of documents) {
    assert.match(content, /franklinbaldo\\/elefante/, path);
    assert.match(content, /franklinbaldo\\/cafezinho/, path);
    assert.match(content, /issues? (?:abertas|abert[ao]s)/i, path);
  }
});

test('Every handoff requires OKF parser version, typed spec, and validated workflow', () => {
  for (const [path, content] of documents) {
    assert.match(content, /okf-parser(?:==| v)0\\.48\\.2/i, path);
    assert.match(content, /\\.okf\\/specs\\/\\{slug\\}\\.md/, path);
    assert.match(content, /OKF all Markdown/, path);
  }
});

test('Previous public coffee is historical, not the active inbox', () => {
  const [team, skill, protocol] = documents.map(([, content]) => content);
  for (const doc of [team, skill, protocol]) {
    assert.match(doc, /#72|conde-incident#72/, 'historical coffee anchor');
    assert.match(doc, /cafezinho#1/, 'new private coffee issue');
  }
});
