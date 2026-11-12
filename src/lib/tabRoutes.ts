// Only tabs actually shipped in the React laboratory are routable.
// The future SSG /stories/ and Evidence pages must not be linked before integration.
export const LAB_TABS = [
  'summary', 'map', 'inverse', 'triangulation',
  'sensitivity', 'montecarlo', 'tles', 'documents',
] as const;

export type LabTab = (typeof LAB_TABS)[number];
export interface LabRoute {
  tab: LabTab;
  invalidHash: string | null;
}

export function tabHref(tab: LabTab): string {
  return `#/${tab}`;
}

export function parseLabRoute(hash: string): LabRoute {
  if (hash === '' || hash === '#' || hash === '#/') {
    return { tab: 'summary', invalidHash: null };
  }
  const match = /^#\/([a-z]+)\/?$/.exec(hash);
  if (match && LAB_TABS.some((tab) => tab === match[1])) {
    return { tab: match[1] as LabTab, invalidHash: null };
  }
  // Explicitly distinguish an unknown deep link from a valid summary route.
  // Do not echo untrusted URL contents into HTML.
  return { tab: 'summary', invalidHash: hash };
}
