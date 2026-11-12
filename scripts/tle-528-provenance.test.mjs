import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';

const file = new URL('../research/tle_custody/mirror_528_1963-10-27.tle', import.meta.url);
const contents = readFileSync(file);
const lines = contents.toString('ascii').trimEnd().split('\n');
const checksum = (line) => {
  let total = 0;
  for (const c of line.slice(0, 68)) {
    if (c >= '0' && c <= '9') total += Number(c);
    if (c === '-') total += 1;
  }
  return total % 10;
};

test('secondary TLE literal is bit-for-bit custodied, not fabricated', () => {
  assert.equal(createHash('sha256').update(contents).digest('hex'),
    '18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd');
  assert.equal(lines.length, 2);
  for (const line of lines) {
    assert.equal(line.length, 69);
    assert.equal(line.at(-1), String(checksum(line)));
  }
});

test('NORAD 528 has sourced October epoch and 198.5261 deg RAAN', () => {
  const [first, second] = lines;
  assert.equal(Number(first.slice(2, 7)), 528);
  assert.equal(Number(second.slice(2, 7)), 528);
  assert.equal(first.slice(18, 32).trim(), '63300.61129783');
  assert.equal(second.slice(17, 25).trim(), '198.5261');
  assert.equal(second.slice(26, 33), '0017147');
  assert.equal(second.slice(52, 63).trim(), '15.74901460');
  assert.ok(!contents.toString('ascii').includes('284.1520'));
});
