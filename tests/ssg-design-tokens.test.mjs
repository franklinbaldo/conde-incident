import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = path => readFileSync(path, 'utf8');
const tokens = read('static/css/tokens.css');
const site = read('static/css/site.css');
const shell = read('templates/shell.html');
const colors = Object.fromEntries(
  [...tokens.matchAll(/(--color-[\w-]+):\s*(#[0-9a-fA-F]{6});/g)]
    .map(([, key, value]) => [key, value])
);
const rgb = hex => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255)
  .map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
const luminance = hex => rgb(hex).reduce((sum, v, i) =>
  sum + v * [.2126, .7152, .0722][i], 0);
const contrast = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + .05) / (lo + .05);
};
const themeLink = '/conde-incident/css/tokens.css';
const siteLink = '/conde-incident/css/site.css';
const assertThemeOrder = html => {
  const tokenAt = html.indexOf('href="' + themeLink + '"');
  const siteAt = html.indexOf('href="' + siteLink + '"');
  assert.ok(tokenAt >= 0 && siteAt > tokenAt,
    'theme must load before editorial CSS');
};

test('SSG theme tokens are a single, static theme loaded before editorial CSS', () => {
  assertThemeOrder(shell);
  assert.doesNotMatch(site, /^:root\{/);
  for (const name of ['page', 'surface', 'text', 'subtle-text', 'border', 'link', 'focus']) {
    assert.ok(colors['--color-' + name], 'missing design token: ' + name);
  }
  for (const legacy of ['paper', 'panel', 'ink', 'muted', 'line', 'accent']) {
    assert.ok(tokens.includes('--' + legacy + ': var(--color-'),
      'missing compatibility variable: ' + legacy);
    assert.ok(site.includes('var(--' + legacy + ')'),
      'site lost compatibility variable: ' + legacy);
  }
  assert.ok(tokens.includes('--font-reading: Georgia, serif;'));
  assert.ok(tokens.includes('--measure-reading: 760px;'));
});

test('WCAG AA contrast: foreground, secondary text and links at least 4.5:1', () => {
  for (const name of ['text', 'subtle-text', 'link']) {
    assert.ok(contrast(colors['--color-' + name], colors['--color-page']) >= 4.5,
      'low contrast for ' + name);
  }
  assert.ok(contrast(colors['--color-focus'], colors['--color-page']) >= 3);
});

test('negative test: an unsafe foreground cannot pass contrast threshold', () => {
  assert.ok(contrast('#333333', '#11141b') < 4.5);
});

if (process.argv.includes('--built-site')) {
  test('built Pages HTML and assets contain the exact static CSS tokens', () => {
    assertThemeOrder(read('public/index.html'));
    assert.equal(read('public/css/tokens.css'), tokens);
    assert.equal(read('public/css/site.css'), site);
  });
}
