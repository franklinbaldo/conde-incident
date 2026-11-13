/** A Wayback lookup negative must be attributed to its own source, not another record. */
export interface ArchiveNegativeRecord {
  readonly id: string;
  readonly source_type?: string | null;
}
export function negativeArchiveLabel(record: ArchiveNegativeRecord): string {
  return record.source_type?.trim() || record.id;
}
