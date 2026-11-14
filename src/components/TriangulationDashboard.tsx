import React, { useState } from 'react';
import { ArrowRightLeft, CalendarDays, ExternalLink, Info, Satellite } from 'lucide-react';
import { HISTORICAL_ORBITAL_DATA } from '../lib/constants';
import { getNodalPrecessionRateDegDay, getTriangulationState } from '../lib/astrodynamics';

interface TriangulationDashboardProps {
  lang: 'pt' | 'en';
}

// The secondary 528 TLE is the reference epoch, not a measured terminal position.
// This experiment does not infer a geographic reentry corridor from companion objects.
const EPOCH_528_MS = Date.parse('1963-10-27T14:40:16.132Z');
const DAY_MS = 86_400_000;
const SOURCE_1963 = 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf';
const SOURCE_1964 = 'https://ntrs.nasa.gov/api/citations/19640019314/downloads/19640019314.pdf';
const SECONDARY_TLE = 'https://www.itau.magnetic-declination.com/satellite/?s=528';
const SECONDARY_CATALOG = 'https://planet4589.org/space/gcat/data/derived/currentcat.html';

const examples = [
  { id: 527, designator: '1963 03A', source: SOURCE_1964, sourceLabel: 'NASA SSR 30/06/1964, p. 5' },
  { id: 528, designator: '1963 03B', source: SOURCE_1963, sourceLabel: 'NASA SSR 15/11/1963, p. 8' },
  { id: 529, designator: '1963 03C', source: SECONDARY_CATALOG, sourceLabel: 'GCAT (catálogo secundário)' },
] as const;

function formatDate(instant: Date) {
  return instant.toISOString().replace('T', ' ').replace('Z', ' UTC');
}

function SourceLink({ href, label }: { href: string; label: string }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer"
      className="inline-flex items-center gap-1 underline underline-offset-2 text-cyan-300 hover:text-cyan-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">
      {label}<ExternalLink className="h-3 w-3" aria-hidden="true" />
    </a>
  );
}

