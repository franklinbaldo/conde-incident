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
    const seenCaptures = new Set();
    for (const c of captures) {
      assert.ok(!seenCaptures.has(c.id), 'Captura Wayback duplicada');
      seenCaptures.add(c.id);
      assert.equal(c.kind, 'VERIFIED_ARCHIVAL_COPY');
      assert.equal(c.new_physical_observations, 0);
      assert.ok(utc(c.capture_utc), 'Data UTC de captura inválida');
      assert.ok(https(c.archived_url) && c.archived_url.startsWith('https://web.archive.org/web/'),
        'Somente URL Wayback verificada no grafo');
      // The archived permalink, CDX origin, UTC time, and frozen source must
      // describe the *same* capture. A plausible Wayback URL alone is not proof.
      const match = /^https:\/\/web\.archive\.org\/web\/(\d{14})id_\/(https?:\/\/[^\s<>"'()]+)$/u.exec(c.archived_url);
      assert.ok(match, 'Formato da captura Wayback divergente');
      assert.equal(match[1], c.capture_utc.replace(/[-:TZ]/gu, ''),
        'Data Wayback divergente da captura CDX');
      assert.equal(match[2], c.cdx_original_url, 'URL arquivada divergente da origem CDX');
      const sourceUrl = new URL(source.original_url);
      const archivedOrigin = new URL(match[2]);
      assert.equal(archivedOrigin.hostname, sourceUrl.hostname,
        'Host arquivado não corresponde à fonte curada');
      // A matching host and filename alone cannot identify the document:
      // /unrelated/19640001198.pdf is not NASA's archived /archive/nasa/... URL.
      // For old NTRS captures, permit only the explicit historical URL scheme
      // corresponding to the modern /api/citations/<id>/downloads/<id>.pdf.
      assert.equal(archivedOrigin.host, sourceUrl.host, 'Host/porta Wayback divergente');
      assert.equal(archivedOrigin.username, '', 'Usuário em URL de arquivo não permitido');
      assert.equal(archivedOrigin.password, '', 'Credencial em URL de arquivo não permitida');
      assert.equal(archivedOrigin.hash, '', 'Fragmento em URL de arquivo não permitido');
      assert.equal(archivedOrigin.search, sourceUrl.search,
        'Consulta da URL arquivada não corresponde à origem curada');
      const ntrs = /^\/api\/citations\/(\d+)\/downloads\/\1\.pdf$/u.exec(sourceUrl.pathname);
      const expectedArchivedPath = ntrs && sourceUrl.hostname === 'ntrs.nasa.gov'
        ? `/archive/nasa/casi.ntrs.nasa.gov/${ntrs[1]}.pdf`
        : sourceUrl.pathname;
      assert.equal(archivedOrigin.pathname, expectedArchivedPath,
        'Caminho completo do PDF Wayback diverge da origem curada');
      assert.equal(c.retrieved_bytes_sha256, payload.sha256, 'Bytes Wayback divergentes');
      assert.ok(Number.isSafeInteger(payload.bytes) && payload.bytes > 0);
      assert.equal(c.retrieved_bytes_length, payload.bytes, 'Tamanho Wayback divergente');
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
