import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = file => readFileSync(file, 'utf8');
const tokens = read('static/css/tokens.css');
const stylesheet = read('static/css/site.css');
const palette = Object.fromEntries(
  [...tokens.matchAll(/(--color-casefile-[\w-]+):\s*(#[0-9a-fA-F]{6});/g)]
    .map(([, name, value]) => [name, value])
);
const linear = component => {
  const x = parseInt(component, 16) / 255;
  return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
};
const luminance = color => {
  const rgb = [color.slice(1, 3), color.slice(3, 5), color.slice(5, 7)];
  return rgb.map(linear).reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
};
const contrast = (first, second) => {
  const values = [luminance(first), luminance(second)].sort((a, b) => b - a);
  return (values[0] + .05) / (values[1] + .05);
};
const alias = {
  paper: 'paper', surface: 'surface', ink: 'ink', muted: 'muted',
  line: 'line', accent: 'accent', warm: 'warm', focus: 'focus'
};
const required = [
  'paper', 'surface', 'ink', 'muted', 'line', 'accent',
  'warm', 'focus', 'status', 'hover', 'highlight', 'button-text'
];
const casefile = stylesheet.split('/* Dossiê SSG v1:')[1]?.split('/* SSG-first print mode:')[0];

test('SSG dossier has one versioned light palette, no independent CSS hex overrides', () => {
  assert.ok(casefile, 'casefile block not found');
  for (const name of required) {
    assert.ok(palette['--color-casefile-' + name], 'missing ' + name + ' color token');
  }
  for (const [component, token] of Object.entries(alias)) {
    assert.ok(casefile.includes('--cf-' + component + ':var(--color-casefile-' + token + ')'),
      'legacy component variable must alias the shared design token: ' + component);
  }
  for (const name of ['status', 'hover', 'highlight', 'button-text']) {
    assert.ok(casefile.includes('var(--color-casefile-' + name + ')'),
      'casefile does not consume theme token ' + name);
  }
  assert.doesNotMatch(casefile, /#[0-9a-fA-F]{3,8}\b/,
    'color literals must be maintained in tokens.css instead of local CSS');
  assert.ok(stylesheet.startsWith('@import url("./tokens.css");'),
    'CSS tokens must be loaded before the casefile');
});

test('light dossier text, action button and focus contrast pass explicit thresholds', () => {
  const value = name => palette['--color-casefile-' + name];
  const examples = [
    ['ink', 'paper', 4.5], ['ink', 'surface', 4.5],
    ['muted', 'surface', 4.5], ['accent', 'surface', 4.5],
    ['warm', 'paper', 4.5], ['button-text', 'accent', 4.5],
    ['button-text', 'hover', 4.5], ['focus', 'paper', 3],
    ['ink', 'status', 4.5], ['ink', 'highlight', 4.5]
  ];
  for (const [text, background, minimum] of examples) {
    assert.ok(contrast(value(text), value(background)) >= minimum,
      text + ' against ' + background + ' must reach ' + minimum + ':1');
  }
});

test('negative: a substituted low-contrast light theme fails the same rule', () => {
  assert.ok(contrast('#dddccc', palette['--color-casefile-paper']) < 4.5);
});

if (process.argv.includes('--built-site')) {
  test('Pages artifact exports the exact light design palette and consumer CSS', () => {
    assert.equal(read('public/css/tokens.css'), tokens);
    assert.equal(read('public/css/site.css'), stylesheet);
    assert.match(read('public/dossie/index.html'), /class="casefile"/);
  });
}
