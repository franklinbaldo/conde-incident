import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { LAB_TABS, parseLabRoute, tabHref } from '../src/lib/tabRoutes.ts';

const app = readFileSync(new URL('../src/App.tsx', import.meta.url), 'utf8');
const nav = readFileSync(new URL('../src/components/Navigation.tsx', import.meta.url), 'utf8');

test('every shipped laboratory tab has a stable, shareable canonical hash', () => {
  assert.equal(new Set(LAB_TABS).size, LAB_TABS.length);
  for (const tab of LAB_TABS) {
    assert.deepEqual(parseLabRoute(tabHref(tab)), { tab, invalidHash: null });
    assert.deepEqual(parseLabRoute(tabHref(tab) + '/'), { tab, invalidHash: null });
  }
  assert.deepEqual(parseLabRoute(''), { tab: 'summary', invalidHash: null });
  assert.deepEqual(parseLabRoute('#/'), { tab: 'summary', invalidHash: null });
});

test('unknown hashes are not mistaken for a verified page or silently accepted', () => {
  for (const hash of ['#/evidence', '#/stories', '#/documents/doc-01',
    '#/map/../../stories', '#/MAP', '#/%3Cscript%3E']) {
    const route = parseLabRoute(hash);
    assert.equal(route.tab, 'summary');
    assert.equal(route.invalidHash, hash);
  }
});

test('navigation uses native links and restores browser history in React', () => {
  assert.match(nav, /href=\{tabHref\(tab\.id\)\}/);
  assert.match(nav, /aria-current=\{isActive \? 'page' : undefined\}/);
  assert.match(app, /addEventListener\('hashchange', handleHashChange\)/);
  assert.match(app, /removeEventListener\('hashchange', handleHashChange\)/);
  assert.match(app, /aria-live="polite"/);
  assert.match(app, /navigateTab\('map'\)/);
  assert.match(app, /document\.documentElement\.lang/);
  assert.doesNotMatch(nav, /Checksums 100%|7 Respostas|N=5000|Desclassificados/);
  assert.doesNotMatch(nav, /Conde-BA: 11\.81° S/);
  assert.doesNotMatch(nav, /\/stories\/|\/evidence\//);
});
