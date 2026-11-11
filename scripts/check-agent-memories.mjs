#!/usr/bin/env node
/**
 * Structural validation of new Conde AgentMemory files. Does not certify facts.
 * Legacy memory notes without YAML frontmatter remain readable.
 */
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, basename } from 'node:path';
import { pathToFileURL } from 'node:url';

export const AGENTS = new Set(['castor', 'coruja', 'elefante', 'gaviao', 'polvo', 'raposa', 'tartaruga', 'texugo']);

function issue(path, message) { return { path, message }; }

export function validateAgentMemory(path, content, agent) {
  const errors = [];
  if (!AGENTS.has(agent)) errors.push(issue(path, 'unknown agent directory'));
  // Historical notes predate the OKF frontmatter requirement. Report but do not rewrite them.
  if (!content.startsWith('---\n')) return { errors, legacy: true };
  const match = /^---\n([\s\S]*?)\n---\n([\s\S]*)$/.exec(content);
  if (!match) return { errors: [...errors, issue(path, 'unterminated frontmatter')], legacy: false };
  const fields = {};
  for (const line of match[1].split('\n')) {
    const parsed = /^([a-z_]+):\s*(.+)$/.exec(line);
    if (!parsed || Object.hasOwn(fields, parsed[1])) {
      errors.push(issue(path, 'invalid or repeated metadata line: ' + line));
      continue;
    }
    fields[parsed[1]] = parsed[2].replace(/^["']|["']$/g, '').trim();
  }
  if (fields.type !== 'AgentMemory') errors.push(issue(path, 'type must be AgentMemory'));
  if (fields.agent !== agent) errors.push(issue(path, 'agent must match its directory'));
  for (const field of ['title', 'description']) {
    if (!fields[field] || fields[field].length < 5) errors.push(issue(path, field + ' must describe the memory'));
  }
  const stamp = fields.timestamp;
  if (!stamp || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(stamp) ||
      Number.isNaN(Date.parse(stamp)) || new Date(stamp).toISOString().replace('.000Z', 'Z') !== stamp) {
    errors.push(issue(path, 'timestamp must be a valid UTC ISO second'));
  } else {
    const prefix = stamp.replace(/[-:]/g, '').replace('T', 'T');
    if (!basename(path).startsWith(prefix + '-')) {
      errors.push(issue(path, 'filename must begin with timestamp YYYYMMDDTHHMMSSZ-'));
    }
  }
  if (!/^\[[^\]]+\]$/.test(fields.tags || '')) errors.push(issue(path, 'tags must be a nonempty inline list'));
  if (!match[2].trim()) errors.push(issue(path, 'memory must have a body'));
  return { errors, legacy: false };
}

export function scanAgentMemories(root) {
  const results = [];
  for (const agent of readdirSync(root)) {
    const dir = join(root, agent);
    if (!statSync(dir).isDirectory()) continue;
    for (const entry of readdirSync(dir)) {
      if (!entry.endsWith('.md')) continue;
      const path = join(dir, entry);
      results.push({ ...validateAgentMemory(path, readFileSync(path, 'utf8'), agent), path });
    }
  }
  return results;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const root = process.argv[2] || 'team/memory';
  try {
    const results = scanAgentMemories(root);
    const errors = results.flatMap(r => r.errors);
    console.log(JSON.stringify({
      checked: results.length,
      structured: results.filter(r => !r.legacy).length,
      legacy: results.filter(r => r.legacy).map(r => r.path),
      errors,
      status: errors.length ? 'FAIL' : 'PASS',
    }, null, 2));
    if (errors.length) process.exitCode = 1;
  } catch (error) {
    console.error('Memory scan failed:', String(error));
    process.exitCode = 1;
  }
}
