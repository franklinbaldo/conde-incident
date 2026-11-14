import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { getLabLanguage, labLanguagePath } from '../src/lib/labLanguage.ts';

test('only one en selects English; unknown and duplicated locale values fail closed', () => {
  for (const search of ['', '?lang=pt', '?lang=fr', '?lang=EN', '?lang=',
    '?lang=en&lang=pt', '?lang=en&lang=en', '?lang=%00en']) {
    assert.equal(getLabLanguage(search), 'pt', search);
  }
  assert.equal(getLabLanguage('?lang=en'), 'en');
  assert.equal(getLabLanguage('?source=archive&lang=en'), 'en');
});

test('PT/EN roundtrip preserves Pages prefix and calculated UTC deep link', () => {
  const root = 'https://example.test';
  const original = root + '/conde-incident/lab/?source=archive#/map?at=1963-10-27T14%3A40%3A16.132Z';
  const english = labLanguagePath(original, 'en');
  assert.equal(english, '/conde-incident/lab/?source=archive&lang=en#/map?at=1963-10-27T14%3A40%3A16.132Z');
  assert.equal(getLabLanguage(new URL(english, root).search), 'en');
  assert.equal(labLanguagePath(new URL(english, root).href, 'pt'),
    '/conde-incident/lab/?source=archive#/map?at=1963-10-27T14%3A40%3A16.132Z');
  assert.equal(labLanguagePath(root + '/conde-incident/lab/?lang=pt&lang=en#/inverse', 'en'),
    '/conde-incident/lab/?lang=en#/inverse');
});

test('app synchronizes native history and language without tracking storage', () => {
  const app = readFileSync(new URL('../src/App.tsx', import.meta.url), 'utf8');
  assert.match(app, /getLabLanguage\(window\.location\.search\)/);
  assert.match(app, /history\.replaceState\(window\.history\.state, '', labLanguagePath/);
  assert.match(app, /addEventListener\('popstate', handleHashChange\)/);
  assert.match(app, /removeEventListener\('popstate', handleHashChange\)/);
  assert.match(app, /setLang=\{selectLanguage\}/);
  assert.doesNotMatch(app, /localStorage|sessionStorage|document\.cookie/);
});
