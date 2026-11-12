import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { archiveEntries, matrixSnapshot } from '../src/lib/documentCatalog.ts';
import { documentRecordFromHash, hashForDocumentRecord, resolveLabHash } from '../src/lib/labRoutes.ts';

const source = readFileSync(new URL('../src/components/DocumentArchive.tsx', import.meta.url), 'utf8');

test('archival records have unique stable links and explicit provenance and limits', () => {
  assert.equal(archiveEntries.length, 8);
  assert.equal(new Set(archiveEntries.map(x => x.id)).size, archiveEntries.length);
  for (const item of archiveEntries) {
    assert.ok(item.matrixUrl.startsWith(matrixSnapshot + '#L'), item.id);
    assert.match(item.originalUrl, /^https:\/\/(ntrs\.nasa\.gov|media\.ondisclosure\.org|github\.com|www\.nro\.gov|www\.ighb\.org\.br)\//);
    assert.ok(item.matrixIds.length > 1 && item.provenance.pt.length > 20 && item.provenance.en.length > 20, item.id);
    assert.ok(item.limitation.pt.length > 20 && item.limitation.en.length > 20, item.id);
    assert.ok(item.evidenceHref.startsWith('#/research'), item.id);
    assert.equal(documentRecordFromHash(hashForDocumentRecord(item.id)), item.id);
    assert.equal(resolveLabHash(hashForDocumentRecord(item.id)), 'documents');
  }
});

test('unknown document routes are rejected without silently substituting records', () => {
  assert.equal(documentRecordFromHash('#/documents/doc-99'), null);
  assert.equal(resolveLabHash('#/documents/doc-99'), null);
  assert.equal(documentRecordFromHash('#/documents/doc-01/'), 'doc-01');
  assert.equal(resolveLabHash('#/documents'), 'documents');
  assert.throws(() => hashForDocumentRecord('doc-99'), /desconhecido/);
});

test('NASA original is contemporary and its day is not dismissed as retrospective', () => {
  const nasa = archiveEntries.find(x => x.id === 'doc-01');
  assert.equal(nasa.kind, 'contemporary');
  assert.match(nasa.finding.pt, /DECAYED OBJECTS/);
  assert.match(nasa.finding.pt, /8\/11\/1963/);
  assert.match(nasa.limitation.pt, /sem hora, coordenadas/);
  assert.match(nasa.provenance.pt, /mesmo documento/);
  assert.ok(nasa.matrixIds.includes('C197'));
});

test('diplomatic documents are not invented literal quotes or independent impact observations', () => {
  for (const id of ['doc-02', 'doc-03', 'doc-04']) {
    const doc = archiveEntries.find(x => x.id === id);
    assert.equal(doc.kind, 'contemporary');
    assert.match(doc.limitation.pt, /não|sem|Não/);
  }
  assert.match(archiveEntries.find(x => x.id === 'doc-03').provenance.pt, /não estão anexados/);
  assert.match(archiveEntries.find(x => x.id === 'doc-04').provenance.pt, /não três testemunhas/);
  for (const prohibited of [
    /The Aircraft That Wasn't There/,
    /entirely groundless/,
    /pressurized suit alleged inside/,
    /First confidential communication/,
    /BSTAR = 0.*manual tracking/,
  ]) {
    assert.doesNotMatch(source + JSON.stringify(archiveEntries), prohibited);
  }
});

test('pending newspaper clippings stay locators, NRO remains retrospective, TLE custody unresolved', () => {
  assert.deepEqual(archiveEntries.slice(-2).map(x => x.kind), ['locator', 'locator']);
  assert.equal(archiveEntries.find(x => x.id === 'doc-06').kind, 'derived');
  assert.match(archiveEntries.find(x => x.id === 'doc-06').provenance.pt, /1994/);
  assert.match(archiveEntries.find(x => x.id === 'doc-05').limitation.pt, /Checksum válido não autentica/);
  assert.match(archiveEntries.find(x => x.id === 'doc-07').limitation.pt, /recorte ausente/);
});

test('archive supports keyboard, mobile, filtered empty state and per-document Evidence links', () => {
  for (const snippet of ['htmlFor="archive-search"', 'htmlFor="archive-filter"', 'type="search"',
    'aria-live="polite"', 'role="status"', 'scroll-mt-44', 'sm:grid-cols-2',
    'hashForDocumentRecord(entry.id)', 'documentRecordFromHash(window.location.hash)',
    'window.addEventListener', 'focus({ preventScroll: true })', 'entry.evidenceHref',
    'entry.matrixUrl', 'entry.originalUrl', 'text-amber-200']) {
    assert.ok(source.includes(snippet), snippet);
  }
  assert.doesNotMatch(source, /Trecho Documental Original|Original Document Excerpt|transcriptExcerpt/);
});
