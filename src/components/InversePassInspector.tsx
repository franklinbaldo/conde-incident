import React, { useState, useMemo } from 'react';
import {
  MapPin,
  Clock,
  Compass,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle,
  AlertTriangle,
  Flame,
  Gauge,
  HelpCircle,
  ExternalLink,
} from 'lucide-react';
import { computeInversePasses } from '../lib/inverseSolver';
import { CONDE_COORDINATES } from '../lib/constants';
import { CandidatePass } from '../types/astrodynamics';

interface InversePassInspectorProps {
  lang: 'pt' | 'en';
  onSelectPassTime: (timeMs: number) => void;
}

export const InversePassInspector: React.FC<InversePassInspectorProps> = ({
  lang,
  onSelectPassTime,
}) => {
  const isPt = lang === 'pt';
  const [filterDate, setFilterDate] = useState<'ALL' | '08' | '07' | '09'>('08');
  const [selectedPass, setSelectedPass] = useState<CandidatePass | null>(null);

  // Compute all candidate passes near Conde across Nov 7-9, 1963
  const allPasses = useMemo(() => {
    return computeInversePasses('1963-11-07T00:00:00Z', '1963-11-09T23:59:59Z');
  }, []);

  const filteredPasses = useMemo(() => {
    if (filterDate === 'ALL') return allPasses;
    return allPasses.filter((p) => {
      const d = new Date(p.epochMs).getUTCDate();
      return d.toString().padStart(2, '0') === filterDate;
    });
  }, [allPasses, filterDate]);

  // Do not preselect a fabricated "closest historical pass": inspect a scenario only on request.
  const chooseDate = (day: 'ALL' | '08' | '07' | '09') => {
    setFilterDate(day);
    setSelectedPass(null);
  };

  return (
    <div className="space-y-6">
      {/* Introduction Card */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono mb-2">
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              <span>{isPt ? 'MÉTODO DE FALSIFICAÇÃO INVERSA' : 'INVERSE FALSIFICATION METHOD'}</span>
            </div>
            <h2 className="text-lg font-bold text-zinc-100">
              {isPt
                ? 'Teste Inverso: Imposição Hipotética de Queda em Conde-BA'
                : 'Inverse Test: Hypothetical Forcing of Impact at Conde-BA'}
            </h2>
            <p className="text-xs text-zinc-300 mt-1 max-w-3xl leading-relaxed">
              {isPt
                ? 'Este experimento parte de uma queda suposta em Conde e calcula aproximações geométricas, sem ajustar uma trajetória histórica a dados independentes. Horas, distâncias e coeficientes abaixo são saídas do modelo legado, não observações ou parâmetros fisicamente admissíveis demonstrados.'
                : 'This experiment assumes a Conde impact and computes geometric approximations, without fitting a historical trajectory to independent observations. Times, distances and coefficients below are legacy-model outputs, not observations or proven physically admissible parameters.'}
            </p>
          </div>

          {/* Date Filter */}
          <div className="flex items-center bg-zinc-950 p-1 rounded-lg border border-zinc-800 shrink-0 text-xs font-mono">
            <button
              onClick={() => chooseDate('07')}
              aria-pressed={filterDate === '07'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '07' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              07/11
            </button>
            <button
              onClick={() => chooseDate('08')}
              aria-pressed={filterDate === '08'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '08' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              08/11 (Catálogo)
            </button>
            <button
              onClick={() => chooseDate('09')}
              aria-pressed={filterDate === '09'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '09' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              09/11
            </button>
            <button
              onClick={() => chooseDate('ALL')}
              aria-pressed={filterDate === 'ALL'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === 'ALL' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Todas (07-09)
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Pass Table + Deep Detail Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Pass List (Left 7 Cols) */}
        <div className="lg:col-span-7 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-zinc-800 bg-zinc-950/60 flex items-center justify-between">
            <div className="text-xs font-bold text-zinc-200 uppercase tracking-wider font-mono">
              {isPt
                ? `Cenários regionais calculados (${filteredPasses.length})`
                : `Calculated Regional Scenarios (${filteredPasses.length})`}
            </div>
            <span className="text-[11px] text-zinc-500 font-mono">
              {isPt ? 'Selecione para inspecionar' : 'Select to inspect'}
            </span>
          </div>

          <div className="divide-y divide-zinc-800/80 overflow-y-auto max-h-[520px] scrollbar-thin">
            {filteredPasses.map((p) => {
              const isSelected = selectedPass?.epochMs === p.epochMs;
              const isClose = p.closestApproachDistanceKm < 900;
              return (
                <button
                  type="button"
                  key={p.epochMs}
                  onClick={() => setSelectedPass(p)}
                  aria-pressed={isSelected}
                  className={`w-full text-left p-3.5 transition-colors cursor-pointer flex items-center justify-between gap-3 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300 ${
                    isSelected
                      ? 'bg-cyan-950/40 border-l-4 border-cyan-400'
                      : 'hover:bg-zinc-800/50'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-zinc-200">
                        Rev #{p.revolutionNumber}
                      </span>
                      <span className="text-zinc-400 font-mono">|</span>
                      <span className="text-cyan-300 font-mono font-medium">
                        {p.utcString.substring(5, 16)} UTC
                      </span>
                      <span className="text-[10px] text-zinc-500 font-mono">
                        ({p.localTimeString.substring(0, 5)} Bahia)
                      </span>
                    </div>

                    <div className="flex items-center gap-3 text-[11px] text-zinc-400 font-mono">
                      <span className="flex items-center gap-1">
                        {p.passType === 'ASCENDING' ? (
                          <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <ArrowDownRight className="w-3.5 h-3.5 text-blue-400" />
                        )}
                        <span>{p.passType === 'ASCENDING' ? 'Ascendente' : 'Descendente'}</span>
                      </span>
                      <span>Alt: {p.altitudeKm} km</span>
                      <span>Elev: {p.elevationDeg}°</span>
                    </div>
                  </div>

                  <div className="text-right space-y-1">
                    <div
                      className={`font-mono font-bold ${
                        p.closestApproachDistanceKm < 500
                          ? 'text-rose-400'
                          : isClose
                          ? 'text-amber-400'
                          : 'text-zinc-300'
                      }`}
                    >
                      {p.closestApproachDistanceKm} km
                    </div>
                    <span className="text-[10px] text-zinc-400">
                      {isPt ? 'saída sintética' : 'synthetic output'}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Pass Deep Investigation Card (Right 5 Cols) */}
        <div className="lg:col-span-5 bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col justify-between space-y-4">
          {selectedPass ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
                <div>
                  <div className="text-xs font-mono text-zinc-500 uppercase">
                    {isPt ? 'Detalhes do cenário simulado' : 'Simulated scenario details'}
                  </div>
                  <h3 className="text-base font-bold text-zinc-100 font-mono">
                    Revolução #{selectedPass.revolutionNumber}
                  </h3>
                </div>
                <button
                  onClick={() => onSelectPassTime(selectedPass.epochMs)}
                  className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition-colors flex items-center gap-1.5 cursor-pointer shadow"
                >
                  <span>{isPt ? 'Explorar hora modelada no mapa' : 'Explore modelled time on map'}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Timing & Geometry Cards */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Hora UTC modelada:</div>
                  <div className="text-zinc-100 font-bold mt-0.5">{selectedPass.utcString}</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Hora local calculada (UTC−3):</div>
                  <div className="text-cyan-300 font-bold mt-0.5">{selectedPass.localTimeString}</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Distância no modelo:</div>
                  <div className="text-amber-400 font-bold mt-0.5">{selectedPass.closestApproachDistanceKm} km</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Altitude no modelo:</div>
                  <div className="text-zinc-100 font-bold mt-0.5">{selectedPass.altitudeKm} km</div>
                </div>
              </div>

              {/* Inverse Physics Required Metrics */}
              <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-3">
                <div className="text-xs font-bold text-zinc-200 flex items-center gap-2">
                  <Gauge className="w-4 h-4 text-cyan-400" />
                  <span>{isPt ? 'Parâmetros hipotéticos (sem validação física)' : 'Hypothetical parameters (not physically validated)'}</span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center text-zinc-300 border-b border-zinc-900 pb-1.5 font-mono">
                    <span className="text-zinc-500">Ajuste de Fase Along-Track (ΔM):</span>
                    <span className="font-bold text-zinc-200">
                      {selectedPass.requiredMeanAnomalyDeltaDeg > 0 ? '+' : ''}
                      {selectedPass.requiredMeanAnomalyDeltaDeg}°
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-zinc-300 border-b border-zinc-900 pb-1.5 font-mono">
                    <span className="text-zinc-500">Derivada de Movimento (dn/dt):</span>
                    <span className="font-bold text-zinc-200">
                      {selectedPass.requiredMeanMotionDerivative} rev/dia²
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-zinc-300 border-b border-zinc-900 pb-1.5 font-mono">
                    <span className="text-zinc-500">Coeficiente Balístico B (C_D A/m):</span>
                    <span className="font-bold text-cyan-300">
                      {selectedPass.requiredBallisticCoeff} m²/kg
                    </span>
                  </div>


                </div>
              </div>

              <p className="text-xs text-amber-200 leading-relaxed">
                {isPt
                  ? 'Nenhuma classificação de viabilidade do cálculo legado foi validada por dinâmica acoplada, custódia TLE ou holdout independente.'
                  : 'No legacy feasibility label has been validated by coupled dynamics, TLE custody or an independent holdout.'}
              </p>
            </div>
          ) : (
            <div className="text-center py-16 text-zinc-500 text-xs font-mono">
              Selecione uma passagem para inspecionar.
            </div>
          )}

          <aside className="p-4 rounded-lg bg-amber-950/20 border border-amber-700/60 space-y-3" aria-label={isPt ? 'Limites do teste inverso' : 'Inverse test limitations'}>
            <p className="text-sm leading-relaxed text-amber-100">
              {isPt
                ? 'Resultado indeterminado: a data NASA C197–C202 indica somente o dia do decaimento. Não há hora/posição terminal observada, domínio físico comprovadamente não vazio, intervalos validados ou comparação cega independente. A RAAN das séries ainda está em conflito.'
                : 'Outcome undetermined: NASA C197–C202 gives only the decay day. No observed terminal time/location, proven nonempty physical domain, validated intervals or independent blind comparison is available. The competing RAAN series remain unresolved.'}
            </p>
            <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm">
              <a href="#/research/c197" className="text-cyan-300 underline underline-offset-4 focus-visible:outline">{isPt ? 'C197–C202 · registro NASA' : 'C197–C202 · NASA record'}</a>
              <a href="#/research/c44-orbital" className="text-cyan-300 underline underline-offset-4 focus-visible:outline">{isPt ? 'C44–C46 · hipótese inversa' : 'C44–C46 · inverse hypothesis'}</a>
              <a href="#/research/raan" className="text-cyan-300 underline underline-offset-4 focus-visible:outline">{isPt ? 'RAAN · custódia pendente' : 'RAAN · custody pending'}</a>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
};
