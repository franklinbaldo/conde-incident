/**
 * Deliberately limited Markdown grammar for the Caderno's authored prose.
 * No raw HTML is interpreted. React renders all text as escaped nodes.
 * Unsupported constructs remain visible as ordinary text.
 */
export type StoryBlock =
  | { kind: 'heading'; level: 1 | 2 | 3; text: string }
  | { kind: 'paragraph' | 'quote'; text: string }
  | { kind: 'list'; ordered: boolean; start: number; items: string[] }
  | { kind: 'code'; text: string }
  | { kind: 'rule' };

export type InlinePart =
  | { kind: 'text' | 'strong' | 'em' | 'code'; text: string }
  | { kind: 'link'; text: string; href: string };

const heading = /^ {0,3}(#{1,3})\s+(.+?)\s*#*\s*$/;
const rule = /^ {0,3}(?:-{3,}|\*{3,}|_{3,})\s*$/;
const quote = /^ {0,3}>\s?(.*)$/;
const listItem = /^ {0,3}([-+*]|\d+[.)])\s+(.+)$/;
const fence = /^ {0,3}(\x60{3,}|~{3,})(.*)$/;

function startsBlock(line: string): boolean {
  return heading.test(line) || rule.test(line) || quote.test(line) ||
    listItem.test(line) || fence.test(line);
}

/** Parse blocks without collapsing newlines inside a code fence or list. */
export function parseStoryBlocks(markdown: string): StoryBlock[] {
  const lines = markdown.replace(/\r\n?/g, '\n').split('\n');
  const blocks: StoryBlock[] = [];
  let i = 0;

  while (i < lines.length) {
    if (!lines[i].trim()) { i++; continue; }
    const line = lines[i];
    const code = fence.exec(line);
    if (code) {
      const marker = code[1];
      const text: string[] = [];
      i++;
      while (i < lines.length) {
        const closing = /^ {0,3}(\x60{3,}|~{3,})\s*$/.exec(lines[i]);
        if (closing && closing[1][0] === marker[0] &&
            closing[1].length >= marker.length) { i++; break; }
        text.push(lines[i++]);
      }
      blocks.push({ kind: 'code', text: text.join('\n') });
      continue;
    }

    const h = heading.exec(line);
    if (h) {
      blocks.push({ kind: 'heading', level: h[1].length as 1 | 2 | 3, text: h[2] });
      i++;
      continue;
    }
    if (rule.test(line)) {
      blocks.push({ kind: 'rule' });
      i++;
      continue;
    }

    if (quote.test(line)) {
      const text: string[] = [];
      while (i < lines.length) {
        const q = quote.exec(lines[i]);
        if (!q) break;
        text.push(q[1]);
        i++;
      }
      blocks.push({ kind: 'quote', text: text.join(' ').trim() });
      continue;
    }

    const firstItem = listItem.exec(line);
    if (firstItem) {
      const ordered = /^\d/.test(firstItem[1]);
      const start = ordered ? Number.parseInt(firstItem[1], 10) : 1;
      const items: string[] = [];
      while (i < lines.length) {
        const item = listItem.exec(lines[i]);
        if (!item || /^\d/.test(item[1]) !== ordered) break;
        items.push(item[2]);
        i++;
      }
      blocks.push({ kind: 'list', ordered, start, items });
      continue;
    }

    const text: string[] = [];
    while (i < lines.length && lines[i].trim() &&
           (!text.length || !startsBlock(lines[i]))) {
      text.push(lines[i++].trim());
    }
    blocks.push({ kind: 'paragraph', text: text.join(' ') });
  }
  return blocks;
}

function validExternalUrl(href: string): boolean {
  try {
    const url = new URL(href);
    return url.protocol === 'https:' || url.protocol === 'http:';
  } catch {
    return false;
  }
}

/**
 * A small safe inline grammar: links, strong, emphasis, code.
 * Link URLs support balanced parentheses (common in archive URLs).
 * Unsupported syntax, HTML and dangerous schemes stay literal text.
 */
export function tokenizeStoryInline(input: string): InlinePart[] {
  const parts: InlinePart[] = [];
  let plain = '';
  let i = 0;
  const flush = () => {
    if (plain) { parts.push({ kind: 'text', text: plain }); plain = ''; }
  };
  const tick = String.fromCharCode(96);

  while (i < input.length) {
    if (input[i] === '[') {
      const labelEnd = input.indexOf('](', i + 1);
      if (labelEnd > i + 1 && !input.slice(i + 1, labelEnd).includes('[')) {
        let cursor = labelEnd + 2, depth = 0;
        while (cursor < input.length) {
          const c = input[cursor];
          if (/\s/.test(c)) break;
          if (c === '(') depth++;
          if (c === ')') {
            if (depth === 0) break;
            depth--;
          }
          cursor++;
        }
        if (input[cursor] === ')' && depth === 0) {
          const href = input.slice(labelEnd + 2, cursor);
          if (validExternalUrl(href)) {
            flush();
            parts.push({ kind: 'link', text: input.slice(i + 1, labelEnd), href });
            i = cursor + 1;
            continue;
          }
        }
      }
    }
    const strong = input.startsWith('**', i);
    const mark = strong ? '**' : input[i] === '*' ? '*' : input[i] === tick ? tick : null;
    if (mark) {
      const end = input.indexOf(mark, i + mark.length);
      if (end > i + mark.length) {
        flush();
        parts.push({ kind: strong ? 'strong' : mark === tick ? 'code' : 'em',
          text: input.slice(i + mark.length, end) });
        i = end + mark.length;
        continue;
      }
    }
    plain += input[i++];
  }
  flush();
  return parts;
}
