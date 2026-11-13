import type { LabTab } from './tabRoutes';

// Published SSG counterparts for each computational laboratory view.
// Links intentionally leave the SPA; no model output is a verified observation.
export const EDITORIAL_ROUTES: Record<LabTab, {
  href: string;
  pt: string;
  en: string;
}> = {
  summary: { href: '/conde-incident/', pt: 'Início do Caderno', en: 'Notebook home' },
  map: { href: '/conde-incident/mapa/', pt: 'Contexto do mapa', en: 'Map context' },
  inverse: { href: '/conde-incident/simulacoes/inverso/', pt: 'Contexto da inversão', en: 'Inverse-model context' },
  triangulation: { href: '/conde-incident/simulacoes/triangulacao/', pt: 'Contexto da comparação', en: 'Comparison context' },
  sensitivity: { href: '/conde-incident/simulacoes/sensibilidade/', pt: 'Contexto do arrasto', en: 'Drag-model context' },
  montecarlo: { href: '/conde-incident/simulacoes/montecarlo/', pt: 'Contexto da amostragem', en: 'Sampling context' },
  tles: { href: '/conde-incident/simulacoes/tles/custodia/', pt: 'Custódia documental dos TLEs', en: 'TLE documentary custody' },
  documents: { href: '/conde-incident/evidencias/arquivo/', pt: 'Arquivo documental', en: 'Document archive' },
};
