// A citation is a documentary link, not a distinct witness or a physical measurement.
export interface CitationRecord {
  occurrence: string;
  matrix_line: number;
  row_sha256: string;
  claim_text: string;
  source_id: string;
  source_family: string;
  work_id: string;
  citation_url: string;
  locator: string;
  source_status: string;
  relation: string;
  scope: string;
  not_a_verified_conde_physical_event: boolean;
}

export interface CitationFeed {
  schema: string;
  matrix_git_blob_sha1: string;
  total_matrix_occurrences: number;
  curated_occurrences: number;
  unmapped_occurrences: number;
  records: CitationRecord[];
}

export function normalizeOccurrence(value: string): string | null {
  const candidate = value.trim().toUpperCase();
  // "#occurrence" is mandatory because some matrix IDs (C44–C46) collide.
  return /^C[0-9]{1,3}#[1-9][0-9]*$/.test(candidate) ? candidate : null;
}

export function isCitationFeed(value: unknown): value is CitationFeed {
  if (!value || typeof value !== 'object') return false;
  const feed = value as Partial<CitationFeed>;
  return feed.schema === 'conde.source-citations/v1'
    && Array.isArray(feed.records)
    && typeof feed.matrix_git_blob_sha1 === 'string'
    && typeof feed.total_matrix_occurrences === 'number'
    && typeof feed.curated_occurrences === 'number'
    && typeof feed.unmapped_occurrences === 'number'
    && feed.records.every((record: CitationRecord) =>
      !!normalizeOccurrence(record.occurrence)
      && typeof record.work_id === 'string'
      && typeof record.source_family === 'string'
      && typeof record.citation_url === 'string'
      && typeof record.matrix_line === 'number'
      && typeof record.not_a_verified_conde_physical_event === 'boolean');
}

export function citationContext(feed: CitationFeed, input: string) {
  const occurrence = normalizeOccurrence(input);
  if (!occurrence) return { state: 'invalid' as const };
  const record = feed.records.find((item) => item.occurrence === occurrence);
  if (!record) return { state: 'unmapped' as const, occurrence };
  // A work can yield multiple matrix citations, but is NOT several witnesses.
  const sameWork = feed.records.filter((item) => item.work_id === record.work_id);
  return { state: 'mapped' as const, occurrence, record, sameWork };
}

// The curated citation feed pins original matrix Git blob a7978c3a75a153b16ab70118a92c434bba674cb7.
// Link to the verified *commit*, not mutable main; otherwise a future inserted line
// silently turns a source citation into a different claim.
export function matrixOccurrenceUrl(matrixLine: number): string {
  return 'https://github.com/franklinbaldo/conde-incident/blob/faf4dd0fd8dfbdd825e4e934b3b30ebd81bf61df/research/evidence_matrix_C001-C238_2026-11-11.md#L' + matrixLine;
}


// Documentary ancestry is an explicit *declaration* by the provenance graph.
// No declared path is not evidence that two sources are independent.
export interface DeclaredUpstreamPath {
  upstream_source_id: string;
  edges: Array<{ from: string; to: string; kind: string }>;
}

export interface DeclaredLineageRecord {
  snapshot_ref: string;
  source_id: string;
  family_id: string;
  declared_upstream_paths: DeclaredUpstreamPath[];
  independent_physical_observation_count: null;
}

export interface DeclaredDependenceFeed {
  schema: 'conde.declared-documentary-dependence/v1';
  canonical_citations_path: string;
  matrix_git_blob_sha1: string;
  epistemic_limits: {
    absence_of_edge_does_not_prove_independence: true;
    independent_physical_observation_count: null;
  };
  citation_lineages: DeclaredLineageRecord[];
}

// Fail closed on malformed declared ancestry: a syntactically shaped edge does
// not establish a path from the cited source to its claimed upstream source.
const nonblank = (value: unknown): value is string =>
  typeof value === 'string' && value.trim().length > 0;

function coherentDeclaredPath(sourceId: string, path: DeclaredUpstreamPath): boolean {
  if (!path || !nonblank(path.upstream_source_id) ||
      !Array.isArray(path.edges) || path.edges.length === 0) return false;
  let cursor = sourceId;
  const visited = new Set([sourceId]);
  for (const edge of path.edges) {
    if (!edge || !nonblank(edge.from) || !nonblank(edge.to) ||
        !nonblank(edge.kind) || edge.from !== cursor || visited.has(edge.to)) {
      return false;
    }
    visited.add(edge.to);
    cursor = edge.to;
  }
  return cursor === path.upstream_source_id;
}

export function isDeclaredDependenceFeed(value: unknown): value is DeclaredDependenceFeed {
  if (!value || typeof value !== 'object') return false;
  const feed = value as Partial<DeclaredDependenceFeed>;
  if (feed.schema !== 'conde.declared-documentary-dependence/v1' ||
      feed.canonical_citations_path !== 'public/data/conde-source-citations.json' ||
      !nonblank(feed.matrix_git_blob_sha1) ||
      !/^[a-f0-9]{40}$/.test(feed.matrix_git_blob_sha1) ||
      feed.epistemic_limits?.absence_of_edge_does_not_prove_independence !== true ||
      feed.epistemic_limits?.independent_physical_observation_count !== null ||
      !Array.isArray(feed.citation_lineages)) return false;

  const seen = new Set<string>();
  return feed.citation_lineages.every((record) => {
    if (!record || !nonblank(record.snapshot_ref) ||
        !nonblank(record.source_id) || !nonblank(record.family_id) ||
        record.independent_physical_observation_count !== null ||
        !Array.isArray(record.declared_upstream_paths)) return false;
    const prefix = `matrix:${feed.matrix_git_blob_sha1}:`;
    const occurrence = record.snapshot_ref.startsWith(prefix)
      ? normalizeOccurrence(record.snapshot_ref.slice(prefix.length)) : null;
    if (!occurrence || record.snapshot_ref !== prefix + occurrence ||
        seen.has(record.snapshot_ref)) return false;
    seen.add(record.snapshot_ref);
    return record.declared_upstream_paths.every((path) =>
      coherentDeclaredPath(record.source_id, path));
  });
}

export function declaredLineageContext(
  dependence: DeclaredDependenceFeed,
  citations: CitationFeed,
  citation: CitationRecord,
) {
  // Companion and canonical feeds must refer to the same immutable matrix.
  if (dependence.matrix_git_blob_sha1 !== citations.matrix_git_blob_sha1) {
    return { state: 'snapshot-mismatch' as const };
  }
  const snapshotRef = `matrix:${citations.matrix_git_blob_sha1}:${citation.occurrence}`;
  const record = dependence.citation_lineages.find((item) => item.snapshot_ref === snapshotRef);
  if (!record) return { state: 'unmapped' as const };
  // Reject a misjoined row rather than displaying another document's ancestry.
  if (record.source_id !== citation.source_id || record.family_id !== citation.source_family) {
    return { state: 'source-mismatch' as const };
  }
  return { state: 'declared' as const, paths: record.declared_upstream_paths, sourceId: record.source_id };
}
