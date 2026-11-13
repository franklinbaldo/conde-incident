import React, { useState, useMemo } from 'react';
import {
  Compass,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  Gauge,
  ExternalLink,
} from 'lucide-react';
import { computeInversePasses } from '../lib/inverseSolver';
import { matrixOccurrenceUrl } from '../lib/sourceCitationAudit';
import { selectVisiblePass } from '../lib/inversePassSelection';

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
  const [selectedPassEpoch, setSelectedPassEpoch] = useState<number | null>(null);

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

  // A filter change must never expose an invisible pass from another day.
  const selectedPass = useMemo(
    () => selectVisiblePass(filteredPasses, selectedPassEpoch, filterDate === '08'),
    [filteredPasses, selectedPassEpoch, filterDate]
  );

  return (
    <div className="space-y-6">
      {/* Introduction Card */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono mb-2">
              <Compass className="w-3.5 h-3.5 text-cyan-400" />
              <span>{isPt ? 'CENÁRIO INVERSO EXPLORATÓRIO' : 'EXPLORATORY INVERSE SCENARIO'}</span>
            </div>
            <h2 className="text-lg font-bold text-zinc-100">
              {isPt
                ? 'Teste Inverso: Imposição Hipotética de Queda em Conde-BA'
                : 'Inverse Test: Hypothetical Forcing of Impact at Conde-BA'}
            </h2>
            <p className="text-xs text-zinc-300 mt-1 max-w-3xl leading-relaxed">
              {isPt
                ? 'Em vez de propagar livremente no vácuo, impomos como hipótese de trabalho que o objeto 528 atingiu Conde em 08/11/1963. A rotina legada gera valores exploratórios de fase, tempo e arrasto sob essa hipótese. Não há ajuste físico calibrado, erro observacional ou validação de impacto.'
                : 'Instead of freely propagating in a vacuum, we hypothesize that object 528 struck Conde on 08/11/1963. The legacy routine generates exploratory phase, time and drag values under this assumption. No calibrated physical fit, observational error or impact validation is available.'}
            </p>
          </div>

          {/* Date Filter */}
          <div className="flex items-center bg-zinc-950 p-1 rounded-lg border border-zinc-800 shrink-0 text-xs font-mono">
            <button
              onClick={() => setFilterDate('07')}
              aria-pressed={filterDate === '07'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '07' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              07/11
            </button>
            <button
              onClick={() => setFilterDate('08')}
              aria-pressed={filterDate === '08'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '08' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {isPt ? '08/11 (catálogo)' : '08 Nov (catalogue)'}
            </button>
            <button
              onClick={() => setFilterDate('09')}
              aria-pressed={filterDate === '09'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '09' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              09/11
            </button>
            <button
              onClick={() => setFilterDate('ALL')}
              aria-pressed={filterDate === 'ALL'}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === 'ALL' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {isPt ? 'Todas (07–09)' : 'All (07–09)'}
            </button>
          </div>
        </div>
      </div>

      <aside role="note" aria-label={isPt ? 'Limites e fontes do cenário' : 'Scenario sources and limits'}
        className="rounded-xl border border-amber-700/70 bg-amber-950/25 p-4 text-sm text-amber-100">
        <p className="leading-relaxed">
          {isPt
            ? 'Estas passagens são saídas de um modelo exploratório, não observações de 1963. Os rótulos de viabilidade são heurísticos legados e NÃO demonstram domínio físico admissível reduzido, hora de reentrada ou impacto. A NASA só fornece o dia de decaimento; o TLE secundário tem proveniência e época pendentes.'
            : 'These passes are exploratory model outputs, not 1963 observations. Legacy feasibility labels are heuristic and do NOT establish a reduced physically admissible domain, reentry time or impact. NASA records only the decay date; the secondary TLE has unresolved provenance and epoch.'}
        </p>
        <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs">
          <a href={matrixOccurrenceUrl(905)} target="_blank" rel="noopener noreferrer"
            className="underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
            {isPt ? 'C197#1 · NASA (dia)' : 'C197#1 · NASA (day)'}
          </a>
          <a href={matrixOccurrenceUrl(839)} target="_blank" rel="noopener noreferrer"
            className="underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
            {isPt ? 'C179#1 · TLE secundário' : 'C179#1 · secondary TLE'}
          </a>
          <a href="https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10"
            target="_blank" rel="noopener noreferrer"
            className="underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300">
            {isPt ? 'Documento NASA, 15/11/1963' : 'NASA document, 15 Nov 1963'}
          </a>
        </div>
      </aside>

      {/* Main Grid: Pass Table + Deep Detail Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Pass List (Left 7 Cols) */}
        <div className="lg:col-span-7 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-zinc-800 bg-zinc-950/60 flex items-center justify-between">
            <div className="text-xs font-bold text-zinc-200 uppercase tracking-wider font-mono">
              {isPt
                ? `Cenários Regionais Gerados (${filteredPasses.length})`
                : `Generated Regional Scenarios (${filteredPasses.length})`}
            </div>
            <span className="text-[11px] text-zinc-400 font-mono">
              {isPt ? 'Selecione para inspecionar' : 'Select to inspect'}
            </span>
          </div>

          <div className="divide-y divide-zinc-800/80 overflow-y-auto max-h-[520px] scrollbar-thin">
            {filteredPasses.map((p) => {
              const isSelected = selectedPass?.epochMs === p.epochMs;
              const isClose = p.closestApproachDistanceKm < 900;
              return (
                <button
                  key={p.epochMs}
                  type="button"
                  onClick={() => setSelectedPassEpoch(p.epochMs)}
                  aria-pressed={isSelected}
                  className={`p-3.5 w-full text-left transition-colors cursor-pointer flex items-center justify-between gap-3 text-xs focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-300 ${
                    isSelected
                      ? 'bg-cyan-950/40 border-l-4 border-cyan-400'
                      : 'hover:bg-zinc-800/50'
                  }`}
                >
                  <span className="block space-y-1">
                    <span className="flex items-center gap-2">
                      <span className="font-mono font-bold text-zinc-200">
                        Rev #{p.revolutionNumber}
                      </span>
                      <span className="text-zinc-400 font-mono">|</span>
                      <span className="text-cyan-300 font-mono font-medium">
                        {p.utcString.substring(5, 16)} UTC
                      </span>
                      <span className="text-[10px] text-zinc-400 font-mono">
                        ({p.localTimeString.substring(0, 5)} Bahia)
                      </span>
                    </span>

                    <span className="flex items-center gap-3 text-[11px] text-zinc-400 font-mono">
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
                    </span>
                  </span>

                  <span className="block text-right space-y-1">
                    <span
                      className={`block font-mono font-bold ${
                        p.closestApproachDistanceKm < 500
                          ? 'text-rose-400'
                          : isClose
                          ? 'text-amber-400'
                          : 'text-zinc-300'
                      }`}
                    >
                      {p.closestApproachDistanceKm} km
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded font-mono border border-zinc-700 bg-zinc-950 text-zinc-300"
                    >
                      {isPt ? `heurística: ${p.physicalFeasibility}` : `heuristic: ${p.physicalFeasibility}`}
                    </span>
                  </span>
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
                  <div className="text-xs font-mono text-zinc-400 uppercase">
                    {isPt ? 'Saída do Modelo Exploratório' : 'Exploratory Model Output'}
                  </div>
                  <h3 className="text-base font-bold text-zinc-100 font-mono">
                    Revolução #{selectedPass.revolutionNumber}
                  </h3>
                </div>
                <button
                  onClick={() => onSelectPassTime(selectedPass.epochMs)}
                  className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition-colors flex items-center gap-1.5 cursor-pointer shadow"
                >
                  <span>{isPt ? 'Ver cenário no mapa' : 'View scenario on map'}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Timing & Geometry Cards: model outputs, not measured epochs */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-400">Tempo do cenário UTC:</div>
                  <div className="text-zinc-100 font-bold mt-0.5">{selectedPass.utcString}</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-400">Tempo do cenário (BA):</div>
                  <div className="text-cyan-300 font-bold mt-0.5">{selectedPass.localTimeString}</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-400">Distância calculada:</div>
                  <div className="text-amber-400 font-bold mt-0.5">{selectedPass.closestApproachDistanceKm} km</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-400">Altitude calculada:</div>
                  <div className="text-zinc-100 font-bold mt-0.5">{selectedPass.altitudeKm} km</div>
                </div>
              </div>

              {/* Inverse Physics Required Metrics */}
              <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-3">
                <div className="text-xs font-bold text-zinc-200 flex items-center gap-2">
                  <Gauge className="w-4 h-4 text-cyan-400" />
                  <span>{isPt ? 'Parâmetros inversos gerados (não validados)' : 'Generated inverse parameters (unvalidated)'}</span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center text-zinc-300 border-b border-zinc-900 pb-1.5 font-mono">
                    <span className="text-zinc-400">Ajuste de Fase Along-Track (ΔM):</span>
                    <span className="font-bold text-zinc-200">
                      {selectedPass.requiredMeanAnomalyDeltaDeg > 0 ? '+' : ''}
                      {selectedPass.requiredMeanAnomalyDeltaDeg}°
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-zinc-300 border-b border-zinc-900 pb-1.5 font-mono">
                    <span className="text-zinc-400">Derivada de Movimento (dn/dt):</span>
                    <span className="font-bold text-zinc-200">
                      {selectedPass.requiredMeanMotionDerivative} rev/dia²
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-zinc-300 border-b border-zinc-900 pb-1.5 font-mono">
                    <span className="text-zinc-400">Coeficiente Balístico B (C_D A/m):</span>
                    <span className="font-bold text-cyan-300">
                      {selectedPass.requiredBallisticCoeff} m²/kg
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-zinc-300 font-mono">
                    <span className="text-zinc-400">{isPt ? 'Heurística legada:' : 'Legacy heuristic:'}</span>
                    <span
                      className="font-semibold text-zinc-300"
                    >
                      {selectedPass.physicalFeasibility} ({isPt ? 'não validada' : 'unvalidated'})
                    </span>
                  </div>
                </div>
              </div>

              {/* Notes */}
              <div className="p-3 rounded-lg bg-zinc-950/80 border border-zinc-800/80 text-xs text-zinc-300 space-y-1">
                <div className="font-semibold text-zinc-400 text-[11px] uppercase tracking-wider">
                  {isPt ? 'Nota do algoritmo legado (não verificada)' : 'Legacy algorithm note (unverified)'}
                </div>
                <p className="leading-relaxed text-[11px]">{selectedPass.notes}</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-zinc-400 text-xs font-mono">
              {isPt ? 'Nenhum cenário gerado para este filtro.' : 'No scenario generated for this filter.'}
            </div>
          )}

          {/* Epistemological Warning Box */}
          <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/50 flex items-start gap-2.5 text-xs text-amber-200/90">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed">
              <strong className="text-amber-300">{isPt ? 'Limite da inferência:' : 'Inference limit:'}</strong>{' '}
              {isPt
                ? 'Uma solução inversa geométrica não comprova admissibilidade física, sobrevoo real, reentrada ou queda em Conde. Faltam custódia dos elementos, épocas, incertezas e comparação com holdouts independentes.'
                : 'A geometric inverse solution does not establish physical admissibility, an actual overpass, reentry or impact in Conde. Element custody, epochs, uncertainty and independent holdout comparisons are missing.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
