import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const ci = readFileSync(new URL('../.github/workflows/integration-head.yml', import.meta.url), 'utf8');
const prek = readFileSync(new URL('../.github/workflows/prek.yml', import.meta.url), 'utf8');

test('CI runs on main pushes and all PRs, not duplicate feature-branch pushes', () => {
  const trigger = ci.split(/^permissions:/m)[0].trimEnd();
  assert.equal(trigger, [
    'name: Integration checks (exact head)',
    '',
    'on:',
    '  push:',
    '    branches: [main]',
    '  pull_request:',
  ].join('\n'));
});

test('Prek gates all PRs and main pushes without duplicate feature-branch pushes', () => {
  const trigger = prek.split(/^permissions:/m)[0].trimEnd();
  assert.equal(trigger, [
    'name: Prek policy (OKF and 20KB)',
    'on:',
    '  push:',
    '    branches: [main]',
    '  pull_request:',
  ].join('\n'));
  assert.match(prek, /persist-credentials: false/);
  assert.match(prek, /git rev-parse HEAD/);
  assert.match(prek, /prek run --all-files/);
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

// Exercise the actual YAML shell block with synthetic directory fixtures, without
// executing repo tests or confusing fixture tests with historical observations.
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { spawnSync } from 'node:child_process';

test('CI discovers root and nested Node suites in both scripts/ and tests/', () => {
  const match = ci.match(/- name: Execute present Node regression suites\n\s*shell: bash\n\s*run: \|\n((?: {10}[^\n]*\n)+)/);
  assert.ok(match, 'unable to extract the CI shell script');
  const script = match[1].split('\n').map(line => line.replace(/^ {10}/, '')).join('\n');
  assert.ok(script.includes('node --test "${tests[@]}"'));
  const dryRun = script.replace('node --test "${tests[@]}"', 'printf "%s\\n" "${tests[@]}"');
  const root = mkdtempSync(join(tmpdir(), 'conde-node-suite-'));
  try {
    const paths = [
      'scripts/contract.test.mjs',
      'scripts/nested/integration.test.mjs',
      'tests/physics.test.mjs',
      'tests/nested/holdout.test.mjs',
    ];
    for (const path of [...paths, 'tests/ignored.js']) {
      const destination = join(root, path);
      mkdirSync(dirname(destination), { recursive: true });
      writeFileSync(destination, '', 'utf8');
    }
    const run = spawnSync('bash', ['-c', dryRun], { cwd: root, encoding: 'utf8' });
    assert.equal(run.status, 0, run.stderr);
    assert.deepEqual(run.stdout.trim().split(/\r?\n/).sort(), paths.sort());
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CI explicitly says NO_NODE_TEST_FILES only for an empty workspace', () => {
  const match = ci.match(/- name: Execute present Node regression suites\n\s*shell: bash\n\s*run: \|\n((?: {10}[^\n]*\n)+)/);
  assert.ok(match);
  const script = match[1].split('\n').map(line => line.replace(/^ {10}/, '')).join('\n');
  const root = mkdtempSync(join(tmpdir(), 'conde-node-empty-'));
  try {
    const run = spawnSync('bash', ['-c', script], { cwd: root, encoding: 'utf8' });
    assert.equal(run.status, 0, run.stderr);
    assert.match(run.stdout, /NO_NODE_TEST_FILES/);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test('CI runs every Python unittest file at the exact checked-out head and fails closed on empty discovery', () => {
  for (const marker of [
    'actions/setup-python@v5',
    'python-version: "3.12"',
    "find tests -type f -name 'test_*.py' -print -quit",
    "python3 -m unittest discover -s tests -p 'test_*.py' -v",
  ]) {
    assert.ok(ci.includes(marker), `missing Python CI contract: ${marker}`);
  }
});
