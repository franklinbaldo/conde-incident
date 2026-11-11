import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Activity,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Info,
  Crosshair,
  BarChart3,
} from 'lucide-react';
import { runMonteCarloSimulation, MonteCarloSummary } from '../lib/monteCarlo';
import { CONDE_COORDINATES } from '../lib/constants';

interface MonteCarloVisualizerProps {
  lang: 'pt' | 'en';
}

export const MonteCarloVisualizer: React.FC<MonteCarloVisualizerProps> = ({
  lang,
}) => {
  const isPt = lang === 'pt';
  const [sampleSize, setSampleSize] = useState<number>(2000);
  const [summary, setSummary] = useState<MonteCarloSummary | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Run simulation
  const executeSimulation = () => {
    setIsRunning(true);
    setTimeout(() => {
      const res = runMonteCarloSimulation(sampleSize);
      setSummary(res);
      setIsRunning(false);
    }, 100);
  };

  // Run initial simulation on mount
  useEffect(() => {
    executeSimulation();
  }, [sampleSize]);

  // Render scatter plot on Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !summary) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear background
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, width, height);

    // Lat/Lon coordinate mapping
    const toScreen = (lon: number, lat: number) => {
      const x = ((lon + 180) / 360) * width;
      const y = ((90 - lat) / 180) * height;
      return { x, y };
    };

    // Grid lines
    ctx.strokeStyle = '#182234';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 4]);

    for (let lat = -80; lat <= 80; lat += 20) {
      ctx.beginPath();
      ctx.moveTo(0, ((90 - lat) / 180) * height);
      ctx.lineTo(width, ((90 - lat) / 180) * height);
      ctx.stroke();
    }
    for (let lon = -180; lon <= 180; lon += 30) {
      ctx.beginPath();
      ctx.moveTo(((lon + 180) / 360) * width, 0);
      ctx.lineTo(((lon + 180) / 360) * width, height);
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // Highlight Conde latitude band (-12.5° to -11.0°)
    const yTop = ((90 - -11.0) / 180) * height;
    const yBottom = ((90 - -12.5) / 180) * height;
    ctx.fillStyle = '#f43f5e10';
    ctx.fillRect(0, yTop, width, yBottom - yTop);

    // Conde Target Pin
    const condePos = toScreen(CONDE_COORDINATES.longitude, CONDE_COORDINATES.latitude);

    // 500 km horizon
    const r500 = (500 / 40075) * width;
    ctx.strokeStyle = '#f43f5e66';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(condePos.x, condePos.y, r500, 0, Math.PI * 2);
    ctx.stroke();

    // 100 km horizon
    const r100 = (100 / 40075) * width;
    ctx.fillStyle = '#f43f5e44';
    ctx.beginPath();
    ctx.arc(condePos.x, condePos.y, r100, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#f43f5e';
    ctx.stroke();

    // Draw individual Monte Carlo Reentry Points
    summary.results.forEach((pt) => {
      const pos = toScreen(pt.reentryLon, pt.reentryLat);

      if (pt.isWithinConde100Km) {
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 4, 0, Math.PI * 2);
        ctx.fill();
      } else if (pt.isWithinConde500Km) {
        ctx.fillStyle = '#fbbf24';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 3, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.fillStyle = '#22d3ee33'; // translucent cyan
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    // Conde marker
    ctx.fillStyle = '#f43f5e';
    ctx.beginPath();
    ctx.arc(condePos.x, condePos.y, 3.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px monospace';
    ctx.fillText('CONDE-BA', condePos.x + 6, condePos.y + 3);
  }, [summary]);

  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1 max-w-3xl">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              <span>{isPt ? 'EXPERIMENTO GEOMÉTRICO SINTÉTICO' : 'SYNTHETIC GEOMETRIC EXPERIMENT'}</span>
            </div>
            <h2 className="text-lg font-bold text-zinc-100">
              {isPt
                ? 'Monte Carlo: distribuição geométrica, não previsão de queda'
                : 'Monte Carlo: geometric sampler, not impact forecast'}
            </h2>
            <p className="text-xs text-zinc-300 leading-relaxed">
              {isPt
                ? 'Este demonstrador sorteia a fase orbital terminal independentemente do TLE e não integra a trajetória física. Os pontos são amostras sintéticas de geometria, não locais previstos de reentrada.'
                : 'We evaluate hypothesis H1 (reentry at Conde) versus hypothesis H0 (reentry elsewhere). We sample stochastic trajectories varying epoch, ballistic drag, scale height, and solar variations in Nov 1963, without conditioning the sample on Conde.'}
            </p>
          </div>

          {/* Sample Size selector & Run Button */}
          <div className="flex items-center gap-2 shrink-0">
            <select
              value={sampleSize}
              onChange={(e) => setSampleSize(Number(e.target.value))}
              className="bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs rounded-lg px-3 py-2 font-mono cursor-pointer"
            >
              <option value={1000}>N = 1.000 trajetórias</option>
              <option value={2000}>N = 2.000 trajetórias</option>
              <option value={5000}>N = 5.000 trajetórias</option>
            </select>

            <button
              onClick={executeSimulation}
              disabled={isRunning}
              className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:bg-zinc-800 text-white font-medium text-xs flex items-center gap-2 transition-colors cursor-pointer shadow"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{isRunning ? 'Simulando...' : 'Re-executar'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Dispersion Scatter Plot Canvas */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-3">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            <span className="font-bold text-zinc-200">
              {isPt
                ? 'Amostras geométricas sintéticas (não são reentradas propagadas)'
                : 'Synthetic geometric samples (not propagated reentries)'}
            </span>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-mono text-zinc-400">
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400/40 inline-block" />
              <span>Reentrada Global (H0)</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
              <span>Regional (&lt;500 km)</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
              <span>Conde (&lt;100 km)</span>
            </span>
          </div>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-lg overflow-hidden">
          <canvas
            ref={canvasRef}
            width={1000}
            height={480}
            className="w-full h-auto block select-none"
          />
        </div>
      </div>

      {/* Metrics Table */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Trajetórias Amostradas:</div>
            <div className="text-lg font-bold text-zinc-100 mt-1">{summary.totalRuns}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              Decaídas em 08/11: {summary.runsDecayedOnNov8} ({((summary.runsDecayedOnNov8/summary.totalRuns)*100).toFixed(1)}%)
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Faixa de Latitude Conde:</div>
            <div className="text-lg font-bold text-cyan-300 mt-1">{summary.runsInCondeLatitudeBand}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              {((summary.runsInCondeLatitudeBand / summary.totalRuns) * 100).toFixed(2)}% da amostra
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Dentro de 500 km de Conde:</div>
            <div className="text-lg font-bold text-amber-300 mt-1">{summary.runsWithin500Km}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              Frequência na amostra: {(summary.empiricalProbability500Km * 100).toFixed(3)}%
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Dentro de 100 km de Conde:</div>
            <div className="text-lg font-bold text-rose-400 mt-1">{summary.runsWithin100Km}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              Frequência na amostra: {(summary.empiricalProbability100Km * 100).toFixed(4)}%
            </div>
          </div>
        </div>
      )}

      {/* Epistemological Discussion */}
      <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-3">
        <h4 className="text-xs font-bold text-zinc-200 flex items-center gap-2">
          <Info className="w-4 h-4 text-cyan-400" />
          <span>{isPt ? 'Limitações deste demonstrador' : 'Limitations of this demonstration'}</span>
        </h4>
        <div className="text-xs text-zinc-300 space-y-2 leading-relaxed">
          <p>Este experimento não representa uma distribuição posterior de localização do NORAD 528. Sorteia uma fase terminal e uma duração ilustrativa sem integrar dinamicamente o estado inicial até a reentrada.</p>
          <p>Os percentuais descrevem apenas a frequência de amostras sob hipóteses escolhidas no código. Não são probabilidades de queda ou evidência independente de Conde.</p>
          <p>Para produzir inferência física válida, é necessário ajustar elementos orbitais documentados, condições atmosféricas e parâmetros balísticos e validar o procedimento com TLEs históricos não utilizados no ajuste.</p>
        </div>
      </div>
    </div>
  );
};
