/** Synthetic tamper tests. These check metadata consistency, not live PDF retrieval. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {verifiedArchiveLinks} from '../scripts/ssg-wayback-links.mjs';

const graph = JSON.parse(readFileSync('public/data/conde-wayback-citation-links.json', 'utf8'));
const citations = JSON.parse(readFileSync('public/data/conde-source-citations.json', 'utf8'));
const clone = object => structuredClone(object);
const capture = object => object.nodes.find(node =>
  node.kind === 'VERIFIED_ARCHIVAL_COPY' && node.id.includes('LEGACY-CAPTURE:20150217133001'));

test('original captured NASA PDF is linked to both frozen matrix citations', () => {
  const links = verifiedArchiveLinks(graph, citations);
  assert.equal(links.size, 2);
  assert.equal(links.values().next().value.count, 3);
});

test('Wayback link cannot silently point to a different archival PDF', () => {
  const forged = clone(graph);
  capture(forged).archived_url = 'https://web.archive.org/web/20150217133001id_/https://example.com/unrelated.pdf';
  assert.throws(() => verifiedArchiveLinks(forged, citations), /URL arquivada divergente/);
});

test('even a matching CDX entry cannot move the PDF to an uncurated source', () => {
  const forged = clone(graph);
  const node = capture(forged);
  node.archived_url = 'https://web.archive.org/web/20150217133001id_/https://example.com/19640001198.pdf';
  node.cdx_original_url = 'https://example.com/19640001198.pdf';
  assert.throws(() => verifiedArchiveLinks(forged, citations), /Host arquivado/);
});

test('capture date must agree with the Wayback permalink timestamp', () => {
  const forged = clone(graph);
  capture(forged).capture_utc = '2015-02-18T13:30:01Z';
  assert.throws(() => verifiedArchiveLinks(forged, citations), /Data Wayback divergente/);
});

test('same declared SHA does not permit a contradictory byte length', () => {
  const forged = clone(graph);
  capture(forged).retrieved_bytes_length = 17;
  assert.throws(() => verifiedArchiveLinks(forged, citations), /Tamanho Wayback divergente/);
});

test('duplicate custody edge cannot inflate the reported capture count', () => {
  const forged = clone(graph);
  const edge = forged.edges.find(item => item.kind === 'SAME_BYTES_NOT_INDEPENDENT_ARCHIVAL_WITNESS');
  forged.edges.push(clone(edge));
  assert.throws(() => verifiedArchiveLinks(forged, citations), /Captura Wayback duplicada/);
});

// G36: same NASA host and PDF basename are insufficient to bind a capture.
test('same host and filename cannot silently substitute a different archived route', () => {
  const forged = clone(graph);
  const node = capture(forged);
  node.cdx_original_url = 'http://ntrs.nasa.gov/unrelated/19640001198.pdf';
  node.archived_url = 'https://web.archive.org/web/20150217133001id_/' + node.cdx_original_url;
  assert.throws(() => verifiedArchiveLinks(forged, citations), /Caminho completo do PDF Wayback/);
});

test('an extra query parameter cannot silently change the archived document', () => {
  const forged = clone(graph);
  const node = capture(forged);
  node.cdx_original_url += '?version=unverified';
  node.archived_url = 'https://web.archive.org/web/20150217133001id_/' + node.cdx_original_url;
  assert.throws(() => verifiedArchiveLinks(forged, citations), /Consulta da URL arquivada/);
});
