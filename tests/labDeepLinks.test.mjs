import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { LAB_TABS, mapTimeHref, MAP_TIME_START, MAP_TIME_END, parseLabRoute, tabHref } from '../src/lib/tabRoutes.ts';

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

test('a calculated map instant has a canonical UTC deep link and roundtrips exactly', () => {
  for (const timeMs of [MAP_TIME_START, Date.parse('1963-10-27T14:40:16.132Z'), MAP_TIME_END]) {
    const hash = mapTimeHref(timeMs);
    assert.match(hash, /^#\/map\?at=1963-/);
    assert.deepEqual(parseLabRoute(hash), { tab: 'map', invalidHash: null, timeMs });
  }
  assert.equal(mapTimeHref(NaN), '#/map');
  assert.equal(mapTimeHref(MAP_TIME_END + 1), '#/map');
  assert.equal(mapTimeHref(MAP_TIME_START - 1), '#/map');
});

test('invalid map times and unexpected query parameters fail closed', () => {
  for (const hash of ['#/map?at=tomorrow', '#/map?at=1963-11-09T00%3A00%3A00.000Z',
    '#/map?at=1963-11-08T24%3A00%3A00.000Z', '#/map?at=1963-10-27T14%3A40%3A16Z',
    '#/map?at=%XX', '#/map?at=1963-10-27T14%3A40%3A16.132Z&fake=true',
    '#/documents?at=1963-10-27T14%3A40%3A16.132Z']) {
    assert.deepEqual(parseLabRoute(hash), { tab: 'summary', invalidHash: hash });
  }
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
  assert.match(app, /mapTimeHref\(timeMs\)/);
  assert.match(app, /next\.timeMs !== undefined/);
  const map = readFileSync(new URL('../src/components/OrbitalMap.tsx', import.meta.url), 'utf8');
  assert.match(map, /href=\{mapTimeHref\(time\)\}/);
  assert.match(map, /não é uma hora observada/);
  assert.match(app, /document\.documentElement\.lang/);
  assert.doesNotMatch(nav, /Checksums 100%|7 Respostas|N=5000|Desclassificados/);
  assert.doesNotMatch(nav, /Conde-BA: 11\.81° S/);
  assert.doesNotMatch(nav, /\/stories\/|\/evidence\//);
});
