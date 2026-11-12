import React, { useRef } from 'react';
import type { GroundTrackPoint, UncertaintyEnvelope } from '../../types/astrodynamics';
import { projectFlat, projectGlobe, projectedSegments } from '../../lib/mapGeometry';

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
  onPan: (dx: number, dy: number) => void;
  onZoom: (next: number) => void;
};

type Geo = { longitude: number; latitude: number };
type Screen = { x: number; y: number; visible: boolean };

// Deliberately schematic background shapes, NOT geodetic coastline data.
const LAND: number[][][] = [
  [[-168,65],[-140,70],[-120,72],[-80,72],[-60,50],[-70,42],[-80,25],[-95,20],[-105,22],[-120,34],[-125,48],[-140,58],[-168,65]],
  [[-80,10],[-60,8],[-50,0],[-35,-5],[-37,-12],[-40,-22],[-50,-30],[-60,-40],[-68,-55],[-75,-48],[-72,-30],[-80,-5],[-80,10]],
  [[-10,36],[0,44],[10,55],[25,70],[60,70],[100,75],[140,70],[170,65],[140,40],[120,30],[105,10],[80,10],[60,25],[45,40],[30,30],[10,36],[-10,36]],
  [[-17,35],[10,37],[32,30],[42,12],[50,10],[40,-10],[30,-34],[18,-34],[10,-5],[-15,10],[-17,25],[-17,35]],
  [[115,-20],[130,-12],[145,-15],[150,-24],[152,-38],[138,-35],[115,-35],[115,-20]],
  [[-180,-70],[180,-70],[180,-85],[-180,-85]],
];

const CONDE = { longitude: -37.6108, latitude: -11.8139 };
const COLORS: Record<SatelliteId, string> = { 527: '#34d399', 528: '#22d3ee', 529: '#c4b5fd' };

export function OrbitalMapSvg({
  lang, mode, zoom, pan, rotation, positions, tracks, envelopes,
  showSisters, showUncertainty, showConnections, onPan, onZoom,
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
  const conde = project(CONDE.longitude, CONDE.latitude);
  const mapTitle = isPt ? 'Mapa orbital esquemático, sem mapa remoto' : 'Schematic orbital map without remote tiles';
  const mapDesc = isPt
    ? 'Trilhas calculadas de cenários SGP4 ilustrativos, não observações de trajetória ou impacto. Sem coordenadas observadas de reentrada.'
    : 'Calculated tracks from illustrative SGP4 scenarios, not observed paths or impact. No observed reentry coordinates.';
  const transform = 'translate(' + pan.x + ' ' + pan.y + ') translate(480 240) scale(' +
    zoom + ') translate(-480 -240)';

  const pointerDown = (event: React.PointerEvent<SVGSVGElement>) => {
    if (event.button !== 0) return;
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
      className="block w-full rounded-lg border border-slate-700 bg-[#081527] select-none"
      viewBox="0 0 960 480"
      width="960"
      height="480"
      role="img"
      aria-labelledby="orbital-map-title orbital-map-desc"
      style={{ touchAction: 'none', maxHeight: '65vh' }}
      onPointerDown={pointerDown}
      onPointerMove={pointerMove}
      onPointerUp={pointerUp}
      onPointerCancel={pointerUp}
      onWheel={(event) => { if (event.ctrlKey) return; onZoom(zoom + (event.deltaY < 0 ? 0.25 : -0.25)); }}
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
          {grids.map((grid, i) => <g key={'grid-' + i}>{lines(grid, '#26374c', 0.8, '4 6')}</g>)}
          {LAND.map((poly, i) => {
            const coords: Geo[] = poly.map(([longitude, latitude]) => ({ longitude, latitude }));
            // Polylines avoid falsely filling across the antimeridian/horizon.
            return <g key={'land-' + i}>{lines(coords, '#50708e', 1.2)}</g>;
          })}
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
          {showConnections && positions[528] && (
            <g>
              {([527, 529] as const).map(id => {
                const from = project(positions[528]!.longitude, positions[528]!.latitude);
                const other = positions[id];
                if (!other) return null;
                const to = project(other.longitude, other.latitude);
                if (!from.visible || !to.visible ||
                    (mode === 'flat' && Math.abs(other.longitude - positions[528]!.longitude) > 180)) return null;
                return <line key={'connection-' + id} x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                  stroke={COLORS[id]} strokeWidth="1" strokeDasharray="3 5" vectorEffect="non-scaling-stroke" />;
              })}
            </g>
          )}
          {conde.visible && (
            <g>
              <circle cx={conde.x} cy={conde.y} r="5" fill="#fb7185" stroke="#fff" strokeWidth="1.2" />
              <text x={conde.x + 9} y={conde.y - 8} fill="#fecdd3" fontSize="13" stroke="#081527"
                strokeWidth="2" paintOrder="stroke">Conde (BA)</text>
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
