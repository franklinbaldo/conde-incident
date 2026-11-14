import React, { useEffect, useMemo, useState } from 'react';
import { OrbitalMapSvg } from './map/OrbitalMapSvg';
import { clampZoom } from '../lib/mapGeometry';
import { mapTimeHref, MAP_TIME_START, MAP_TIME_END } from '../lib/tabRoutes';
import { CONDE_COORDINATES, HISTORICAL_ORBITAL_DATA } from '../lib/constants';
import { propagateState, generateGroundTrack, computeGroundTrackWithUncertainty } from '../lib/astrodynamics';
import type { GroundTrackPoint } from '../types/astrodynamics';

type Lang = 'pt' | 'en';
type Id = 527 | 528 | 529;
type Props = { lang: Lang; selectedTimeMs?: number; onTimeChange?: (value: number) => void };
const START = MAP_TIME_START;
const END = MAP_TIME_END;
const EPOCH = HISTORICAL_ORBITAL_DATA[528].epochDate.getTime();
// Fixed historical sources; these are DOCUMENTS, not impact coordinates.
const MATRIX = 'https://github.com/franklinbaldo/conde-incident/blob/a7978c3a75a153b16ab70118a92c434bba674cb7/research/evidence_matrix_C001-C238_2026-11-11.md';
const NASA = 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10';
const PRIMARY_TLE = 'https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/README.md';

const copy = {
  pt: {
    title: 'Mapa orbital exploratório',
    subtitle: 'Litoral Natural Earth 1:110m embarcado: sem Google Maps, API, tiles ou quota.',
    warning: 'O dia 08/11/1963 está documentado como decaimento de 1963-003B (C197#1), mas não há hora, ponto terminal ou impacto em Conde comprovados. Os vetores SGP4 e a altitude modelada NÃO foram calibrados com observação terminal.',
    source: 'Fonte e limites', dynamics: 'Trilhas derivadas de elementos ilustrativos, não medições',
    model: 'NORAD 528: TLE de espelho secundário (C179#1). NORAD 527 e 529: vetores de cenário legado, NÃO observações históricas.',
    time: 'Instante de cálculo (UTC, não hora de reentrada)', date: 'Dia escolhido, com 12:00 UTC arbitrário',
    resetTime: 'Época secundária 528', back: 'Anterior (1 h)', next: 'Seguinte (1 h)',
    play: 'Reproduzir cenário', pause: 'Pausar cenário', flat: 'Mapa 2D', globe: 'Globo 3D',
    sisters: 'Cenários 527/529', uncertain: 'Trilhas-limite hipotéticas', vectors: 'Conexões geométricas de cenários',
    zoomIn: 'Aproximar', zoomOut: 'Afastar', left: 'Mover à esquerda', right: 'Mover à direita',
    up: 'Mover para cima', down: 'Mover para baixo', resetView: 'Restaurar vista',
    rotateL: 'Girar globo à esquerda', rotateR: 'Girar globo à direita',
    noMarkers: 'Nenhuma observação radar com posição/erro autenticados foi localizada para este mapa. Não são desenhados marcadores de queda nem coordenadas fictícias.',
    legend: 'Legenda de cálculo (mesma época UTC, não triangulação instrumental)',
    conde: 'Conde, BA (referência geográfica)', displayed: 'modelo disponível', missing: 'sem posição de cenário',
    uncertainty: 'Faixas opcionais: envelopes heurísticos do código legado, SEM incerteza empírica calibrada nem nível de confiança.',
    geometry: 'Litoral Natural Earth 1:110m generalizado; não é levantamento local nem evidência de queda. Nenhum tile externo é solicitado.',
    instructions: 'No computador, arraste com mouse ou caneta. No celular, deslize para rolar a página e use os botões para mover, aproximar ou girar o mapa.',
    nodecay: 'O intervalo do controle não estima a hora de decaimento. Após 08/11, não é propagado o 528.',
    sources: 'Matriz C179#1 / C197#1', nasa: 'Boletim NASA 15/11/1963 (dia apenas)', custody: 'Auditoria TLE',
    land: 'Litoral Natural Earth 1:110m (domínio público)',
    permalink: 'Link para este instante do cenário (não é uma hora observada)',
    coastlines: 'Mostrar litoral generalizado', graticule: 'Mostrar grade geográfica',
  },
  en: {
    title: 'Exploratory orbit map',
    subtitle: 'Bundled Natural Earth 1:110m coastlines: no Google Maps, API, tiles or quota.',
    warning: '8 Nov 1963 is documented as the decay DAY for 1963-003B (C197#1), but no terminal hour, location or impact at Conde is established. The SGP4 vectors and modeled altitude are NOT calibrated against a terminal observation.',
    source: 'Sources and limits', dynamics: 'Tracks derived from illustrative elements, not measurements',
    model: 'NORAD 528: secondary mirrored TLE (C179#1). NORAD 527 and 529: legacy scenario vectors, NOT historical observations.',
    time: 'Calculation instant (UTC, not reentry time)', date: 'Selected day, with arbitrary 12:00 UTC',
    resetTime: 'Secondary 528 epoch', back: 'Previous (1 h)', next: 'Next (1 h)',
    play: 'Play scenario', pause: 'Pause scenario', flat: '2D map', globe: '3D globe',
    sisters: '527/529 scenarios', uncertain: 'Hypothetical envelope rails', vectors: 'Scenario geometry connections',
    zoomIn: 'Zoom in', zoomOut: 'Zoom out', left: 'Pan left', right: 'Pan right',
    up: 'Pan up', down: 'Pan down', resetView: 'Reset view',
    rotateL: 'Rotate globe left', rotateR: 'Rotate globe right',
    noMarkers: 'No radar observation with an authenticated position/error has been identified for this map. No impact pins or invented coordinates are plotted.',
    legend: 'Calculated legend (same UTC instant, not instrumental triangulation)',
    conde: 'Conde, Bahia (geographic reference)', displayed: 'scenario output available', missing: 'no scenario position',
    uncertainty: 'Optional rails: legacy code heuristic, with NO empirically calibrated uncertainty or confidence level.',
    geometry: 'Generalized Natural Earth 1:110m coastline, not a local survey or impact evidence. No external map tiles are requested.',
    instructions: 'On desktop, drag with a mouse or pen. On mobile, swipe to scroll the page; use the buttons to pan, zoom or rotate the map.',
    nodecay: 'This control does not estimate decay time. After 8 Nov, 528 is not propagated.',
    sources: 'Matrix C179#1 / C197#1', nasa: 'NASA bulletin 15 Nov 1963 (day only)', custody: 'TLE custody audit',
    land: 'Natural Earth 1:110m coastlines (public domain)',
    permalink: 'Link to this scenario instant (not an observed time)',
    coastlines: 'Show generalized coastline', graticule: 'Show geographic grid',
  },
};

