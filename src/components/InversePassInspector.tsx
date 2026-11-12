import React, {useMemo, useState} from 'react';
import {ArrowRight, Compass, AlertTriangle} from 'lucide-react';
import {computeInversePasses} from '../lib/inverseSolver';

export const InversePassInspector: React.FC<{
  lang: 'pt' | 'en';
  onSelectPassTime: (timeMs: number) => void;
}> = ({lang, onSelectPassTime}) => {
  const pt = lang === 'pt';
  const [day, setDay] = useState('08');
  const passes = useMemo(() => computeInversePasses(), []);
  const filtered = passes.filter(p => day === 'ALL' || new Date(p.epochMs).getUTCDate().toString().padStart(2, '0') === day);
  return <div className="space-y-6">
    <section className="rounded-3xl border border-zinc-800 bg-gradient-to-br from-slate-900 to-zinc-950 p-7 md:p-10">
      <div className="flex items-center gap-2 text-xs uppercase tracking-widest text-cyan-300"><Compass size={16}/>{pt?'Experimento geométrico':'Geometric experiment'}</div>
      <h1 className="mt-4 text-3xl font-semibold text-white">{pt?'Aproximações do SGP4 não são reentradas observadas':'SGP4 approaches are not observed reentries'}</h1>
      <p className="mt-4 max-w-4xl text-sm leading-relaxed text-zinc-300">{pt?'A tabela abaixo preserva apenas distâncias e horários calculados a partir do TLE atualmente incluído no aplicativo. O conjunto de elementos está sob auditoria de proveniência, e uma extrapolação de aproximadamente 12 dias não determina a trajetória terminal.':'The table below shows only distances and times computed from the currently embedded TLE. Its provenance is under audit, and extrapolation over roughly 12 days does not establish the terminal trajectory.'}</p>
    </section>
    <div className="flex flex-wrap gap-2">{['07','08','09','ALL'].map(x=><button key={x} onClick={()=>setDay(x)} className={`rounded-md border px-4 py-2 text-xs font-mono ${day===x?'border-cyan-600 bg-cyan-950 text-cyan-200':'border-zinc-800 bg-zinc-900 text-zinc-300'}`}>{x==='ALL'?(pt?'Todos':'All'):`${x}/11`}</button>)}</div>
    <div className="overflow-hidden rounded-2xl border border-zinc-800">
      <div className="grid grid-cols-3 gap-3 border-b border-zinc-800 bg-zinc-900 px-5 py-3 text-xs font-semibold text-zinc-400"><div>UTC</div><div>{pt?'Distância superficial':'Ground distance'}</div><div>{pt?'SGP4 altitude':'SGP4 altitude'}</div></div>
      <div className="max-h-[540px] overflow-y-auto divide-y divide-zinc-800 bg-zinc-950">{filtered.length ? filtered.map(p=><button key={p.epochMs} onClick={()=>onSelectPassTime(p.epochMs)} className="grid w-full grid-cols-3 items-center gap-3 px-5 py-3 text-left text-xs font-mono text-zinc-300 hover:bg-zinc-900"><span className="text-cyan-300">{p.utcString.slice(5,19)}</span><span>{p.closestApproachDistanceKm} km</span><span className="flex items-center justify-between gap-2">{p.altitudeKm} km <ArrowRight size={13}/></span></button>):<div className="p-6 text-sm text-zinc-400">{pt?'Nenhuma aproximação regional neste recorte do modelo.':'No regional approaches in this model window.'}</div>}</div>
    </div>
    <div className="flex items-start gap-3 rounded-xl border border-amber-800/40 bg-amber-950/20 p-5 text-sm text-amber-200"><AlertTriangle className="mt-0.5 shrink-0" size={18}/><p>{pt?'O solucionador inverso legado calculava coeficientes balísticos e “viabilidade” a partir da diferença de longitude, o que não é fisicamente válido. Esses números foram retirados desta apresentação até que exista um ajuste dinâmico com observações e validação independente.':'The previous inverse solver derived ballistic coefficients and feasibility from longitude displacement, which is physically invalid. These values have been removed pending a dynamically fitted and independently validated solver.'}</p></div>
  </div>;
};
