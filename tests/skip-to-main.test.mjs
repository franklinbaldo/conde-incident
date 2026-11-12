import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { skipToMain } from '../src/lib/skipToMain.js';

test('skip to main preserves hash route and moves keyboard focus', () => {
  let prevented = false;
  let focused = false;
  const fakeLocation = { hash: '#/map' };
  const element = { focus() { focused = true; } };
  const doc = { getElementById(id) {
    assert.equal(id, 'main-content');
    return element;
  } };
  const result = skipToMain({ preventDefault() { prevented = true; } }, doc);
  assert.equal(result, true);
  assert.equal(prevented, true, 'do not let href=#main-content reset #/map');
  assert.equal(focused, true);
  assert.equal(fakeLocation.hash, '#/map');
});

test('if main is missing, do not swallow native navigation', () => {
  let prevented = false;
  const result = skipToMain(
    { preventDefault() { prevented = true; } },
    { getElementById() { return null; } },
  );
  assert.equal(result, false);
  assert.equal(prevented, false);
});

test('visible on focus, localized and with programmatic main focus target', () => {
  const app = readFileSync(new URL('../src/App.tsx', import.meta.url), 'utf8');
  assert.match(app, /href="#main-content"/);
  assert.match(app, /onClick=\{event => skipToMain\(event, document\)\}/);
  assert.match(app, /focus:not-sr-only/);
  assert.match(app, /Pular para o conteúdo/);
  assert.match(app, /Skip to main content/);
  assert.match(app, /id="main-content" tabIndex=\{-1\}/);
});
