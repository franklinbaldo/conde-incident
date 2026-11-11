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
              <span>{isPt ? 'PROPAGAÇÃO ESTOCÁSTICA DE DECISÃO' : 'STOCHASTIC DECISION PROPAGATION'}</span>
            </div>
            <h2 className="text-lg font-bold text-zinc-100">
              {isPt
                ? 'Simulação Monte Carlo: Teste de Falsificação H1 vs H0'
                : 'Monte Carlo Simulation: Falsification Test H1 vs H0'}
            </h2>
            <p className="text-xs text-zinc-300 leading-relaxed">
              {isPt
                ? 'Avaliamos a hipótese H1 (reentrada em Conde) contra a hipótese H0 (reentrada noutra região). Amostramos trajetórias estocásticas variando a época, arrasto balístico, escala de altura e flutuações solares de nov/1963, sem condicionar a amostra a priori a Conde.'
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
                ? 'Dispersão Global dos Pontos de Reentrada Terminal (<80 km)'
                : 'Global Dispersion of Terminal Reentry Points (<80 km)'}
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
              Probabilidade empírica: {(summary.empiricalProbability500Km * 100).toFixed(3)}%
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Dentro de 100 km de Conde:</div>
            <div className="text-lg font-bold text-rose-400 mt-1">{summary.runsWithin100Km}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              Probabilidade empírica: {(summary.empiricalProbability100Km * 100).toFixed(4)}%
            </div>
          </div>
        </div>
      )}

      {/* Epistemological Discussion */}
      <div className="p-5 rounded-xl bg-zinc-900 border border-zinc-800 space-y-3">
        <h4 className="text-xs font-bold text-zinc-200 flex items-center gap-2">
          <Info className="w-4 h-4 text-cyan-400" />
          <span>{isPt ? 'Conclusão Estatística e Falsificação Bayesiana' : 'Statistical & Bayesian Falsification Conclusion'}</span>
        </h4>
        <div className="text-xs text-zinc-300 space-y-2 leading-relaxed">
          <p>
            <strong className="text-zinc-100">1. A Densidade Geométrica Polar:</strong> Devido à inclinação de 81,86°, a velocidade angular em latitude é mínima próximo dos pontos de reversão (máxima latitude norte e sul). Isso faz com que a probabilidade de reentrada por unidade de latitude seja máxima nas regiões sub-polares e mínima no equador e trópicos (como Conde, a -11,8°).
          </p>
          <p>
            <strong className="text-zinc-100">2. A Falácia da Hipótese Condicionada:</strong> Uma área circular de 100 km de raio representa apenas <strong>0,0062%</strong> da superfície da Terra coberta pela órbita (1 em cada 16.000 áreas equivalentes). Selecionar Conde a posteriori apenas porque houve uma transmissão de rádio no Rio de Janeiro sem rastreamento radar independente não constitui evidência astrodinâmica.
          </p>
          <p>
            <strong className="text-zinc-100">3. Veredito Final:</strong> A hipótese H1 é matematicamente admissível dentro do espaço de fases, mas estatisticamente indistinguível de um ruído de fundo entre milhares de regiões desabitadas. Conjuntamente com o fato de que a Força Aérea Brasileira e o Consulado dos EUA constataram que não houve esfera, cratera ou restos em Conde, <strong>a hipótese de reentrada terminal em Conde permanece sem sustentação empírica</strong>.
          </p>
        </div>
      </div>
    </div>
  );
};
