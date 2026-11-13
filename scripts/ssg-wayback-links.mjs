/**
 * Narrow, fail-closed join from frozen matrix citation to archived PDF bytes.
 * A modern archival copy is never an additional historical observation.
 */
import assert from 'node:assert/strict';

const https = url => typeof url === 'string' && /^https:\/\/[^\s<>"'()]+$/u.test(url);
const key = (snapshot, source) => JSON.stringify([snapshot, source]);
const sha256 = value => /^[a-f0-9]{64}$/.test(value ?? '');
const utc = value => /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value ?? '') &&
  !Number.isNaN(Date.parse(value)) && new Date(value).toISOString().replace('.000Z','Z') === value;

export function verifiedArchiveLinks(graph, citations) {
  assert.equal(graph.schema, 'conde.wayback-citation-links/v1');
  assert.equal(graph.matrix_git_blob_sha1, citations.matrix_git_blob_sha1,
    'Wayback deve apontar para o snapshot exato da matriz');
  assert.equal(graph.counts?.independent_physical_observations_added, 0);
  assert.ok(Array.isArray(graph.nodes) && Array.isArray(graph.edges));
  const nodes = new Map();
  for (const node of graph.nodes) {
    assert.ok(typeof node.id === 'string' && !nodes.has(node.id), 'Nó Wayback duplicado');
    nodes.set(node.id, node);
  }
  for (const edge of graph.edges) {
    assert.ok(nodes.has(edge.from) && nodes.has(edge.to), 'Aresta Wayback órfã');
  }
  const citationsByKey = new Map(citations.records.map(record =>
    [key(record.snapshot_ref,record.source_id), record]));
  const archived = new Map();
  for (const frozen of graph.nodes.filter(n => n.kind === 'FROZEN_MATRIX_CITATION')) {
    const record = citationsByKey.get(key(frozen.snapshot_ref, frozen.source_id));
    assert.ok(record, 'Referência Wayback sem citação curada');
    assert.equal(frozen.row_sha256, record.row_sha256, 'Linha da matriz Wayback divergente');
    assert.equal(frozen.matrix_line, record.matrix_line);
    assert.equal(frozen.activation, false);
    assert.equal(frozen.simulator_value, null);
    assert.equal(frozen.new_physical_observations, 0);
    const edges = graph.edges.filter(e => e.to === frozen.id &&
      e.kind === 'DOC_SOURCE_TO_SNAPSHOT_CITATION');
    assert.equal(edges.length, 1, 'Citação Wayback requer exatamente uma obra de origem');
    const source = nodes.get(edges[0].from);
    assert.equal(source.kind, 'DOCUMENTARY_SOURCE');
    assert.equal(source.new_physical_observations, 0);
    assert.ok(source.source_refs.includes(record.occurrence));
    assert.ok(https(source.original_url), 'URL original documental insegura');
    assert.ok(citations.records.some(r =>
      r.work_id === record.work_id && r.citation_url === source.original_url),
    'Cópia não corresponde à obra da matriz');
    const payloadEdges = graph.edges.filter(e => e.to === source.id &&
      e.kind === 'SAME_SSR_WORK_NOT_NEW_INSTRUMENT');
    assert.equal(payloadEdges.length, 1, 'Obra requer um único payload PDF preservado');
    const payload = nodes.get(payloadEdges[0].from);
    assert.equal(payload.kind, 'ONE_ARCHIVED_DOCUMENT_PAYLOAD');
    assert.ok(sha256(payload.sha256), 'SHA-256 do PDF inválido');
    assert.equal(payload.distinct_documentary_payload_count, 1);
    const captures = graph.edges.filter(e => e.to === payload.id &&
      e.kind === 'SAME_BYTES_NOT_INDEPENDENT_ARCHIVAL_WITNESS')
      .map(e => nodes.get(e.from));
    assert.ok(captures.length > 0, 'Sem replay verificado da obra');
    for (const c of captures) {
      assert.equal(c.kind, 'VERIFIED_ARCHIVAL_COPY');
      assert.equal(c.new_physical_observations, 0);
      assert.ok(utc(c.capture_utc), 'Data UTC de captura inválida');
      assert.ok(https(c.archived_url) && c.archived_url.startsWith('https://web.archive.org/web/'),
        'Somente URL Wayback verificada no grafo');
      assert.equal(c.retrieved_bytes_sha256, payload.sha256, 'Bytes Wayback divergentes');
      assert.ok(Number.isSafeInteger(c.retrieved_bytes_length) && c.retrieved_bytes_length > 0);
    }
    captures.sort((a,b)=>a.capture_utc.localeCompare(b.capture_utc));
    assert.ok(!archived.has(key(record.snapshot_ref,record.source_id)), 'Ligação Wayback duplicada');
    archived.set(key(record.snapshot_ref,record.source_id), {
      url: captures[0].archived_url, utc: captures[0].capture_utc,
      sha256: payload.sha256, count: captures.length,
    });
  }
  return archived;
}
export const archiveKey = key;
