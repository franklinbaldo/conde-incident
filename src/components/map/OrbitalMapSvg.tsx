import React, { useRef } from 'react';
import type { GroundTrackPoint, UncertaintyEnvelope } from '../../types/astrodynamics';
import { projectFlat, projectGlobe, projectedSegments, canDrawFlatConnection } from '../../lib/mapGeometry';
import { canPanWithPointer, shouldShowScenarioConnections } from '../../lib/mapInteraction';
import { CONDE_COORDINATES } from '../../lib/constants';
import { coastline110mPart1 } from '../../lib/coastline110mPart1';
import { coastline110mPart2 } from '../../lib/coastline110mPart2';
import { coastline110mPart3 } from '../../lib/coastline110mPart3';

type Mode = 'flat' | 'globe';
type Marker = GroundTrackPoint | null;
type SatelliteId = 527 | 528 | 529;
type Props = {
  lang: 'pt' | 'en';
  mode: Mode;
  zoom: number;
  pan: { x: number; y: number };
  rotation: number;
  positions: Record<SatelliteId, Marker>;
  tracks: Record<SatelliteId, GroundTrackPoint[]>;
  envelopes: UncertaintyEnvelope[];
  showSisters: boolean;
  showUncertainty: boolean;
  showConnections: boolean;
  showCoastlines: boolean;
  showGraticule: boolean;
  onPan: (dx: number, dy: number) => void;
};

type Geo = { longitude: number; latitude: number };
type Screen = { x: number; y: number; visible: boolean };

// Natural Earth 1:110m public-domain coastlines, bundled locally with no tile provider.
// They are generalized geographic context, NOT geolocated impact evidence.
const COASTLINES: number[][][] = [
  ...coastline110mPart1, ...coastline110mPart2, ...coastline110mPart3,
];

const COLORS: Record<SatelliteId, string> = { 527: '#34d399', 528: '#22d3ee', 529: '#c4b5fd' };

