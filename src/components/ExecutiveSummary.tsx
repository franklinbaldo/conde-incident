import React from 'react';
import { BookOpen, Compass, FileSearch, GitBranch, ShieldAlert } from 'lucide-react';
import type { TabId } from './Navigation';
import { matrixOccurrenceUrl } from '../lib/sourceCitationAudit';

type Lang = 'pt' | 'en';
type Localized = { pt: string; en: string };

interface ExecutiveSummaryProps {
  lang: Lang;
  onJumpToTab: (tab: TabId) => void;
}

const claims: readonly {
  occurrence: string;
  title: Localized;
  status: Localized;
  explanation: Localized;
  matrixLine: number;
  otherMatrixLine?: number;
  source: string;
}[] = [
  {
    occurrence: 'C01#1 / C02#1',
    title: { pt: 'O relato é documentado', en: 'The report is documented' },
    status: { pt: 'Relato contemporâneo, não observação física', en: 'Contemporary report, not a physical observation' },
    explanation: {
      pt: 'A transcrição FBIS preserva notícias atribuídas à Rádio Tupi sobre esfera e cratera. A retransmissão não cria uma segunda testemunha independente nem verifica a existência dos objetos.',
      en: 'The FBIS transcript preserves reports attributed to Rádio Tupi of a sphere and crater. Repeating a report creates neither an independent witness nor proof the reported objects existed.',
    },
    matrixLine: 19,
    otherMatrixLine: 20,
    source: 'https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf',
  },
  {
    occurrence: 'C197#1 / C198#1',
    title: { pt: 'A NASA registrou o dia', en: 'NASA recorded the date' },
    status: { pt: 'Documento de 15/11/1963, sem hora ou local', en: 'November 15, 1963 document, no time or place' },
    explanation: {
      pt: 'O boletim NASA registra o decaimento de 1963-003B em 08/11/1963, mas não fornece hora terminal, coordenadas ou impacto em Conde. C197 e C198 remetem à mesma obra documental.',
      en: 'The NASA bulletin dates the decay of 1963-003B to November 8, 1963, but gives no terminal time, coordinates or Conde impact. C197 and C198 refer to the same documentary work.',
    },
    matrixLine: 905,
    otherMatrixLine: 906,
    source: 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10',
  },
  {
    occurrence: 'C179#1 / C241-L3',
    title: { pt: 'Os elementos orbitais exigem conciliação', en: 'Orbital elements need reconciliation' },
    status: { pt: 'Conflito de proveniência e épocas', en: 'Unresolved provenance and epochs' },
    explanation: {
      pt: 'C179#1 registra um TLE do 528 obtido de espelho secundário, com época em 27/10/1963. A origem instrumental ainda não foi autenticada; os vetores 527/529 do laboratório são cenários, não observações. Nenhum desses dados fixa uma trajetória terminal.',
      en: 'C179#1 records a 528 TLE from a secondary mirror, with an epoch on 27 October 1963. Its original tracking provenance remains unverified; the laboratory’s 527/529 vectors are scenarios, not observations. None establishes a terminal trajectory.',
    },
    matrixLine: 839,
    source: 'https://github.com/franklinbaldo/conde-incident/blob/d368bc2340f49cd637fa2b88a00bc47dfd91018d/research/constraints/norad_1963_epoch_availability_C241-L3.json',
  },
];

