/** Language is a shareable lab URL parameter, independent of hash routes. */
export type LabLanguage = 'pt' | 'en';

/** Unknown or duplicated language values fail closed to pt-BR. */
export function getLabLanguage(search: string): LabLanguage {
  const values = new URLSearchParams(search).getAll('lang');
  return values.length === 1 && values[0] === 'en' ? 'en' : 'pt';
}

/** Preserve scientific hash deep links and unrelated query parameters. */
export function labLanguagePath(href: string, lang: LabLanguage): string {
  const url = new URL(href);
  url.searchParams.delete('lang');
  if (lang === 'en') url.searchParams.set('lang', 'en');
  return url.pathname + url.search + url.hash;
}
