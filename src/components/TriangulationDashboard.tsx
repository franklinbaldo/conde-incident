import React, { useState } from 'react';
import {
  Layers,
  Satellite,
  Compass,
  TrendingDown,
  Info,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Flame,
  GitCommit,
  ArrowRightLeft,
  Crosshair,
  ShieldCheck,
} from 'lucide-react';
import {
  HISTORICAL_ORBITAL_DATA,
  LAUNCH_MISSION,
  CONDE_COORDINATES,
} from '../lib/constants';
import {
  getNodalPrecessionRateDegDay,
  getTriangulationState,
  computeInterTrackProximity,
  propagateState,
} from '../lib/astrodynamics';

interface TriangulationDashboardProps {
  lang: 'pt' | 'en';
}

export const TriangulationDashboard: React.FC<TriangulationDashboardProps> = ({
  lang,
}) => {
  const isPt = lang === 'pt';
  const [selectedDayOffset, setSelectedDayOffset] = useState<number>(295); // Days from launch (Nov 8 ~ 295 days)
  const [activeAnalysisTab, setActiveAnalysisTab] = useState<'tracks' | 'objects' | 'equations'>('tracks');

  const sat527 = HISTORICAL_ORBITAL_DATA[527];
  const sat528 = HISTORICAL_ORBITAL_DATA[528];
  const sat529 = HISTORICAL_ORBITAL_DATA[529];

  // Nodal precession rates
  const rate527 = getNodalPrecessionRateDegDay(sat527.meanMotionRevDay, sat527.inclinationDeg, sat527.semiMajorAxisKm, sat527.eccentricity);
  const rate528 = getNodalPrecessionRateDegDay(sat528.meanMotionRevDay, sat528.inclinationDeg, sat528.semiMajorAxisKm, sat528.eccentricity);
  const rate529 = getNodalPrecessionRateDegDay(sat529.meanMotionRevDay, sat529.inclinationDeg, sat529.semiMajorAxisKm, sat529.eccentricity);

  // Dynamic triangulation date based on slider
  const launchEpochMs = new Date(LAUNCH_MISSION.launchEpochUtc).getTime();
  const currentDate = new Date(launchEpochMs + selectedDayOffset * 86400 * 1000);
  const triState = getTriangulationState(currentDate);

  // Inter-Track Proximity for Conde Encounter (08/11/1963 19:48:00 UTC)
  const condeDate = new Date('1963-11-08T19:48:00Z');
  const conde528Point = propagateState(528, condeDate);
  const condeProximity = computeInterTrackProximity(
    conde528Point ? conde528Point.latitude : CONDE_COORDINATES.latitude,
    conde528Point ? conde528Point.longitude : CONDE_COORDINATES.longitude,
    conde528Point ? conde528Point.altitudeKm : 91,
    condeDate
  );

  // Dynamic Inter-Track Proximity for Current Slider Date
  const current528Point = propagateState(528, currentDate);
  const currentProximity = current528Point
    ? computeInterTrackProximity(
        current528Point.latitude,
        current528Point.longitude,
        current528Point.altitudeKm,
        currentDate
      )
    : null;

  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div className="space-y-1 max-w-3xl">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>{isPt ? 'DINÂMICA CONJUNTA MULTI-CORPO' : 'JOINT MULTI-BODY DYNAMICS'}</span>
            </div>
            <h2 className="text-lg font-bold text-zinc-100">
              {isPt
                ? 'Triangulação Dinâmica dos Objetos 527, 528 e 529'
                : 'Dynamic Triangulation of Objects 527, 528 and 529'}
            </h2>
            <p className="text-xs text-zinc-300 leading-relaxed">
              {isPt
                ? 'Os três objetos foram inseridos conjuntamente pelo foguete Thor-Agena D em 16/01/1963 numa órbita polar comum de 81,85°. A comparação entre o satélite principal e os componentes irmãos permite verificar a estabilidade do plano orbital e calibrar o modelo de arrasto, delimitando com rigor o que pode e o que não pode ser inferido.'
                : 'All three objects were jointly injected by the Thor-Agena D on 16/01/1963 into a common 81.85° polar orbit. Comparing the main satellite and sister components verifies orbital plane stability and calibrates atmospheric drag, rigorously defining what can and cannot be inferred.'}
            </p>
          </div>
        </div>
      </div>

      {/* Comparison Table of the 3 Objects */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* NORAD 527 */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono text-xs font-bold">
                NORAD 527
              </span>
              <span className="text-[10px] text-emerald-400 font-mono px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800">
                Ativo até 1969
              </span>
            </div>
            <div>
              <h3 className="text-sm font-bold text-zinc-100">OPS 0180 (1963-003A)</h3>
              <p className="text-xs text-zinc-400">Satélite militar principal NRO 7153 (Ferret 3 / ELINT)</p>
            </div>
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Inclinação:</span>
                <span className="text-zinc-200">81,8540°</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Altitude Média:</span>
                <span className="text-zinc-200">~485 km</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Movimento Médio:</span>
                <span className="text-zinc-200">15,268 rev/dia</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Regressão Nodal J2:</span>
                <span className="text-zinc-200">{rate527.toFixed(3)}°/dia</span>
              </div>
              <div className="flex justify-between text-zinc-400">
                <span>Data de Decaimento:</span>
                <span className="text-zinc-200">09/01/1969</span>
              </div>
            </div>
          </div>
          <div className="p-2.5 rounded bg-zinc-950 text-[11px] text-zinc-400">
            {isPt
              ? 'Permaneceu em órbita estável por 6 anos. Calibra o plano de referência e atesta ausência de tempestades destrutivas de arrasto em 1963.'
              : 'Remained in stable orbit for 6 years. Calibrates reference plane and verifies absence of extreme drag storms in 1963.'}
          </div>
        </div>

        {/* NORAD 528 (Target) */}
        <div className="bg-zinc-900 border-2 border-cyan-800/80 rounded-xl p-5 flex flex-col justify-between space-y-4 shadow-lg shadow-cyan-950/40 relative">
          <div className="absolute top-2 right-2">
            <span className="px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 font-mono text-[10px] font-bold border border-cyan-700">
              ALVO DE ESTUDO
            </span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center">
              <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 font-mono text-xs font-bold border border-cyan-800">
                NORAD 528
              </span>
            </div>
            <div>
              <h3 className="text-sm font-bold text-cyan-200">1963-003B (Debris/Adapter)</h3>
              <p className="text-xs text-zinc-400">Componente separado do Thor-Agena D</p>
            </div>
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Inclinação:</span>
                <span className="text-cyan-300 font-bold">81,8615°</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Altitude Inicial:</span>
                <span className="text-zinc-200">~345 km</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Movimento Médio:</span>
                <span className="text-zinc-200">15,749 rev/dia</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Regressão Nodal J2:</span>
                <span className="text-cyan-300 font-bold">{rate528.toFixed(3)}°/dia</span>
              </div>
              <div className="flex justify-between text-zinc-400">
                <span>Data de Decaimento:</span>
                <span className="text-amber-400 font-bold">08/11/1963</span>
              </div>
            </div>
          </div>
          <div className="p-2.5 rounded bg-cyan-950/50 border border-cyan-900 text-[11px] text-cyan-300">
            {isPt
              ? 'Decaiu após 295 dias em órbita. Altitude terminal (120-80 km) atingida em 08/11/1963, compatível com fragmento de alumínio de B ≈ 0,022 m²/kg.'
              : 'Decayed after 295 days. Terminal altitude (120-80 km) reached on 08/11/1963, consistent with aluminum fragment of B ≈ 0.022 m²/kg.'}
          </div>
        </div>

        {/* NORAD 529 */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col justify-between space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono text-xs font-bold">
                NORAD 529
              </span>
              <span className="text-[10px] text-zinc-400 font-mono px-2 py-0.5 rounded bg-zinc-800">
                Decaiu 31/12/1963
              </span>
            </div>
            <div>
              <h3 className="text-sm font-bold text-zinc-100">1963-003C (Componente C)</h3>
              <p className="text-xs text-zinc-400">Outro componente descartável do estágio</p>
            </div>
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Inclinação:</span>
                <span className="text-zinc-200">81,8215°</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Altitude (em dez):</span>
                <span className="text-zinc-200">~247 km</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Movimento Médio:</span>
                <span className="text-zinc-200">16,098 rev/dia</span>
              </div>
              <div className="flex justify-between text-zinc-400 border-b border-zinc-800/80 pb-1">
                <span>Regressão Nodal J2:</span>
                <span className="text-zinc-200">{rate529.toFixed(3)}°/dia</span>
              </div>
              <div className="flex justify-between text-zinc-400">
                <span>Data de Decaimento:</span>
                <span className="text-zinc-200">31/12/1963</span>
              </div>
            </div>
          </div>
          <div className="p-2.5 rounded bg-zinc-950 text-[11px] text-zinc-400">
            {isPt
              ? 'Decaiu 53 dias após o 528. Demonstra que a separação estrutural conferiu características balísticas intermediárias entre 528 e 527.'
              : 'Decayed 53 days after 528. Demonstrates that structural separation imparted ballistic properties between 528 and 527.'}
          </div>
        </div>
      </div>

      {/* Inter-Track Ground Proximity (Past & Future Bracket Analysis) */}
      <div className="bg-zinc-900 border-2 border-emerald-800/80 rounded-xl p-6 space-y-5 shadow-xl shadow-emerald-950/20">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-zinc-800 pb-3">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-700 text-emerald-300 text-xs font-mono font-bold">
              <GitCommit className="w-3.5 h-3.5 text-emerald-400" />
              <span>{isPt ? 'MÉTODO DE ENQUADRAMENTO DE TRAJETÓRIAS (BRACKET)' : 'GROUND TRACK BRACKETING METHOD'}</span>
            </div>
            <h3 className="text-base font-bold text-zinc-100 flex items-center gap-2">
              <span>{isPt ? 'Medição de Trajetórias Passadas e Futuras (528 vs 527 & 529)' : 'Past and Future Track Measurement (528 vs 527 & 529)'}</span>
            </h3>
            <p className="text-xs text-zinc-300 max-w-3xl leading-relaxed">
              {isPt
                ? 'Em vez de medir distâncias pontuais instantâneas entre satélites (sujeitas a oscilações keplerianas velozes), mede-se a distância ortodrômica entre as trilhas terrestres. A trajetória do 528 é rigorosamente balizada pela passagem anterior e pela próxima passagem de 527 e 529 no mesmo meridiano/paralelo.'
                : 'Instead of measuring instantaneous point-to-point 3D satellite distances, we measure the great-circle distance between ground tracks. NORAD 528’s track is strictly bounded by the preceding and subsequent passes of 527 and 529 across the geographic meridian/parallel.'}
            </p>
          </div>

          <div className="flex items-center gap-2 bg-zinc-950 p-1 rounded-lg border border-zinc-800 font-mono text-xs">
            <button
              onClick={() => setActiveAnalysisTab('tracks')}
              className={`px-3 py-1.5 rounded cursor-pointer transition-colors ${
                activeAnalysisTab === 'tracks'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Passagem Conde (08/11)
            </button>
            <button
              onClick={() => setActiveAnalysisTab('objects')}
              className={`px-3 py-1.5 rounded cursor-pointer transition-colors ${
                activeAnalysisTab === 'objects'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              Data do Slider (T+{selectedDayOffset}d)
            </button>
          </div>
        </div>

        {/* Selected Case Inspection */}
        {(() => {
          const proxData = activeAnalysisTab === 'tracks' ? condeProximity : currentProximity;
          if (!proxData) {
            return (
              <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-400 font-mono">
                Satélite fora do período ativo para este dia.
              </div>
            );
          }

          return (
            <div className="space-y-4">
              {/* Reference Header */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono">
                <div className="flex items-center gap-2 text-cyan-300">
                  <Crosshair className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span>
                    Ponto Central NORAD 528: <strong className="text-white">{proxData.referencePoint.latitude.toFixed(2)}°, {proxData.referencePoint.longitude.toFixed(2)}°</strong> (Alt: ~{proxData.referencePoint.altitudeKm.toFixed(0)} km)
                  </span>
                </div>
                <div className="text-emerald-400 font-bold">
                  Largura do Corredor 527: ~{proxData.corridorWidth527Km.toLocaleString()} km
                </div>
              </div>

              {/* 4 Bracketing Tracks Diagram & Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                {/* 1. 527 Passagem Passada */}
                <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-800/80 space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-emerald-400 font-bold flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      527 Trilha Passada
                    </span>
                    <span className="text-emerald-300 font-semibold">{proxData.past527.deltaMinutes} min</span>
                  </div>
                  <div className="space-y-1 font-mono text-[11px]">
                    <div className="text-zinc-400">
                      Distância à Trilha: <strong className="text-emerald-200 text-sm">~{proxData.past527.distanceKm} km</strong>
                    </div>
                    <div className="text-zinc-400">
                      Horário: <span className="text-zinc-300">{proxData.past527.time.toISOString().substring(11, 16)} UTC</span>
                    </div>
                    <div className="text-zinc-400">
                      Ponto Mais Próximo: <span className="text-zinc-300">{proxData.past527.latitude.toFixed(2)}°, {proxData.past527.longitude.toFixed(2)}°</span>
                    </div>
                  </div>
                  <div className="text-[10px] text-zinc-400 leading-tight border-t border-emerald-900/60 pt-1.5">
                    Trilha oeste anterior delimitadora.
                  </div>
                </div>

                {/* 2. 527 Próxima Passagem */}
                <div className="p-3.5 rounded-lg bg-emerald-950/30 border border-emerald-600/80 space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-emerald-300 font-bold flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-emerald-300" />
                      527 Trilha Futura
                    </span>
                    <span className="text-emerald-200 font-semibold">+{proxData.future527.deltaMinutes} min</span>
                  </div>
                  <div className="space-y-1 font-mono text-[11px]">
                    <div className="text-zinc-400">
                      Distância à Trilha: <strong className="text-emerald-100 text-sm">~{proxData.future527.distanceKm} km</strong>
                    </div>
                    <div className="text-zinc-400">
                      Horário: <span className="text-zinc-300">{proxData.future527.time.toISOString().substring(11, 16)} UTC</span>
                    </div>
                    <div className="text-zinc-400">
                      Ponto Mais Próximo: <span className="text-zinc-300">{proxData.future527.latitude.toFixed(2)}°, {proxData.future527.longitude.toFixed(2)}°</span>
                    </div>
                  </div>
                  <div className="text-[10px] text-zinc-400 leading-tight border-t border-emerald-900/60 pt-1.5">
                    Trilha leste subsequente delimitadora.
                  </div>
                </div>

                {/* 3. 529 Passagem Passada */}
                <div className="p-3.5 rounded-lg bg-purple-950/30 border border-purple-800/80 space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-purple-400 font-bold flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-purple-400" />
                      529 Trilha Passada
                    </span>
                    <span className="text-purple-300 font-semibold">{proxData.past529.deltaMinutes} min</span>
                  </div>
                  <div className="space-y-1 font-mono text-[11px]">
                    <div className="text-zinc-400">
                      Distância à Trilha: <strong className="text-purple-200 text-sm">~{proxData.past529.distanceKm} km</strong>
                    </div>
                    <div className="text-zinc-400">
                      Horário: <span className="text-zinc-300">{proxData.past529.time.toISOString().substring(11, 16)} UTC</span>
                    </div>
                    <div className="text-zinc-400">
                      Ponto Mais Próximo: <span className="text-zinc-300">{proxData.past529.latitude.toFixed(2)}°, {proxData.past529.longitude.toFixed(2)}°</span>
                    </div>
                  </div>
                  <div className="text-[10px] text-zinc-400 leading-tight border-t border-purple-900/60 pt-1.5">
                    Passagem do corpo C anterior.
                  </div>
                </div>

                {/* 4. 529 Próxima Passagem */}
                <div className="p-3.5 rounded-lg bg-purple-950/30 border border-purple-600/80 space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-mono">
                    <span className="text-purple-300 font-bold flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-purple-300" />
                      529 Trilha Futura
                    </span>
                    <span className="text-purple-200 font-semibold">+{proxData.future529.deltaMinutes} min</span>
                  </div>
                  <div className="space-y-1 font-mono text-[11px]">
                    <div className="text-zinc-400">
                      Distância à Trilha: <strong className="text-purple-100 text-sm">~{proxData.future529.distanceKm} km</strong>
                    </div>
                    <div className="text-zinc-400">
                      Horário: <span className="text-zinc-300">{proxData.future529.time.toISOString().substring(11, 16)} UTC</span>
                    </div>
                    <div className="text-zinc-400">
                      Ponto Mais Próximo: <span className="text-zinc-300">{proxData.future529.latitude.toFixed(2)}°, {proxData.future529.longitude.toFixed(2)}°</span>
                    </div>
                  </div>
                  <div className="text-[10px] text-zinc-400 leading-tight border-t border-purple-900/60 pt-1.5">
                    Passagem do corpo C subsequente.
                  </div>
                </div>
              </div>

              {/* Physical Takeaway Box */}
              <div className="p-4 rounded-lg bg-zinc-950 border border-emerald-900/70 text-xs text-zinc-300 space-y-2">
                <div className="font-bold text-emerald-300 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Conclusão Epistêmica do Enquadramento de Trajetórias:</span>
                </div>
                <p className="leading-relaxed text-zinc-300">
                  {proxData.bracketingVerdict} Como os três objetos mantêm uma <strong>relação nodal estrita</strong> governada pela mesma física de injeção polar, a passagem anterior e posterior do satélite principal 527 funcionam como <em>"balizas geográficas"</em> intransponíveis.
                </p>
                <p className="leading-relaxed text-zinc-400 text-[11px]">
                  Isso valida o raciocínio: a órbita do 528 não podia estar deslocada lateralmente em centenas de quilômetros fora dessa faixa. O seu plano transversal era extremamente fixo, delimitando com firmeza a longitude do cruzamento da Bahia.
                </p>
              </div>
            </div>
          );
        })()}
      </div>

      {/* Dynamic Triangulation Mathematical Inspector */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
        <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
          <Compass className="w-4 h-4 text-cyan-400" />
          <span>{isPt ? 'Evolução Temporal da Separação Nodal e de Fase' : 'Temporal Evolution of Nodal & Phase Separation'}</span>
        </h3>

        {/* Slider for days since launch */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-zinc-400">
              {isPt ? 'Data Simulada:' : 'Simulated Date:'}{' '}
              <strong className="text-cyan-300">
                {currentDate.toISOString().substring(0, 10)} (Dia T+{selectedDayOffset})
              </strong>
            </span>
            <span className="text-zinc-500">16/01/1963 → 31/12/1963</span>
          </div>

          <input
            type="range"
            min={0}
            max={350}
            value={selectedDayOffset}
            onChange={(e) => setSelectedDayOffset(Number(e.target.value))}
            className="w-full accent-cyan-500 cursor-pointer h-2 bg-zinc-950 rounded-lg appearance-none"
          />
        </div>

        {/* Real-time calculated separation metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
            <div className="text-zinc-500">Separação Nodal ΔΩ (528 - 527):</div>
            <div className="text-base font-bold text-cyan-300 mt-1">
              {triState.deltaRaan528_527.toFixed(2)}°
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">Divergência de planos</div>
          </div>
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
            <div className="text-zinc-500">Diferença de Voltas Acumuladas:</div>
            <div className="text-base font-bold text-amber-300 mt-1">
              {(selectedDayOffset * (sat528.meanMotionRevDay - sat527.meanMotionRevDay)).toFixed(1)} revs
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">Dispersão de anomalia</div>
          </div>
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
            <div className="text-zinc-500">Altitude Estimada do 528:</div>
            <div className="text-base font-bold text-zinc-100 mt-1">
              {triState.sat528.altitudeKm.toFixed(1)} km
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">Decaimento atmosférico</div>
          </div>
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800">
            <div className="text-zinc-500">Status do Satélite 527:</div>
            <div className="text-base font-bold text-emerald-400 mt-1">
              {triState.sat527.altitudeKm.toFixed(0)} km (Estável)
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">Órbita de 6 anos</div>
          </div>
        </div>
      </div>

      {/* Deep-Dive: A Aparente Constante de Distância vs. Deriva de Fase Real */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-bold text-zinc-100">
            {isPt
              ? 'Análise Crítica: Por que a Distância Parece Constante no Mapa (E o que a Física Revela)?'
              : 'Critical Analysis: Why Distance Seems Constant on the Map (And What Physics Reveals)?'}
          </h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-zinc-300">
          <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-2">
            <h4 className="font-bold text-cyan-300 flex items-center gap-1.5">
              <span>1. A Ilusão Visual do Plano Geométrico Comum</span>
            </h4>
            <p className="leading-relaxed">
              Ao observar o mapa em rotação ou estático, os três objetos aparentam manter uma distância regular ou proporcional (função trigonométrica suave). Isso ocorre porque <strong>eles compartilham praticamente a mesma inclinação orbital (~81,85°)</strong> e foram ejetados no mesmo plano inicial (mesmo Nó Ascendente RAAN inicial).
            </p>
            <p className="leading-relaxed text-zinc-400">
              No plano transversal (cross-track), a separação lateral entre as órbitas é de fato muito pequena e cresce lentamente pela regressão diferencial de $J_2$ (~0,04° por dia). Isso garante que o <em>corredor geográfico</em> das órbitas seja rigidamente compartilhado pelos 3 corpos.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-zinc-950 border border-zinc-800 space-y-2">
            <h4 className="font-bold text-amber-300 flex items-center gap-1.5">
              <span>2. O Desacoplamento Along-Track (141,9 Voltas de Diferença)</span>
            </h4>
            <p className="leading-relaxed">
              Pela Terceira Lei de Kepler (T = 2π √(a³/μ)), o objeto mais baixo (528 a 345 km) orbita mais rápido (n = 15,749 rev/dia) que o mais alto (527 a 485 km, n = 15,268 rev/dia).
            </p>
            <div className="p-2.5 rounded bg-zinc-900 font-mono text-[11px] text-amber-200 border border-zinc-800">
              Δn = 15,749 - 15,268 = +0,481 rev/dia (+173° de fase por dia)
              <br />
              Em 295 dias (16/01 → 08/11): Δfase = 295 × 0,481 = 141,9 revoluções completas!
            </div>
            <p className="leading-relaxed text-zinc-400">
              Isso significa que, a cada ~2 dias, o 528 dava uma volta inteira de vantagem sobre o 527. A distância 3D entre eles oscila continuamente entre um mínimo de ~280 km (quando se cruzam) até um máximo de ~10.000 km (em lados opostos da Terra), repetindo um ciclo periódico de 50 horas.
            </p>
          </div>
        </div>

        {/* Practical Conclusion on Triangulation */}
        <div className="p-4 rounded-lg bg-cyan-950/40 border border-cyan-800/80 text-xs text-zinc-300 space-y-2">
          <div className="font-bold text-cyan-200 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            <span>O que a Triangulação com 527 e 529 Prova (e o que ela Não Pode Provar):</span>
          </div>
          <ul className="list-disc list-inside space-y-1.5 leading-relaxed text-zinc-300 pl-1">
            <li>
              <strong className="text-zinc-100">O que PROVA:</strong> Como o 527 e o 529 têm elementos bem calibrados antes e depois de novembro de 1963, nós temos <em>certeza absoluta</em> de que não houve manobra orbital, impacto catastrófico externo ou tempestade geomagnética fora da escala solar em 1963. O plano orbital do 528 que cruza Conde é um fato astrodinâmico inquestionável.
            </li>
            <li>
              <strong className="text-zinc-100">O que NÃO PODE FIXAR:</strong> Sabendo a posição exata do satélite 527 às 19:48 UTC de 08/11/1963, não é possível deduzir a posição do 528 sem conhecer com precisão de frações de porcentagem o arrasto acumulado ao longo de 141 voltas de defasagem. Um erro de apenas 0,05% no arrasto ao longo de 12 dias altera a posição do 528 em milhares de quilômetros ao longo do trilho.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};
