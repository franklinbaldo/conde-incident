import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const ci = readFileSync(new URL('../.github/workflows/integration-head.yml', import.meta.url), 'utf8');

test('CI executes for pushes and pull requests', () => {
  assert.match(ci, /^on:\s*\n  push:\s*\n  pull_request:/m);
});

test('both jobs checkout and verify the exact PR head SHA, not synthetic PR merge', () => {
  const ref = 'ref: ${{ github.event.pull_request.head.sha || github.sha }}';
  assert.equal(ci.split(ref).length - 1, 2);
  assert.equal(ci.split('git rev-parse HEAD').length - 1, 2);
});

test('CI is read only and cannot publish Pages', () => {
  assert.match(ci, /^permissions:\s*\n  contents: read/m);
  assert.doesNotMatch(ci, /(?:pages: write|id-token: write|actions\/deploy-pages|upload-pages-artifact)/);
});

test('CI runs web checks, Node tests and actual Lean compilation if a package exists', () => {
  for (const required of [
    'bun install --frozen-lockfile',
    'bun run lint',
    'bun run build',
    'node --test',
    'formal/lean-toolchain',
    'lake build',
    'NO_LEAN_PACKAGE',
  ]) {
    assert.ok(ci.includes(required), `missing CI contract: ${required}`);
  }
});