export function OrbitalMap({ lang, selectedTimeMs, onTimeChange }: Props) {
  const t = copy[lang];
  const [time, setTime] = useState(() => selectedTimeMs ?? EPOCH);
  const [running, setRunning] = useState(false);
  const [mode, setMode] = useState<'flat' | 'globe'>('flat');
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [rotation, setRotation] = useState(0);
  const [showSisters, setShowSisters] = useState(true);
  const [showUncertainty, setShowUncertainty] = useState(false);
  const [showConnections, setShowConnections] = useState(false);
  const [showCoastlines, setShowCoastlines] = useState(true);
  const [showGraticule, setShowGraticule] = useState(true);

  const clampTime = (value: number) => Math.min(END, Math.max(START, Number.isFinite(value) ? value : EPOCH));
  const changeTime = (value: number) => {
    const next = clampTime(value);
    setTime(next);
    onTimeChange?.(next);
  };

  useEffect(() => {
    if (selectedTimeMs !== undefined && Number.isFinite(selectedTimeMs)) {
      setTime(clampTime(selectedTimeMs));
    }
  }, [selectedTimeMs]);

  useEffect(() => {
    if (!running) return;
    const interval = window.setInterval(() => {
      setTime(prev => {
        const next = clampTime(prev + 60 * 60 * 1000);
        onTimeChange?.(next);
        if (next >= END) setRunning(false);
        return next;
      });
    }, 700);
    return () => window.clearInterval(interval);
  }, [running, onTimeChange]);

  const now = new Date(time);
  const positions = useMemo(() => ({
    527: propagateState(527, new Date(time)),
    528: propagateState(528, new Date(time)),
    529: propagateState(529, new Date(time)),
  }), [time]);

  const data528 = useMemo(() => {
    const start = new Date(time - 45 * 60 * 1000);
    return showUncertainty
      ? computeGroundTrackWithUncertainty(528, start, 90, 90)
      : { points: generateGroundTrack(528, start, 90, 90), envelopes: [] };
  }, [time, showUncertainty]);

  const tracks: Record<Id, GroundTrackPoint[]> = useMemo(() => ({
    527: showSisters ? generateGroundTrack(527, new Date(time - 45 * 60 * 1000), 90, 90) : [],
    528: data528.points,
    529: showSisters ? generateGroundTrack(529, new Date(time - 45 * 60 * 1000), 90, 90) : [],
  }), [time, showSisters, data528]);

  const viewButton = (text: string, action: () => void, title?: string) => (
    <button type="button" onClick={action} title={title ?? text} aria-label={title ?? text}
      className="rounded border border-slate-600 bg-slate-800 px-2.5 py-1.5 text-slate-100 hover:bg-slate-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">
      {text}
    </button>
  );
  const layer = (label: string, checked: boolean, set: (value: boolean) => void) => (
    <label className="inline-flex items-center gap-2 rounded-md border border-slate-700 px-2 py-1.5 text-xs text-slate-200">
      <input type="checkbox" checked={checked} onChange={e => set(e.target.checked)}
        className="accent-cyan-500" />{label}
    </label>
  );

  return (
    <section className="min-w-0 space-y-4 [overflow-wrap:anywhere]" aria-labelledby="orbital-heading">
      <header className="space-y-2">
        <h1 id="orbital-heading" className="text-2xl font-semibold text-slate-100">{t.title}</h1>
        <p className="text-sm text-slate-300">{t.subtitle}</p>
        <p role="note" className="rounded-lg border border-amber-700 bg-amber-950/40 p-3 text-sm leading-relaxed text-amber-100">{t.warning}</p>
      </header>

      <div className="flex flex-wrap gap-2 items-center" role="group" aria-label={lang === 'pt' ? 'Projeção e camadas' : 'Projection and layers'}>
        <button type="button" aria-pressed={mode === 'flat'} onClick={() => setMode('flat')}
          className={'rounded-md px-3 py-1.5 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300 ' + (mode === 'flat' ? 'bg-cyan-700 text-white' : 'bg-slate-800 text-slate-200')}>{t.flat}</button>
        <button type="button" aria-pressed={mode === 'globe'} onClick={() => setMode('globe')}
          className={'rounded-md px-3 py-1.5 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300 ' + (mode === 'globe' ? 'bg-cyan-700 text-white' : 'bg-slate-800 text-slate-200')}>{t.globe}</button>
        {layer(t.sisters, showSisters, setShowSisters)}
        {layer(t.uncertain, showUncertainty, setShowUncertainty)}
        {layer(t.vectors, showConnections, setShowConnections)}
        {layer(t.coastlines, showCoastlines, setShowCoastlines)}
        {layer(t.graticule, showGraticule, setShowGraticule)}
      </div>

      <div className="min-w-0 max-w-full rounded-xl border border-slate-700 bg-slate-900 p-2 sm:p-3">
        <OrbitalMapSvg
          lang={lang} mode={mode} zoom={zoom} pan={pan} rotation={rotation}
          positions={positions} tracks={tracks} envelopes={data528.envelopes}
          showSisters={showSisters} showUncertainty={showUncertainty}
          showConnections={showConnections}
          showCoastlines={showCoastlines} showGraticule={showGraticule}
          onPan={(dx, dy) => setPan(p => ({ x: Math.max(-600, Math.min(600, p.x + dx)), y: Math.max(-400, Math.min(400, p.y + dy)) }))}
        />
        <div className="flex flex-wrap items-center gap-2 pt-3" role="group"
          aria-label={lang === 'pt' ? 'Controles acessíveis do mapa' : 'Accessible map controls'}>
          {viewButton('+', () => setZoom(z => clampZoom(z + 0.25)), t.zoomIn)}
          {viewButton('−', () => setZoom(z => clampZoom(z - 0.25)), t.zoomOut)}
          {viewButton('←', () => setPan(p => ({ ...p, x: Math.min(600, p.x + 30) })), t.left)}
          {viewButton('→', () => setPan(p => ({ ...p, x: Math.max(-600, p.x - 30) })), t.right)}
          {viewButton('↑', () => setPan(p => ({ ...p, y: Math.min(400, p.y + 30) })), t.up)}
          {viewButton('↓', () => setPan(p => ({ ...p, y: Math.max(-400, p.y - 30) })), t.down)}
          {mode === 'globe' && viewButton('⟲', () => setRotation(r => r - 15), t.rotateL)}
          {mode === 'globe' && viewButton('⟳', () => setRotation(r => r + 15), t.rotateR)}
          {viewButton(lang === 'pt' ? 'Restaurar' : 'Reset', () => { setZoom(1); setPan({ x: 0, y: 0 }); setRotation(0); }, t.resetView)}
        </div>
        <p className="pt-2 text-xs text-slate-400">{t.instructions} {t.geometry}</p>
      </div>

      <section className="min-w-0 space-y-3 rounded-lg border border-slate-800 bg-slate-900 p-3" aria-label={t.time}>
        <div className="flex flex-wrap items-center gap-3">
          <strong className="min-w-0 max-w-full font-mono text-sm text-cyan-200 [overflow-wrap:anywhere]" aria-live="off">{now.toISOString().replace('.000Z', 'Z')}</strong>
          <label className="flex min-w-0 max-w-full flex-col gap-1 text-xs text-slate-200">{t.date}{' '}
            <input type="date" min="1963-01-16" max="1963-11-08" value={now.toISOString().slice(0, 10)}
              onChange={e => { if (e.target.value) changeTime(Date.parse(e.target.value + 'T12:00:00Z')); }}
              className="min-w-0 max-w-full rounded bg-slate-800 p-1.5 text-white" />
          </label>
        </div>
        <input type="range" min={START} max={END} step={3600000} value={time}
          onChange={e => changeTime(Number(e.target.value))} aria-label={t.time}
          className="min-w-0 w-full accent-cyan-400" />
        <div className="flex flex-wrap gap-2">
          {viewButton(t.back, () => changeTime(time - 3600000))}
          {viewButton(running ? t.pause : t.play, () => setRunning(v => !v))}
          {viewButton(t.next, () => changeTime(time + 3600000))}
          {viewButton(t.resetTime, () => { setRunning(false); changeTime(EPOCH); })}
        </div>
        <p className="text-xs text-slate-400">{t.nodecay}</p>
        <a href={mapTimeHref(time)} className="inline-block rounded text-sm text-cyan-300 underline underline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300">{t.permalink}</a>
      </section>

      <section className="space-y-3 rounded-lg border border-slate-800 bg-slate-900 p-3" aria-label={t.legend}>
        <h2 className="font-semibold text-slate-100">{t.legend}</h2>
        <ul className="min-w-0 grid grid-cols-[minmax(0,1fr)] gap-2 text-sm sm:grid-cols-2" aria-live={running ? "off" : "polite"}>
          {([527, 528, 529] as const).filter(id => id === 528 || showSisters).map(id => (
            <li key={id} className="min-w-0 rounded border border-slate-700 p-2">
              <strong className={id === 528 ? 'text-cyan-300' : id === 527 ? 'text-emerald-300' : 'text-violet-300'}>NORAD {id}</strong>
              <span className="ml-2 text-slate-300">{positions[id]
                ? t.displayed + ' · ' + positions[id]!.altitudeKm.toFixed(0) + ' km (scenario)'
                : t.missing}</span>
            </li>
          ))}
          <li className="rounded border border-slate-700 p-2 text-rose-200">{t.conde}
            {' · ' + CONDE_COORDINATES.latitude.toFixed(4) + '°, ' + CONDE_COORDINATES.longitude.toFixed(4) + '°'}</li>
        </ul>
        <p className="text-xs text-slate-400">{t.model}</p>
        {showUncertainty && <p className="text-xs text-amber-200" role="note">{t.uncertainty}</p>}
        <p className="text-xs text-slate-400">{t.noMarkers}</p>
      </section>

      <aside role="note" className="space-y-2 text-xs text-slate-300" aria-label={t.source}>
        <p>{t.dynamics}</p>
        <div className="flex flex-wrap gap-x-5 gap-y-2 underline underline-offset-2">
          <a href={MATRIX + '#L839-L845'} target="_blank" rel="noopener noreferrer">{t.sources}</a>
          <a href={NASA} target="_blank" rel="noopener noreferrer">{t.nasa}</a>
          <a href={PRIMARY_TLE} target="_blank" rel="noopener noreferrer">{t.custody}</a>
          <a href="https://www.naturalearthdata.com/downloads/110m-physical-vectors/" target="_blank" rel="noopener noreferrer">{t.land}</a>
        </div>
      </aside>
    </section>
  );
}
