import test from 'node:test';
import assert from 'node:assert/strict';
import { LAB_TABS } from '../src/lib/tabRoutes.ts';
import { EDITORIAL_ROUTES } from '../src/lib/editorialRoutes.ts';
import { existsSync, readFileSync } from 'node:fs';

test('all eight laboratory views have unique, existing SSG editorial destinations', () => {
  assert.deepEqual(Object.keys(EDITORIAL_ROUTES).sort(), [...LAB_TABS].sort());
  const destinations = new Set();
  for (const tab of LAB_TABS) {
    const route = EDITORIAL_ROUTES[tab];
    assert.match(route.href, /^\/conde-incident\/(?:[a-z/-]+\/)?$/);
    assert(!route.href.includes('/lab/'), 'context links must leave the SPA');
    assert(route.pt.length > 5 && route.en.length > 5, 'context link must name destination');
    assert(!destinations.has(route.href), 'two tabs should not silently share context: ' + tab);
    destinations.add(route.href);
    const slug = route.href.slice('/conde-incident/'.length);
    if (slug === '') continue;
    const authored = 'pages/' + slug + 'page.md';
    // Some routes (archive, custody) are generated from versioned evidence.
    if (!existsSync(authored)) {
      const preparation = readFileSync('scripts/prepare-ssg.mjs', 'utf8');
      const archive = readFileSync('scripts/ssg-documentary-archive.mjs', 'utf8');
      const tle = readFileSync('scripts/ssg-tle-custody.mjs', 'utf8');
      assert(
        [preparation, archive, tle].some(source => source.includes(slug)),
        'no generated or authored route for ' + tab + ': ' + route.href
      );
    }
  }
});

test('the laboratory keeps the home link and exposes contextual links as native anchors', () => {
  const nav = readFileSync('src/components/Navigation.tsx', 'utf8');
  assert.match(nav, /href=\{editorialContext\.href\}/);
  assert.match(nav, /activeTab !== 'summary'/);
  assert.match(nav, /aria-label=\{lang === 'pt'/);
  assert.match(nav, /href=\{EDITORIAL_ROUTES\.summary\.href\}/);
});
