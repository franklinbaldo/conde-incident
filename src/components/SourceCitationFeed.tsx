import React, { useEffect, useState } from 'react';
import {
  citationContext, declaredLineageContext, isCitationFeed, isDeclaredDependenceFeed, matrixOccurrenceUrl,
  type CitationFeed, type DeclaredDependenceFeed,
} from '../lib/sourceCitationAudit';

type Props = { lang: 'pt' | 'en' };
const examples = ['C197#1', 'C198#1', 'C232#1', 'C01#1', 'C02#1', 'C03#1', 'C44#1'];

// Show HTTPS documentary Markdown links as native links, never as clipped URL text.
// Everything outside the narrow [label](https://...) grammar stays verbatim;
// React escapes it instead of interpreting arbitrary Markdown/HTML from the feed.
function documentaryClaimParts(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  const link = /\[([^\]\r\n]+)\]\((https:\/\/[^\s)]+)\)/g;
  let cursor = 0;
  for (const match of text.matchAll(link)) {
    const start = match.index;
    parts.push(text.slice(cursor, start));
    parts.push(
      <a key={start} href={match[2]} target="_blank" rel="noopener noreferrer"
        className="text-cyan-300 underline underline-offset-2 [overflow-wrap:anywhere] focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
        {match[1]}
      </a>,
    );
    cursor = start + match[0].length;
  }
  parts.push(text.slice(cursor));
  return parts;
}

