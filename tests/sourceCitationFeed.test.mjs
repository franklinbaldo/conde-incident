import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { citationContext, isCitationFeed, normalizeOccurrence, matrixOccurrenceUrl } from '../src/lib/sourceCitationAudit.ts';

const feed = JSON.parse(readFileSync(new URL('../public/data/conde-source-citations.json', import.meta.url), 'utf8'));
const component = readFileSync(new URL('../src/components/SourceCitationFeed.tsx', import.meta.url), 'utf8');
const archive = readFileSync(new URL('../src/components/DocumentArchive.tsx', import.meta.url), 'utf8');

test('strict occurrence IDs and matrix collision handling', () => {
  assert.equal(normalizeOccurrence(' c197#1 '), 'C197#1');
  assert.equal(normalizeOccurrence('C44'), null);
  assert.equal(normalizeOccurrence('C197'), null);
  assert.equal(normalizeOccurrence('C44#2'), 'C44#2');
  assert.equal(normalizeOccurrence('C197#0'), null);
  assert.equal(citationContext(feed, 'C44#1').state, 'unmapped');
  assert.equal(citationContext(feed, 'C197').state, 'invalid');
});

test('curated feed is current and does not invent additional witnesses', () => {
  assert.equal(isCitationFeed(feed), true);
  assert.equal(feed.curated_occurrences + feed.unmapped_occurrences, feed.total_matrix_occurrences);
  const nasa = citationContext(feed, 'C197#1');
  const ntrs = citationContext(feed, 'C198#1');
  assert.equal(nasa.state, 'mapped');
  assert.equal(ntrs.state, 'mapped');
  assert.equal(nasa.record.work_id, ntrs.record.work_id);
  assert.equal(nasa.record.source_family, ntrs.record.source_family);
  assert.ok(nasa.sameWork.some((x) => x.occurrence === 'C198#1'));
  assert.equal(nasa.record.scope, 'CATALOGUED_DAY_ONLY');
  assert.equal(nasa.record.not_a_verified_conde_physical_event, true);
  const tupi = ['C01#1', 'C02#1', 'C03#1'].map((id) => citationContext(feed, id));
  assert.ok(tupi.every((x) => x.state === 'mapped'));
  assert.equal(new Set(tupi.map((x) => x.record.work_id)).size, 1);
  assert.ok(tupi.every((x) => x.record.not_a_verified_conde_physical_event));
});

test('UI exposes provenance, real source links, accessibility and partial-coverage warning', () => {
  assert.match(component, /aria-live="polite"/);
  assert.match(component, /aria-pressed=\{selected === id\}/);
  assert.match(component, /htmlFor="citation-occurrence"/);
  assert.match(component, /BASE_URL/);
  assert.match(component, /UNMAPPED/);
  assert.match(component, /sameWork\.length/);
  assert.match(component, /rel="noopener noreferrer"/);
  assert.match(component, /not independent witnesses|não são testemunhos independentes/);
  assert.match(archive, /<SourceCitationFeed lang=\{lang\} \/>/);
  assert.ok(matrixOccurrenceUrl(901).endsWith('#L901'));
  assert.equal(matrixOccurrenceUrl(901), 'https://github.com/franklinbaldo/conde-incident/blob/faf4dd0fd8dfbdd825e4e934b3b30ebd81bf61df/research/evidence_matrix_C001-C238_2026-11-11.md#L901');
  assert.ok(!matrixOccurrenceUrl(901).includes('/blob/main/'));
  assert.equal(feed.matrix_git_blob_sha1, 'a7978c3a75a153b16ab70118a92c434bba674cb7');
  assert.equal(isCitationFeed({ schema: 'unknown', records: [] }), false);
});
