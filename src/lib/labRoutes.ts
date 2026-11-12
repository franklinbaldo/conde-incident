import type { TabId } from '../components/Navigation';

// A URL must identify an actual view. Evidence records distinguish repeated C44-C46 labels
// by occurrence, not merely by the historic ID reused in the cumulative matrix.
const routes: ReadonlySet<TabId> = new Set([
  'research', 'summary', 'map', 'inverse', 'triangulation', 'sensitivity',
  'montecarlo', 'tles', 'documents',
]);

export const evidenceRecordIds = [
  'c01', 'c197', 'c44-geographic', 'c44-orbital', 'holdout529', 'raan',
] as const;
export type EvidenceRecordId = (typeof evidenceRecordIds)[number];
const evidenceIds: ReadonlySet<string> = new Set(evidenceRecordIds);

export function evidenceRecordFromHash(hash: string): EvidenceRecordId | null {
  const match = /^#\/research\/([a-z0-9-]+)\/?$/.exec(hash);
  if (!match || !evidenceIds.has(match[1])) return null;
  return match[1] as EvidenceRecordId;
}

export function hashForEvidenceRecord(id: EvidenceRecordId): string {
  if (!evidenceIds.has(id)) throw new Error('Ocorrência de evidência desconhecida: ' + id);
  return '#/research/' + id;
}

export function resolveLabHash(hash: string): TabId | null {
  if (hash === '' || hash === '#') return 'summary';
  if (evidenceRecordFromHash(hash)) return 'research';
  const match = /^#\/([a-z]+)\/?$/.exec(hash);
  if (!match || !routes.has(match[1] as TabId)) return null;
  return match[1] as TabId;
}

export function hashForLabTab(tab: TabId): string {
  if (!routes.has(tab)) throw new Error('A aba não possui rota pública: ' + tab);
  return '#/' + tab;
}
