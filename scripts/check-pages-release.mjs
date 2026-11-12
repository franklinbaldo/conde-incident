#!/usr/bin/env node
/** Read-only proof of one Pages release. A green web build is not a deployment. */
import { pathToFileURL } from 'node:url';
export const EXPECTED_SITE = 'https://franklinbaldo.github.io/conde-incident/';
export function assessRelease({ sha, pages, runs = [], deployments = [], statuses = {}, site, upstreamConclusion }) {
  const checks = [];
  const check = (label, ok, evidence) => checks.push({ label, status: ok ? 'PASS' : 'NOT_VERIFIED', evidence });
  check('exact SHA', typeof sha === 'string' && /^[0-9a-f]{40}$/.test(sha), sha || '(missing)');
  check('upstream workflow conclusion', upstreamConclusion === 'success', upstreamConclusion || '(missing)');
  check('Pages setting is GitHub Actions', pages?.build_type === 'workflow', pages?.build_type || '(missing)');
  check('Pages URL is repo URL', pages?.html_url === EXPECTED_SITE, pages?.html_url || '(missing)');
  const matchingRuns = runs.filter(r => r.head_sha === sha && r.event === 'push' &&
    r.head_branch === 'main' && r.name === 'Publish Conde site');
  const successfulRun = matchingRuns.find(r => r.status === 'completed' && r.conclusion === 'success');
  check('successful publish run on exact main SHA', Boolean(successfulRun),
    matchingRuns.length ? matchingRuns.map(r => r.status + '/' + r.conclusion).join(', ') : '(missing)');
  const matchingDeployments = deployments.filter(d => d.sha === sha && d.environment === 'github-pages');
  const successfulDeployment = matchingDeployments.find(d =>
    Array.isArray(statuses[d.id]) && statuses[d.id][0]?.state === 'success');
  check('successful github-pages deployment on exact SHA', Boolean(successfulDeployment),
    successfulDeployment ? String(successfulDeployment.id) : '(missing)');
  // The public entrypoint is Zola. React/Vite lives *only* under /lab/.
  // A successful workflow + Pages deployment does not alone prove the live URL is correct.
  const homeOk = site?.status === 200 && typeof site.body === 'string' &&
    /<header\s+class=["']masthead["']/.test(site.body) &&
    /<section\s+class=["']journal["']/.test(site.body) &&
    site.body.includes('/conde-incident/stories/') &&
    site.body.includes('/conde-incident/lab/') &&
    site.body.includes('/conde-incident/css/site.css');
  check('live HTTPS root renders Zola journal and correct base URLs', Boolean(homeOk),
    site ? 'HTTP ' + site.status : '(unreachable)');
  // Every indexed story must resolve to the expected source, not just the first card.
  const indexedCards = Array.from((site?.stories?.body || '').matchAll(
    /<article\s+class=["']story-card["'][^>]*>([\s\S]*?)<\/article>/gi
  ), match => match[1]);
  const storyLink = /href=["'](?:https:\/\/franklinbaldo\.github\.io)?(\/conde-incident\/stories\/(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\/)["']/i;
  const storyMatches = indexedCards.map(card => card.match(storyLink));
  const chapterPaths = storyMatches.map(match => match?.[1]);
  const storiesOk = site?.stories?.status === 200 &&
    /<section\s+class=["']journal["']/.test(site.stories.body || '') &&
    indexedCards.length > 0 &&
    storyMatches.every(Boolean) &&
    new Set(chapterPaths).size === indexedCards.length;
  check('live Zola story listing resolves every unique dated chapter', Boolean(storiesOk),
    site?.stories ? 'HTTP ' + site.stories.status + ', cards: ' + indexedCards.length : '(unreachable)');
  const chaptersOk = storiesOk && Array.isArray(site?.chapters) &&
    site.chapters.length === chapterPaths.length &&
    storyMatches.every((match, i) => {
      const chapter = site.chapters[i];
      const expectedSource = 'https://github.com/franklinbaldo/conde-incident/blob/main/stories/' +
        match[2] + '.md';
      const body = chapter?.body || '';
      return chapter?.path === match[1] && chapter.status === 200 &&
        /<article\s+class=["']full-story["']/.test(body) &&
        /<div\s+class=["']story-body["']/.test(body) &&
        (body.includes('href="' + expectedSource + '"') ||
          body.includes("href='" + expectedSource + "'")) &&
        body.includes('Consultar Markdown-fonte e histórico editorial');
    });
  check('every indexed Zola chapter is live, complete, and cites its own Markdown source',
    Boolean(chaptersOk), site?.chapters ? 'Fetched: ' + site.chapters.length : '(not fetched)');
  const labOk = site?.lab?.status === 200 &&
    /<div\s+id=["']root["']/.test(site.lab.body || '') &&
    /\/conde-incident\/lab\/assets\/[^"'\s>]+\.js/.test(site.lab.body || '');
  check('live React lab has separate /lab/ bundle', Boolean(labOk),
    site?.lab ? 'HTTP ' + site.lab.status : '(unreachable)');
  const cssOk = site?.style?.status === 200 &&
    /\.masthead|\.story-card/.test(site.style.body || '');
  check('live Zola stylesheet available at repository base', Boolean(cssOk),
    site?.style ? 'HTTP ' + site.style.status : '(unreachable)');
  return { status: checks.every(c => c.status === 'PASS') ? 'PASS' : 'NOT_VERIFIED', checks };
}
async function getJson(url, token) {
  const headers = { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' };
  if (token) headers.Authorization = 'Bearer ' + token;
  const r = await fetch(url, { headers, signal: AbortSignal.timeout(15000) });
  if (!r.ok) throw new Error(url + ': HTTP ' + r.status);
  return r.json();
}
export async function auditFromGitHub({ repo, sha, token, upstreamConclusion, siteUrl = EXPECTED_SITE }) {
  if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repo)) throw new Error('Invalid repository');
  if (!/^[0-9a-f]{40}$/.test(sha)) throw new Error('Invalid or missing 40-character SHA');
  if (siteUrl !== EXPECTED_SITE) throw new Error('Unexpected site URL');
  const api = 'https://api.github.com/repos/' + repo;
  const pages = await getJson(api + '/pages', token);
  const result = await getJson(api + '/actions/workflows/pages.yml/runs?head_sha=' +
    encodeURIComponent(sha) + '&event=push&per_page=30', token);
  const deployments = await getJson(api + '/deployments?sha=' + encodeURIComponent(sha) +
    '&environment=github-pages&per_page=30', token);
  const statuses = {};
  for (const d of deployments) {
    if (d.sha === sha && d.environment === 'github-pages') {
      statuses[d.id] = await getJson(api + '/deployments/' + d.id + '/statuses?per_page=10', token);
    }
  }
  const readPage = async suffix => {
    const r = await fetch(siteUrl + suffix, {
      signal: AbortSignal.timeout(15000), redirect: 'follow',
    });
    return { status: r.status, body: r.ok ? await r.text() : '' };
  };
  const site = await readPage('');
  site.stories = await readPage('stories/');
  const cards = Array.from(site.stories.body.matchAll(
    /<article\s+class=["']story-card["'][^>]*>([\s\S]*?)<\/article>/gi
  ), match => match[1]);
  const chapters = cards.map(card => card.match(
    /href=["'](?:https:\/\/franklinbaldo\.github\.io)?(\/conde-incident\/stories\/\d{4}-\d{2}-\d{2}-[a-z0-9-]+\/)["']/i
  )?.[1]);
  if (chapters.length > 100) throw new Error('More than 100 chapters: review bounded audit');
  site.chapters = [];
  for (const chapterPath of chapters) {
    if (!chapterPath) continue; // assessRelease fails closed on a malformed card.
    // Each article is fetched, so later broken chapters cannot hide behind the first.
    site.chapters.push({
      ...await readPage(chapterPath.slice('/conde-incident/'.length)),
      path: chapterPath,
    });
  }
  site.lab = await readPage('lab/');
  site.style = await readPage('css/site.css');
  return assessRelease({ sha, pages, runs: result.workflow_runs, deployments, statuses, site, upstreamConclusion });
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const repo = process.env.GITHUB_REPOSITORY || 'franklinbaldo/conde-incident';
  const sha = process.env.TARGET_SHA || '';
  try {
    const result = await auditFromGitHub({
      repo, sha, token: process.env.GITHUB_TOKEN,
      upstreamConclusion: process.env.UPSTREAM_CONCLUSION,
    });
    console.log(JSON.stringify({ repo, sha, ...result }, null, 2));
    if (result.status !== 'PASS') process.exitCode = 1;
  } catch (error) {
    console.error(JSON.stringify({ repo, sha, status: 'NOT_VERIFIED',
      reason: String(error) }, null, 2));
    process.exitCode = 1;
  }
}
