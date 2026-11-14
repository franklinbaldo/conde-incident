/** Read-only, byte-verified SSG source lookup. No runtime backend and no epistemic inference. */
const SHA = /^[a-f0-9]{64}$/;
const POINTER = 'data/conde-source-lookup-manifest.json';
const EVIDENCE = 'data/conde-evidence-index-manifest.json';
const EVIDENCE_SOURCE = 'public/data/conde-evidence-index-manifest.json';
const INDEX_PATH = /^public\/data\/conde-source-lookup\/part-([a-f0-9]{64})\.json$/;

export class SourceLookupIntegrityError extends Error {
  constructor(code) {
    super(`Source lookup cannot be trusted: ${code}`);
    this.name = 'SourceLookupIntegrityError';
    this.code = code;
  }
}
const requireTrue = (value, code) => {
  if (!value) throw new SourceLookupIntegrityError(code);
};
const keysEqual = (value, expected) => value && typeof value === 'object'
  && !Array.isArray(value) && Object.keys(value).sort().join('|') === [...expected].sort().join('|');
const decode = bytes => {
  try { return JSON.parse(new TextDecoder('utf-8', {fatal:true}).decode(bytes)); }
  catch { throw new SourceLookupIntegrityError('invalid-json'); }
};
const hex = bytes => Array.from(new Uint8Array(bytes), x => x.toString(16).padStart(2,'0')).join('');

export async function sha256Browser(bytes) {
  requireTrue(globalThis.crypto?.subtle, 'webcrypto-unavailable');
  return hex(await globalThis.crypto.subtle.digest('SHA-256', bytes));
}

/**
 * baseUrl: deployment root, e.g. https://example.org/conde-incident/.
 * fetcher: injected only for tests; production defaults to native fetch.
 * hashBytes: injected only for tests; production uses WebCrypto SHA-256.
 * Returns the verified source index, or throws a typed integrity error.
 * Never silently falls back to unverified localStorage, old pointers or missing data.
 */
export async function loadCondeSourceLookup({baseUrl, fetcher=globalThis.fetch,
  hashBytes=sha256Browser}={}) {
  requireTrue(typeof baseUrl === 'string' && baseUrl.endsWith('/'), 'invalid-base-url');
  requireTrue(typeof fetcher === 'function', 'fetch-unavailable');
  let base;
  try { base=new URL(baseUrl); }
  catch { throw new SourceLookupIntegrityError('invalid-base-url'); }
  requireTrue(base.protocol === 'https:' || (base.protocol === 'http:' &&
    ['localhost','127.0.0.1','[::1]'].includes(base.hostname)), 'unsafe-origin');
  const get = async (relative, cache, limit) => {
    const url = new URL(relative, base);
    requireTrue(url.origin === base.origin && url.pathname.startsWith(base.pathname), 'path-escape');
    let response;
    try { response = await fetcher(url.toString(), {cache}); }
    catch { throw new SourceLookupIntegrityError('network-failure'); }
    requireTrue(response?.ok, 'http-failure');
    let data;
    try { data = new Uint8Array(await response.arrayBuffer()); }
    catch { throw new SourceLookupIntegrityError('body-read-failure'); }
    requireTrue(data.length > 0 && data.length <= limit, 'invalid-byte-length');
    return data;
  };
  // Mutable pointers must be revalidated, immutable digest-named shard may be cached.
  const pointer = decode(await get(POINTER, 'no-store', 4096));
  requireTrue(keysEqual(pointer,['schema','source_index','inputs_sha256'])
    && pointer.schema === 'conde.source-reverse-lookup-manifest/v1', 'pointer-schema');
  const {source_index: shard,inputs_sha256: dependencies}=pointer;
  requireTrue(keysEqual(shard,['path','bytes','sha256'])
    && typeof shard.path === 'string' && SHA.test(shard.sha256)
    && shard.path.match(INDEX_PATH)?.[1] === shard.sha256
    && Number.isInteger(shard.bytes) && shard.bytes > 0 && shard.bytes <= 20_000,
  'shard-contract');
  requireTrue(keysEqual(dependencies,[
    'public/data/conde-source-citations.json',
    'public/data/conde-declared-dependence.json',
    'public/data/conde-evidence-index-manifest.json',
    'research/evidence_matrix_C001-C238_2026-11-11.md',
  ]) && Object.values(dependencies).every(v=>typeof v==='string'&&SHA.test(v)),
  'dependency-contract');
  const [evidenceBytes, indexBytes] = await Promise.all([
    get(EVIDENCE,'no-store',20_000),
    get(shard.path.replace(/^public\//,''),'force-cache',20_000),
  ]);
  requireTrue(await hashBytes(evidenceBytes) === dependencies[EVIDENCE_SOURCE],
    'mixed-snapshot');
  requireTrue(indexBytes.length === shard.bytes && await hashBytes(indexBytes) === shard.sha256,
    'shard-digest');
  const evidence = decode(evidenceBytes);
  const index = decode(indexBytes);
  requireTrue(index.schema === 'conde.source-reverse-lookup/v1'
    && index.matrix_git_blob_sha1 === evidence.matrix_git_blob_sha1
    && index.independent_physical_observation_count === null
    && index.absence_of_declared_edge_proves_independence === false,
  'scientific-contract');
  requireTrue(keysEqual(index.source_files_sha256,[
    'public/data/conde-source-citations.json',
    'public/data/conde-declared-dependence.json',
  ]) && Object.entries(index.source_files_sha256)
    .every(([p,hash])=>hash===dependencies[p]), 'source-snapshot');
  requireTrue(Array.isArray(index.sources) && Array.isArray(index.families)
    && Array.isArray(index.post_matrix_only), 'index-shape');
  // A verified digest does not make duplicated source IDs or broken family joins safe
  // for the browser: the UI selects sources by ID and would silently overwrite them.
  const ids=index.sources.map(s=>s.source_id);
  const families=index.families.map(f=>f.family_id);
  requireTrue(ids.every(id=>typeof id==='string' && id.length>0)
    && new Set(ids).size===ids.length
    && families.every(id=>typeof id==='string' && id.length>0)
    && new Set(families).size===families.length
    && index.sources.every(s=>typeof s.source_family==='string'
      && Array.isArray(s.references) && s.references.length>0)
    && index.families.every(f=>Array.isArray(f.source_ids)
      && new Set(f.source_ids).size===f.source_ids.length
      && f.source_ids.every(id=>ids.includes(id)))
    && index.sources.every(s=>index.families.some(f=>f.family_id===s.source_family
      && f.source_ids.includes(s.source_id)))
    && index.families.reduce((n,f)=>n+f.source_ids.length,0)===ids.length,
  'index-shape');
  requireTrue(index.curated_reference_count===evidence.curated_reference_count
    && index.curated_occurrence_count===evidence.curated_occurrences
    && index.unmapped_occurrence_count===evidence.unmapped_matrix_occurrences
    && index.curated_occurrence_count+index.unmapped_occurrence_count
      ===evidence.total_matrix_occurrences
    && dependencies['research/evidence_matrix_C001-C238_2026-11-11.md']
      ===evidence.matrix_source?.sha256, 'coverage-mismatch');
  const references=index.sources.flatMap(s=>s.references??[]);
  requireTrue(index.curated_reference_count===references.length
    && index.curated_occurrence_count===new Set(references.map(x=>x.occurrence)).size
    && index.unmapped_occurrence_count>=0, 'coverage-mismatch');
  requireTrue(index.post_matrix_only.every(x=>x.matrix_line===null
    && x.independent_physical_observation_count===null), 'post-matrix-promotion');
  return index;
}
