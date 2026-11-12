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

export function matrixOccurrenceUrl(matrixLine: number): string {
  return 'https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md#L' + matrixLine;
}
