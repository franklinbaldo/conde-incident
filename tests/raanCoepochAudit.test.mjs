/**
 * CI bridge: run Cervo's pinned Python evidence checks from the existing
 * Integration checks (exact head) Node test glob. No workflow permission needed.
 */
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';

const python = (args) => {
  const r = spawnSync('python3', args, { encoding: 'utf8', timeout: 30000 });
  assert.equal(r.error, undefined, r.error?.message);
  assert.equal(r.status, 0, [r.stdout, r.stderr].join('\n'));
};

test('real secondary C25/C179 RAAN co-epochs and duplicate checks', () => {
  python(['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_raan_coepoch_audit.py', '-v']);
});

test('pin exact real data statistics report on the PR HEAD', () => {
  python([
    'tools/raan_coepoch_audit.py',
    '--input', 'research/statistics/raan_527_528_529_1963.json',
    '--check', 'research/statistics/raan_coepoch_1963_report.json',
  ]);
});