export function SourceCitationFeed({ lang }: Props) {
  const pt = lang === 'pt';
  const [feed, setFeed] = useState<CitationFeed | null>(null);
  const [error, setError] = useState(false);
  const [dependenceFeed, setDependenceFeed] = useState<DeclaredDependenceFeed | null>(null);
  const [dependenceError, setDependenceError] = useState(false);
  const [input, setInput] = useState('C197#1');
  const [selected, setSelected] = useState('C197#1');

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${import.meta.env.BASE_URL}data/conde-source-citations.json`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error('citation feed HTTP error');
        const content: unknown = await response.json();
        if (!isCitationFeed(content)) throw new Error('unsupported citation feed');
        setFeed(content);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          console.error('Could not load documentary citation feed', reason);
          setError(true);
        }
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${import.meta.env.BASE_URL}data/conde-declared-dependence.json`, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error('documentary lineage HTTP error');
        const content: unknown = await response.json();
        if (!isDeclaredDependenceFeed(content)) throw new Error('unsupported documentary lineage feed');
        setDependenceFeed(content);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          console.error('Could not load declared documentary lineage', reason);
          setDependenceError(true);
        }
      });
    return () => controller.abort();
  }, []);

  const context = feed && citationContext(feed, selected);
  return (
    <section aria-labelledby="source-citations-heading" className="rounded-xl border border-cyan-900/70 bg-zinc-900 p-4 sm:p-6 space-y-4">
      <div className="space-y-2">
        <h3 id="source-citations-heading" className="text-lg font-semibold text-zinc-100">
          {pt ? 'Citações documentais por ocorrência' : 'Documentary citations by occurrence'}
        </h3>
        <p className="text-sm leading-relaxed text-zinc-300">
          {pt
            ? 'Explore a proveniência da matriz cumulativa. Citações da mesma obra não são testemunhos independentes. Um documento pode comprovar que um relato existiu, sem comprovar o evento físico relatado.'
            : 'Explore the cumulative matrix provenance. Citations to the same work are not independent witnesses. A document may establish that a report existed without proving the reported physical event.'}
        </p>
      </div>
      <form className="flex flex-wrap items-end gap-2" onSubmit={(event) => { event.preventDefault(); setSelected(input); }}>
        <label htmlFor="citation-occurrence" className="flex flex-col gap-1 text-sm text-zinc-200">
          {pt ? 'ID e ocorrência exatos (ex.: C197#1)' : 'Exact ID and occurrence (e.g. C197#1)'}
          <input id="citation-occurrence" name="occurrence" value={input} onChange={(event) => setInput(event.target.value)}
            className="rounded-md border border-zinc-600 bg-zinc-950 px-3 py-2 text-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
            spellCheck={false} autoComplete="off" />
        </label>
        <button type="submit" className="rounded-md border border-cyan-600 bg-cyan-950 px-4 py-2 text-sm font-medium text-cyan-100 hover:bg-cyan-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
          {pt ? 'Consultar' : 'Look up'}
        </button>
      </form>
      <div className="flex flex-wrap gap-2" aria-label={pt ? 'Ocorrências de exemplo' : 'Example occurrences'}>
        {examples.map((id) => (
          <button key={id} type="button" onClick={() => { setInput(id); setSelected(id); }}
            aria-pressed={selected === id}
            className="rounded border border-zinc-700 px-2 py-1 text-xs font-mono text-zinc-200 hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
            {id}
          </button>
        ))}
      </div>

      <div aria-live="polite" aria-atomic="true" className="min-w-0 text-sm text-zinc-200 [overflow-wrap:anywhere]">
        {error && <p role="alert">{pt ? 'Feed indisponível ou formato não reconhecido. Nenhuma citação foi confirmada nesta consulta.' : 'Feed unavailable or unrecognized format. No citations were confirmed in this lookup.'}</p>}
        {!feed && !error && <p>{pt ? 'Carregando feed documental…' : 'Loading documentary feed…'}</p>}
        {context?.state === 'invalid' && <p>{pt ? 'Informe Cnn#ocorrência, incluindo #1. C44, C45 e C46 possuem IDs repetidos.' : 'Enter Cnn#occurrence, including #1. C44, C45 and C46 contain colliding IDs.'}</p>}
        {context?.state === 'unmapped' && <p>
          <strong>{context.occurrence}</strong>: {pt
            ? 'UNMAPPED: nenhuma citação curada para esta ocorrência no feed parcial. Isso não significa que a evidência ou sua fonte não exista.'
            : 'UNMAPPED: no curated citation for this occurrence in this partial feed. This does not mean the evidence or source does not exist.'}
        </p>}
        {context?.state === 'mapped' && (
          <div className="space-y-3">
            <p><strong className="font-mono text-cyan-200">{context.occurrence}</strong> · {documentaryClaimParts(context.record.claim_text)}</p>
            <p className="text-xs text-amber-200">{pt
              ? `${context.records.length} referências documentais curadas para esta ocorrência. Não equivalem a testemunhos independentes nem a novas observações físicas.`
              : `${context.records.length} curated documentary references for this occurrence. These are not independent witnesses or additional physical observations.`}</p>
            <ol className="space-y-4" aria-label={pt ? 'Fontes desta ocorrência' : 'Sources for this occurrence'}>
              {context.records.map((record, index) => {
                const lineage = feed && dependenceFeed
                  ? declaredLineageContext(dependenceFeed, feed, record) : null;
                const related = feed?.records.filter((item) =>
                  item.work_id === record.work_id && item.occurrence !== record.occurrence) ?? [];
                return (
                  <li key={`${record.occurrence}-${record.source_id}`} className="rounded-lg border border-zinc-700 bg-zinc-950/60 p-3 space-y-3">
                    <h4 className="font-semibold text-zinc-100 break-all">
                      {index + 1}. <code>{record.source_id}</code>
                    </h4>
            <dl className="grid gap-2 sm:grid-cols-2 text-xs">
              <div><dt className="text-zinc-400">{pt ? 'Família da fonte' : 'Source family'}</dt><dd className="font-mono break-words">{record.source_family}</dd></div>
              <div><dt className="text-zinc-400">{pt ? 'Obra documental' : 'Documentary work'}</dt><dd className="font-mono break-words">{record.work_id}</dd></div>
              <div><dt className="text-zinc-400">{pt ? 'Tipo / relação' : 'Type / relation'}</dt><dd className="font-mono break-words">{record.relation}</dd></div>
              <div><dt className="text-zinc-400">{pt ? 'Limite / estado' : 'Limit / status'}</dt><dd className="font-mono break-words">{record.scope}</dd></div>
            </dl>
            <p className="text-xs text-amber-200">{pt
              ? 'Sem confirmação de impacto em Conde, hora ou longitude de reentrada. Este vínculo não fornece uma observação física adicional.'
              : 'No confirmed impact in Conde, reentry time or longitude. This link does not add an independent physical observation.'}</p>
            <p className="text-xs text-zinc-300">{record.locator}</p>
            <div className="flex flex-wrap gap-4 text-sm">
              {record.citation_url.startsWith('https://') && (
                <a href={record.citation_url} rel="noopener noreferrer" target="_blank" className="text-cyan-300 underline underline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
                  {pt ? 'Abrir fonte externa' : 'Open external source'}
                </a>
              )}
              <a href={matrixOccurrenceUrl(record.matrix_line)} rel="noopener noreferrer" target="_blank" className="text-cyan-300 underline underline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
                {pt ? 'Abrir linha da matriz' : 'Open matrix row'} {record.matrix_line}
              </a>
            </div>
            <section aria-labelledby={`citation-lineage-${index}`} className="rounded border border-zinc-700 p-3 space-y-2 text-xs">
              <h4 id={`citation-lineage-${index}`} className="font-semibold text-zinc-100">
                {pt ? 'Ancestralidade documental declarada' : 'Declared documentary ancestry'}
              </h4>
              <p className="text-zinc-300">
                {pt
                  ? 'As setas representam relações documentadas entre fontes, não sensores ou testemunhas adicionais. A ausência de uma seta não comprova independência.'
                  : 'Arrows represent declared relationships between sources, not additional sensors or witnesses. A missing arrow does not establish independence.'}
              </p>
              {lineage?.state === 'declared' && lineage.paths.length > 0 ? (
                <ol className="space-y-2">
                  {lineage.paths.map((path, index) => (
                    <li key={`${path.upstream_source_id}-${index}`} className="rounded bg-zinc-950/70 p-2">
                      <p className="text-zinc-400">{pt ? 'Origem declarada' : 'Declared upstream source'}: <code className="break-all text-zinc-200">{path.upstream_source_id}</code></p>
                      <ul className="mt-1 space-y-1">
                        {path.edges.map((edge, edgeIndex) => (
                          <li key={`${edge.from}-${edge.to}-${edgeIndex}`} className="break-words text-zinc-200">
                            <code>{edge.from}</code> → <code>{edge.to}</code> (<code>{edge.kind}</code>)
                          </li>
                        ))}
                      </ul>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="text-amber-200" role="status">
                  {dependenceError
                    ? (pt ? 'Feed de genealogia indisponível ou inválido; nenhuma relação de independência pode ser inferida.' : 'Lineage feed unavailable or invalid; no independence relationship can be inferred.')
                    : !dependenceFeed
                      ? (pt ? 'Carregando genealogia…' : 'Loading ancestry…')
                      : lineage?.state === 'snapshot-mismatch'
                        ? (pt ? 'Snapshot da matriz divergente; nenhuma cadeia pode ser associada.' : 'Matrix snapshot mismatch; no lineage can be attached.')
                        : lineage?.state === 'source-mismatch'
                          ? (pt ? 'Fonte ou família divergente; nenhuma cadeia pode ser associada.' : 'Source or family mismatch; no lineage can be attached.')
                          : (pt ? 'Nenhuma cadeia ancestral verificável foi declarada para esta fonte neste snapshot. Independência desconhecida.' : 'No verifiable upstream chain is declared for this source in this snapshot. Independence is unknown.')}
                </p>
              )}
            </section>
            <details className="rounded border border-zinc-700 p-3 text-xs">
              <summary className="cursor-pointer font-medium text-zinc-200">{pt ? 'Ocorrências relacionadas à mesma obra, não novos testemunhos' : 'Related occurrences of the same work, not additional witnesses'} ({related.length})</summary>
              <ul className="mt-2 space-y-1">
                {related.map((record) => <li key={`${record.occurrence}-${record.source_id}`} className="font-mono text-zinc-300">{record.occurrence}: {record.relation}</li>)}
              </ul>
            </details>
                  </li>
                );
              })}
            </ol>
          </div>
        )}
      </div>
      {feed && <p className="text-xs text-zinc-400">
        {pt ? 'Cobertura curada' : 'Curated coverage'}: {feed.curated_occurrences}/{feed.total_matrix_occurrences};
        {' '}{feed.unmapped_occurrences} UNMAPPED.
        {' '}{pt ? 'Versão da matriz (blob Git)' : 'Matrix revision (Git blob)'}: <code className="break-all">{feed.matrix_git_blob_sha1}</code>.
        {' '}{pt ? 'Nenhuma independência instrumental é presumida.' : 'No independent instrument is presumed.'}
      </p>}
    </section>
  );
}
