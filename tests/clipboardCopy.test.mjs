import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { copyTextToClipboard } from '../src/lib/clipboardCopy.js';

const modalSource = readFileSync(new URL('../src/components/PythonScriptModal.tsx', import.meta.url), 'utf8');

test('clipboard success is only reported after writeText resolves', async () => {
  let resolveWrite;
  let written;
  const promise = copyTextToClipboard('script', {
    writeText: text => {
      written = text;
      return new Promise(resolve => { resolveWrite = resolve; });
    },
  });
  assert.equal(written, 'script');
  resolveWrite();
  assert.equal(await promise, true);
});

test('clipboard rejection and missing API are not reported as success', async () => {
  assert.equal(await copyTextToClipboard('script', undefined), false);
  assert.equal(await copyTextToClipboard('script', {}), false);
  assert.equal(await copyTextToClipboard('script', { writeText: async () => { throw new Error('NotAllowedError'); } }), false);
});

test('Python export modal makes failure observable and offers manual fallback', () => {
  assert.match(modalSource, /await copyTextToClipboard\(/);
  assert.match(modalSource, /setCopyState\(succeeded \? 'copied' : 'failed'\)/);
  assert.match(modalSource, /role="alert"/);
  assert.match(modalSource, /Selecione o código abaixo e copie manualmente/);
  assert.match(modalSource, /Select the code below and copy it manually/);
});
