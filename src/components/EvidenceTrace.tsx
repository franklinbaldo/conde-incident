import React from 'react';
import { evidenceRecordFromHash, hashForEvidenceRecord, type EvidenceRecordId } from '../lib/labRoutes';

type Language = 'pt' | 'en';
type Localized = { pt: string; en: string };
type RecordEntry = {
  id: EvidenceRecordId;
  ids: string;
  label: Localized;
  description: Localized;
  premise: Localized;
  status: Localized;
  evidence: string;
  proof?: string;
  proofName?: string;
};

// The URLs identify a historical snapshot being reviewed in PR #1, not a current
// observational feed. Numerical claims must not be synthesized from Lean examples.
const matrix = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md';
const lean = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/formal/Conde1963/Core.lean';
const records: readonly RecordEntry[] = [
  {
    id: 'c01',
    ids: 'C01/C02',
    label: { pt: 'Relato Tupi → FBIS', en: 'Tupi → FBIS report' },
    description: {
      pt: 'A transcrição contemporânea documenta a divulgação do relato de esfera e cratera, não uma inspeção independente em Conde.',
      en: 'The contemporary transcript documents a sphere-and-crater report, not an independent inspection at Conde.',
    },
    premise: {
      pt: 'C01 e C02 reutilizam a mesma cadeia jornalística. A prova modela essa classificação fornecida, não autentica o acontecimento.',
      en: 'C01 and C02 share one journalistic chain. The proof assumes that classification; it does not authenticate the event.',
    },
    status: { pt: 'Relato documentado; impacto não verificado', en: 'Report documented; impact unverified' },
    evidence: matrix + '#L19-L20',
    proof: lean + '#L26-L33',
    proofName: 'no_double_count_tupi',
  },
  {
    id: 'c197',
    ids: 'C197–C202',
    label: { pt: 'Dia de decaimento na NASA', en: 'NASA decay date' },
    description: {
      pt: 'Boletim de 15/11/1963, página impressa 8: 1963-003B consta em 8/11. O registro não fornece hora nem coordenadas terminais.',
      en: 'The November 15, 1963 bulletin, printed page 8, dates 1963-003B to November 8 without terminal time or coordinates.',
    },
    premise: {
      pt: 'O teorema constrói dois exemplos lógicos compatíveis com a data, mas não prova admissibilidade dinâmica de nenhum deles.',
      en: 'The theorem constructs two logical examples consistent with the date, but establishes physical admissibility of neither.',
    },
    status: { pt: 'Data registrada; local e hora indeterminados', en: 'Date recorded; place and time undetermined' },
    evidence: matrix + '#L899-L912',
    proof: lean + '#L79-L100',
    proofName: 'date_alone_does_not_identify_place',
  },
  {
    id: 'c44-geographic',
    ids: 'C44–C46 · solo/geologia',
    label: { pt: 'Primeira ocorrência de C44–C46', en: 'First occurrence of C44–C46' },
    description: {
      pt: 'Mapas regionais CONDER para um ponto aproximado da sede, seguidos de um cálculo hipotético de penetração; nenhum sítio histórico de impacto foi medido.',
      en: 'Regional CONDER maps around an approximate town point, followed by a hypothetical penetration calculation; no historic impact site was measured.',
    },
    premise: {
      pt: 'Classificação cartográfica contemporânea e resistência/forma física não verificadas para uma cratera de 1963.',
      en: 'Modern map classification and unverified resistance/physical shape for a purported 1963 crater.',
    },
    status: { pt: 'Sem restrição Lean física certificada para esta ocorrência', en: 'No certified physical Lean constraint for this occurrence' },
    evidence: matrix + '#L160-L168',
  },
  {
    id: 'c44-orbital',
    ids: 'C44–C46 · ajuste orbital',
    label: { pt: 'Segunda ocorrência de C44–C46', en: 'Second occurrence of C44–C46' },
    description: {
      pt: 'Os IDs foram reutilizados para TLEs e ajustes inversos; não podem ser confundidos com os itens homônimos de solo e geologia.',
      en: 'The IDs were reused for TLEs and inverse fits; these are not the soil and geology entries with identical labels.',
    },
    premise: {
      pt: 'A monotonicidade demonstrada vale para predicados fornecidos. Não garante que as soluções numéricas sejam físicas ou que o conjunto admissível seja não vazio.',
      en: 'The proved monotonicity holds for supplied predicates. It does not establish physical solutions or a nonempty admissible set.',
    },
    status: { pt: 'Ajustes exploratórios; domínio físico ainda não certificado', en: 'Exploratory fits; physical domain not yet certified' },
    evidence: matrix + '#L171-L185',
    proof: lean + '#L102-L107',
    proofName: 'more_constraints_never_expand',
  },
  {
    id: 'holdout529',
    ids: 'NORAD 529 · holdout',
    label: { pt: 'Controle de previsão', en: 'Prediction holdout' },
    description: {
      pt: 'A desigualdade do Lean compara dois erros fixados no código. Não certifica estimador, trajetória nem melhora de previsão fora da amostra.',
      en: 'The Lean inequality compares two error constants supplied in code. It certifies no estimator, trajectory or general out-of-sample improvement.',
    },
    premise: {
      pt: 'Entradas numéricas assumidas, com genealogia e avaliação adicional tratadas na PR #20. A avaliação física permanece separada.',
      en: 'Fixed numeric inputs; provenance and further evaluation are tracked in PR #20. Physical validation remains separate.',
    },
    status: { pt: 'Comparação condicional; não é validação física', en: 'Conditional comparison; not a physical validation' },
    evidence: 'https://github.com/franklinbaldo/conde-incident/pull/20',
    proof: lean + '#L60-L65',
    proofName: 'joint_model_did_not_beat_quadratic_on_holdout',
  },
  {
    id: 'raan',
    ids: 'NORAD 528 · RAAN',
    label: { pt: 'Conflito de elementos orbitais', en: 'Orbital element conflict' },
    description: {
      pt: 'A RAAN 284,1520° do aplicativo diverge dos ~198,5261° de uma série histórica. As épocas e a custódia primária não estão conciliadas.',
      en: 'The app RAAN 284.1520° conflicts with ~198.5261° from a historical series. Epochs and primary custody remain unresolved.',
    },
    premise: {
      pt: 'Ter checksum sintaticamente válido não demonstra a proveniência histórica de um TLE. A PR #14 audita esse limite.',
      en: 'A syntactically valid checksum does not prove a TLE’s historical provenance. PR #14 audits this limit.',
    },
    status: { pt: 'Conflito aberto; nenhuma órbita terminal selecionada', en: 'Conflict open; no terminal orbit selected' },
    evidence: 'https://github.com/franklinbaldo/conde-incident/pull/14',
    proof: lean + '#L67-L77',
    proofName: 'last528 (entrada, não prova)',
  },
];

