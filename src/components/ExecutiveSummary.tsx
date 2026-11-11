import React from 'react';
import { AlertTriangle, ArrowRight, CheckCircle2, CircleHelp, Orbit } from 'lucide-react';

type Tab = 'research' | 'map' | 'inverse' | 'triangulation' | 'sensitivity' | 'montecarlo' | 'tles' | 'documents' | 'summary' | 'python';
interface Props { lang: 'pt' | 'en'; onJumpToTab: (tab: Tab) => void }

const questions = [
  { pt: 'O NORAD 528 reentrou em novembro de 1963?', en: 'Did NORAD 528 decay in November 1963?', answerPt: 'Sim. O boletim NASA de 15/11 registra 08/11/1963 como a data de decaimento. Não fornece horário nem lugar.', answerEn: 'Yes. The 15 November NASA bulletin records 8 November as the decay date. No time or place is supplied.', state: 'confirmed' },
  { pt: 'A órbita podia atingir a latitude de Conde?', en: 'Could the orbit reach Conde’s latitude?', answerPt: 'Sim. A inclinação catalogada permite cruzar o paralelo de Conde. Isso não prova uma passagem sobre a cidade.', answerEn: 'Yes. The recorded inclination allows the Conde parallel to be crossed. This does not establish a pass over the town.', state: 'conditional' },
  { pt: 'Houve uma passagem observada às 19h48 UTC?', en: 'Was a 19:48 UTC pass observed?', answerPt: 'Não foi demonstrado. Esse horário vem de um modelo exploratório com TLEs cuja proveniência está em auditoria.', answerEn: 'Not established. The time comes from an exploratory model with TLEs under provenance review.', state: 'unknown' },
  { pt: 'Os objetos 527 e 529 determinam a posição final do 528?', en: 'Do objects 527 and 529 determine the final position of 528?', answerPt: 'Não. Podem restringir forças compartilhadas, mas os estados e coeficientes balísticos são individuais. Não há ajuste conjunto validado.', answerEn: 'No. They can constrain shared forces, but orbital states and ballistic coefficients differ. No validated joint fit exists.', state: 'unknown' },
  { pt: 'Qual a chance de cair a 100 km de Conde?', en: 'What is the chance of impact within 100 km of Conde?', answerPt: 'Não estimável com rigor pelos dados disponíveis. O número anterior de 0,0062% era uma razão de áreas, não uma probabilidade histórica.', answerEn: 'Not rigorously estimable. The earlier 0.0062% was an area ratio, not a historically conditioned probability.', state: 'unknown' },
  { pt: 'A esfera e a cratera foram fisicamente confirmadas?', en: 'Were a sphere and crater physically confirmed?', answerPt: 'Não. O FBIS confirma a circulação do relato de rádio, não a existência física dos objetos descritos.', answerEn: 'No. FBIS documents circulation of the broadcast, not physical recovery of the reported objects.', state: 'unknown' },
  { pt: 'A hipótese de Conde foi refutada?', en: 'Has the Conde hypothesis been falsified?', answerPt: 'Não por geometria orbital. Também não foi confirmada. A investigação consular enfraquece os detalhes extraordinários.', answerEn: 'Not by orbital geometry. Nor has it been confirmed. The consular inquiry undermines the extraordinary details.', state: 'conditional' },
];

export const ExecutiveSummary: React.FC<Props> = ({ lang, onJumpToTab }) => {
  const pt = lang === 'pt';
  return <div className="space-y-7">
    <header className="relative overflow-hidden rounded-3xl border border-zinc-800 bg-gradient-to-br from-zinc-900 to-slate-950 p-7 md:p-11">
      <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-[.2em] text-cyan-300"><Orbit size={17}/>{pt ? 'Síntese científica · revisão crítica' : 'Scientific synthesis · critical review'}</div>
      <h1 className="mt-5 max-w-3xl text-3xl font-semibold tracking-tight text-white md:text-5xl">{pt ? 'Uma reentrada real. Uma história extraordinária. Uma localização ainda desconhecida.' : 'A real orbital decay. An extraordinary story. A location still unknown.'}</h1>
      <p className="mt-5 max-w-3xl text-zinc-300 leading-relaxed">{pt ? 'A data catalogada é documentada. A ligação com Conde não é. Nesta síntese, “compatível” não é sinônimo de “aconteceu”.' : 'The documented decay date is real. The Conde connection is not established. In this analysis “compatible” does not mean “occurred”.'}</p>
      <button className="mt-6 flex items-center gap-2 rounded-lg border border-cyan-700 bg-cyan-950/50 px-5 py-3 text-sm font-semibold text-cyan-200 hover:bg-cyan-900/50" onClick={()=>onJumpToTab('research')}>{pt ? 'Ver documentos e proveniência' : 'Inspect sources and provenance'}<ArrowRight size={16}/></button>
    </header>
    <div className="grid gap-4 md:grid-cols-2">{questions.map((q, i) => {
      const Icon = q.state==='confirmed'?CheckCircle2:q.state==='conditional'?AlertTriangle:CircleHelp;
      const color = q.state==='confirmed'?'text-emerald-400':q.state==='conditional'?'text-amber-400':'text-zinc-400';
      return <article key={i} className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-6"><div className="flex items-start gap-3"><Icon className={`mt-0.5 h-5 w-5 shrink-0 ${color}`}/><div><h2 className="font-semibold text-zinc-100">{pt?q.pt:q.en}</h2><p className="mt-3 text-sm leading-relaxed text-zinc-400">{pt?q.answerPt:q.answerEn}</p></div></div></article>;
    })}</div>
    <div className="rounded-xl border border-amber-800/40 bg-amber-950/15 p-5 text-sm text-amber-200"><strong>{pt?'Estado do modelo:':'Model status:'}</strong> {pt?'Uma implementação anterior modificava separadamente altitude e longitude após SGP4. Essa alteração foi removida, mas a extrapolação de 12 dias, a calibração do arrasto e as probabilidades continuam sem validação.':'A prior implementation independently modified altitude and longitude after SGP4. That adjustment is removed, but 12-day extrapolation, drag fitting and probability estimates remain unvalidated.'}</div>
  </div>;
};
