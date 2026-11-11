import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { parseStoryBlocks, tokenizeStoryInline } from '../src/lib/storyMarkdown.ts';

test('real chapter remains readable with headings, sources and editorial note', () => {
  const raw = readFileSync(new URL('../stories/2026-11-11-o-dia-em-que-dois-relatos-se-cruzaram.md', import.meta.url), 'utf8');
  const blocks = parseStoryBlocks(raw.split(/^---\s*$/m).slice(2).join('---'));
  assert.ok(blocks.some(block => block.kind === 'heading' && block.text.includes('Primeira pista')));
  assert.ok(blocks.some(block => block.kind === 'paragraph' && block.text.includes('Fonte primária:')));
  assert.equal(blocks.at(-2)?.kind, 'rule');
  assert.equal(blocks.at(-1)?.kind, 'paragraph');
});

test('structural Markdown keeps lists, quote, ordered numbering and fenced newlines', () => {
  const blocks = parseStoryBlocks(
    '# Título\n\n> Fonte A\n> Fonte B\n\n- Um\n- Dois\n\n3. Terceiro\n4. Quarto\n\n~~~txt\nx\n  y\n~~~\n\nFim.'
  );
  assert.deepEqual(blocks, [
    { kind: 'heading', level: 1, text: 'Título' },
    { kind: 'quote', text: 'Fonte A Fonte B' },
    { kind: 'list', ordered: false, start: 1, items: ['Um', 'Dois'] },
    { kind: 'list', ordered: true, start: 3, items: ['Terceiro', 'Quarto'] },
    { kind: 'code', text: 'x\n  y' },
    { kind: 'paragraph', text: 'Fim.' },
  ]);
});

test('safe inline source links preserve URL parentheses and distinct typography', () => {
  assert.deepEqual(tokenizeStoryInline('**Original** e [arquivo](https://example.org/doc_(1963).pdf) *incerto*'), [
    { kind: 'strong', text: 'Original' },
    { kind: 'text', text: ' e ' },
    { kind: 'link', text: 'arquivo', href: 'https://example.org/doc_(1963).pdf' },
    { kind: 'text', text: ' ' },
    { kind: 'em', text: 'incerto' },
  ]);
});

test('dangerous links and raw HTML are rendered as literal text, never as a link token', () => {
  const input = '[abrir](javascript:alert(1)) <script>alert(1)</script>';
  assert.deepEqual(tokenizeStoryInline(input), [{ kind: 'text', text: input }]);
});