export const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({ lang, onJumpToTab }) => {
  const pt = lang === 'pt';

  return (
    <div className="space-y-7 pb-12 wrap-anywhere">
      <section aria-labelledby="summary-title" className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 sm:p-8">
        <p className="mb-3 flex items-center gap-2 text-sm text-cyan-300">
          <BookOpen aria-hidden="true" className="h-5 w-5" />
          {pt ? 'Síntese documental, não veredito' : 'Documentary summary, not a verdict'}
        </p>
        <h1 id="summary-title" className="text-2xl font-semibold leading-tight text-zinc-50 sm:text-3xl">
          {pt ? 'O que sabemos e o que ainda não sabemos sobre Conde' : 'What we know and do not know about Conde'}
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-relaxed text-zinc-200">
          {pt
            ? 'Um relato jornalístico e um registro orbital compartilham uma data. Isso não demonstra que relatem o mesmo evento. Documentos, hipóteses e simulações são apresentados separadamente.'
            : 'A news report and an orbital record share a date. This does not establish they describe the same event. Documents, hypotheses and simulations are kept separate.'}
        </p>
        <p role="status" className="mt-5 rounded-lg border border-amber-700 bg-amber-950/30 p-4 text-sm text-amber-100">
          <ShieldAlert aria-hidden="true" className="mr-2 inline-block h-4 w-4" />
          <strong>{pt ? 'Resultado: indeterminado.' : 'Outcome: undetermined.'}</strong>{' '}
          {pt
            ? 'Não existem hora, posição, probabilidade de impacto ou intervalo físico terminal validados neste conjunto de fontes.'
            : 'No validated terminal time, position, impact probability or physically fitted terminal interval is available in this source set.'}
        </p>
      </section>

      <section aria-labelledby="claims-title" className="space-y-4">
        <h2 id="claims-title" className="text-xl font-semibold text-zinc-100">
          {pt ? 'Ocorrências e limites das fontes' : 'Source occurrences and limitations'}
        </h2>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          {claims.map((claim) => (
            <article key={claim.occurrence} className="rounded-xl border border-zinc-700 bg-zinc-900/70 p-5">
              <p className="font-mono text-xs text-cyan-300">{claim.occurrence}</p>
              <h3 className="mt-2 text-base font-semibold text-zinc-100">{claim.title[lang]}</h3>
              <p className="mt-2 text-xs font-medium text-amber-200">{claim.status[lang]}</p>
              <p className="mt-3 text-sm leading-relaxed text-zinc-300">{claim.explanation[lang]}</p>
              <div className="mt-4 flex flex-wrap gap-3 text-sm">
                <a href={matrixOccurrenceUrl(claim.matrixLine)} target="_blank" rel="noopener noreferrer"
                  className="text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                  {pt ? 'Matriz cumulativa' : 'Cumulative matrix'}
                </a>
                {claim.otherMatrixLine && (
                  <a href={matrixOccurrenceUrl(claim.otherMatrixLine)} target="_blank" rel="noopener noreferrer"
                    className="text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                    {pt ? 'Matriz: outra ocorrência' : 'Matrix: related occurrence'}
                  </a>
                )}
                <a href={claim.source} target="_blank" rel="noopener noreferrer"
                  className="text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
                  {pt ? 'Fonte / custódia' : 'Source / custody'}
                </a>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section aria-labelledby="constraints-title" className="rounded-xl border border-zinc-700 bg-zinc-900/70 p-5 sm:p-7">
        <h2 id="constraints-title" className="flex items-center gap-2 text-xl font-semibold text-zinc-100">
          <GitBranch aria-hidden="true" className="h-5 w-5 text-cyan-300" />
          {pt ? 'Restrições conectadas, não uma trajetória demonstrada' : 'Connected constraints, not a proven trajectory'}
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-zinc-300">
          {pt
            ? 'O grafo científico preserva relações entre observáveis, parâmetros e fontes, inclusive dependências ainda sem calibração. Isso avança a rastreabilidade, sem demonstrar automaticamente redução do domínio admissível. Provas Lean são condicionais às premissas, e simulações exigem erro e holdouts reproduzíveis.'
            : 'The scientific graph records relationships among observables, parameters and sources, including dependencies pending calibration. This improves traceability without automatically demonstrating a smaller admissible domain. Lean proofs depend on their premises, and simulations require reproducible errors and holdouts.'}
        </p>
        <a href="https://github.com/franklinbaldo/conde-incident/blob/d368bc2340f49cd637fa2b88a00bc47dfd91018d/research/constraints/ssr_1963_observable_graph.json"
          target="_blank" rel="noopener noreferrer"
          className="mt-3 inline-block text-sm text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
          {pt ? 'Grafo cumulativo: fontes, equações e pontes pendentes' : 'Cumulative graph: sources, equations and pending bridges'}
        </a>
        <p className="mt-3 text-xs text-amber-200">
          {pt
            ? 'Estado dos dados: CONNECTED_PENDING_CALIBRATION não é um resultado numérico nem uma evidência de impacto.'
            : 'Data status: CONNECTED_PENDING_CALIBRATION is not a numerical result or evidence of an impact.'}
        </p>
      </section>

      <nav aria-label={pt ? 'Investigar no laboratório' : 'Explore the laboratory'} className="flex flex-wrap gap-3">
        <button type="button" onClick={() => onJumpToTab('documents')}
          className="inline-flex items-center gap-2 rounded-lg bg-cyan-700 px-4 py-3 text-sm font-medium text-white hover:bg-cyan-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300">
          <FileSearch aria-hidden="true" className="h-4 w-4" />
          {pt ? 'Arquivo e genealogia documental' : 'Document archive and lineage'}
        </button>
        <button type="button" onClick={() => onJumpToTab('map')}
          className="inline-flex items-center gap-2 rounded-lg border border-zinc-600 bg-zinc-800 px-4 py-3 text-sm font-medium text-zinc-100 hover:bg-zinc-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-300">
          <Compass aria-hidden="true" className="h-4 w-4" />
          {pt ? 'Mapa exploratório, não impacto' : 'Exploratory map, not impact'}
        </button>
      </nav>
    </div>
  );
};
