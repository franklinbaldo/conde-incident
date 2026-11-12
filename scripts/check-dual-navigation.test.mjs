import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { journalPath } from '../src/lib/sitePaths.mjs';

const read = path => readFileSync(new URL('../' + path, import.meta.url), 'utf8');

test('journal route remains inside the site from local and Pages lab deployments', () => {
  assert.equal(journalPath('/'), '/stories/');
  assert.equal(journalPath('/lab/'), '/stories/');
  assert.equal(journalPath('/conde-incident/'), '/conde-incident/stories/');
  assert.equal(journalPath('/conde-incident/lab/'), '/conde-incident/stories/');
  assert.equal(journalPath('/group/conde-incident/lab/'), '/group/conde-incident/stories/');
});

test('external, absolute, traversal and encoded slash paths cannot redirect journal links', () => {
  for (const unsafe of [
    'https://example.org/conde-incident/lab/', '//example.org/lab/',
    '/conde-incident/../lab/', '/conde-incident/%2e%2e/lab/',
    '/conde-incident/%2f/lab/', '/conde-incident/lab?next=evil/',
    '/conde-incident/lab#evil/', '/conde-incident//lab/', 'lab/',
  ]) {
    assert.throws(() => journalPath(unsafe), {name: 'TypeError'}, unsafe);
  }
});

test('scientific landing page remains Evidence and retains ResearchLedger', () => {
  const app = read('src/App.tsx');
  assert.match(app, /useState<TabId>\('research'\)/);
  assert.match(app, /activeTab === 'research' && <ResearchLedger/);
  assert.match(app, /activeTab !== 'research' && <div/);
  assert.doesNotMatch(app, /useState<TabId>\('summary'\)/);
});

test('navigation includes both research and a separate real Caderno link', () => {
  const nav = read('src/components/Navigation.tsx');
  assert.match(nav, /\| 'research'/);
  assert.match(nav, /id: 'research' as TabId/);
  assert.match(nav, /labelPt: 'Evidências & Pesquisa'/);
  assert.match(nav, /journalPath\(import\.meta\.env\.BASE_URL\)/);
  assert.match(nav, /href=\{storiesHref\}/);
  assert.match(nav, /Caderno de histórias/);
  assert.doesNotMatch(nav, /Veredito & Resumo/);
});

test('published lab assets use /conde-incident/lab/ and workflow checks navigation', () => {
  const vite = read('vite.config.ts');
  assert.match(vite, /GITHUB_PAGES === 'true' \? '\/conde-incident\/lab\/'/);
  const workflow = read('.github/workflows/science.yml');
  assert.match(workflow, /node --test scripts\/check-dual-navigation\.test\.mjs/);
  assert.match(workflow, /github\.event\.pull_request\.head\.sha \|\| github\.sha/);
  assert.doesNotMatch(workflow, /deploy-pages/);
});
