#!/usr/bin/env node
// Independent review aid. Compares claim text, not merely matching C identifiers.
// Historical branch snapshots are inputs; this does not authenticate events in 1963.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';

function normalized(row) {
  return row.replace(/^\|\s*\*\*C\d{2,3}\*\*\s*\|/, '')
    .replace(/\s*\|\s*/g, ' | ').replace(/\s+/g, ' ').trim();
}

export function collectMatrixClaims(markdown, source) {
  if (!markdown || typeof markdown !== 'string') throw Error('Matriz vazia: '+source);
  const claims = new Map();
  for (const [index, line] of markdown.split(/\r?\n/).entries()) {
    const match = /^\|\s*\*\*(C\d{2,3})\*\*\s*\|/.exec(line);
    if (!match) continue; // Ignore headings/ranges and references within prose.
    const id = match[1];
    const statement = normalized(line);
    if (!statement || statement === '|') throw Error('Afirmação vazia: '+source+' '+id);
    const digest = createHash('sha256').update(statement).digest('hex');
    const item = {id, source, line: index + 1, digest, statement};
    if (claims.has(id) && claims.get(id).digest !== digest) {
      throw Error('ID duplicado com afirmações diferentes dentro de '+source+': '+id);
    }
    claims.set(id, item);
  }
  if (!claims.size) throw Error('Sem linhas de evidência reconhecidas: '+source);
  return [...claims.values()];
}

export function crossBranchConflicts(sources) {
  const indexed = new Map();
  for (const {label, markdown} of sources) {
    for (const item of collectMatrixClaims(markdown, label)) {
      if (!indexed.has(item.id)) indexed.set(item.id, []);
      indexed.get(item.id).push(item);
    }
  }
  return [...indexed.entries()].filter(([, items]) =>
    new Set(items.map(item => item.digest)).size > 1
  ).map(([id, items]) => ({id, items})).sort((a,b) => a.id.localeCompare(b.id));
}

function parseArgs(args) {
  const options = {sources: []};
  for (let i=0;i<args.length;i++) {
    if (args[i] === '--source') {
      const spec = args[++i] || '';
      const n = spec.indexOf('=');
      if (n < 1 || n === spec.length-1) throw Error('Uso: --source label=arquivo.md');
      options.sources.push({label:spec.slice(0,n), file:spec.slice(n+1)});
    } else if (args[i] === '--expect') {
      options.expected = (args[++i] || '').split(',').filter(Boolean).sort();
    } else throw Error('Argumento desconhecido: '+args[i]);
  }
  if (options.sources.length < 2 || !options.expected) {
    throw Error('Requer duas fontes ou mais e --expect IDs (vazio permitido)');
  }
  if (new Set(options.sources.map(s=>s.label)).size !== options.sources.length) {
    throw Error('Rótulos de origem duplicados');
  }
  return options;
}

export function main(args) {
  const options = parseArgs(args);
  const conflicts = crossBranchConflicts(options.sources.map(s => ({
    label:s.label, markdown: readFileSync(s.file, 'utf8')
  })));
  const actual = conflicts.map(c => c.id);
  const ok = JSON.stringify(actual) === JSON.stringify(options.expected);
  console.log(JSON.stringify({
    status:ok?'EXPECTED_COLLISION_CONFIRMED':'UNEXPECTED_COLLISION_SET',
    comparison:'historical branch ledger text only; not primary historical verification',
    actual_ids:actual, expected_ids:options.expected,
    conflicts:conflicts.map(c=>({id:c.id, evidence:c.items.map(x=>({
      source:x.source, source_line:x.line, normalized_sha256:x.digest,
      excerpt:x.statement.slice(0,260)
    }))}))
  }, null, 2));
  if (!ok) process.exitCode=1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try { main(process.argv.slice(2)); } catch(e) {
    console.error(String(e)); process.exitCode=1;
  }
}
