#!/usr/bin/env node
/** Read-only proof of one Pages release. A green web build is not a deployment. */
import { pathToFileURL } from 'node:url';
export const EXPECTED_SITE = 'https://franklinbaldo.github.io/conde-incident/';
export function assessRelease({ sha, pages, runs = [], deployments = [], statuses = {}, sourceTree, site, upstreamConclusion,
  mainHead, latestDeployments, finalControl }) {
  const checks = [];
  const check = (label, ok, evidence) => checks.push({ label, status: ok ? 'PASS' : 'NOT_VERIFIED', evidence });
  check('exact SHA', typeof sha === 'string' && /^[0-9a-f]{40}$/.test(sha), sha || '(missing)');
  check('upstream workflow conclusion', upstreamConclusion === 'success', upstreamConclusion || '(missing)');
  check('Pages setting is GitHub Actions', pages?.build_type === 'workflow', pages?.build_type || '(missing)');
  check('Pages URL is repo URL', pages?.html_url === EXPECTED_SITE, pages?.html_url || '(missing)');
  check('current main HEAD is the audited release SHA', mainHead?.commit?.sha === sha,
    mainHead?.commit?.sha || '(missing)');
  const matchingRuns = runs.filter(r => r.head_sha === sha && r.event === 'push' &&
    r.head_branch === 'main' && r.name === 'Publish Conde site');
  // GitHub lists workflow runs newest first. An older successful attempt must not mask a newer failure.
  const latestRun = matchingRuns[0];
  const successfulRun = latestRun?.status === 'completed' && latestRun?.conclusion === 'success';
  check('latest publish run on exact main SHA succeeded', Boolean(successfulRun),
    matchingRuns.length ? matchingRuns.map(r => r.status + '/' + r.conclusion).join(', ') : '(missing)');
  // A historical green deployment is not proof that the current public site still serves that SHA.
  // GitHub returns deployments newest first; the latest must be the audited release.
  const latestDeployment = Array.isArray(latestDeployments) ? latestDeployments[0] : null;
  const currentDeployment = latestDeployment?.sha === sha &&
    latestDeployment?.environment === 'github-pages';
  check('newest Pages deployment is from audited SHA', Boolean(currentDeployment),
    latestDeployment ? String(latestDeployment.id) + '/' + latestDeployment.sha : '(missing)');
  const matchingDeployments = deployments.filter(d => d.sha === sha && d.environment === 'github-pages');
  const successfulDeployment = currentDeployment && matchingDeployments.find(d =>
    d.id === latestDeployment.id && Array.isArray(statuses[d.id]) && statuses[d.id][0]?.state === 'success');
  check('successful github-pages deployment on exact SHA', Boolean(successfulDeployment),
    successfulDeployment ? String(successfulDeployment.id) : '(missing)');
  // The editorial entrypoint may be SSG; stable HTML selectors form a publication contract. React/Vite remains under /lab/.
  // A successful workflow + Pages deployment does not alone prove the live URL is correct.
  const homeOk = site?.status === 200 && typeof site.body === 'string' &&
    /<header\s+class=["']masthead["']/.test(site.body) &&
    /<section\s+class=["']journal["']/.test(site.body) &&
    site.body.includes('/conde-incident/stories/') &&
    site.body.includes('/conde-incident/lab/') &&
    site.body.includes('/conde-incident/css/site.css');
  check('live HTTPS root renders editorial journal and correct base URLs', Boolean(homeOk),
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
  check('live story listing resolves every unique dated chapter', Boolean(storiesOk),
    site?.stories ? 'HTTP ' + site.stories.status + ', cards: ' + indexedCards.length : '(unreachable)');
  // Compare published cards with Markdown source files from the exact commit tree.
  // The tree can be fetched without trusting the rendered site or mutable main refs.
  const sourceEntries = Array.isArray(sourceTree?.tree)
    ? sourceTree.tree.filter(e => typeof e.path === 'string' &&
        e.path.startsWith('stories/') && e.path.endsWith('.md') &&
        e.path !== 'stories/README.md')
    : [];
  const sourceSlugs = sourceEntries.map(e => e.path.slice('stories/'.length, -'.md'.length));
  const sourceOk = sourceTree?.truncated === false && sourceEntries.length > 0 &&
    sourceEntries.length <= 100 &&
    sourceEntries.every(e => e.type === 'blob' &&
      /^stories\/\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$/.test(e.path)) &&
    new Set(sourceSlugs).size === sourceSlugs.length &&
    sourceSlugs.length === indexedCards.length &&
    sourceSlugs.every(slug => storyMatches.some(m => m?.[2] === slug));
  check('all canonical Markdown sources in exact SHA tree are publicly indexed',
    Boolean(sourceOk), sourceTree?.truncated ? '(tree truncated)' :
      'source files: ' + sourceEntries.length + ', cards: ' + indexedCards.length);
  const chaptersOk = storiesOk && sourceOk && Array.isArray(site?.chapters) &&
    site.chapters.length === chapterPaths.length &&
    storyMatches.every((match, i) => {
      const chapter = site.chapters[i];
      const expectedSource = 'https://github.com/franklinbaldo/conde-incident/blob/' + sha + '/stories/' +
        match[2] + '.md';
      const body = chapter?.body || '';
      return chapter?.path === match[1] && chapter.status === 200 &&
        /<article\s+class=["']full-story["']/.test(body) &&
        /<div\s+class=["']story-body["']/.test(body) &&
        (body.includes('href="' + expectedSource + '"') ||
          body.includes("href='" + expectedSource + "'")) &&
        body.includes('Consultar Markdown-fonte e histórico editorial');
    });
  check('every chapter is live and links to source at exact immutable commit SHA',
    Boolean(chaptersOk), site?.chapters ? 'Fetched: ' + site.chapters.length : '(not fetched)');
  const labOk = site?.lab?.status === 200 &&
    /<div\s+id=["']root["']/.test(site.lab.body || '') &&
    /\/conde-incident\/lab\/assets\/[^"'\s>]+\.js/.test(site.lab.body || '');
  check('live React lab has separate /lab/ bundle', Boolean(labOk),
    site?.lab ? 'HTTP ' + site.lab.status : '(unreachable)');
  const cssOk = site?.style?.status === 200 &&
    /\.masthead|\.story-card/.test(site.style.body || '');
  check('live editorial stylesheet available at repository base', Boolean(cssOk),
    site?.style ? 'HTTP ' + site.style.status : '(unreachable)');
  // Check the control plane again AFTER all potentially slow public HTTP reads.
  // The initial success snapshot alone is vulnerable to a mid-audit main advance,
  // rerun, redeploy or Pages source-setting change.
  const finalRun = (finalControl?.runs || []).filter(r =>
    r.head_sha === sha && r.event === 'push' && r.head_branch === 'main' &&
    r.name === 'Publish Conde site')[0];
  const finalDeployment = finalControl?.latestDeployments?.[0];
  check('main remained at audited SHA through end of HTTP inspection',
    finalControl?.mainHead?.commit?.sha === sha && mainHead?.commit?.sha === sha,
    finalControl?.mainHead?.commit?.sha || '(missing)');
  check('Pages GitHub Actions configuration remained unchanged through inspection',
    finalControl?.pages?.build_type === 'workflow' &&
    finalControl?.pages?.html_url === EXPECTED_SITE &&
    finalControl?.pages?.build_type === pages?.build_type &&
    finalControl?.pages?.html_url === pages?.html_url,
    finalControl?.pages?.build_type || '(missing)');
  check('latest successful publish run remained identical through inspection',
    Number.isSafeInteger(latestRun?.id) && latestRun.id > 0 &&
    finalRun?.id === latestRun.id && finalRun?.status === 'completed' &&
    finalRun?.conclusion === 'success',
    finalRun ? String(finalRun.id) + '/' + finalRun.status + '/' + finalRun.conclusion : '(missing)');
  check('newest deployment stayed successful through inspection',
    Number.isSafeInteger(latestDeployment?.id) && latestDeployment.id > 0 &&
    finalDeployment?.id === latestDeployment.id &&
    finalDeployment?.sha === sha && finalDeployment?.environment === 'github-pages' &&
    finalControl?.latestStatuses?.[0]?.state === 'success',
    finalDeployment ? String(finalDeployment.id) + '/' +
      (finalControl?.latestStatuses?.[0]?.state || '(missing status)') : '(missing)');
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
  const mainHead = await getJson(api + '/branches/main', token);
  const latestDeployments = await getJson(api + '/deployments?environment=github-pages&per_page=1', token);
  const result = await getJson(api + '/actions/workflows/pages.yml/runs?head_sha=' +
    encodeURIComponent(sha) + '&event=push&per_page=30', token);
  const deployments = await getJson(api + '/deployments?sha=' + encodeURIComponent(sha) +
    '&environment=github-pages&per_page=30', token);
  // Git trees API accepts a commit SHA; request all paths from that exact release.
  const sourceTree = await getJson(api + '/git/trees/' + sha + '?recursive=1', token);
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
  // Re-read at the end, rather than extrapolating the initial snapshot.
  // A PASS means only that these independent reads remained consistent;
  // GitHub APIs and the CDN do not provide an atomic cross-service snapshot.
  const finalPages = await getJson(api + '/pages', token);
  const finalMainHead = await getJson(api + '/branches/main', token);
  const finalLatestDeployments = await getJson(api + '/deployments?environment=github-pages&per_page=1', token);
  const finalRuns = await getJson(api + '/actions/workflows/pages.yml/runs?head_sha=' +
    encodeURIComponent(sha) + '&event=push&per_page=30', token);
  const finalDeployment = finalLatestDeployments[0];
  const finalLatestStatuses = finalDeployment?.id
    ? await getJson(api + '/deployments/' + finalDeployment.id + '/statuses?per_page=1', token)
    : [];
  return assessRelease({ sha, pages, runs: result.workflow_runs, deployments, statuses,
    sourceTree, site, upstreamConclusion, mainHead, latestDeployments,
    finalControl: { pages: finalPages, mainHead: finalMainHead,
      latestDeployments: finalLatestDeployments, runs: finalRuns.workflow_runs,
      latestStatuses: finalLatestStatuses } });
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
