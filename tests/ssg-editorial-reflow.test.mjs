import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const css = readFileSync('static/css/site.css', 'utf8');
const template = readFileSync('templates/tera/page.html', 'utf8');

test('capas editoriais são fluidas, sem largura fixa de 1200px', () => {
  assert.match(template, /class="editorial-cover"/);
  assert.match(css, /\.full-story \.editorial-cover\s*\{[^}]*width:\s*100%/);
  assert.match(css, /\.full-story \.editorial-cover\s*\{[^}]*max-width:\s*100%/);
  assert.match(css, /\.full-story \.editorial-cover\s*\{[^}]*height:\s*auto/);
});

test('subtítulos de família quebram identificadores sem espaços', () => {
  assert.match(template, /class="deck"/);
  assert.match(css, /\.full-story \.deck\s*\{[^}]*overflow-wrap:\s*anywhere/);
});
