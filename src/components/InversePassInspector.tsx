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

  // Set default selected pass to the closest encounter on Nov 8 (Rev 14)
  React.useEffect(() => {
    if (!selectedPass && filteredPasses.length > 0) {
      // Find pass with min distance on Nov 8
      const nov8Passes = allPasses.filter(
        (p) => new Date(p.epochMs).getUTCDate() === 8
      );
      if (nov8Passes.length > 0) {
        const closest = nov8Passes.reduce((min, p) =>
          p.closestApproachDistanceKm < min.closestApproachDistanceKm ? p : min
        );
        setSelectedPass(closest);
      } else {
        setSelectedPass(filteredPasses[0]);
      }
    }
  }, [filteredPasses, allPasses, selectedPass]);

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
                ? 'Em vez de propagar livremente no vácuo, impomos como hipótese de trabalho que o objeto 528 atingiu Conde em 08/11/1963. Calculamos então quais valores exatos de anomalia orbital, instante temporal, taxa de arrasto dn/dt e coeficiente balístico B seriam fisicamente necessários para forçar a reentrada no município.'
                : 'Instead of freely propagating in a vacuum, we hypothesize that object 528 struck Conde on 08/11/1963. We then compute the exact along-track anomaly, timestamp, drag rate dn/dt, and ballistic coefficient B physically required to force terminal entry at this location.'}
            </p>
          </div>

          {/* Date Filter */}
          <div className="flex items-center bg-zinc-950 p-1 rounded-lg border border-zinc-800 shrink-0 text-xs font-mono">
            <button
              onClick={() => setFilterDate('07')}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '07' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              07/11
            </button>
            <button
              onClick={() => setFilterDate('08')}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '08' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              08/11 (Catálogo)
            </button>
            <button
              onClick={() => setFilterDate('09')}
              className={`px-3 py-1.5 rounded transition-colors cursor-pointer ${
                filterDate === '09' ? 'bg-cyan-600 text-white font-semibold' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              09/11
            </button>
            <button
              onClick={() => setFilterDate('ALL')}
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
                ? `Passagens Regionais Identificadas (${filteredPasses.length})`
                : `Identified Regional Passes (${filteredPasses.length})`}
            </div>
            <span className="text-[11px] text-zinc-500 font-mono">
              {isPt ? 'Clique para inspecionar' : 'Click to inspect'}
            </span>
          </div>

          <div className="divide-y divide-zinc-800/80 overflow-y-auto max-h-[520px] scrollbar-thin">
            {filteredPasses.map((p) => {
              const isSelected = selectedPass?.epochMs === p.epochMs;
              const isClose = p.closestApproachDistanceKm < 900;
              return (
                <div
                  key={p.epochMs}
                  onClick={() => setSelectedPass(p)}
                  className={`p-3.5 transition-colors cursor-pointer flex items-center justify-between gap-3 text-xs ${
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
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold border ${
                        p.physicalFeasibility === 'ALTA'
                          ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800'
                          : p.physicalFeasibility === 'MODERADA'
                          ? 'text-cyan-400 bg-cyan-950/60 border-cyan-800'
                          : p.physicalFeasibility === 'EXTREMA'
                          ? 'text-amber-400 bg-amber-950/60 border-amber-800'
                          : 'text-zinc-400 bg-zinc-950 border-zinc-800'
                      }`}
                    >
                      {p.physicalFeasibility}
                    </span>
                  </div>
                </div>
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
                    {isPt ? 'Diagnóstico Físico da Passagem' : 'Physical Pass Diagnostic'}
                  </div>
                  <h3 className="text-base font-bold text-zinc-100 font-mono">
                    Revolução #{selectedPass.revolutionNumber}
                  </h3>
                </div>
                <button
                  onClick={() => onSelectPassTime(selectedPass.epochMs)}
                  className="px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-medium transition-colors flex items-center gap-1.5 cursor-pointer shadow"
                >
                  <span>Ver no Mapa</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Timing & Geometry Cards */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Horário UTC:</div>
                  <div className="text-zinc-100 font-bold mt-0.5">{selectedPass.utcString}</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Horário Local (BA):</div>
                  <div className="text-cyan-300 font-bold mt-0.5">{selectedPass.localTimeString}</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Distância Mínima:</div>
                  <div className="text-amber-400 font-bold mt-0.5">{selectedPass.closestApproachDistanceKm} km</div>
                </div>
                <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800">
                  <div className="text-zinc-500">Altitude na Passagem:</div>
                  <div className="text-zinc-100 font-bold mt-0.5">{selectedPass.altitudeKm} km</div>
                </div>
              </div>

              {/* Inverse Physics Required Metrics */}
              <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-3">
                <div className="text-xs font-bold text-zinc-200 flex items-center gap-2">
                  <Gauge className="w-4 h-4 text-cyan-400" />
                  <span>{isPt ? 'Condições Inversas Exigidas para Queda em Conde' : 'Inverse Conditions Required for Impact'}</span>
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

                  <div className="flex justify-between items-center text-zinc-300 font-mono">
                    <span className="text-zinc-500">Viabilidade Física:</span>
                    <span
                      className={`font-bold ${
                        selectedPass.physicalFeasibility === 'ALTA'
                          ? 'text-emerald-400'
                          : selectedPass.physicalFeasibility === 'MODERADA'
                          ? 'text-cyan-400'
                          : 'text-amber-400'
                      }`}
                    >
                      {selectedPass.physicalFeasibility}
                    </span>
                  </div>
                </div>
              </div>

              {/* Notes */}
              <div className="p-3 rounded-lg bg-zinc-950/80 border border-zinc-800/80 text-xs text-zinc-300 space-y-1">
                <div className="font-semibold text-zinc-400 text-[11px] uppercase tracking-wider">
                  {isPt ? 'Análise do Especialista' : 'Expert Analysis'}
                </div>
                <p className="leading-relaxed text-[11px]">{selectedPass.notes}</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-zinc-500 text-xs font-mono">
              Selecione uma passagem para inspecionar.
            </div>
          )}

          {/* Epistemological Warning Box */}
          <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/50 flex items-start gap-2.5 text-xs text-amber-200/90">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed">
              <strong className="text-amber-300">Regra de Falsificação:</strong> O fato de que os parâmetros físicos requeridos para cruzar Conde são admissíveis demonstra que o sobrevoo era geometricamente possível, mas <em>NÃO PROVA</em> que ocorreu em Conde, pois outras ~16 revoluções no mesmo dia também cruzavam latitudes povoadas com a mesma compatibilidade física.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
