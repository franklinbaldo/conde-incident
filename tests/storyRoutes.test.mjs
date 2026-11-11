import assert from 'node:assert/strict';
import test from 'node:test';
import { readSiteRoute, STORIES_INDEX, storyHref, tabHref } from '../src/lib/storyRoutes.ts';

test('static Pages story links are shareable and preserve the requested chapter', () => {
  const slug = '2026-11-11-o-dia-em-que-dois-relatos-se-cruzaram';
  assert.equal(storyHref(slug), '#/stories/' + slug);
  assert.deepEqual(readSiteRoute(storyHref(slug)), { kind: 'stories', slug });
  assert.deepEqual(readSiteRoute(STORIES_INDEX), { kind: 'stories', slug: null });
  assert.deepEqual(readSiteRoute('#/stories/'), { kind: 'stories', slug: null });
});

test('navigation tab hashes remain distinct from story hashes', () => {
  assert.equal(tabHref('map'), '#/tab/map');
  assert.deepEqual(readSiteRoute('#/tab/map'), { kind: 'tab', tab: 'map' });
  assert.deepEqual(readSiteRoute('#/tab/research'), { kind: 'tab', tab: 'research' });
});

test('unknown-but-valid slug routes to explicit not-found state in reader', () => {
  assert.deepEqual(readSiteRoute('#/stories/nao-existe'), { kind: 'stories', slug: 'nao-existe' });
});

test('malformed slugs cannot become arbitrary paths or fake links', () => {
  for (const hash of ['#/stories/../../x', '#/stories/%2Ffoo', '#/stories/%ZZ', '#/stories/a?x=1', '#/stories/UPPER']) {
    assert.equal(readSiteRoute(hash), null, hash);
  }
  assert.equal(readSiteRoute('#/tab/map/other'), null);
  assert.equal(readSiteRoute(''), null);
  assert.throws(() => storyHref('../x'), /Invalid story slug/);
  assert.throws(() => tabHref('map/other'), /Invalid tab id/);
});
