import React from 'react';
import { BookOpen, Compass, FileSearch, GitBranch, ShieldAlert } from 'lucide-react';
import type { TabId } from './Navigation';

type Language = 'pt' | 'en';
type Localized = { pt: string; en: string };
interface ExecutiveSummaryProps {
  lang: Language;
  onJumpToTab: (tab: TabId) => void;
}

// These are snapshots and proposals in draft PRs, not fitted terminal orbits.
const matrix = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md';
const lean = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/formal/Conde1963/Core.lean';

const records: readonly {
  id: string; title: Localized; status: Localized; detail: Localized;
  href: string; source: string; sourceLabel: Localized;
}[] = [
  {
    id: 'C01/C02',
    title: { pt: 'O relato circulou', en: 'The report circulated' },
    status: { pt: 'Relato documentado', en: 'Documented report' },
    detail: {
      pt: 'A cadeia Rádio Tupi → FBIS reproduz um relato de esfera e cratera. Não são duas observações independentes, e a notícia não comprova um objeto em solo.',
      en: 'The Rádio Tupi → FBIS chain preserves a sphere-and-crater report. It is not two independent observations, and the report does not prove an object on the ground.',
    },
    href: '#/research/c01', source: matrix + '#L19-L20',
    sourceLabel: { pt: 'Matriz: C01/C02', en: 'Matrix: C01/C02' },
  },
  {
    id: 'C197–C202',
    title: { pt: 'A NASA catalogou um dia', en: 'NASA catalogued a date' },
    status: { pt: 'Registro contemporâneo', en: 'Contemporary record' },
    detail: {
      pt: 'Boletim de 15/11/1963: decaimento de 1963-003B em 08/11/1963. Sem hora, coordenadas de reentrada, fragmentos identificados ou vínculo demonstrado com Conde.',
      en: 'The November 15, 1963 bulletin dates the decay of 1963-003B to November 8. It provides no terminal time, coordinates, identified fragments or demonstrated link to Conde.',
    },
    href: '#/research/c197', source: matrix + '#L899-L912',
    sourceLabel: { pt: 'Matriz: C197–C202', en: 'Matrix: C197–C202' },
  },
  {
    id: 'NORAD 528 · RAAN',
    title: { pt: 'Elementos orbitais em conflito', en: 'Conflicting orbital elements' },
    status: { pt: 'Proveniência não conciliada', en: 'Provenance unresolved' },
    detail: {
      pt: 'O elemento usado no site legado diverge de uma série histórica alternativa. Sem conciliar épocas, referencial e custódia, não se pode escolher nem combinar uma órbita terminal.',
      en: 'The legacy site element set differs from an alternative historical series. Epochs, frames and custody must be reconciled before selecting or combining a terminal orbit.',
    },
    href: '#/research/raan',
    source: 'https://github.com/franklinbaldo/conde-incident/pull/14',
    sourceLabel: { pt: 'Auditoria de custódia #14', en: 'Custody audit #14' },
  },
];