const flow: readonly { name: Localized; state: Localized }[] = [
  { name: { pt: 'Fonte e custódia', en: 'Source and custody' }, state: { pt: 'Parcial', en: 'Partial' } },
  { name: { pt: 'Ocorrência/independência', en: 'Occurrence/independence' }, state: { pt: 'Parcial', en: 'Partial' } },
  { name: { pt: 'Lean 4.35.0', en: 'Lean 4.35.0' }, state: { pt: 'Condicional', en: 'Conditional' } },
  { name: { pt: 'Domínio não vazio/reduzido', en: 'Nonempty/reduced domain' }, state: { pt: 'Não verificado', en: 'Not verified' } },
  { name: { pt: 'Simulação e holdouts', en: 'Simulation and holdouts' }, state: { pt: 'Não validado', en: 'Not validated' } },
];

export function EvidenceTrace({ lang }: { lang: Language }) {
  const [selected, setSelected] = React.useState<EvidenceRecordId | null>(() => evidenceRecordFromHash(window.location.hash));
  React.useEffect(() => {
    const sync = () => {
      const id = evidenceRecordFromHash(window.location.hash);
      setSelected(id);
      if (id) {
        const item = document.getElementById('evidence-' + id);
        item?.focus({ preventScroll: true });
        item?.scrollIntoView({ block: 'start' });
      }
    };
    window.addEventListener('hashchange', sync);
    sync();
    return () => window.removeEventListener('hashchange', sync);
  }, []);

  const pt = lang === 'pt';
  return (
    <section aria-labelledby="trace-title" className="mt-8 rounded-2xl border border-zinc-700 bg-zinc-900/60 p-5 sm:p-8">
      <p className="text-xs font-semibold uppercase tracking-widest text-cyan-300">{pt ? 'Rastreabilidade, não veredito' : 'Traceability, not a verdict'}</p>
      <h2 id="trace-title" className="mt-2 text-2xl font-semibold text-zinc-50">{pt ? 'Do documento à restrição formal' : 'From documents to formal constraints'}</h2>
      <p className="mt-3 max-w-3xl text-sm leading-relaxed text-zinc-300">
        {pt
          ? 'Cada ligação aponta para a ocorrência exata ou código condicional da PR #1 em revisão. IDs repetidos são separados; nenhum link transforma hipótese em observação.'
          : 'Each link points to a specific occurrence or conditional code in the unmerged PR #1. Reused IDs are distinguished; no link turns a hypothesis into an observation.'}
      </p>
      <ol aria-label={pt ? 'Etapas de verificação científica' : 'Scientific verification stages'} className="mt-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-5">
        {flow.map((step) => (
          <li key={step.name.pt} className="rounded-lg border border-zinc-700 bg-zinc-950/60 px-3 py-3 text-xs">
            <span className="block font-semibold text-zinc-200">{step.name[lang]}</span>
            <span className="mt-1 block text-amber-200">{step.state[lang]}</span>
          </li>
        ))}
      </ol>
      <ol className="mt-6 grid gap-4 lg:grid-cols-2">
        {records.map((r) => (
          <li
            id={'evidence-' + r.id}
            key={r.id}
            tabIndex={-1}
            aria-labelledby={'title-' + r.id}
            className={'scroll-mt-44 rounded-xl border p-4 outline-offset-4 ' + (selected === r.id ? 'border-cyan-400 bg-cyan-950/20 ring-2 ring-cyan-400/50' : 'border-zinc-700')}
          >
            <p className="font-mono text-xs text-cyan-300">{r.ids}</p>
            <h3 id={'title-' + r.id} className="mt-1 font-semibold text-zinc-100">{r.label[lang]}</h3>
            <p className="mt-2 text-sm leading-relaxed text-zinc-300">{r.description[lang]}</p>
            <p className="mt-2 text-sm leading-relaxed text-zinc-300"><strong>{pt ? 'Premissa/limite:' : 'Assumption/limit:'}</strong> {r.premise[lang]}</p>
            <p className="mt-3 text-xs text-amber-200">{r.status[lang]}</p>
            <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm">
              <a href={hashForEvidenceRecord(r.id)} aria-label={(pt ? 'Link permanente: ' : 'Permalink: ') + r.ids} className="text-cyan-300 underline underline-offset-4 focus-visible:outline">{pt ? 'Link deste registro' : 'Record permalink'}</a>
              <a href={r.evidence} target="_blank" rel="noopener noreferrer" className="text-cyan-300 underline underline-offset-4 focus-visible:outline">{pt ? 'Fonte / ocorrência' : 'Source / occurrence'}</a>
              {r.proof && <a href={r.proof} target="_blank" rel="noopener noreferrer" className="text-cyan-300 underline underline-offset-4 focus-visible:outline">{'Lean: ' + r.proofName}</a>}
            </div>
          </li>
        ))}
      </ol>
      <aside aria-label={pt ? 'Intervalos e simulação' : 'Intervals and simulation'} className="mt-6 border-t border-zinc-700 pt-5">
        <h3 className="font-semibold text-zinc-100">{pt ? 'Domínio admissível e intervalos numéricos' : 'Admissible domain and numerical intervals'}</h3>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-zinc-300">
          {pt
            ? 'Neste snapshot não há domínio físico comprovadamente não vazio e reduzido nem intervalos numéricos validados para hora, latitude, longitude, arrasto ou probabilidade de impacto. Para exibir valores, serão necessários premissas, unidades, erro numérico, fonte e holdouts reproduzíveis.'
            : 'This snapshot has no proven nonempty, reduced physical domain or validated numerical intervals for time, latitude, longitude, drag or impact probability. Publishing values requires assumptions, units, numerical error, provenance and reproducible holdouts.'}
        </p>
        <p className="mt-2 text-sm text-zinc-300">
          <strong className="text-amber-200">{pt ? 'Resultado atual: indeterminado.' : 'Current outcome: undetermined.'}</strong>{' '}
          {pt ? 'Conde não está demonstrado nem excluído.' : 'Conde is neither proven nor excluded.'}{' '}
          <a className="text-cyan-300 underline underline-offset-4" href="https://github.com/franklinbaldo/conde-incident/pull/5" target="_blank" rel="noopener noreferrer">{pt ? 'Simulador físico em revisão' : 'Physical simulator under review'}</a>
        </p>
      </aside>
    </section>
  );
}
