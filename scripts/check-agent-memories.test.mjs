import test from 'node:test';
import assert from 'node:assert/strict';
import { validateAgentMemory } from './check-agent-memories.mjs';

const path = 'team/memory/elefante/20261111T193400Z-continuity.md';
const good = `---
type: AgentMemory
title: "Continuity of team knowledge"
description: "Evidence-grade separation between projects"
agent: elefante
timestamp: "2026-11-11T19:34:00Z"
tags: [conde, memory]
---

A real summary, not a scientific observation.
`;

test('valid structured memory can be retrieved with a trustworthy path', () => {
  assert.deepEqual(validateAgentMemory(path, good, 'elefante'), { errors: [], legacy: false });
});
test('wrong agent is rejected instead of silently reassigned', () => {
  assert.match(validateAgentMemory(path, good.replace('agent: elefante', 'agent: raposa'), 'elefante').errors[0].message, /agent/);
});
test('timestamp and filename must agree', () => {
  assert.ok(validateAgentMemory(path, good.replace('19:34:00', '19:35:00'), 'elefante').errors.some(e => /filename/.test(e.message)));
});
test('invalid UTC date does not pass by regex alone', () => {
  assert.ok(validateAgentMemory(path, good.replace('2026-11-11', '2026-02-31'), 'elefante').errors.some(e => /timestamp/.test(e.message)));
});
test('truncated frontmatter fails', () => {
  assert.ok(validateAgentMemory(path, good.replace('\n---\n\nA real summary', '\nA real summary'), 'elefante').errors.length > 0);
});
test('duplicate metadata, missing tags and empty body fail', () => {
  for (const content of [good.replace('type: AgentMemory', 'type: AgentMemory\ntype: AgentMemory'),
    good.replace('tags: [conde, memory]', 'tags: []'),
    good.replace('A real summary, not a scientific observation.', '')]) {
    assert.ok(validateAgentMemory(path, content, 'elefante').errors.length > 0);
  }
});
test('older Markdown note is preserved, not falsely called structured', () => {
  assert.deepEqual(validateAgentMemory('team/memory/elefante/old.md', '# Legacy note\n', 'elefante'),
    { errors: [], legacy: true });
});
test('unknown animal directory is rejected', () => {
  assert.ok(validateAgentMemory('team/memory/other/old.md', '# Legacy note\n', 'other').errors.length);
});
