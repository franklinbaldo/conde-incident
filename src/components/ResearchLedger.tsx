import React from 'react';
import { AlertTriangle, ArrowUpRight, BookOpen, CheckCircle2, FlaskConical, GitBranch, ShieldAlert } from 'lucide-react';

type Language = 'pt' | 'en';

const sources = [
  { id: 'NASA-1963-11-15', title: 'NASA · Satellite Situation Report (15 Nov 1963)', url: 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf', kind: 'Primary contemporary', finding: 'Table of decayed objects lists 1963-003B on 8 November; no terminal coordinates or time.' },
  { id: 'DOS-1963-11-14', title: 'US State Department · Diplomatic cable (14 Nov 1963)', url: 'https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf', kind: 'Primary contemporary', finding: 'Documents the diplomatic inquiry, not an independently observed impact.' },
  { id: 'BN-OJORNAL', title: 'Biblioteca Nacional · O Jornal, 9 Nov 1963', url: 'https://memoria.bn.gov.br/DocReader/110523_06/31712', kind: 'Archive locator only', finding: 'A precise page identifier is known; no Conde article has yet been verified on that page.' },
  { id: 'IGBH', title: 'Instituto Geográfico e Histórico da Bahia · Biblioteca', url: 'https://www.ighb.org.br/biblioteca', kind: 'Collection inventory', finding: 'Potential source for original Bahia newspapers; issue-specific pages not yet checked.' },
];

const chronology = [
  { time: '08 NOV 1963', title: 'Reentry date recorded', description: 'NASA reports the decay of object 1963-003B. Day only; no geographic impact location.', status: 'document' },
  { time: '08–09 NOV 1963', title: 'The Conde story circulates', description: 'A Rádio Tupi report was preserved through FBIS. This verifies the report, not its extraordinary claims.', status: 'report' },
  { time: '14 NOV 1963', title: 'US diplomatic inquiry', description: 'Embassy correspondence confirms an official effort to clarify the reported event.', status: 'document' },
  { time: '20 NOV 1963', title: 'Consular follow-up', description: 'A-628 describes inquiries and newspaper clippings. Original Bahia clippings remain a priority.', status: 'followup' },
];

const limits = [
  { title: 'Historical TLE provenance', detail: 'The current site carries one October 27 element set with RAAN 284.152°. Earlier research references another set near 198.5261°. Neither may be silently preferred without matching original records and epochs.' },
  { title: 'Phase uncertainty', detail: 'A plane can geometrically intersect the latitude of Conde without its object being there at reentry. The final orbital phase is not identified by the date alone.' },
  { title: 'Monte Carlo assumptions', detail: 'The legacy random-anomaly sampler is a geometric thought experiment, not a posterior probability of impact or a model-calibrated terminal orbit.' },
  { title: 'Dynamic triangulation', detail: 'Objects 527 and 529 can help constrain shared forces. Their later positions cannot be treated as fixed geographic fences for 528 without a fitted joint dynamical model.' },
];

export function ResearchLedger({ lang }: { lang: Language }) {
  const pt = lang === 'pt';
  return <div className="space-y-8 pb-12">
    <section className="relative overflow-hidden rounded-3xl border border-cyan-800/40 bg-gradient-to-br from-slate-900 via-zinc-950 to-cyan-950/30 px-6 py-10 md:p-12">
      <div className="absolute -right-20 -top-24 h-80 w-80 rounded-full border border-cyan-400/10 shadow-[0_0_120px_60px_rgba(8,145,178,.08)]" aria-hidden="true" />
      <div className="relative">
        <div className="mb-5 flex items-center gap-2 text-xs font-mono uppercase tracking-[.22em] text-cyan-300"><FlaskConical size={16} /> {pt ? 'Laboratório de evidências' : 'Evidence laboratory'}</div>
        <h1 className="max-w-4xl text-3xl font-semibold tracking-tight text-white md:text-5xl">{pt ? 'Conde, 1963: o que os documentos realmente permitem concluir?' : 'Conde, 1963: what can the evidence actually establish?'}</h1>
        <p className="mt-5 max-w-3xl text-base leading-relaxed text-zinc-300">{pt ? 'Uma investigação aberta sobre uma notícia extraordinária e uma reentrada orbital real. Documentos, modelos e conjecturas permanecem separados, inclusive quando se contradizem.' : 'An open investigation of an extraordinary news report and a real orbital decay. Documents, models and conjectures remain distinct, including where they disagree.'}</p>
        <div className="mt-7 flex flex-wrap gap-3 text-sm">
          <span className="rounded-full border border-emerald-700/60 bg-emerald-950/40 px-4 py-2 text-emerald-300">{pt ? 'Confirmado: registro de reentrada em 8/11' : 'Confirmed: reentry dated Nov 8'}</span>
          <span className="rounded-full border border-amber-700/60 bg-amber-950/30 px-4 py-2 text-amber-300">{pt ? 'Desconhecido: lugar e hora' : 'Unknown: place and time'}</span>
          <span className="rounded-full border border-zinc-700 bg-zinc-900/70 px-4 py-2 text-zinc-300">{pt ? 'Sem confirmação: queda em Conde' : 'Unverified: impact at Conde'}</span>
        </div>
      </div>
    </section>

    <section className="grid gap-4 md:grid-cols-3">
      {[
        { icon: CheckCircle2, title: pt ? 'Evidência contemporânea' : 'Contemporary evidence', value: '08.11.1963', detail: pt ? 'A data consta no boletim NASA de 15/11; o relatório não traz coordenadas.' : 'The November 15 NASA bulletin gives the date, not coordinates.' },
        { icon: GitBranch, title: pt ? 'Três objetos vinculados' : 'Three related objects', value: '527 · 528 · 529', detail: pt ? 'Origem comum não significa fase orbital comum meses depois.' : 'Common origin does not imply shared orbital phase months later.' },
        { icon: ShieldAlert, title: pt ? 'Local terminal' : 'Terminal location', value: pt ? 'Não identificado' : 'Not identified', detail: pt ? 'Nenhuma trajetória final foi validada independentemente.' : 'No terminal trajectory has been independently validated.' },
      ].map(c => <article key={c.title} className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6"><c.icon className="mb-5 h-5 w-5 text-cyan-400"/><div className="text-xs uppercase tracking-wider text-zinc-400">{c.title}</div><div className="mt-2 text-xl font-semibold text-white">{c.value}</div><p className="mt-3 text-sm leading-relaxed text-zinc-400">{c.detail}</p></article>)}
    </section>

    <section className="grid gap-6 lg:grid-cols-5">
      <div className="lg:col-span-3 rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 md:p-8">
        <div className="mb-7 flex items-center gap-3"><BookOpen className="text-cyan-400"/><h2 className="text-xl font-semibold">{pt ? 'Cronologia documental' : 'Documentary chronology'}</h2></div>
        <div className="space-y-7 border-l border-zinc-700 pl-6">{chronology.map(c => <article key={c.time} className="relative"><div className="absolute -left-[29px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-cyan-400 bg-zinc-900" /><div className="text-xs font-mono text-cyan-300">{c.time}</div><h3 className="mt-1 font-semibold text-zinc-100">{c.title}</h3><p className="mt-1 text-sm leading-relaxed text-zinc-400">{c.description}</p></article>)}</div>
      </div>
      <div className="lg:col-span-2 rounded-2xl border border-amber-800/40 bg-amber-950/10 p-6 md:p-8">
        <div className="mb-5 flex items-center gap-3"><AlertTriangle className="text-amber-400"/><h2 className="text-xl font-semibold">{pt ? 'Integridade da simulação' : 'Simulation integrity'}</h2></div>
        <p className="mb-5 text-sm leading-relaxed text-zinc-300">{pt ? 'A versão anterior misturava uma propagação SGP4 com alterações independentes de altura e longitude. Essa correção foi removida nesta revisão, mas a extrapolação ainda é exploratória.' : 'The earlier version combined SGP4 with independent altitude and longitude changes. That adjustment has been removed; extrapolation remains exploratory.'}</p>
        <div className="space-y-4">{limits.map(c=><div key={c.title} className="border-t border-amber-800/20 pt-3"><h3 className="text-sm font-medium text-amber-200">{c.title}</h3><p className="mt-1 text-xs leading-relaxed text-zinc-400">{c.detail}</p></div>)}</div>
      </div>
    </section>

    <section className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 md:p-8">
      <h2 className="text-xl font-semibold">{pt ? 'Fontes e cadeia de custódia' : 'Sources and provenance'}</h2>
      <p className="mt-2 mb-6 text-sm text-zinc-400">{pt ? 'Cada documento prova uma afirmação específica. Uma reprodução em outro veículo não é, por si só, corroboração independente.' : 'Each record supports a specific claim. Republication is not independent corroboration.'}</p>
      <div className="grid gap-3 sm:grid-cols-2">{sources.map(s=><a key={s.id} href={s.url} target="_blank" rel="noopener noreferrer" className="group rounded-xl border border-zinc-800 bg-zinc-950/60 p-5 transition hover:border-cyan-700"><div className="flex items-start justify-between gap-2"><div className="text-sm font-semibold text-zinc-100 group-hover:text-cyan-300">{s.title}</div><ArrowUpRight className="h-4 w-4 shrink-0 text-zinc-500"/></div><div className="mt-2 text-[11px] font-mono text-cyan-400">{s.kind} · {s.id}</div><p className="mt-3 text-xs leading-relaxed text-zinc-400">{s.finding}</p></a>)}</div>
    </section>
    <section className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 md:p-8">
      <h2 className="text-xl font-semibold">{pt ? 'Rastreabilidade das provas formais' : 'Formal-proof traceability'}</h2>
      <p className="mt-2 text-sm leading-relaxed text-zinc-400">{pt ? 'Os teoremas Lean verificam implicações lógicas condicionadas, não a autenticidade dos documentos nem a localização da reentrada. Os IDs levam à matriz cumulativa; repetições do mesmo documento não são corroboração independente.' : 'Lean theorems verify conditional logical implications, not the authenticity of documents or a reentry site. IDs link to the cumulative evidence matrix; repetitions of a document are not independent corroboration.'}</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {[
          { ids: 'C01', matrixLine: 20, label: pt ? 'Relato Tupi/FBIS, não queda comprovada' : 'Tupi/FBIS report, not proven impact', url: 'https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf' },
          { ids: 'C131', matrixLine: 502, label: pt ? 'Boletim NASA: dia de decaimento, sem lugar/hora' : 'NASA bulletin: decay day, not place/time', url: 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10' },
          { ids: 'C197', matrixLine: 905, label: pt ? 'Mesmo boletim NASA, não uma segunda observação' : 'Same NASA bulletin, not a second observation', url: 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10' },
        ].map(({ ids, label, url, matrixLine }) => (
          <div key={ids} className="rounded-xl border border-zinc-800 bg-zinc-950/50 p-4">
            <a href={`https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L${matrixLine}`} target="_blank" rel="noopener noreferrer" className="text-xs font-mono text-cyan-300 underline hover:text-white">{ids} · {pt ? 'matriz' : 'matrix'}</a>
            <p className="mt-2 text-sm text-zinc-300">{label}</p>
            <a href={url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-xs text-cyan-400 underline">{pt ? 'Documento de referência' : 'Reference document'}</a>
          </div>
        ))}
      </div>
      <a href="https://github.com/franklinbaldo/conde-incident/blob/feature/polvo-lean-audit-conditional-15/formal/Conde1963/Provenance.lean" target="_blank" rel="noopener noreferrer" className="mt-4 inline-block text-xs text-cyan-400 underline">{pt ? 'Provas condicionais em Lean 4.35.0 (em revisão)' : 'Conditional Lean 4.35.0 proofs (under review)'}</a>
    </section>
    <p className="text-xs text-zinc-500">{pt ? 'Nota de método: números condicionais e provas Lean de identificabilidade não certificam uma trajetória SGP4. Nenhum dado experimental novo é criado por esta interface.' : 'Method note: conditional calculations and Lean identifiability proofs do not certify an SGP4 trajectory. This interface creates no new experimental observations.'}</p>
  </div>;
}
