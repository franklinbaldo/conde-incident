import React, { useState } from 'react';
import { ArrowLeftRight, BookOpen, Compass, ExternalLink, FlaskConical, ShieldAlert } from 'lucide-react';

type Language = 'pt' | 'en';
type SatelliteId = '527' | '528' | '529';
type Localized = { pt: string; en: string };

interface TriangulationDashboardProps {
  lang: Language;
}

const matrix = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md';
const nasa = 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf';

const objects: readonly {
  id: SatelliteId;
  designation: string;
  role: Localized;
  supported: Localized;
  unknown: Localized;
  evidence: string;
}[] = [
  {
    id: '527',
    designation: '1963-003A',
    role: { pt: 'Objeto de comparação', en: 'Comparison object' },
    supported: {
      pt: 'Usado como objeto relacionado na análise orbital exploratória. Sua trajetória pode fornecer um controle, após verificar épocas e custódia.',
      en: 'Used as a related object in exploratory orbital analysis. Its trajectory may supply a control after epochs and provenance are checked.',
    },
    unknown: {
      pt: 'Sua posição posterior não é uma fronteira geográfica para o 528. Não há ajuste dinâmico conjunto validado.',
      en: 'Its later position is not a geographic fence for 528. No validated joint dynamical fit is available.',
    },
    evidence: '#/research/raan',
  },
  {
    id: '528',
    designation: '1963-003B',
    role: { pt: 'Objeto investigado', en: 'Object under investigation' },
    supported: {
      pt: 'O boletim NASA de 15/11/1963 registra o dia 08/11/1963 como data de decaimento. Não registra uma hora ou posição terminal.',
      en: 'The November 15, 1963 NASA bulletin lists November 8 as its decay date. It provides no terminal time or position.',
    },
    unknown: {
      pt: 'A trajetória terminal, a relação com o relato de Conde e os parâmetros de arrasto continuam indeterminados.',
      en: 'The terminal trajectory, any relation to the Conde report and drag parameters remain undetermined.',
    },
    evidence: '#/research/c197',
  },
  {
    id: '529',
    designation: '1963-003C',
    role: { pt: 'Controle fora da amostra', en: 'Out-of-sample control' },
    supported: {
      pt: 'O 529 é tratado como controle de previsão nas análises do repositório. Os erros de teste devem ser examinados independentemente.',
      en: 'Object 529 is treated as a prediction control in repository analyses. Holdout errors must be examined independently.',
    },
    unknown: {
      pt: 'Um teorema sobre erros fornecidos ao Lean não valida a trajetória do 529 nem a previsão do 528.',
      en: 'A theorem about error values supplied to Lean does not validate the trajectory of 529 or predict 528.',
    },
    evidence: '#/research/holdout529',
  },
];

const conditions: readonly { label: Localized; detail: Localized; href: string }[] = [
  {
    label: { pt: '1. Custódia dos elementos orbitais', en: '1. Orbital-element provenance' },
    detail: {
      pt: 'Há conflito de RAAN entre séries (~198,5261° e 284,1520°). Comparar épocas e registros originais antes de selecionar uma solução.',
      en: 'RAAN conflicts between series (~198.5261° and 284.1520°). Compare epochs and original records before selecting any solution.',
    },
    href: '#/research/raan',
  },
  {
    label: { pt: '2. Restrições formais e premissas', en: '2. Formal constraints and assumptions' },
    detail: {
      pt: 'Lean 4.35.0 verifica implicações condicionais. As ocorrências orbitais C44–C46 são distintas das ocorrências geográficas homônimas.',
      en: 'Lean 4.35.0 checks conditional implications. The orbital C44–C46 entries differ from the geographic entries with reused IDs.',
    },
    href: '#/research/c44-orbital',
  },
  {
    label: { pt: '3. Domínio admissível e simulação', en: '3. Admissible domain and simulation' },
    detail: {
      pt: 'Ainda não há domínio físico não vazio e reduzido, intervalos de hora/local calibrados ou erro de integração validado. Os contratos da PR #43 são cenários, não medidas.',
      en: 'No validated nonempty, reduced physical domain, calibrated time/place intervals or integration error exists. PR #43 contains scenario contracts, not measurements.',
    },
    href: 'https://github.com/franklinbaldo/conde-incident/pull/43',
  },
  {
    label: { pt: '4. Contraprova independente', en: '4. Independent holdout' },
    detail: {
      pt: 'Avaliar o 529 fora da amostra antes de afirmar que uma triangulação restringe a reentrada. A PR #20 documenta controles e resultados negativos.',
      en: 'Evaluate 529 out of sample before claiming that triangulation constrains reentry. PR #20 tracks controls and negative results.',
    },
    href: '#/research/holdout529',
  },
];