export function OrbitalMapSvg({
  lang, mode, zoom, pan, rotation, positions, tracks, envelopes,
  showSisters, showUncertainty, showConnections, showCoastlines, showGraticule, onPan,
}: Props) {
  const start = useRef<{ x: number; y: number } | null>(null);
  const isPt = lang === 'pt';
  const project = (lon: number, lat: number): Screen =>
    mode === 'flat' ? projectFlat(lon, lat) : projectGlobe(lon, lat, rotation);

  const lines = (points: Geo[], color: string, strokeWidth = 1, dash = '') =>
    projectedSegments(points, project).map((segment: Screen[], i: number) => (
      <polyline
        key={i}
        points={segment.map(p => p.x + ',' + p.y).join(' ')}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeDasharray={dash || undefined}
        strokeLinejoin="round"
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
      />
    ));

  const grids: Geo[][] = [];
  for (let lat = -60; lat <= 60; lat += 30) {
    grids.push(Array.from({ length: 73 }, (_, i) => ({ longitude: -180 + i * 5, latitude: lat })));
  }
  for (let lon = -150; lon <= 180; lon += 30) {
    grids.push(Array.from({ length: 37 }, (_, i) => ({ longitude: lon, latitude: -90 + i * 5 })));
  }

  const displayed: SatelliteId[] = showSisters ? [527, 529, 528] : [528];
  const conde = project(CONDE_COORDINATES.longitude, CONDE_COORDINATES.latitude);
  const mapTitle = isPt ? 'Mapa orbital esquemático, sem mapa remoto' : 'Schematic orbital map without remote tiles';
  const mapDesc = isPt
    ? 'Trilhas SGP4 ilustrativas não observadas. O quadrado marca Conde apenas como referência geográfica, nunca como ponto de impacto. Litoral e grade podem ser ocultados.'
    : 'Illustrative SGP4 tracks are not observed. The square marks Conde as a geographic reference only, never as an impact location. Coastline and grid may be hidden.';
  const transform = 'translate(' + pan.x + ' ' + pan.y + ') translate(480 240) scale(' +
    zoom + ') translate(-480 -240)';

  const pointerDown = (event: React.PointerEvent<SVGSVGElement>) => {
    if (event.button !== 0 || !canPanWithPointer(event.pointerType)) return;
    start.current = { x: event.clientX, y: event.clientY };
    event.currentTarget.setPointerCapture(event.pointerId);
  };
  const pointerMove = (event: React.PointerEvent<SVGSVGElement>) => {
    if (!start.current) return;
    const rect = event.currentTarget.getBoundingClientRect();
    onPan(
      (event.clientX - start.current.x) * 960 / Math.max(rect.width, 1),
      (event.clientY - start.current.y) * 480 / Math.max(rect.height, 1),
    );
    start.current = { x: event.clientX, y: event.clientY };
  };
  const pointerUp = () => { start.current = null; };

  return (
    <svg
      className="block min-w-0 max-w-full rounded-lg border border-slate-700 bg-[#081527] select-none"
      viewBox="0 0 960 480"
      width="960"
      height="480"
      role="img"
      aria-labelledby="orbital-map-title orbital-map-desc"
      style={{ touchAction: 'pan-y', maxHeight: '65vh' }}
      onPointerDown={pointerDown}
      onPointerMove={pointerMove}
      onPointerUp={pointerUp}
      onPointerCancel={pointerUp}
    >
      <title id="orbital-map-title">{mapTitle}</title>
      <desc id="orbital-map-desc">{mapDesc}</desc>
      <defs>
        <clipPath id="raposa-globe-clip"><circle cx="480" cy="240" r="210" /></clipPath>
      </defs>
      <rect x="0" y="0" width="960" height="480" fill="#081527" />
      <g transform={transform}>
        {mode === 'globe' && <circle cx="480" cy="240" r="210" fill="#13243a" stroke="#52657d" strokeWidth="1.5" />}
        <g clipPath={mode === 'globe' ? 'url(#raposa-globe-clip)' : undefined}>
          {showGraticule && <g data-layer="graticule">
            {grids.map((grid, i) => <g key={'grid-' + i}>{lines(grid, '#26374c', 0.8, '4 6')}</g>)}
          </g>}
          {showCoastlines && <g data-layer="coastline">{COASTLINES.map((poly, i) => {
            const coords: Geo[] = poly.map(([longitude, latitude]) => ({ longitude, latitude }));
            // Polylines avoid falsely filling across the antimeridian/horizon.
            return <g key={'land-' + i}>{lines(coords, '#50708e', 1.2)}</g>;
          })}</g>}
          {showUncertainty && mode === 'flat' && envelopes.length > 1 && (
            <g aria-label={isPt ? 'Limites hipotéticos não calibrados' : 'Uncalibrated hypothetical bounds'}>
              {lines(envelopes.map(e => ({ longitude: e.leftLon, latitude: e.leftLat })), '#a5f3fc', 1.3, '5 5')}
              {lines(envelopes.map(e => ({ longitude: e.rightLon, latitude: e.rightLat })), '#a5f3fc', 1.3, '5 5')}
            </g>
          )}
          {displayed.map(id => (
            <g key={'track-' + id}>
              {lines(tracks[id], COLORS[id], id === 528 ? 2.6 : 1.5)}
            </g>
          ))}
          {shouldShowScenarioConnections(showConnections, showSisters, Boolean(positions[528])) && (
            <g>
              {([527, 529] as const).map(id => {
                const from = project(positions[528]!.longitude, positions[528]!.latitude);
                const other = positions[id];
                if (!other) return null;
                const to = project(other.longitude, other.latitude);
                if (!from.visible || !to.visible ||
                    (mode === 'flat' && !canDrawFlatConnection(positions[528]!, other))) return null;
                return <line key={'connection-' + id} x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                  stroke={COLORS[id]} strokeWidth="1" strokeDasharray="3 5" vectorEffect="non-scaling-stroke" />;
              })}
            </g>
          )}
          {conde.visible && (
            <g>
              <rect x={conde.x - 5} y={conde.y - 5} width="10" height="10"
                fill="#fb7185" stroke="#fff" strokeWidth="1.2" />
              <text x={conde.x + 9} y={conde.y - 8} fill="#fecdd3" fontSize="13" stroke="#081527"
                strokeWidth="2" paintOrder="stroke">{isPt ? "Conde (BA) · referência" : "Conde (BA) · reference"}</text>
            </g>
          )}
          {displayed.map(id => {
            const pos = positions[id];
            if (!pos) return null;
            const p = project(pos.longitude, pos.latitude);
            if (!p.visible) return null;
            return <g key={'satellite-' + id}>
              <circle cx={p.x} cy={p.y} r={id === 528 ? 7 : 5} fill={COLORS[id]} stroke="#fff" strokeWidth="1" />
              <text x={p.x + 10} y={p.y + 4} fill={COLORS[id]} fontSize="13" stroke="#081527"
                strokeWidth="2" paintOrder="stroke">NORAD {id}</text>
            </g>;
          })}
        </g>
      </g>
      <text x="12" y="466" fill="#cbd5e1" fontSize="12">
        {isPt ? 'ESQUEMA · contornos simplificados · trilhas calculadas · sem tiles' : 'SCHEMATIC · simplified outlines · calculated tracks · no tiles'}
      </text>
    </svg>
  );
}
