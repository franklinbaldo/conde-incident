import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');

test('entrypoint and map have no global Google quota interceptors', () => {
  const main = read('src/main.tsx');
  const app = read('src/App.tsx');
  const map = read('src/components/OrbitalMap.tsx');
  const svg = read('src/components/map/OrbitalMapSvg.tsx');
  assert.match(main, /createRoot\(/);
  for (const file of [main, app, map, svg]) {
    assert.doesNotMatch(file, /gm_authFailure|gmp-quota-exceeded|OverQuotaMapError|QuotaExceededError/);
    assert.doesNotMatch(file, /@vis\.gl\/react-google-maps|maps\.googleapis\.com/);
  }
  assert.doesNotMatch(main, /console\.error\s*=/);
});
