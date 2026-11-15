import React, { useState, useMemo, useId } from 'react';
import {
  Wind,
  Layers,
  Gauge,
  Calendar,
} from 'lucide-react';
import { HISTORICAL_ORBITAL_DATA } from '../lib/constants';
import { getThermosphericDensity } from '../lib/astrodynamics';

interface AtmosphereSensitivityProps {
  lang: 'pt' | 'en';
}

export const AtmosphereSensitivity: React.FC<AtmosphereSensitivityProps> = ({
  lang,
}) => {
  const isPt = lang === 'pt';
  const scaleHeightId = useId();
  const solarFluxId = useId();
  const ballisticCoeffId = useId();

  const [scaleHeightKm, setScaleHeightKm] = useState<number>(45);
  const [solarFluxF107, setSolarFluxF107] = useState<number>(76.5);
  const [ballisticCoeff, setBallisticCoeff] = useState<number>(0.022);

  const resetParameters = () => {
    setScaleHeightKm(45);
    setSolarFluxF107(76.5);
    setBallisticCoeff(0.022);
  };
  const isReferenceScenario = scaleHeightKm === 45 && solarFluxF107 === 76.5 && ballisticCoeff === 0.022;

  // Compute simulated arrival at 120 km interface based on sliders
  const simulatedDecayDays = useMemo(() => {
    // Reference: H = 45 km, B = 0.022, F10.7 = 76.5 -> 12 days (08/11/1963)
    const bRatio = 0.022 / Math.max(0.005, ballisticCoeff);
    const hRatio = scaleHeightKm / 45.0;
    const fRatio = 76.5 / Math.max(65, solarFluxF107);
    return 12.0 * Math.pow(bRatio, 0.28) * Math.pow(hRatio, 0.25) * Math.pow(fRatio, 0.18);
  }, [scaleHeightKm, ballisticCoeff, solarFluxF107]);

  const simulatedDecayDate = useMemo(() => {
    const epochMs = HISTORICAL_ORBITAL_DATA[528].epochDate.getTime();
    return new Date(epochMs + simulatedDecayDays * 86400 * 1000);
  }, [simulatedDecayDays]);

  // Historical Reference Table from the Handoff
  const sensitivityTable = [
    {
      scale: 40,
      arrivalDate: '06/11/1963',
      matchStatus: isPt ? 'Anterior ao dia catalogado (−2 dias)' : 'Before the catalogued day (−2 days)',
      matchColor: 'text-zinc-400',
    },
    {
      scale: 45,
      arrivalDate: '08/11/1963',
      matchStatus: isPt ? 'MESMO DIA DO CATÁLOGO (não é validação)' : 'SAME CATALOGUED DAY (not validation)',
      matchColor: 'text-emerald-400 font-bold',
    },
    {
      scale: 50,
      arrivalDate: '09/11/1963',
      matchStatus: isPt ? 'Posterior ao dia catalogado (+1 dia)' : 'After the catalogued day (+1 day)',
      matchColor: 'text-amber-400',
    },
    {
      scale: 60,
      arrivalDate: '11/11/1963',
      matchStatus: isPt ? 'Posterior ao dia catalogado (+3 dias)' : 'After the catalogued day (+3 days)',
      matchColor: 'text-zinc-400',
    },
  ];

  // Atmospheric altitude curve points (80 km to 350 km)
  const altitudeProfile = useMemo(() => {
    const points = [];
    for (let alt = 350; alt >= 80; alt -= 30) {
      const rho = getThermosphericDensity(alt, scaleHeightKm);
      points.push({ alt, rho });
    }
    return points;
  }, [scaleHeightKm]);

  return (
    <div className="space-y-6 min-w-0">
      {/* Intro Header */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 sm:p-6">
        <div className="space-y-1 max-w-3xl">
          <div className="inline-flex flex-wrap max-w-full min-w-0 items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono">
            <Wind className="w-3.5 h-3.5 text-cyan-400" />
            <span className="min-w-0 break-words">{isPt ? 'MODELAGEM TERMOESFÉRICA & ARRASTO' : 'THERMOSPHERIC DRAG MODELING'}</span>
          </div>
          <h1 className="text-lg font-bold text-zinc-100 break-words">
            {isPt
              ? 'Análise de Sensibilidade do Decaimento Atmosférico'
              : 'Atmospheric Decay Sensitivity Analysis'}
          </h1>
          <p className="text-xs text-zinc-300 leading-relaxed">
            {isPt
              ? 'Este experimento varia parâmetros ilustrativos de arrasto, fluxo solar e escala atmosférica para um cálculo simplificado de chegada a 120 km. Os valores não foram calibrados com observações instrumentais autenticadas do NORAD 528 e não determinam a data nem o local de reentrada.'
              : 'This experiment varies illustrative drag, solar-flux and atmospheric scale parameters for a simplified calculation of arrival at 120 km. These inputs were not calibrated against authenticated NORAD 528 instrumental observations and do not establish a reentry date or location.'}
          </p>
        </div>
      </div>

      {/* Sliders & Active Projection */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-w-0">
        {/* Controls (7 Cols) */}
        <div className="lg:col-span-7 min-w-0 bg-zinc-900 border border-zinc-800 rounded-xl p-4 sm:p-6 space-y-5">
          <h2 className="text-sm font-bold text-zinc-100 flex flex-wrap items-center gap-2 min-w-0 break-words">
            <Gauge className="w-4 h-4 text-cyan-400" />
            <span>{isPt ? 'Parâmetros Físicos e Ambientais de 1963' : '1963 Physical & Environmental Parameters'}</span>
          </h2>

          {/* Scale Height Slider */}
          <div className="space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-xs font-mono min-w-0">
              <label htmlFor={scaleHeightId} className="text-zinc-200 min-w-0 break-words">
                {isPt ? 'Escala de Altura Termoesférica (H):' : 'Thermospheric Scale Height (H):'}{' '}
                <strong className="text-cyan-300">{scaleHeightKm} km</strong>
              </label>
              <span className="text-zinc-400">{isPt ? 'Referência do cenário: 45 km' : 'Scenario reference: 45 km'}</span>
            </div>
            <input
              id={scaleHeightId}
              type="range"
              aria-valuetext={`${scaleHeightKm} km`}
              min={35}
              max={65}
              step={1}
              value={scaleHeightKm}
              onChange={(e) => setScaleHeightKm(Number(e.target.value))}
              className="w-full accent-cyan-500 cursor-pointer h-2 bg-zinc-950 rounded-lg appearance-none"
            />
          </div>

          {/* Solar Flux F10.7 Slider */}
          <div className="space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-xs font-mono min-w-0">
              <label htmlFor={solarFluxId} className="text-zinc-200 min-w-0 break-words">
                {isPt ? 'Fluxo Solar F10.7 (comprimento 10,7 cm):' : 'Solar Flux F10.7 (10.7 cm):'}{' '}
                <strong className="text-amber-300">{solarFluxF107} sfu</strong>
              </label>
              <span className="text-zinc-400">{isPt ? 'Referência do cenário: 76,5 sfu' : 'Scenario reference: 76.5 sfu'}</span>
            </div>
            <input
              id={solarFluxId}
              type="range"
              aria-valuetext={`${solarFluxF107} sfu`}
              min={65}
              max={120}
              step={0.5}
              value={solarFluxF107}
              onChange={(e) => setSolarFluxF107(Number(e.target.value))}
              className="w-full accent-amber-500 cursor-pointer h-2 bg-zinc-950 rounded-lg appearance-none"
            />
          </div>

          {/* Ballistic Coefficient B */}
          <div className="space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 text-xs font-mono min-w-0">
              <label htmlFor={ballisticCoeffId} className="text-zinc-200 min-w-0 break-words">
                {isPt ? 'Coeficiente Balístico B (C_D · A / m):' : 'Ballistic Coefficient B (C_D · A / m):'}{' '}
                <strong className="text-emerald-300">{ballisticCoeff.toFixed(4)} m²/kg</strong>
              </label>
              <span className="text-zinc-400">{isPt ? 'Faixa ilustrativa: 0,015–0,035 m²/kg' : 'Illustrative range: 0.015–0.035 m²/kg'}</span>
            </div>
            <input
              id={ballisticCoeffId}
              type="range"
              aria-valuetext={`${ballisticCoeff.toFixed(4)} m²/kg`}
              min={0.008}
              max={0.05}
              step={0.001}
              value={ballisticCoeff}
              onChange={(e) => setBallisticCoeff(Number(e.target.value))}
              className="w-full accent-emerald-500 cursor-pointer h-2 bg-zinc-950 rounded-lg appearance-none"
            />
          </div>

          <button
            type="button"
            onClick={resetParameters}
            disabled={isReferenceScenario}
            className="min-h-11 rounded-lg border border-cyan-700 px-4 py-2 text-xs font-semibold text-cyan-200 enabled:hover:bg-cyan-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isPt ? 'Restaurar parâmetros de referência' : 'Reset reference parameters'}
          </button>

          {/* Simulated Decay Output Card */}
          <div className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2 font-mono text-xs">
            <div className="text-zinc-400 uppercase tracking-wider text-[10px]">
              {isPt ? 'Resultado do modelo simplificado' : 'Simplified model result'}
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 min-w-0">
              <div>
                <span className="text-zinc-400">{isPt ? 'Chegada simulada a 120 km:' : 'Simulated arrival at 120 km:'}</span>{' '}
                <span className="text-base font-bold text-zinc-100 break-words">
                  {simulatedDecayDate.toISOString().substring(0, 10)}
                </span>
              </div>
              <span
                className={`text-[11px] px-2.5 py-0.5 rounded font-semibold border ${
                  simulatedDecayDate.toISOString().substring(0, 10) === '1963-11-08'
                    ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800'
                    : 'text-amber-400 bg-amber-950/60 border-amber-800'
                }`}
              >
                {simulatedDecayDate.toISOString().substring(0, 10) === '1963-11-08'
                  ? (isPt ? 'Mesmo dia catalogado (não valida queda)' : 'Same catalogued day (not impact proof)')
                  : (isPt ? 'Dia diferente do catálogo (não valida queda)' : 'Different catalogued day (not impact proof)')}
              </span>
            </div>
          </div>
          <p className="text-xs text-zinc-300 leading-relaxed" data-testid="sensitivity-reference-caveat">
            {isPt
              ? 'A duração de referência de 12 dias, contada desde a época codificada de 27/10/1963, produz 08/11/1963 por construção. Mudar os controles mostra apenas a sensibilidade desta fórmula, não uma validação histórica.'
              : 'The 12-day reference duration, counted from the encoded epoch of October 27, 1963, yields November 8, 1963 by construction. Changing the controls shows only this formula’s sensitivity, not historical validation.'}
          </p>
        </div>

        {/* Reference Table (5 Cols) */}
        <div className="lg:col-span-5 min-w-0 bg-zinc-900 border border-zinc-800 rounded-xl p-4 sm:p-5 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex flex-wrap items-center gap-2 min-w-0">
              <Calendar className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-zinc-100">
                {isPt ? 'Cenários ilustrativos de sensibilidade' : 'Illustrative sensitivity scenarios'}
              </h2>
            </div>
            <p className="text-xs text-zinc-300">
              {isPt
                ? 'Escolha uma escala de altura para recalcular a simulação acima. As datas abaixo pertencem à tabela legada ilustrativa, não são resultados da fórmula interativa.'
                : 'Choose a scale height to recalculate the simulation above. The dates below are from the illustrative legacy table, not outputs of the interactive formula.'}
            </p>

            <div className="space-y-2" role="group" aria-label={isPt ? 'Selecionar escala de altura ilustrativa' : 'Select illustrative scale height'}>
              {sensitivityTable.map((row) => (
                <button
                  key={row.scale}
                  type="button"
                  onClick={() => setScaleHeightKm(row.scale)}
                  aria-pressed={scaleHeightKm === row.scale}
                  className={`w-full text-left p-3 rounded-lg border text-xs font-mono flex flex-wrap items-start justify-between gap-2 min-w-0 min-h-11 cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 ${
                    scaleHeightKm === row.scale
                      ? 'bg-cyan-950/40 border-cyan-500'
                      : 'bg-zinc-950 border-zinc-700 hover:border-cyan-700'
                  }`}
                >
                  <span>
                    <span className="text-zinc-100 font-bold block">H = {row.scale} km</span>
                    <span className="text-[11px] text-zinc-300 block">{isPt ? 'Tabela legada:' : 'Legacy table:'} {row.arrivalDate}</span>
                  </span>
                  <span className={`text-[10px] min-w-0 break-words ${row.matchColor}`}>
                    {row.matchStatus}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-[11px] text-zinc-400 space-y-1">
            <strong className="text-zinc-200 block font-semibold">
              {isPt ? 'Limites do campo BSTAR = 0:' : 'Limits of the BSTAR = 0 field:'}
            </strong>
            <p className="leading-relaxed">
              {isPt
                ? 'O campo BSTAR = 0 do par TLE secundário preservado não demonstra arrasto físico nulo nem fornece o coeficiente balístico histórico. H = 45 km e B ≈ 0,022 m²/kg são hipóteses ilustrativas, não parâmetros calibrados para o objeto. A coincidência com 08/11 decorre do cenário de referência definido no modelo, não de uma previsão independente.'
                : 'The BSTAR = 0 field in the preserved secondary TLE does not establish zero physical drag or provide the historical ballistic coefficient. H = 45 km and B ≈ 0.022 m²/kg are illustrative assumptions, not parameters calibrated for this object. The match with November 8 follows from the model reference scenario, not an independent prediction.'}
            </p>
          </div>
        </div>
      </div>

      {/* Thermospheric Density Profile Card */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 sm:p-6 space-y-3">
        <h2 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>{isPt ? 'Perfil de Densidade Atmosférica (80 a 350 km)' : 'Atmospheric Density Profile (80 to 350 km)'}</span>
        </h2>
        <div className="grid grid-cols-1 min-[420px]:grid-cols-2 sm:grid-cols-5 gap-3 font-mono text-xs">
          {altitudeProfile.map((pt) => (
            <div key={pt.alt} className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800">
              <div className="text-zinc-400 font-semibold">{pt.alt} km</div>
              <div className="text-cyan-300 font-bold mt-1">{pt.rho.toExponential(2)}</div>
              <div className="text-[10px] text-zinc-400">kg/m³</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
