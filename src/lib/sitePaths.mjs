/**
 * Derive the canonical Caderno link from the Vite laboratory base URL.
 * This is route computation only: it does not claim the site is published.
 */
export function journalPath(baseUrl) {
  if (typeof baseUrl !== 'string' || !baseUrl.startsWith('/') || !baseUrl.endsWith('/')) {
    throw new TypeError('Vite base must be a root-relative directory path');
  }
  const fragments = baseUrl.slice(1, -1).split('/');
  if (fragments.length === 1 && fragments[0] === '') fragments.pop();
  if (fragments.some(part => !/^[a-zA-Z0-9_.~-]+$/.test(part) || part === '.' || part === '..')) {
    throw new TypeError('Vite base contains an unsafe path component');
  }
  if (fragments.at(-1) === 'lab') fragments.pop();
  return '/' + [...fragments, 'stories'].join('/') + '/';
}
