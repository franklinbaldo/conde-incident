import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const rules = readFileSync(new URL('../AGENTS.md', import.meta.url), 'utf8');
test('private workspace is first-class but science remains in project repo', () => {
  assert.match(rules, /private personal repository/);
  assert.match(rules, /public\/shared `conde-incident` remains the source of truth/);
  assert.match(rules, /new personal memories go into the private home/);
});
test('personal repo allows direct commits without review or PR', () => {
  assert.match(rules, /push straight to `main` without approvals, review, PR or CI/);
  assert.match(rules, /private Git is not a vault for passwords/);
});
test('interagent messages go to recipient issues', () => {
  assert.match(rules, /issue in B's private repository/);
  assert.match(rules, /De:/);
  assert.match(rules, /Para:/);
  assert.match(rules, /logical roles under the owner's same GitHub identity/);
});
test('user task capacity and other tasks are respected', () => {
  assert.match(rules, /without disabling unrelated user automations/);
  assert.match(rules, /15 active \/ 15 allowed/);
});
