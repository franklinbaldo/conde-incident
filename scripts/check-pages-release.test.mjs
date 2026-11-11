import test from 'node:test';
import assert from 'node:assert/strict';
import { assessRelease, EXPECTED_SITE } from './check-pages-release.mjs';

const SHA = 'a'.repeat(40);
function good() {
  return {
    sha: SHA, upstreamConclusion: 'success',
    pages: { build_type: 'workflow', html_url: EXPECTED_SITE },
    runs: [{ name: 'Publish Conde site', head_sha: SHA, head_branch: 'main',
      event: 'push', status: 'completed', conclusion: 'success' }],
    deployments: [{ id: 12, sha: SHA, environment: 'github-pages' }],
    statuses: { 12: [{ state: 'success' }] },
    site: {
      status: 200,
      body: '<header class="masthead"></header><section class="journal"></section>' +
        '<a href="/conde-incident/stories/">Stories</a><a href="/conde-incident/lab/">Lab</a>' +
        '<link rel="stylesheet" href="https://franklinbaldo.github.io/conde-incident/css/site.css">',
      stories: { status: 200, body: '<section class="journal"><article class="story-card">' +
        '<a href="/conde-incident/stories/2026-11-11-primeira-historia/">Chapter</a></article></section>' },
      lab: { status: 200, body: '<div id="root"></div>' +
        '<script src="/conde-incident/lab/assets/main-xyz.js"></script>' },
      style: { status: 200, body: '.masthead{color:#fff}.story-card{padding:1rem}' },
    },
  };
}
test('all four independent release signals must agree', () => {
  assert.equal(assessRelease(good()).status, 'PASS');
});
test('a green build does not prove actual Pages source setting', () => {
  const x = good(); x.pages.build_type = 'legacy';
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('a successful run for another SHA is not this release', () => {
  const x = good(); x.runs[0].head_sha = 'b'.repeat(40);
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('manual dispatch is not proof of post-merge publishing', () => {
  const x = good(); x.runs[0].event = 'workflow_dispatch';
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('pending run and absent deploy both prevent publication claim', () => {
  const x = good(); x.runs[0].status = 'in_progress'; x.runs[0].conclusion = null;
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
  const y = good(); y.statuses = {};
  assert.equal(assessRelease(y).status, 'NOT_VERIFIED');
});
test('deployment of a different commit does not prove this release', () => {
  const x = good(); x.deployments[0].sha = 'b'.repeat(40);
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('wrong site URL, replaced Zola homepage, and HTTP 404 all fail closed', () => {
  const a = good(); a.pages.html_url = 'https://example.com/';
  const b = good(); b.site.body = '<div id="root"></div><script src="/conde-incident/assets/x.js"></script>';
  const c = good(); c.site.status = 404;
  for (const x of [a,b,c]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('Zola root must link to both stories and laboratory under repository base', () => {
  const a = good(); a.site.body = a.site.body.replace('/conde-incident/stories/', '/stories/');
  const b = good(); b.site.body = b.site.body.replace('/conde-incident/lab/', '/lab/');
  const c = good(); c.site.body = c.site.body.replace('/conde-incident/css/', '/css/');
  for (const x of [a,b,c]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('story listing must be published with at least one dated chapter', () => {
  const a = good(); a.site.stories.status = 404;
  const b = good(); b.site.stories.body = '<section class="journal"></section>';
  const c = good(); c.site.stories.body = c.site.stories.body.replace('/conde-incident/stories/2026-', '/stories/2026-');
  for (const x of [a,b,c]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('legacy React homepage cannot replace Zola and lab must remain isolated', () => {
  const a = good(); a.site.lab.body = a.site.lab.body.replace('/conde-incident/lab/assets/', '/conde-incident/assets/');
  const b = good(); b.site.lab.status = 404;
  for (const x of [a,b]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('a missing or misplaced Zola stylesheet rejects the release', () => {
  const a = good(); a.site.style.status = 404;
  const b = good(); b.site.style.body = '';
  for (const x of [a,b]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('failed upstream and invalid SHA cannot pass', () => {
  const a = good(); a.upstreamConclusion = 'failure';
  const b = good(); b.sha = 'abc';
  for (const x of [a,b]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
