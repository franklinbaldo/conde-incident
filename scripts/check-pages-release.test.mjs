import test from 'node:test';
import assert from 'node:assert/strict';
import { assessRelease, EXPECTED_SITE } from './check-pages-release.mjs';

const SHA = 'a'.repeat(40);
function good() {
  return {
    sha: SHA, upstreamConclusion: 'success',
    pages: { build_type: 'workflow', html_url: EXPECTED_SITE },
    mainHead: { commit: { sha: SHA } },
    latestDeployments: [{ id: 12, sha: SHA, environment: 'github-pages' }],
    runs: [{ id: 42, name: 'Publish Conde site', head_sha: SHA, head_branch: 'main',
      event: 'push', status: 'completed', conclusion: 'success' }],
    deployments: [{ id: 12, sha: SHA, environment: 'github-pages' }],
    statuses: { 12: [{ state: 'success' }] },
    finalControl: {
      pages: { build_type: 'workflow', html_url: EXPECTED_SITE },
      mainHead: { commit: { sha: SHA } },
      latestDeployments: [{ id: 12, sha: SHA, environment: 'github-pages' }],
      runs: [{ id: 42, name: 'Publish Conde site', head_sha: SHA, head_branch: 'main',
        event: 'push', status: 'completed', conclusion: 'success' }],
      latestStatuses: [{ state: 'success' }],
    },
    sourceTree: { truncated: false, tree: [
      { path: 'stories/2026-11-11-primeira-historia.md', type: 'blob' },
    ] },
    site: {
      status: 200,
      body: '<header class="masthead"></header><section class="journal"></section>' +
        '<a href="/conde-incident/stories/">Stories</a><a href="/conde-incident/lab/">Lab</a>' +
        '<link rel="stylesheet" href="https://franklinbaldo.github.io/conde-incident/css/site.css">',
      stories: { status: 200, body: '<section class="journal"><article class="story-card">' +
        '<a href="/conde-incident/stories/2026-11-11-primeira-historia/">Chapter</a></article></section>' },
      chapters: [{ status: 200, path: '/conde-incident/stories/2026-11-11-primeira-historia/',
        body: '<article class="full-story"><div class="story-body"><p>Documented advance.</p></div>' +
          '<a href="https://github.com/franklinbaldo/conde-incident/blob/' + SHA + '/stories/2026-11-11-primeira-historia.md">' +
          'Consultar Markdown-fonte e histórico editorial</a></article>' }],
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

test('chapter link must lead to a live full Zola story with source attribution', () => {
  const a = good(); a.site.chapters[0].status = 404;
  const b = good(); b.site.chapters[0].body = '<html><body>Generic error fallback</body></html>';
  const c = good(); c.site.chapters[0].body = '<article class="full-story"><div class="story-body">No source link</div></article>';
  const d = good(); d.site.chapters[0].path = '/conde-incident/stories/2026-11-11-outra/';
  const e = good(); delete e.site.chapters;
  for (const x of [a,b,c,d,e]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('a fake date outside a journal link is not a published story', () => {
  const x = good();
  x.site.stories.body = '<section class="journal"><article class="story-card">' +
    '/conde-incident/stories/2026-11-11-primeira-historia/' +
    '</article></section>';
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('Zola absolute permalink on the canonical host is allowed', () => {
  const x = good();
  x.site.stories.body = x.site.stories.body.replace(
    'href="/conde-incident/stories/',
    'href="https://franklinbaldo.github.io/conde-incident/stories/'
  );
  assert.equal(assessRelease(x).status, 'PASS');
});
test('an external host must not be followed as a first-party chapter', () => {
  const x = good();
  x.site.stories.body = x.site.stories.body.replace(
    'href="/conde-incident/stories/',
    'href="https://unrelated.example/conde-incident/stories/'
  );
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});


function withTwoChapters() {
  const x = good();
  x.sourceTree.tree.push({ path: 'stories/2026-11-12-segunda-historia.md', type: 'blob' });
  const slug = '2026-11-12-segunda-historia';
  const path = '/conde-incident/stories/' + slug + '/';
  x.site.stories.body = x.site.stories.body.replace('</section>',
    '<article class="story-card"><a href="' + path + '">Second chapter</a></article></section>');
  x.site.chapters.push({
    path, status: 200,
    body: '<article class="full-story"><div class="story-body"><p>Independent new lead.</p></div>' +
      '<a href="https://github.com/franklinbaldo/conde-incident/blob/' + SHA + '/stories/' + slug + '.md">' +
      'Consultar Markdown-fonte e histórico editorial</a></article>',
  });
  return x;
}
test('all published chapters are checked, not only the first one', () => {
  const x = withTwoChapters();
  assert.equal(assessRelease(x).status, 'PASS');
  x.site.chapters[1].status = 404;
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
  x.site.chapters[1].status = 200;
  x.site.chapters[1].body = '<article class="full-story"><div class="story-body">No source</div></article>';
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('incomplete chapter fetch or altered article order must fail closed', () => {
  const x = withTwoChapters();
  x.site.chapters.pop();
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
  const y = withTwoChapters();
  y.site.chapters.reverse();
  assert.equal(assessRelease(y).status, 'NOT_VERIFIED');
});
test('each chapter must cite its own source Markdown, not another story', () => {
  const x = good();
  x.site.chapters[0].body = x.site.chapters[0].body.replace(
    'stories/2026-11-11-primeira-historia.md', 'stories/another.md');
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('duplicate story links and untrusted external chapter links fail', () => {
  const x = withTwoChapters();
  x.site.stories.body = x.site.stories.body.replace(
    '/conde-incident/stories/2026-11-12-segunda-historia/',
    '/conde-incident/stories/2026-11-11-primeira-historia/');
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
  const y = withTwoChapters();
  y.site.stories.body = y.site.stories.body.replace(
    'href="/conde-incident/stories/2026-11-12',
    'href="https://external.example/conde-incident/stories/2026-11-12');
  assert.equal(assessRelease(y).status, 'NOT_VERIFIED');
});

test('source tree for the exact release is mandatory and cannot be truncated', () => {
  const missing = good(); delete missing.sourceTree;
  const partial = good(); partial.sourceTree.truncated = true;
  const empty = good(); empty.sourceTree.tree = [];
  for (const x of [missing, partial, empty]) {
    assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
  }
});
test('a source chapter omitted from a seemingly healthy live listing fails', () => {
  const x = good();
  x.sourceTree.tree.push({ path: 'stories/2026-11-12-nao-publicada.md', type: 'blob' });
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('extra chapter card not present at source commit fails', () => {
  const x = withTwoChapters();
  x.sourceTree.tree.pop();
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('source tree rejects duplicate or malformed chapter source filenames', () => {
  const a = good(); a.sourceTree.tree.push(a.sourceTree.tree[0]);
  const b = good(); b.sourceTree.tree[0].path = 'stories/README.md';
  const c = good(); c.sourceTree.tree[0].type = 'tree';
  for (const x of [a,b,c]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('each published story links to immutable exact-SHA source, not moving main or another SHA', () => {
  const a = good(); a.site.chapters[0].body = a.site.chapters[0].body.replace(
    '/blob/' + SHA + '/stories/', '/blob/main/stories/');
  const b = good(); b.site.chapters[0].body = b.site.chapters[0].body.replace(
    '/blob/' + SHA + '/stories/', '/blob/' + 'b'.repeat(40) + '/stories/');
  for (const x of [a,b]) assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('two chapters with immutable matching source references pass the source ledger check', () => {
  const x = withTwoChapters();
  assert.equal(assessRelease(x).status, 'PASS');
});

test('canonical stories README is editorial documentation, not a missing chapter', () => {
  const x = good();
  x.sourceTree.tree.push({ path: 'stories/README.md', type: 'blob' });
  assert.equal(assessRelease(x).status, 'PASS');
  x.sourceTree.tree.push({ path: 'stories/unexpected.md', type: 'blob' });
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});

test('published SHA is not current main HEAD: stale successful run cannot pass', () => {
  const x = good();
  x.mainHead.commit.sha = 'b'.repeat(40);
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
  assert.ok(assessRelease(x).checks.some(c =>
    c.label === 'current main HEAD is the audited release SHA' && c.status === 'NOT_VERIFIED'));
});
test('newer Pages deployment supersedes an older successful deployment', () => {
  const x = good();
  x.latestDeployments = [{ id: 13, sha: 'b'.repeat(40), environment: 'github-pages' }];
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('latest deployment pending, old success on same SHA must not be accepted', () => {
  const x = good();
  x.latestDeployments = [{ id: 13, sha: SHA, environment: 'github-pages' }];
  x.deployments.unshift(x.latestDeployments[0]);
  x.statuses[13] = [{ state: 'pending' }];
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('newer failed publication run cannot be masked by previous successful run', () => {
  const x = good();
  x.runs.unshift({ name: 'Publish Conde site', head_sha: SHA, head_branch: 'main',
    event: 'push', status: 'completed', conclusion: 'failure' });
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('missing freshest-main and latest-deployment evidence fails closed', () => {
  const x = good(); delete x.mainHead;
  const y = good(); delete y.latestDeployments;
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
  assert.equal(assessRelease(y).status, 'NOT_VERIFIED');
});

test('main advanced during multi-chapter fetch: initial clean snapshot is insufficient', () => {
  const x = good();
  x.finalControl.mainHead.commit.sha = 'b'.repeat(40);
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('Pages switched from Actions to branch source during public HTTP reads', () => {
  const x = good();
  x.finalControl.pages.build_type = 'legacy';
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('new push publication run appears after initial green snapshot', () => {
  const x = good();
  x.finalControl.runs.unshift({ id: 43, name: 'Publish Conde site',
    head_sha: SHA, head_branch: 'main', event: 'push',
    status: 'completed', conclusion: 'failure' });
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('post-read deployment supersedes initially successful deployment', () => {
  const x = good();
  x.finalControl.latestDeployments = [{ id: 13, sha: SHA, environment: 'github-pages' }];
  x.finalControl.latestStatuses = [{ state: 'success' }];
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('deployment success revoked or pending while fetching last chapter', () => {
  const x = good();
  x.finalControl.latestStatuses[0].state = 'pending';
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('missing second control-plane snapshot cannot imply published', () => {
  const x = good();
  delete x.finalControl;
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
test('latest publish run identity is mandatory: no unidentified green run', () => {
  const x = good();
  delete x.runs[0].id;
  assert.equal(assessRelease(x).status, 'NOT_VERIFIED');
});
