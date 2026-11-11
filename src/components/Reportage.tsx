import React, { useEffect, useMemo, useRef, useState } from 'react';
import { readSiteRoute, STORIES_INDEX, storyHref } from '../lib/storyRoutes';
import { parseStoryBlocks, tokenizeStoryInline } from '../lib/storyMarkdown';
import { ArrowLeft, ArrowRight, BookOpen, CalendarDays, Feather, FileText } from 'lucide-react';

// Vite bundles authored Markdown sources directly. The formatter deliberately
// renders React text nodes instead of using dangerouslySetInnerHTML.
const chapters = import.meta.glob('../../stories/*.md', { query: '?raw', import: 'default', eager: true }) as Record<string, string>;

type Story = {
  slug: string; title: string; date: string; summary: string;
  chapter: string; author: string; status: string; body: string;
};
function parseStory(path: string, raw: string): Story {
  const match = /^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/.exec(raw);
  const data: Record<string, string> = {};
  if (match) for (const line of match[1].split('\n')) {
    const entry = /^([a-zA-Z]+):\s*(.*)$/.exec(line);
    if (entry) data[entry[1]] = entry[2].trim().replace(/^["']|["']$/g, '');
  }
  return {
    slug: path.split('/').pop()!.replace(/\.md$/, ''),
    title: data.title || 'Sem título', date: data.date || '',
    summary: data.summary || '', chapter: data.chapter || '',
    author: data.author || 'Coruja', status: data.status || '',
    body: match ? match[2].trim() : raw.trim(),
  };
}
const allStories = Object.entries(chapters).map(([path, raw]) => parseStory(path, raw))
  .sort((a, b) => b.date.localeCompare(a.date) || b.chapter.localeCompare(a.chapter));

function inlineText(text: string): React.ReactNode[] {
  return tokenizeStoryInline(text).map((part, i) => {
    switch (part.kind) {
      case 'link':
        return <a key={i} className="break-words text-cyan-300 underline decoration-cyan-800 underline-offset-4 hover:text-cyan-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-400" href={part.href} target="_blank" rel="noopener noreferrer">{part.text}</a>;
      case 'strong':
        return <strong key={i} className="font-semibold text-zinc-100">{part.text}</strong>;
      case 'em':
        return <em key={i}>{part.text}</em>;
      case 'code':
        return <code key={i} className="break-words rounded bg-zinc-800 px-1.5 py-0.5 text-sm text-cyan-200">{part.text}</code>;
      default:
        return <React.Fragment key={i}>{part.text}</React.Fragment>;
    }
  });
}

function StoryBody({ markdown }: {markdown: string}) {
  const blocks = parseStoryBlocks(markdown);
  return <div className="space-y-6 text-[16px] leading-[1.85] text-zinc-300 md:text-[17px]">
    {blocks.map((block, i) => {
      switch (block.kind) {
        case 'rule':
          return <hr key={i} className="my-10 border-zinc-700"/>;
        case 'heading':
          return block.level === 1
            ? <h2 key={i} className="pt-3 text-3xl font-semibold leading-tight tracking-tight text-white">{inlineText(block.text)}</h2>
            : block.level === 2
              ? <h3 key={i} className="pt-4 text-xl font-semibold leading-snug text-white">{inlineText(block.text)}</h3>
              : <h4 key={i} className="pt-3 text-lg font-semibold leading-snug text-white">{inlineText(block.text)}</h4>;
        case 'quote':
          return <blockquote key={i} className="border-l-2 border-cyan-500 bg-cyan-950/20 px-5 py-4 text-zinc-200">{inlineText(block.text)}</blockquote>;
        case 'list': {
          const items = block.items.map((item, j) => <li key={j}>{inlineText(item)}</li>);
          return block.ordered
            ? <ol key={i} start={block.start} className="list-decimal space-y-2 pl-6">{items}</ol>
            : <ul key={i} className="list-disc space-y-2 pl-6">{items}</ul>;
        }
        case 'code':
          return <pre key={i} className="overflow-x-auto rounded-lg border border-zinc-700 bg-zinc-950 p-4 text-sm leading-relaxed text-zinc-200"><code>{block.text}</code></pre>;
        default:
          return <p key={i}>{inlineText(block.text)}</p>;
      }
    })}
  </div>;
}

export function Reportage({ lang }: {lang: 'pt'|'en'}) {
  const pt=lang==='pt';
  const [selected, setSelected] = useState<string|null>(() => {
    const route = readSiteRoute(window.location.hash);
    return route?.kind === 'stories' ? route.slug : null;
  });
  const current = useMemo(()=>allStories.find(s=>s.slug===selected), [selected]);
  const titleRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    const onHashChange = () => {
      const route = readSiteRoute(window.location.hash);
      if (route?.kind === 'stories') setSelected(route.slug);
    };
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  useEffect(() => {
    if (current) titleRef.current?.focus();
  }, [current]);

  // Runtime metadata follows the selected deep link. Static Pages crawlers do
  // not execute fragment routes, so this is browser UX, not per-story OG preview.
  useEffect(() => {
    const previousTitle = document.title;
    const description = document.querySelector<HTMLMetaElement>('meta[name="description"]');
    const previousDescription = description?.content;
    document.title = current
      ? current.title + ' | Caderno de histórias · Conde'
      : 'Caderno de histórias | Caso Conde (1963)';
    if (description) {
      description.content = current?.summary || 'Reportagens documentais com fontes e limites da investigação de Conde (1963).';
    }
    return () => {
      document.title = previousTitle;
      if (description && previousDescription !== undefined) description.content = previousDescription;
    };
  }, [current]);

  return <div className="space-y-8 pb-16">
    <section className="relative overflow-hidden rounded-3xl border border-zinc-800 bg-[radial-gradient(ellipse_at_85%_0%,rgba(14,116,144,.21),transparent_58%),linear-gradient(145deg,#111827,#09090b)] px-6 py-10 md:px-12 md:py-14">
      <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[.25em] text-cyan-300"><Feather size={15}/>{pt?'Caderno de investigação · Conde, Bahia':'Investigative journal · Conde, Brazil'}</div>
      <h1 className="mt-6 max-w-3xl font-serif text-4xl font-semibold leading-tight tracking-tight text-white md:text-6xl">{pt?'A história por trás da investigação':'The story behind the investigation'}</h1>
      <p className="mt-5 max-w-2xl text-sm leading-relaxed text-zinc-300 md:text-base">{pt?'Cada capítulo acompanha uma descoberta, uma dúvida ou uma hipótese que resistiu a um teste. Jornalismo narrativo com as fontes à vista, sem confundir a notícia com o acontecimento.':'Each chapter follows a discovery, a question, or a hypothesis tested against evidence. Narrative journalism with sources in plain view.'}</p>
      <div className="mt-8 flex items-center gap-3 text-xs text-zinc-400"><BookOpen size={16}/>{allStories.length} {pt?'capítulo(s) em Markdown':'Markdown chapter(s)'}</div>
    </section>
    {selected && !current ? <section role="status" className="rounded-2xl border border-amber-800/60 bg-amber-950/20 p-7">
      <h2 className="text-xl font-semibold text-amber-200">{pt?'Capítulo não encontrado':'Chapter not found'}</h2>
      <p className="mt-3 text-sm leading-relaxed text-zinc-300">{pt?'O endereço não corresponde a um capítulo incluído nesta versão.':'This link does not match a chapter included in this version.'}</p>
      <a href={STORIES_INDEX} className="mt-5 inline-flex items-center gap-2 rounded text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-cyan-400"><ArrowLeft size={16}/>{pt?'Voltar ao caderno':'Back to the journal'}</a>
    </section> : current ? <>
      <a href={STORIES_INDEX} className="inline-flex items-center gap-2 rounded text-sm text-cyan-300 hover:text-cyan-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-cyan-400"><ArrowLeft size={16}/>{pt?'Todos os capítulos':'All chapters'}</a>
      <article lang="pt-BR" aria-labelledby="story-title" className="mx-auto max-w-3xl rounded-2xl border border-zinc-800 bg-zinc-900/40 px-5 py-9 sm:px-6 md:px-12 md:py-14">
        <div className="flex flex-wrap gap-4 text-xs font-mono text-zinc-400"><span className="text-cyan-300">{pt?'CAPÍTULO':'CHAPTER'} {current.chapter}</span><time dateTime={current.date}>{current.date}</time><span>{current.author}</span>{current.status && <span className="rounded border border-zinc-700 px-2 py-0.5 text-zinc-300">{current.status}</span>}</div>
        <h2 ref={titleRef} id="story-title" tabIndex={-1} className="mt-5 font-serif text-3xl font-semibold leading-tight text-white focus:outline-none sm:text-4xl md:text-5xl">{current.title}</h2>
        <p className="mt-5 border-b border-zinc-700 pb-8 text-lg leading-relaxed text-zinc-400">{current.summary}</p>
        <StoryBody markdown={current.body.replace(/^# .+\n\s*/, '')}/>
        <aside aria-label={pt?'Proveniência e limites':'Provenance and limits'} className="mt-10 rounded-xl border border-cyan-900/50 bg-cyan-950/15 p-5 text-sm leading-relaxed text-zinc-300">
          <p>{pt?'Para conferir a classificação e a dependência das fontes, consulte a matriz cumulativa C001–C238 da PR #1 (versão de pesquisa ainda em revisão). A notícia da esfera e a data orbital são registros distintos, não testemunhos independentes de uma queda.':'Check source classification and dependencies in the C001–C238 research matrix from PR #1 (review-stage snapshot). The radio report and orbital date are distinct records, not independent observations of an impact.'}</p>
          <a href="https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md" target="_blank" rel="noopener noreferrer" className="mt-3 inline-block rounded font-medium text-cyan-300 underline underline-offset-4 hover:text-cyan-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-400">{pt?'Abrir matriz de evidências (PR #1)':'Open evidence matrix (PR #1)'}</a>
        </aside>
        <footer className="mt-12 border-t border-zinc-700 pt-6 text-xs text-zinc-400"><FileText size={14} className="mr-2 inline"/>{pt?'Texto-fonte editável:':'Editable Markdown source:'} <a className="text-cyan-300 underline underline-offset-4 hover:text-cyan-100" href={`https://github.com/franklinbaldo/conde-incident/blob/main/stories/${current.slug}.md`} target="_blank" rel="noopener noreferrer">{current.slug}.md</a></footer>
      </article>
    </> : allStories.length ? <section className="grid gap-5 md:grid-cols-2">
      {allStories.map((s,i)=><a key={s.slug} href={storyHref(s.slug)} className={`group flex flex-col items-start rounded-2xl border border-zinc-800 bg-zinc-900/65 p-6 text-left transition hover:border-cyan-700/70 hover:bg-zinc-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-400 motion-safe:hover:-translate-y-0.5 sm:p-7 ${i===0?'md:col-span-2 md:p-10':''}`}>
        <div className="flex items-center gap-3 text-xs font-mono text-cyan-400"><span>{pt?'CAPÍTULO':'CHAPTER'} {s.chapter}</span><CalendarDays size={13}/><time dateTime={s.date} className="text-zinc-400">{s.date}</time></div>
        <h2 className={`mt-5 max-w-3xl font-serif font-semibold leading-tight text-white ${i===0?'text-3xl md:text-4xl':'text-2xl'}`}>{s.title}</h2>
        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-zinc-400">{s.summary}</p>
        <span className="mt-7 flex items-center gap-2 text-sm font-medium text-cyan-300">{pt?'Ler reportagem':'Read chapter'}<ArrowRight size={16} className="transition group-hover:translate-x-1"/></span>
      </a>)}
    </section> : <p className="rounded-xl border border-zinc-800 p-6 text-zinc-400">{pt?'Nenhum capítulo publicado.':'No chapters published.'}</p>}
    <p className="border-t border-zinc-800 pt-5 text-xs leading-relaxed text-zinc-500">{pt?'Os capítulos descrevem os documentos e as hipóteses da investigação, não substituem o registro auditável das fontes. Publicação no site depende de merge e implantação.':'Chapters explain evidence and hypotheses; they do not replace the auditable evidence registry. Publishing depends on merge and deployment.'}</p>
  </div>;
}
