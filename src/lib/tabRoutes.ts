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
  timeMs?: number; // Model selection, never an observed reentry time.
}

// Date bounds are those offered by the exploratory map UI, not an impact window.
export const MAP_TIME_START = Date.parse('1963-01-16T21:59:00Z');
export const MAP_TIME_END = Date.parse('1963-11-08T23:59:59Z');

export function mapTimeHref(timeMs: number): string {
  if (!Number.isFinite(timeMs) || timeMs < MAP_TIME_START || timeMs > MAP_TIME_END) {
    return '#/map';
  }
  // Explicit UTC and millisecond precision, with no inferred historical accuracy.
  return '#/map?at=' + encodeURIComponent(new Date(timeMs).toISOString());
}

export function tabHref(tab: LabTab): string {
  return `#/${tab}`;
}

export function parseLabRoute(hash: string): LabRoute {
  if (hash === '' || hash === '#' || hash === '#/') {
    return { tab: 'summary', invalidHash: null };
  }
  const selected = /^#\/map\?at=([^&#]+)$/.exec(hash);
  if (selected) {
    try {
      const instant = decodeURIComponent(selected[1]);
      // Canonical ISO timestamps only. Date.parse accepts too many ambiguous formats.
      if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/.test(instant)) {
        const timeMs = Date.parse(instant);
        if (Number.isFinite(timeMs) && new Date(timeMs).toISOString() === instant &&
            timeMs >= MAP_TIME_START && timeMs <= MAP_TIME_END) {
          return { tab: 'map', invalidHash: null, timeMs };
        }
      }
    } catch {
      // Invalid percent escapes are an invalid route, not a crash.
    }
    return { tab: 'summary', invalidHash: hash };
  }
  const match = /^#\/([a-z]+)\/?$/.exec(hash);
  if (match && LAB_TABS.some((tab) => tab === match[1])) {
    return { tab: match[1] as LabTab, invalidHash: null };
  }
  // Explicitly distinguish an unknown deep link from a valid summary route.
  // Do not echo untrusted URL contents into HTML.
  return { tab: 'summary', invalidHash: hash };
}
