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
              <span>{isPt ? 'AMOSTRAGEM GEOMÉTRICA EXPLORATÓRIA' : 'EXPLORATORY GEOMETRIC SAMPLING'}</span>
            </div>
            <h2 className="text-lg font-bold text-zinc-100">
              {isPt
                ? 'Amostras sintéticas: não são probabilidades de impacto'
                : 'Synthetic samples: not impact probabilities'}
            </h2>
            <p className="text-xs text-zinc-300 leading-relaxed">
              {isPt
                ? 'O algoritmo sorteia fase orbital e parâmetros hipotéticos; não ajusta a trajetória a observações independentes do NORAD 528. Cada ponto representa uma amostra de demonstração, não um lugar de reentrada observado nem uma distribuição calibrada.'
                : 'The algorithm randomly samples orbital phase and hypothetical parameters; it is not fitted to independent NORAD 528 observations. Each point is a demonstration sample, not an observed reentry location or a calibrated distribution.'}
            </p>
          </div>

          {/* Sample Size selector & Run Button */}
          <div className="flex items-center gap-2 shrink-0">
            <select
              value={sampleSize}
              onChange={(e) => setSampleSize(Number(e.target.value))}
              className="bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs rounded-lg px-3 py-2 font-mono cursor-pointer"
            >
              <option value={1000}>N = 1.000 amostras</option>
              <option value={2000}>N = 2.000 amostras</option>
              <option value={5000}>N = 5.000 amostras</option>
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
                ? 'Distribuição sintética de coordenadas (limiar simulado de 80 km)'
                : 'Synthetic coordinate distribution (modelled 80 km threshold)'}
            </span>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-mono text-zinc-400">
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400/40 inline-block" />
              <span>{isPt ? 'Amostra global' : 'Global sample'}</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" />
              <span>Regional (&lt;500 km)</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" />
              <span>{isPt ? 'Dentro de 100 km (modelo)' : 'Within 100 km (model)'}</span>
            </span>
          </div>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-lg overflow-hidden">
          <canvas
            ref={canvasRef}
            width={1000}
            height={480}
            className="w-full h-auto block select-none"
            role="img"
            aria-label={isPt ? "Gráfico de amostras sintéticas de latitude e longitude, não pontos observados de reentrada" : "Plot of synthetic latitude and longitude samples, not observed reentry points"}
          />
        </div>
        <p className="text-xs text-zinc-300 leading-relaxed">
          {isPt
            ? "Visualização apenas geométrica. A marca de Conde indica a sede aproximada, não um local confirmado de impacto. As posições simuladas não possuem incerteza física ou validação por holdout."
            : "Geometric visualization only. The Conde marker denotes the approximate town centre, not a confirmed impact site. Sampled positions lack physically calibrated uncertainty and holdout validation."}
        </p>
      </div>

      {/* Metrics Table */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Amostras sintéticas:</div>
            <div className="text-lg font-bold text-zinc-100 mt-1">{summary.totalRuns}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              Com data simulada 08/11: {summary.runsDecayedOnNov8} ({((summary.runsDecayedOnNov8/summary.totalRuns)*100).toFixed(1)}%)
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Faixa de latitude da sede:</div>
            <div className="text-lg font-bold text-cyan-300 mt-1">{summary.runsInCondeLatitudeBand}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              {((summary.runsInCondeLatitudeBand / summary.totalRuns) * 100).toFixed(2)}% da amostra
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Dentro de 500 km de Conde:</div>
            <div className="text-lg font-bold text-amber-300 mt-1">{summary.runsWithin500Km}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              Fração das amostras: {(summary.empiricalProbability500Km * 100).toFixed(2)}%
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-zinc-900 border border-zinc-800">
            <div className="text-zinc-500">Dentro de 100 km de Conde:</div>
            <div className="text-lg font-bold text-rose-400 mt-1">{summary.runsWithin100Km}</div>
            <div className="text-[10px] text-zinc-500 mt-0.5">
              Fração das amostras: {(summary.empiricalProbability100Km * 100).toFixed(2)}%
            </div>
          </div>
        </div>
      )}

      {/* Interpretation depends on calibrated evidence, not visually persuasive samples. */}
      <section aria-labelledby="montecarlo-limits" className="p-5 rounded-xl bg-zinc-900 border border-zinc-700 space-y-3">
        <h3 id="montecarlo-limits" className="text-sm font-semibold text-zinc-100">
          {isPt ? 'O que estes números não medem' : 'What these numbers do not measure'}
        </h3>
        <p className="text-sm text-zinc-300 leading-relaxed">
          {isPt
            ? 'As frações acima descrevem somente esta execução do gerador. Não são probabilidades de uma queda em Conde: a fase é sorteada, a escala de arrasto é hipotética, a RAAN histórica está em disputa e não houve ajuste temporal validado, domínio admissível comprovadamente não vazio ou teste cego de previsão.'
            : 'The fractions describe this generator run only. They are not probabilities of a fall in Conde: orbital phase is random, drag settings are hypothetical, historical RAAN is disputed, and no validated temporal fit, proven nonempty admissible domain or blind prediction test is available.'}
        </p>
        <p className="text-sm text-amber-200">
          {isPt
            ? 'Resultado: indeterminado. A amostragem usa números aleatórios sem seed de reprodução; ela não testa nem rejeita a hipótese histórica.'
            : 'Outcome: undetermined. Sampling uses unseeded random numbers and neither tests nor rejects the historical hypothesis.'}
        </p>
        <div className="flex flex-wrap gap-x-5 gap-y-2 text-sm">
          <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline" href="#/research/c197">
            {isPt ? 'C197–C202: decaimento NASA, somente dia' : 'C197–C202: NASA decay day only'}
          </a>
          <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline" href="#/research/raan">
            {isPt ? 'Conflito RAAN e premissas' : 'RAAN conflict and assumptions'}
          </a>
          <a className="text-cyan-300 underline underline-offset-4 focus-visible:outline" href="#/research/holdout529">
            {isPt ? 'Controle e limites do holdout 529' : '529 holdout limits'}
          </a>
        </div>
      </section>
    </div>
  );
};
