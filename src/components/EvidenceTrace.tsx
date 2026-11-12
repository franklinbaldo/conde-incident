import React from 'react';

// This UI is a trace of *conditional* statements in the pinned PR #1 snapshot.
// It does not turn a model into a historical observation or certify a parameter interval.
const links = {
  c01: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L19',
  c02: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L20',
  c197: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905',
  c201: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L909',
  ambiguous: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L164',
  noDouble: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/formal/Conde1963/Core.lean#L32',
  dateOnly: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/formal/Conde1963/Core.lean#L96',
  monotone: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/formal/Conde1963/Core.lean#L105',
  holdout: 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/formal/Conde1963/Core.lean#L64',
};

const records = [
  {
    ids: 'C01, C02', label: 'Relato Tupi/FBIS',
    description: 'Documento contemporâneo da circulação da história, sem observação independente da suposta cratera.',
    evidence: links.c01, proof: links.noDouble, proofName: 'no_double_count_tupi',
    status: 'Documento e dependência registrados; impacto não verificado',
  },
  {
    ids: 'C197–C202', label: 'Data catalogada pela NASA',
    description: 'Boletim de 15/11/1963 registra o dia 8/11 para 1963-003B; não registra hora ou local terminal.',
    evidence: links.c197, proof: links.dateOnly, proofName: 'date_alone_does_not_identify_place',
    status: 'Dia documentado; localização não identificada',
  },
  {
    ids: 'C44–C46 (ocorrências distintas)', label: 'Restrições conflitantes e revisões',
    description: 'Os mesmos rótulos foram reutilizados na matriz. Não são chaves únicas e não podem ser fundidos sem proveniência.',
    evidence: links.ambiguous, proof: links.monotone, proofName: 'more_constraints_never_expand',
    status: 'Exige identificação por ocorrência antes de admissão formal',
  },
  {
    ids: 'Holdout NORAD 529', label: 'Controle de previsão',
    description: 'A desigualdade registrada no Lean compara entradas numéricas fixadas; não certifica órbita, solver nem ganho geral.',
    evidence: 'https://github.com/franklinbaldo/conde-incident/pull/20',
    proof: links.holdout, proofName: 'joint_model_did_not_beat_quadratic_on_holdout',
    status: 'Resultado condicional; calibração física independente pendente',
  },
] as const;

export function EvidenceTrace() {
  return (
    <section aria-labelledby="trace-title" className="mt-8 rounded-2xl border border-zinc-700 bg-zinc-900/60 p-5 sm:p-8">
      <p className="text-xs font-semibold uppercase tracking-widest text-cyan-300">Rastreabilidade, não veredito</p>
      <h2 id="trace-title" className="mt-2 text-2xl font-semibold text-zinc-50">Do documento à restrição formal</h2>
      <p className="mt-3 max-w-3xl text-sm leading-relaxed text-zinc-300">
        As ligações abaixo apontam para um snapshot da matriz e do código Lean 4.35.0 na PR #1, ainda em revisão.
        A prova verifica implicações das premissas, não autentica a fonte nem simula a física.
      </p>
      <ol className="mt-6 grid gap-4 lg:grid-cols-2">
        {records.map((r) => (
          <li key={r.ids} className="rounded-xl border border-zinc-700 p-4">
            <p className="font-mono text-xs text-cyan-300">{r.ids}</p>
            <h3 className="mt-1 font-semibold text-zinc-100">{r.label}</h3>
            <p className="mt-2 text-sm text-zinc-300">{r.description}</p>
            <p className="mt-3 text-xs text-amber-200">{r.status}</p>
            <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm">
              <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline" href={r.evidence} target="_blank" rel="noopener noreferrer">Fonte e ocorrência</a>
              <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline" href={r.proof} target="_blank" rel="noopener noreferrer">Lean: {r.proofName}</a>
            </div>
          </li>
        ))}
      </ol>
      <aside aria-label="Intervalos e simulação" className="mt-6 border-t border-zinc-700 pt-5">
        <h3 className="font-semibold text-zinc-100">Domínio admissível e intervalos numéricos</h3>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-zinc-300">
          Nenhum intervalo numérico de hora, longitude, latitude, coeficiente de arrasto ou probabilidade de impacto
          está validado por um solver com erro e holdouts neste snapshot. A monotonicidade lógica do conjunto de
          candidatos não comprova que ele seja não vazio. O simulador deve publicar limites, unidades, cenário,
          erro numérico e testes independentes antes que apareçam números aqui.
        </p>
        <p className="mt-2 text-sm text-zinc-300">
          Situação: <strong className="text-amber-200">indeterminado com premissas físicas abertas</strong>.
          A hipótese de impacto em Conde não está demonstrada nem excluída.
          <a className="ml-2 text-cyan-300 underline underline-offset-4" href="https://github.com/franklinbaldo/conde-incident/pull/4" target="_blank" rel="noopener noreferrer">Acompanhar o simulador em revisão</a>.
        </p>
      </aside>
    </section>
  );
}
