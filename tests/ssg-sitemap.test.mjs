import assert from 'node:assert/strict';
import {mkdtempSync, mkdirSync, readFileSync, rmSync, unlinkSync, writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';
import test from 'node:test';
import {BASE, generateSitemap} from '../scripts/build-sitemap.mjs';

const checker = resolve('tools/check_sitemap.py');
function fixture() {
  const dir = mkdtempSync(join(tmpdir(), 'conde-sitemap-'));
  for (const subdir of ['', 'stories', 'lab']) {
    const target = join(dir, subdir);
    mkdirSync(target, {recursive: true});
    writeFileSync(join(target, 'index.html'), '<!doctype html><html lang="pt-BR"><body>OK</body></html>');
  }
  writeFileSync(join(dir, 'robots.txt'), 'User-agent: *\nSitemap: ' + BASE + 'sitemap.xml\n');
  return dir;
}
function parsed(dir) {
  return spawnSync('python3', [checker, dir], {encoding: 'utf8'});
}
function expectReject(dir, message) {
  const result = parsed(dir);
  assert.notEqual(result.status, 0, 'Invalid sitemap passed: ' + message);
}
function withFixture(fn) {
  const dir = fixture();
  try { fn(dir); } finally { rmSync(dir, {recursive: true, force: true}); }
}

test('inventories actual SSG and Vite index pages, ordered and unique', () => withFixture(dir => {
  const urls = generateSitemap(dir);
  assert.deepEqual(urls, [BASE, BASE + 'lab/', BASE + 'stories/']);
  const xml = readFileSync(join(dir, 'sitemap.xml'), 'utf8');
  assert.equal((xml.match(/<loc>/g) || []).length, 3);
  const audit = parsed(dir);
  assert.equal(audit.status, 0, audit.stderr);
}));

test('fails closed for empty artifact and a broken robots sitemap URL', () => withFixture(dir => {
  for (const subdir of ['', 'stories', 'lab'])
    unlinkSync(join(dir, subdir, 'index.html'));
  assert.throws(() => generateSitemap(dir), /Sitemap vazio/);
  writeFileSync(join(dir, 'index.html'), '<html lang="pt-BR"></html>');
  writeFileSync(join(dir, 'robots.txt'), 'Sitemap: https://example.com/sitemap.xml');
  assert.throws(() => generateSitemap(dir), /robots.txt/);
}));

test('parser rejects empty, foreign, duplicated and missing-target URLs', () => withFixture(dir => {
  generateSitemap(dir);
  const file = join(dir, 'sitemap.xml');
  const original = readFileSync(file, 'utf8');
  writeFileSync(file, original.replaceAll(/^\s*<url>.*<\/url>\n/gm, ''));
  expectReject(dir, 'empty urlset');
  writeFileSync(file, original.replace(BASE + 'lab/', 'https://example.com/lab/'));
  expectReject(dir, 'foreign host');
  writeFileSync(file, original.replace(BASE + 'lab/', BASE + 'outside/'));
  expectReject(dir, 'missing actual HTML');
  writeFileSync(file, original.replace(BASE + 'lab/', 'https://franklinbaldo.github.io/outside/'));
  expectReject(dir, 'outside repository prefix');
  writeFileSync(file, original.replace('</urlset>', '  <url><loc>' + BASE + 'lab/</loc></url>\n</urlset>'));
  expectReject(dir, 'duplicate URL');
  writeFileSync(file, original);
  unlinkSync(join(dir, 'lab', 'index.html'));
  expectReject(dir, 'deleted destination');
}));