export const TriangulationDashboard: React.FC<TriangulationDashboardProps> = ({ lang }) => {
  const isPt = lang === 'pt';
  const [dayOffset, setDayOffset] = useState(0);
  const instant = new Date(EPOCH_528_MS + dayOffset * DAY_MS);
  const model = getTriangulationState(instant);

  const orbitalRate = (id: 527 | 528 | 529) => {
    const data = HISTORICAL_ORBITAL_DATA[id];
    const value = getNodalPrecessionRateDegDay(
      data.meanMotionRevDay, data.inclinationDeg,
      data.semiMajorAxisKm, data.eccentricity
    );
    return Number.isFinite(value) ? value.toFixed(4) : (isPt ? 'indisponível' : 'unavailable');
  };

  return (
    <section className="space-y-5" aria-labelledby="triangulation-title">
      <header className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 space-y-3">
        <div className="flex items-center gap-2 text-cyan-300 text-xs font-semibold uppercase tracking-wide">
          <Satellite className="h-4 w-4" aria-hidden="true" />
          {isPt ? 'Comparação documental e condicional' : 'Documentary and conditional comparison'}
        </div>
        <h1 id="triangulation-title" className="text-xl font-bold text-zinc-100">
          {isPt ? 'Objetos 527, 528 e 529: o que sabemos e o que calculamos'
            : 'Objects 527, 528 and 529: records versus calculations'}
        </h1>
        <p className="text-sm leading-relaxed text-zinc-300">
          {isPt
            ? 'Os registros relacionam os três números de catálogo ao lançamento de janeiro de 1963. Os vetores de 527 e 529 usados no modelo exploratório não foram autenticados como observações coépocas do 528. Compará-los não determina hora, local ou corredor de reentrada.'
            : 'The catalog records associate these three objects with the January 1963 launch. The 527 and 529 vectors used in the exploratory model have not been authenticated as observations contemporaneous with 528. Their comparison does not determine a reentry time, location or corridor.'}
        </p>
        <p className="text-xs text-zinc-400 flex gap-2">
          <Info className="h-4 w-4 shrink-0" aria-hidden="true" />
          {isPt
            ? 'Separação epistemológica: registro NASA, TLE secundário e simulação condicional não são medidas equivalentes.'
            : 'Evidence distinction: NASA record, secondary TLE and conditional simulation are not equivalent measurements.'}
        </p>
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {examples.map((item) => (
          <article key={item.id} className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 space-y-3">
            <h3 className="text-zinc-100 font-semibold">
              NORAD {item.id} <span className="text-xs font-normal text-zinc-400">{item.designator}</span>
            </h3>
            <p className="text-sm text-zinc-300">
              {item.id === 527
                ? (isPt
                  ? 'Boletim NASA de junho de 1964 contém elementos de situação do 527. Não valida a linha inicial de 1963 usada na simulação.'
                  : 'NASA June 1964 report lists 527 orbital status. It does not authenticate the model’s assumed early-1963 elements.')
                : item.id === 528
                ? (isPt
                  ? 'Boletim NASA registra 8/11/1963 como data de decaimento de 1963 3B, sem hora ou coordenadas. Existe TLE de espelho com época 27/10/1963, sem autenticação primária.'
                  : 'NASA lists 8 Nov 1963 as the recorded decay day for 1963 3B, without a time or coordinates. A secondary-mirror TLE has a 27 Oct epoch but no verified primary chain.')
                : (isPt
                  ? 'Data de decaimento tabulada no catálogo secundário. O vetor numérico empregado no simulador ainda carece de custódia instrumental.'
                  : 'Decay date from a secondary catalog. The numerical vector used by the simulator still lacks an authenticated instrumental chain.')}
            </p>
            <p className="text-xs text-zinc-400">
              <SourceLink href={item.source} label={item.sourceLabel} />
            </p>
            {item.id === 528 && (
              <p className="text-xs text-zinc-400">
                <SourceLink href={SECONDARY_TLE}
                  label={isPt ? 'C179#1: espelho TLE 528' : 'C179#1: secondary 528 TLE'} />
              </p>
            )}
          </article>
        ))}
      </div>

      <section aria-labelledby="triangulation-model-title"
        className="rounded-xl border border-cyan-900 bg-zinc-900 p-5 space-y-4">
        <div className="flex items-center gap-2">
          <ArrowRightLeft className="h-4 w-4 text-cyan-300" aria-hidden="true" />
          <h3 id="triangulation-model-title" className="font-semibold text-zinc-100">
            {isPt ? 'Experimento: sensibilidade à época escolhida'
              : 'Experiment: sensitivity to the selected epoch'}
          </h3>
        </div>
        <p className="text-xs leading-relaxed text-amber-200">
          {isPt
            ? 'MODELO EXPLORATÓRIO: J2 e evolução de altitude usam parâmetros legados e hipóteses não calibradas. Resultados abaixo NÃO são posições observadas, validação orbital nem limites geográficos demonstrados.'
            : 'EXPLORATORY MODEL: J2 and altitude evolution use legacy inputs and uncalibrated assumptions. Values below are NOT observed positions, validated orbits or demonstrated geographic bounds.'}
        </p>
        <div className="space-y-2">
          <label htmlFor="triangulation-day" className="block text-sm text-zinc-200">
            <CalendarDays className="h-4 w-4 inline mr-2" aria-hidden="true" />
            {isPt ? 'Deslocamento em dias desde o TLE secundário de 528' : 'Days from the secondary 528 TLE epoch'}
          </label>
          <input id="triangulation-day" type="range" min={-10} max={35} step={1}
            value={dayOffset} onChange={(e) => setDayOffset(Number(e.target.value))}
            className="w-full accent-cyan-400" aria-valuetext={formatDate(instant)} />
          <p className="text-sm text-zinc-300">
            {isPt ? 'Época do cálculo:' : 'Calculated epoch:'}{' '}
            <output htmlFor="triangulation-day" className="font-mono text-cyan-300">
              {formatDate(instant)}
            </output>
          </p>
          <p className="text-xs text-zinc-500">
            {isPt ? 'A hora é definida pelo controle da simulação, não por observação histórica.'
              : 'This time comes from the simulation control, not a historical observation.'}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4" aria-live="off">
          <div className="bg-zinc-950 rounded-lg border border-zinc-800 p-3">
            <div className="text-xs text-zinc-400">{isPt ? 'ΔΩ modelo 528–527' : 'Model ΔΩ 528–527'}</div>
            <div className="text-lg font-mono text-cyan-300">{model.deltaRaan528_527.toFixed(2)}°</div>
          </div>
          <div className="bg-zinc-950 rounded-lg border border-zinc-800 p-3">
            <div className="text-xs text-zinc-400">{isPt ? 'ΔΩ modelo 528–529' : 'Model ΔΩ 528–529'}</div>
            <div className="text-lg font-mono text-cyan-300">{model.deltaRaan528_529.toFixed(2)}°</div>
          </div>
          <div className="bg-zinc-950 rounded-lg border border-zinc-800 p-3">
            <div className="text-xs text-zinc-400">{isPt ? 'Altitude simulada 528' : 'Simulated 528 altitude'}</div>
            <div className="text-lg font-mono text-cyan-300">{model.sat528.altitudeKm.toFixed(1)} km</div>
          </div>
          <div className="bg-zinc-950 rounded-lg border border-zinc-800 p-3">
            <div className="text-xs text-zinc-400">{isPt ? 'Defasagem nominal 528–527' : 'Nominal phase drift 528–527'}</div>
            <div className="text-lg font-mono text-cyan-300">
              {(model.timeSinceLaunchDays *
                (HISTORICAL_ORBITAL_DATA[528].meanMotionRevDay -
                  HISTORICAL_ORBITAL_DATA[527].meanMotionRevDay)).toFixed(1)} rev
            </div>
          </div>
        </div>
        <details className="rounded-md border border-zinc-800 p-3 text-xs text-zinc-300">
          <summary className="cursor-pointer font-semibold">
            {isPt ? 'Taxas J2 condicionais dos três vetores' : 'Conditional J2 rates from the three vectors'}
          </summary>
          <dl className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-3">
            {([527, 528, 529] as const).map((id) => (
              <div key={id}>
                <dt className="text-zinc-400">NORAD {id}</dt>
                <dd className="font-mono">{orbitalRate(id)} °/{isPt ? 'dia' : 'day'}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-2 text-zinc-400">
            {isPt ? 'Taxas calculadas sobre entradas do modelo, não séries instrumentais comparáveis.'
              : 'Rates computed from model inputs, not comparable instrumental time series.'}
          </p>
        </details>
      </section>

      <p className="text-xs text-zinc-400 leading-relaxed">
        {isPt
          ? 'Condição para restringir a trajetória de 528: recuperar vetores autênticos, épocas e covariâncias comparáveis, calibrar o arrasto e testar o operador de propagação. A data NASA C197#1 é documental e não fixa hora nem coordenadas.'
          : 'To constrain the 528 trajectory: recover authenticated vectors, comparable epochs and covariances, calibrate drag and validate propagation. NASA C197#1 is a documentary date, not a terminal timestamp or position.'}
      </p>
    </section>
  );
};
