import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');
const manifest = JSON.parse(read('package.json'));
const lock = JSON.parse(read('bun.lock').replace(/,\s*([}\]])/g, '$1'));
const mapsOnly = ['@vis.gl/react-google-maps', '@googlemaps/js-api-loader', '@types/google.maps', 'fast-equals'];

test('Bun lock direct dependencies match the application manifest', () => {
  for (const scope of ['dependencies', 'devDependencies']) {
    assert.deepEqual(lock.workspaces[''][scope], manifest[scope]);
  }
});

test('Google Maps packages and their unused transitive dependencies are absent', () => {
  for (const name of mapsOnly) {
    assert.equal(Object.hasOwn(manifest.dependencies, name), false, name);
    assert.equal(Object.hasOwn(lock.packages, name), false, name);
  }
  for (const [name, entry] of Object.entries(lock.packages)) {
    for (const scope of ['dependencies', 'optionalDependencies', 'peerDependencies']) {
      for (const dep of Object.keys(entry?.[2]?.[scope] ?? {})) {
        assert.equal(mapsOnly.includes(dep), false, `${name} still depends on ${dep}`);
      }
    }
  }
});