export const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({ lang, onJumpToTab }) => {
  const pt = lang === 'pt';
  return (
    <div className="space-y-8 pb-12">
      <section aria-labelledby="summary-title" className="rounded-2xl border border-zinc-700 bg-zinc-900/70 px-5 py-8 sm:p-10">
        <p className="mb-3 flex items-center gap-2 text-sm font-medium text-cyan-300">
          <BookOpen aria-hidden="true" className="h-5 w-5" />
          {pt ? 'Síntese documental, não veredito' : 'Documentary overview, not a verdict'}
        </p>
        <h1 id="summary-title" className="max-w-4xl text-3xl font-semibold leading-tight text-zinc-50 sm:text-4xl">
          {pt ? 'O que os documentos permitem afirmar sobre Conde, 1963' : 'What the documents establish about Conde, 1963'}
        </h1>
        <p className="mt-4 max-w-3xl text-base leading-relaxed text-zinc-200">
          {pt
            ? 'Existem um relato jornalístico contemporâneo e um registro de decaimento orbital no mesmo dia. A coincidência cronológica não demonstra que sejam o mesmo evento nem prova uma queda em Conde.'
            : 'A contemporary news report and an orbital decay record share a calendar date. That coincidence does not show they describe one event or that anything struck Conde.'}
        </p>
        <div role="note" className="mt-6 rounded-lg border-l-4 border-amber-400 bg-amber-950/25 px-4 py-3 text-sm leading-relaxed text-amber-100">
          <ShieldAlert aria-hidden="true" className="mr-2 inline-block h-4 w-4" />
          <strong>{pt ? 'Resultado: indeterminado.' : 'Outcome: undetermined.'}</strong>{' '}
          {pt
            ? 'Nenhuma hora, posição terminal, probabilidade de impacto ou intervalo físico validado está disponível neste snapshot.'
            : 'No terminal time, location, impact probability or physically validated interval is available in this snapshot.'}
        </div>
      </section>
      <section aria-labelledby="records-title">
        <h2 id="records-title" className="mb-4 text-xl font-semibold text-zinc-100">
          {pt ? 'Três pontos para conferir nas fontes' : 'Three claims to check against sources'}
        </h2>
        <div className="grid gap-4 lg:grid-cols-3">
          {records.map(record => (
            <article key={record.id} className="rounded-xl border border-zinc-700 bg-zinc-900/50 p-5">
              <p className="font-mono text-xs text-cyan-300">{record.id}</p>
              <h3 className="mt-2 text-lg font-semibold text-zinc-50">{record.title[lang]}</h3>
              <p className="mt-2 text-xs font-medium text-amber-200">{record.status[lang]}</p>
              <p className="mt-3 text-sm leading-relaxed text-zinc-300">{record.detail[lang]}</p>
              <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm">
                <a className="text-cyan-300 underline underline-offset-4" href={record.href}>
                  {pt ? 'Ver ocorrência e premissas' : 'See occurrence and assumptions'}
                </a>
                <a className="text-cyan-300 underline underline-offset-4" href={record.source} target="_blank" rel="noopener noreferrer">
                  {record.sourceLabel[lang]}
                </a>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section aria-labelledby="constraints-title" className="rounded-2xl border border-zinc-700 bg-zinc-900/50 p-5 sm:p-7">
        <div className="flex items-start gap-3">
          <GitBranch aria-hidden="true" className="mt-1 h-5 w-5 shrink-0 text-cyan-300" />
          <div>
            <h2 id="constraints-title" className="text-xl font-semibold text-zinc-100">
              {pt ? 'Das premissas aos intervalos: verificação física pendente' : 'From assumptions to intervals: physical validation pending'}
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-zinc-300">
              {pt
                ? 'O Lean demonstra implicações condicionais das premissas fornecidas, não a autenticidade de um TLE nem uma trajetória. Domínio não vazio, erro numérico e holdouts reproduzíveis ainda precisam ser estabelecidos.'
                : 'Lean proves conditional implications of supplied assumptions, not TLE authenticity or a trajectory. A nonempty physical domain, numerical errors and reproducible holdouts remain to be established.'}
            </p>
            <div className="mt-4 flex flex-wrap gap-x-6 gap-y-3 text-sm">
              <a className="text-cyan-300 underline underline-offset-4" href={lean + '#L79-L107'} target="_blank" rel="noopener noreferrer">
                {pt ? 'Lean: limite da data e não expansão' : 'Lean: date limit and monotonicity'}
              </a>
              <a className="text-cyan-300 underline underline-offset-4" href="https://github.com/franklinbaldo/conde-incident/blob/b8ebd31ef89b94e7adc8dc3b363b0f11964655d7/research/ADMISSIBLE_DOMAIN_GATE.md" target="_blank" rel="noopener noreferrer">
                {pt ? '#37: intervalos exatos, contrato sintético' : '#37: exact intervals, synthetic contract'}
              </a>
              <a className="text-cyan-300 underline underline-offset-4" href="https://github.com/franklinbaldo/conde-incident/blob/65043a6a711f9be77967a0835210ede9397658e9/research/ALTERNATIVE_DOMAINS.md" target="_blank" rel="noopener noreferrer">
                {pt ? '#43: cenários TLE não conciliados' : '#43: unresolved TLE scenarios'}
              </a>
              <a className="text-cyan-300 underline underline-offset-4" href="#/research/holdout529">
                {pt ? 'Holdout 529: limite do controle' : 'Holdout 529: control limitations'}
              </a>
            </div>
            <p className="mt-4 text-xs leading-relaxed text-amber-200">
              {pt
                ? 'Status: #37/#43 são propostas ainda não integradas, com testes sintéticos. REDUCED/CONTRADICTORY não constituem medidas orbitais nem exclusão geográfica.'
                : 'Status: #37/#43 are unmerged proposals with synthetic tests. REDUCED/CONTRADICTORY are neither orbital observations nor proof of geographic exclusion.'}
            </p>
          </div>
        </div>
      </section>
      <nav aria-label={pt ? 'Próximas leituras no laboratório' : 'More laboratory sections'} className="flex flex-wrap gap-3">
        <button type="button" onClick={() => onJumpToTab('research')} className="inline-flex items-center gap-2 rounded-lg bg-cyan-700 px-4 py-3 text-sm font-semibold text-white hover:bg-cyan-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300">
          <FileSearch aria-hidden="true" className="h-4 w-4" />
          {pt ? 'Evidências e restrições' : 'Evidence and constraints'}
        </button>
        <button type="button" onClick={() => onJumpToTab('map')} className="inline-flex items-center gap-2 rounded-lg border border-zinc-600 bg-zinc-800 px-4 py-3 text-sm font-semibold text-zinc-100 hover:bg-zinc-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300">
          <Compass aria-hidden="true" className="h-4 w-4" />
          {pt ? 'Mapa exploratório, não trajetória terminal' : 'Exploratory map, not a terminal track'}
        </button>
      </nav>
    </div>
  );
};
