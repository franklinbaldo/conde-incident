import type { TabId } from '../components/Navigation';

// A real URL fragment identifies a view; unknown routes must not silently claim a valid tab.
const routes: ReadonlySet<TabId> = new Set([
  'research', 'summary', 'map', 'inverse', 'triangulation', 'sensitivity',
  'montecarlo', 'tles', 'documents',
]);

export function resolveLabHash(hash: string): TabId | null {
  if (hash === '' || hash === '#') return 'summary';
  const match = /^#\/([a-z]+)\/?$/.exec(hash);
  if (!match || !routes.has(match[1] as TabId)) return null;
  return match[1] as TabId;
}

export function hashForLabTab(tab: TabId): string {
  if (!routes.has(tab)) throw new Error('A aba não possui rota pública: ' + tab);
  return '#/' + tab;
}
