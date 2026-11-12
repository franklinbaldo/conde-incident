import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

// Regression guard: avoid depositing personal memory or coffee in public Conde.
const paths = [
  'team/elefante.md',
  '.agents/skills/conde-elefante/SKILL.md',
  'docs/AGENT_WORKSPACES.md',
];
const documents = paths.map((path) => [path, readFileSync(path, 'utf8')]);

test('Elefante instructions identify private workspace, private cafe and issue lookup', () => {
  for (const [path, content] of documents) {
    assert.ok(content.includes('franklinbaldo/elefante'), path);
    assert.ok(content.includes('franklinbaldo/cafezinho'), path);
    assert.ok(content.includes('issues abertas') || content.includes('issues **abertas'), path);
  }
});

test('Personal Markdown requires normative OKF and a green exact-head workflow', () => {
  for (const [path, content] of documents) {
    assert.ok(content.includes('okf-parser==0.48.2') || content.includes('okf-parser v0.48.2'), path);
    assert.ok(content.includes('.okf/specs/{slug}.md'), path);
    assert.ok(content.includes('OKF all Markdown'), path);
  }
});

test('Coffee #72 remains an archive and cafezinho#1 is the current venue', () => {
  for (const [path, content] of documents) {
    assert.ok(content.includes('#72'), path);
    assert.ok(content.includes('cafezinho#1'), path);
  }
});
