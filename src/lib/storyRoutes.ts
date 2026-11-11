/**
 * URL contract for the Caderno. Hash routing survives static GitHub Pages hosting
 * without requiring any server-side rewrite rules.
 */
export type SiteRoute =
  | { kind: 'stories'; slug: string | null }
  | { kind: 'tab'; tab: string };

const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const TAB = /^[a-z]+$/;

export const STORIES_INDEX = '#/stories';

export function storyHref(slug: string): string {
  if (!SLUG.test(slug)) throw new Error('Invalid story slug');
  return `#/stories/${slug}`;
}

export function tabHref(tab: string): string {
  if (!TAB.test(tab)) throw new Error('Invalid tab id');
  return `#/tab/${tab}`;
}

export function readSiteRoute(hash: string): SiteRoute | null {
  if (hash === STORIES_INDEX || hash === '#/stories/') {
    return { kind: 'stories', slug: null };
  }

  if (hash.startsWith('#/stories/')) {
    const rawSlug = hash.slice('#/stories/'.length);
    try {
      const slug = decodeURIComponent(rawSlug);
      return SLUG.test(slug) ? { kind: 'stories', slug } : null;
    } catch {
      return null;
    }
  }

  const tab = /^#\/tab\/([a-z]+)$/.exec(hash);
  return tab ? { kind: 'tab', tab: tab[1] } : null;
}
