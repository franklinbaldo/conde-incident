import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { renderShell, checkOrWrite } from '../scripts/ssg-shell-sync.mjs';

const shell = readFileSync('templates/shell.html', 'utf8');
const links = readFileSync('templates/components/nav-links.html', 'utf8');

test('SSG 0.0.75 uses one authored shell and a shared navigation partial', () => {
  assert.equal(checkOrWrite({ check: true }), 4);
  const html = renderShell(shell, links);
  assert.equal((html.match(/<details class="mobile-navigation">/g) ?? []).length, 1);
  assert.equal((html.match(/<nav aria-label="Navegação principal">/g) ?? []).length, 2);
  assert.equal((html.match(/href="\/conde-incident\/lab\/"/g) ?? []).length, 2);
  assert.doesNotMatch(html, /{% include/);
  assert.match(html, /<main id="main" class="wrap" tabindex="-1">/);
});

test('negative: a missing include or duplicated destination fails closed', () => {
  assert.throws(() => renderShell(shell.replace('{% include "components/nav-links.html" %}', ''), links),
    /exactly two landmarks/);
  assert.throws(() => renderShell(shell, links.replace(
    'href="/conde-incident/cronologia/"', 'href="/conde-incident/stories/"')),
  /unique/);
});
