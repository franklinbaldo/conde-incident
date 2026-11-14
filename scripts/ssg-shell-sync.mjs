import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const ENTRYPOINTS = ['index', 'page', 'post', 'template']
  .map(name => 'templates/' + name + '.html');
const PARTIAL = '{% include "components/nav-links.html" %}';

export function renderShell(shell, navigation) {
  assert.equal(shell.split(PARTIAL).length - 1, 2,
    'one navigation partial must be reused in exactly two landmarks');
  assert.doesNotMatch(shell.replaceAll(PARTIAL, ''), /{%[\s\S]*?%}/,
    'unsupported SSG 0.0.75 template directive');
  const links = [...navigation.matchAll(/<a href="([^"]+)">([^<]+)<\/a>/g)];
  assert.equal(links.length, 9, 'expected exactly nine navigation items');
  assert.equal(new Set(links.map(m => m[1])).size, 9,
    'navigation paths must be unique');
  for (const [, href, label] of links) {
    assert.match(href, /^\/conde-incident\/(?:[\w-]+\/)?$/);
    assert.ok(label.trim(), 'every navigation item needs a label');
  }
  const output = shell.replaceAll(PARTIAL, navigation);
  assert.equal((output.match(/<nav aria-label="Navegação principal">/g) ?? []).length, 2);
  return output;
}

export function checkOrWrite({ check = true } = {}) {
  const shell = readFileSync('templates/shell.html', 'utf8');
  const navigation = readFileSync('templates/components/nav-links.html', 'utf8');
  const output = renderShell(shell, navigation);
  for (const file of ENTRYPOINTS) {
    if (check) {
      assert.equal(readFileSync(file, 'utf8'), output,
        file + ' has drifted from canonical SSG shell');
    } else {
      writeFileSync(file, output);
    }
  }
  return ENTRYPOINTS.length;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const check = process.argv.includes('--check');
  if (process.argv.length > 3 || (process.argv.length === 3 && !check)) {
    throw new Error('Usage: node scripts/ssg-shell-sync.mjs [--check]');
  }
  const count = checkOrWrite({ check });
  process.stdout.write((check ? 'CHECK ' : 'GENERATED ') + count + ' SSG templates\n');
}
