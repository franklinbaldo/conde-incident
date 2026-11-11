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
    site: { status: 200, body: '<div id="root"></div><script src="/conde-incident/assets/main-xyz.js"></script>' },
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
test('wrong site URL, stale asset root, and HTTP 404 all fail closed', () => {
  const a = good(); a.pages.html_url = 'https://example.com/';
  const b = good(); b.site.body = '<div id="root"></div><script src="/assets/x.js"></script>';
  const c = good(); c.site.status = 404;
  for (const x of [a,b,c]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('failed upstream and invalid SHA cannot pass', () => {
  const a = good(); a.upstreamConclusion = 'failure';
  const b = good(); b.sha = 'abc';
  for (const x of [a,b]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
