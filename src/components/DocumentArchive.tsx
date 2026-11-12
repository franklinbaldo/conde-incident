import React from 'react';
import { BookOpen, ExternalLink, FileText, Search, ShieldAlert } from 'lucide-react';
import { archiveEntries, type ArchiveKind, type ArchiveEntry } from '../lib/documentCatalog';
import { documentRecordFromHash, hashForDocumentRecord } from '../lib/labRoutes';

type Language = 'pt' | 'en';
const filters: readonly ('all' | ArchiveKind)[] = ['all', 'contemporary', 'derived', 'locator'];
const kindLabel: Record<ArchiveKind, Record<Language, string>> = {
  contemporary: { pt: 'Documento de época', en: 'Contemporary record' },
  derived: { pt: 'Fonte derivada ou retrospectiva', en: 'Derivative or retrospective source' },
  locator: { pt: 'Localizador, original não lido', en: 'Locator, original unread' },
};
const kindColor: Record<ArchiveKind, string> = {
  contemporary: 'border-emerald-800 bg-emerald-950/30 text-emerald-200',
  derived: 'border-cyan-800 bg-cyan-950/30 text-cyan-200',
  locator: 'border-amber-800 bg-amber-950/30 text-amber-200',
};

export function DocumentArchive({ lang }: { lang: Language }) {
  const pt = lang === 'pt';
  const [query, setQuery] = React.useState('');
  const [filter, setFilter] = React.useState<'all' | ArchiveKind>('all');
  const [selected, setSelected] = React.useState<string | null>(() => documentRecordFromHash(window.location.hash));

  React.useEffect(() => {
    const sync = () => {
      const id = documentRecordFromHash(window.location.hash);
      setSelected(id);
      if (id) {
        setQuery('');
        setFilter('all');
      }
    };
    window.addEventListener('hashchange', sync);
    sync();
    return () => window.removeEventListener('hashchange', sync);
  }, []);

  React.useEffect(() => {
    if (!selected) return;
    const card = document.getElementById('archive-' + selected);
    card?.focus({ preventScroll: true });
    card?.scrollIntoView({ block: 'start' });
  }, [selected, filter, query]);

  const normalized = query.trim().toLocaleLowerCase(lang === 'pt' ? 'pt-BR' : 'en');
  const results = archiveEntries.filter((entry: ArchiveEntry) => {
    if (filter !== 'all' && entry.kind !== filter) return false;
    const fields = [entry.id, entry.date, entry.title.pt, entry.title.en, entry.agency, entry.matrixIds];
    return fields.some((field) => field.toLocaleLowerCase(lang === 'pt' ? 'pt-BR' : 'en').includes(normalized));
  });

  return <section className="space-y-6 pb-12" aria-labelledby="archive-heading">
    <header className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 sm:p-7">
      <p className="mb-2 flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-cyan-300"><FileText size={16} aria-hidden="true" />{pt ? 'Arquivo e crítica de fontes' : 'Archive and source criticism'}</p>
      <h1 id="archive-heading" className="text-2xl font-semibold text-zinc-50 sm:text-3xl">{pt ? 'Documentos, registros e lacunas' : 'Documents, records and gaps'}</h1>
      <p className="mt-3 max-w-3xl text-sm leading-relaxed text-zinc-300">{pt
        ? 'Este inventário distingue documentos de época, compilações posteriores e recortes ainda não recuperados. A verificação da existência de um relato não demonstra que seu conteúdo aconteceu. Nenhuma transcrição literal é reproduzida sem cotejo com a página.'
        : 'This inventory separates contemporary records, later compilations and missing clippings. Verifying that a report exists does not establish that its claims occurred. No verbatim transcript is presented without page-level checking.'}</p>
      <p className="mt-3 text-xs text-amber-200"><ShieldAlert className="mr-1 inline-block h-4 w-4" aria-hidden="true" />{pt
        ? 'Estado científico: indeterminado. Sem hora ou posição terminal validada, domínio admissível certificado ou prova de impacto em Conde.'
        : 'Scientific outcome: undetermined. No validated terminal time or position, certified admissible domain or proof of impact at Conde.'}</p>
    </header>

    <div className="rounded-xl border border-zinc-700 bg-zinc-900/70 p-4 sm:p-5">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="archive-search" className="mb-1.5 block text-sm font-medium text-zinc-200">{pt ? 'Pesquisar documento, órgão ou ID' : 'Search document, agency or ID'}</label>
          <div className="relative"><Search size={16} className="pointer-events-none absolute left-3 top-3 text-zinc-400" aria-hidden="true" />
            <input id="archive-search" type="search" value={query} onChange={(e) => setQuery(e.target.value)}
              placeholder={pt ? 'Ex.: C197, FBIS, A-628' : 'e.g. C197, FBIS, A-628'}
              className="w-full rounded-lg border border-zinc-600 bg-zinc-950 py-2.5 pl-10 pr-3 text-sm text-zinc-100 placeholder:text-zinc-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300" />
          </div>
        </div>
        <div>
          <label htmlFor="archive-filter" className="mb-1.5 block text-sm font-medium text-zinc-200">{pt ? 'Tipo de fonte' : 'Source type'}</label>
          <select id="archive-filter" value={filter} onChange={(e) => setFilter(e.target.value as 'all' | ArchiveKind)}
            className="w-full rounded-lg border border-zinc-600 bg-zinc-950 px-3 py-2.5 text-sm text-zinc-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
            {filters.map((value) => <option key={value} value={value}>{value === 'all' ? (pt ? 'Todos os registros' : 'All records') : kindLabel[value][lang]}</option>)}
          </select>
        </div>
      </div>
      <p aria-live="polite" className="mt-3 text-xs text-zinc-300">{pt ? 'Registros exibidos:' : 'Displayed records:'} {results.length} / {archiveEntries.length}</p>
    </div>

    <div className="grid gap-4 lg:grid-cols-2">
      {results.map((entry) => <article
        key={entry.id} id={'archive-' + entry.id} tabIndex={-1}
        aria-labelledby={'archive-title-' + entry.id}
        className={'scroll-mt-44 rounded-xl border bg-zinc-900 p-5 outline-offset-4 focus-visible:outline-2 focus-visible:outline-cyan-300 ' +
          (selected === entry.id ? 'border-cyan-400 ring-2 ring-cyan-400/40' : 'border-zinc-700')}>
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <a className="font-mono font-semibold text-cyan-300 underline underline-offset-4" href={hashForDocumentRecord(entry.id)}
            aria-label={(pt ? 'Link permanente para ' : 'Permalink to ') + entry.id}>{entry.id.toUpperCase()}</a>
          <span className={'rounded border px-2 py-1 ' + kindColor[entry.kind]}>{kindLabel[entry.kind][lang]}</span>
          <span className="text-zinc-400">{entry.date}</span>
        </div>
        <h2 id={'archive-title-' + entry.id} className="mt-3 text-lg font-semibold leading-snug text-zinc-50">{entry.title[lang]}</h2>
        <p className="mt-1 break-words text-xs text-zinc-400">{entry.agency}</p>
        <dl className="mt-4 space-y-3 text-sm leading-relaxed">
          <div><dt className="font-semibold text-zinc-100">{pt ? 'O que o registro sustenta' : 'What the record supports'}</dt>
            <dd className="mt-1 text-zinc-300">{entry.finding[lang]}</dd></div>
          <div><dt className="font-semibold text-zinc-100">{pt ? 'Proveniência e independência' : 'Provenance and independence'}</dt>
            <dd className="mt-1 text-zinc-300">{entry.provenance[lang]}</dd></div>
          <div><dt className="font-semibold text-amber-200">{pt ? 'Incerteza e limite' : 'Uncertainty and limitation'}</dt>
            <dd className="mt-1 text-zinc-300">{entry.limitation[lang]}</dd></div>
        </dl>
        <nav aria-label={(pt ? 'Fontes para ' : 'Sources for ') + entry.id} className="mt-5 flex flex-wrap gap-x-5 gap-y-2 border-t border-zinc-700 pt-4 text-sm">
          <a className="inline-flex items-center gap-1 text-cyan-300 underline underline-offset-4 hover:text-cyan-100 focus-visible:outline-2" href={entry.originalUrl} target="_blank" rel="noopener noreferrer">
            <ExternalLink size={14} aria-hidden="true" />{entry.kind === 'locator' ? (pt ? 'Catálogo do acervo' : 'Collection catalogue') : (pt ? 'Documento ou auditoria' : 'Document or audit')}</a>
          <a className="text-cyan-300 underline underline-offset-4 hover:text-cyan-100 focus-visible:outline-2" href={entry.matrixUrl} target="_blank" rel="noopener noreferrer">
            {pt ? 'Matriz:' : 'Matrix:'} {entry.matrixIds}</a>
          <a className="inline-flex items-center gap-1 text-cyan-300 underline underline-offset-4 hover:text-cyan-100 focus-visible:outline-2" href={entry.evidenceHref}>
            <BookOpen size={14} aria-hidden="true" />Evidence / Lean</a>
        </nav>
      </article>)}
    </div>
    {results.length === 0 && <p role="status" className="rounded-lg border border-zinc-700 p-5 text-sm text-zinc-300">
      {pt ? 'Nenhum registro corresponde aos filtros. Isso não prova ausência documental.' : 'No record matches the filters. That does not establish historical absence.'}
    </p>}
    <p className="text-xs leading-relaxed text-zinc-400">{pt
      ? 'Fonte do inventário: matriz C01–C238 da PR #1 (snapshot pinado). Os documentos primários foram classificados por pesquisa anterior; esta revisão editorial não reinspecionou seus fac-símiles. A leitura de cada prova Lean é condicional às premissas, não certifica os fatos.'
      : 'Inventory source: C01–C238 matrix from PR #1 (pinned snapshot). Earlier research classified the primary documents; this editorial pass did not re-inspect their facsimiles. Lean proofs are conditional on premises, not historical certification.'}</p>
  </section>;
}
