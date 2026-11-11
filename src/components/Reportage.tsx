import React, { useMemo, useState } from 'react';
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
  // Safe, limited Markdown typography: links, emphasis, bold and inline code.
  const token = /(\[[^\]]+\]\(https?:\/\/[^\s)]+\)|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  const out: React.ReactNode[] = [];
  let last = 0;
  for (const m of text.matchAll(token)) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const val = m[0], key = m.index;
    if (val.startsWith('[')) {
      const i = val.indexOf('](');
      const href = val.slice(i + 2, -1);
      out.push(<a key={key} className="text-cyan-300 underline decoration-cyan-800 underline-offset-4 hover:text-cyan-100" href={href} target="_blank" rel="noopener noreferrer">{val.slice(1, i)}</a>);
    } else if (val.startsWith('**')) out.push(<strong key={key} className="font-semibold text-zinc-100">{val.slice(2, -2)}</strong>);
    else if (val.startsWith('*')) out.push(<em key={key}>{val.slice(1, -1)}</em>);
    else out.push(<code key={key} className="rounded bg-zinc-800 px-1.5 py-0.5 text-sm text-cyan-200">{val.slice(1,-1)}</code>);
    last = m.index + val.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

function StoryBody({ markdown }: {markdown: string}) {
  const blocks = markdown.split(/\n\s*\n/).map(s => s.trim()).filter(Boolean);
  return <div className="space-y-6 text-[16px] leading-[1.85] text-zinc-300 md:text-[17px]">
    {blocks.map((block, i) => {
      if (block === '---') return <hr key={i} className="my-10 border-zinc-700"/>;
      const h = /^(#{1,3})\s+([\s\S]*)$/.exec(block);
      if (h) return h[1].length===1
        ? <h2 key={i} className="pt-3 text-3xl font-semibold leading-tight tracking-tight text-white">{inlineText(h[2])}</h2>
        : <h3 key={i} className="pt-4 text-xl font-semibold leading-snug text-white">{inlineText(h[2])}</h3>;
      if (block.startsWith('> ')) return <blockquote key={i} className="border-l-2 border-cyan-500 bg-cyan-950/20 px-5 py-4 italic text-zinc-200">{inlineText(block.replace(/^>\s?/gm, '').replace(/\n/g,' '))}</blockquote>;
      if (block.startsWith('- ')) return <ul key={i} className="list-disc space-y-2 pl-6">{block.split('\n').map((line, j)=><li key={j}>{inlineText(line.replace(/^-\s*/,''))}</li>)}</ul>;
      return <p key={i}>{inlineText(block.replace(/\n/g, ' '))}</p>;
    })}
  </div>;
}

export function Reportage({ lang }: {lang: 'pt'|'en'}) {
  const pt=lang==='pt';
  const [selected, setSelected] = useState<string|null>(null);
  const current = useMemo(()=>allStories.find(s=>s.slug===selected), [selected]);
  return <div className="space-y-8 pb-16">
    <section className="relative overflow-hidden rounded-3xl border border-zinc-800 bg-[radial-gradient(ellipse_at_85%_0%,rgba(14,116,144,.21),transparent_58%),linear-gradient(145deg,#111827,#09090b)] px-6 py-10 md:px-12 md:py-14">
      <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-[.25em] text-cyan-300"><Feather size={15}/>{pt?'Caderno de investigação · Conde, Bahia':'Investigative journal · Conde, Brazil'}</div>
      <h1 className="mt-6 max-w-3xl font-serif text-4xl font-semibold leading-tight tracking-tight text-white md:text-6xl">{pt?'A história por trás da investigação':'The story behind the investigation'}</h1>
      <p className="mt-5 max-w-2xl text-sm leading-relaxed text-zinc-300 md:text-base">{pt?'Cada capítulo acompanha uma descoberta, uma dúvida ou uma hipótese que resistiu a um teste. Jornalismo narrativo com as fontes à vista, sem confundir a notícia com o acontecimento.':'Each chapter follows a discovery, a question, or a hypothesis tested against evidence. Narrative journalism with sources in plain view.'}</p>
      <div className="mt-8 flex items-center gap-3 text-xs text-zinc-400"><BookOpen size={16}/>{allStories.length} {pt?'capítulo(s) em Markdown':'Markdown chapter(s)'}</div>
    </section>
    {current ? <>
      <button onClick={()=>setSelected(null)} className="flex items-center gap-2 text-sm text-cyan-300 hover:text-cyan-100"><ArrowLeft size={16}/>{pt?'Todos os capítulos':'All chapters'}</button>
      <article className="mx-auto max-w-3xl rounded-2xl border border-zinc-800 bg-zinc-900/40 px-6 py-9 md:px-12 md:py-14">
        <div className="flex flex-wrap gap-4 text-xs font-mono text-zinc-400"><span className="text-cyan-300">{pt?'CAPÍTULO':'CHAPTER'} {current.chapter}</span><span>{current.date}</span><span>{current.author}</span></div>
        <h2 className="mt-5 font-serif text-4xl font-semibold leading-tight text-white md:text-5xl">{current.title}</h2>
        <p className="mt-5 border-b border-zinc-700 pb-8 text-lg leading-relaxed text-zinc-400">{current.summary}</p>
        <StoryBody markdown={current.body.replace(/^# .+\n\s*/, '')}/>
        <footer className="mt-12 border-t border-zinc-700 pt-6 text-xs text-zinc-400"><FileText size={14} className="mr-2 inline"/>{pt?'Texto-fonte editável:':'Editable Markdown source:'} <a className="text-cyan-300 underline" href={`https://github.com/franklinbaldo/conde-incident/blob/main/stories/${current.slug}.md`} target="_blank" rel="noopener noreferrer">{current.slug}.md</a></footer>
      </article>
    </> : allStories.length ? <section className="grid gap-5 md:grid-cols-2">
      {allStories.map((s,i)=><button key={s.slug} onClick={()=>setSelected(s.slug)} className={`group flex flex-col items-start rounded-2xl border border-zinc-800 bg-zinc-900/65 p-7 text-left transition hover:-translate-y-0.5 hover:border-cyan-700/70 hover:bg-zinc-900 ${i===0?'md:col-span-2 md:p-10':''}`}>
        <div className="flex items-center gap-3 text-xs font-mono text-cyan-400"><span>{pt?'CAPÍTULO':'CHAPTER'} {s.chapter}</span><CalendarDays size={13}/><span className="text-zinc-400">{s.date}</span></div>
        <h2 className={`mt-5 max-w-3xl font-serif font-semibold leading-tight text-white ${i===0?'text-3xl md:text-4xl':'text-2xl'}`}>{s.title}</h2>
        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-zinc-400">{s.summary}</p>
        <span className="mt-7 flex items-center gap-2 text-sm font-medium text-cyan-300">{pt?'Ler reportagem':'Read chapter'}<ArrowRight size={16} className="transition group-hover:translate-x-1"/></span>
      </button>)}
    </section> : <p className="rounded-xl border border-zinc-800 p-6 text-zinc-400">{pt?'Nenhum capítulo publicado.':'No chapters published.'}</p>}
    <p className="border-t border-zinc-800 pt-5 text-xs leading-relaxed text-zinc-500">{pt?'Os capítulos descrevem os documentos e as hipóteses da investigação, não substituem o registro auditável das fontes. Publicação no site depende de merge e implantação.':'Chapters explain evidence and hypotheses; they do not replace the auditable evidence registry. Publishing depends on merge and deployment.'}</p>
  </div>;
}