export const TriangulationDashboard: React.FC<TriangulationDashboardProps> = ({ lang }) => {
  const [selectedId, setSelectedId] = useState<SatelliteId>('528');
  const selected = objects.find((object) => object.id === selectedId) ?? objects[1];
  const pt = lang === 'pt';

  return (
    <section aria-labelledby="triangulation-title" className="space-y-7 pb-12">
      <header className="rounded-2xl border border-cyan-900/70 bg-zinc-900 p-5 sm:p-8">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-cyan-300">
          <Compass aria-hidden="true" className="h-4 w-4" />
          {pt ? 'Comparação orbital sob auditoria' : 'Orbital comparison under audit'}
        </p>
        <h1 id="triangulation-title" className="mt-3 text-2xl font-semibold leading-tight text-zinc-50 sm:text-3xl">
          {pt ? 'Três objetos não determinam sozinhos uma queda' : 'Three objects do not determine an impact on their own'}
        </h1>
        <p className="mt-4 max-w-3xl text-sm leading-7 text-zinc-300">
          {pt
            ? '527, 528 e 529 são candidatos úteis a um ajuste conjunto. A origem orbital relacionada não preserva uma posição relativa fixa durante meses. Este painel apresenta evidências e condições para um teste; não mostra uma triangulação histórica já calibrada.'
            : '527, 528 and 529 are useful candidates for a joint fit. Related orbital origin does not preserve a fixed relative position over months. This panel presents evidence and test conditions, not a calibrated historical triangulation.'}
        </p>
        <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm">
          <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300" href="#/research/c197">
            {pt ? 'NASA: dia registrado (C197–C202)' : 'NASA: recorded day (C197–C202)'}
          </a>
          <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300" href="#/research/raan">
            {pt ? 'Conflito RAAN' : 'RAAN conflict'}
          </a>
          <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300" href="#/map">
            {pt ? 'Mapa exploratório' : 'Exploratory map'}
          </a>
        </div>
      </header>

      <section aria-labelledby="objects-title">
        <div className="mb-4 flex items-center gap-2">
          <ArrowLeftRight aria-hidden="true" className="h-5 w-5 text-cyan-300" />
          <h2 id="objects-title" className="text-lg font-semibold text-zinc-100">
            {pt ? 'Compare o papel de cada objeto' : 'Compare each object’s role'}
          </h2>
        </div>
        <div role="group" aria-label={pt ? 'Selecionar objeto orbital para leitura' : 'Choose orbital object to inspect'} className="grid gap-3 sm:grid-cols-3">
          {objects.map((object) => (
            <button
              key={object.id}
              type="button"
              aria-pressed={selectedId === object.id}
              aria-controls="triangulation-object-detail"
              onClick={() => setSelectedId(object.id)}
              className={'min-w-0 rounded-xl border px-4 py-4 text-left transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 ' + (
                selectedId === object.id
                  ? 'border-cyan-400 bg-cyan-950/40 text-white'
                  : 'border-zinc-700 bg-zinc-900 text-zinc-200 hover:border-zinc-400'
              )}
            >
              <span className="block text-lg font-semibold">NORAD {object.id}</span>
              <span className="mt-1 block text-xs text-zinc-300">{object.designation}</span>
              <span className="mt-3 block text-sm">{object.role[lang]}</span>
            </button>
          ))}
        </div>
        <article id="triangulation-object-detail" aria-live="polite" aria-atomic="true" className="mt-4 rounded-xl border border-zinc-700 bg-zinc-900/70 p-5 sm:p-6">
          <h3 className="text-lg font-semibold text-zinc-50">NORAD {selected.id}: {selected.role[lang]}</h3>
          <p className="mt-3 text-sm leading-7 text-zinc-300">{selected.supported[lang]}</p>
          <p className="mt-3 flex gap-2 text-sm leading-7 text-amber-200">
            <ShieldAlert aria-hidden="true" className="mt-1 h-4 w-4 shrink-0" />
            <span><strong>{pt ? 'Não demonstrado: ' : 'Not established: '}</strong>{selected.unknown[lang]}</span>
          </p>
          <a href={selected.evidence} className="mt-4 inline-block text-sm font-medium text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
            {pt ? 'Abrir ocorrência e premissas na aba Evidence' : 'Open record and assumptions in Evidence'}
          </a>
        </article>
      </section>

      <section aria-labelledby="conditions-title" className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-5 sm:p-7">
        <h2 id="conditions-title" className="flex items-center gap-2 text-lg font-semibold text-zinc-100">
          <FlaskConical aria-hidden="true" className="h-5 w-5 text-cyan-300" />
          {pt ? 'O que falta para uma triangulação quantitativa' : 'What quantitative triangulation still requires'}
        </h2>
        <ol className="mt-5 grid gap-3 md:grid-cols-2">
          {conditions.map((condition) => (
            <li key={condition.label.pt} className="rounded-lg border border-zinc-700 bg-zinc-950/50 p-4">
              <h3 className="font-semibold text-zinc-100">{condition.label[lang]}</h3>
              <p className="mt-2 text-sm leading-6 text-zinc-300">{condition.detail[lang]}</p>
              <a href={condition.href} className="mt-3 inline-block text-sm text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
                {pt ? 'Ver fonte e restrição' : 'View source and constraint'}
              </a>
            </li>
          ))}
        </ol>
        <p className="mt-5 text-sm leading-7 text-amber-200">
          <strong>{pt ? 'Resultado: indeterminado.' : 'Result: undetermined.'}</strong>{' '}
          {pt
            ? 'Não há hora, coordenadas, largura de corredor, probabilidade ou intervalo físico de impacto validado a exibir. A data de decaimento não identifica lugar ou impacto.'
            : 'There is no validated impact time, coordinates, corridor width, probability or physical interval to display. A decay date does not identify a location or impact.'}
        </p>
      </section>

      <aside className="rounded-xl border border-zinc-700 p-5 text-sm leading-7 text-zinc-300">
        <h2 className="flex items-center gap-2 font-semibold text-zinc-100">
          <BookOpen aria-hidden="true" className="h-4 w-4" />
          {pt ? 'Fontes e grau de verificação' : 'Sources and verification level'}
        </h2>
        <p className="mt-2">
          {pt
            ? 'Esta apresentação deriva da matriz cumulativa C001–C238 da PR #1, ainda em revisão. Trata-se de auditoria da interface e do código, não de nova inspeção dos TLEs originais. O vínculo NASA/NORAD pode compartilhar a mesma cadeia de rastreamento.'
            : 'This presentation is based on the cumulative C001–C238 matrix in the unmerged PR #1. It is a UI and code audit, not a new inspection of original TLEs. NASA/NORAD may share a tracking chain.'}
        </p>
        <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2">
          <a href={matrix} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-cyan-300 underline underline-offset-4">
            {pt ? 'Matriz cumulativa (snapshot)' : 'Cumulative matrix (snapshot)'} <ExternalLink aria-hidden="true" className="h-3 w-3" />
          </a>
          <a href={nasa} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-cyan-300 underline underline-offset-4">
            {pt ? 'Boletim NASA, 15/11/1963' : 'NASA bulletin, Nov 15, 1963'} <ExternalLink aria-hidden="true" className="h-3 w-3" />
          </a>
        </div>
      </aside>
    </section>
  );
};
