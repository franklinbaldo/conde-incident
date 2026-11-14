#!/usr/bin/env python3
"""Deterministic offline overview of Conde from the site's pinned Natural Earth coast.

Not a cadastral map, historical geometry, sensor track, or impact location.
The source modules document Natural Earth revision and original SHA-256.
"""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'static/img/conde-bahia-context.svg'
# Explicit coordinate frame: lon/lat degrees, WGS84-like for visual context only.
LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -45.0, -33.0, -20.0, -5.0
X0, X1, Y0, Y1 = 55.0, 745.0, 55.0, 430.0
CONDE_LON, CONDE_LAT = -37.61, -11.81  # Approximate municipal seat, not the event.


def project(lon, lat):
    return (X0 + (lon - LON_MIN) / (LON_MAX - LON_MIN) * (X1 - X0),
            Y0 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * (Y1 - Y0))


def clip_segment(a, b):
    """Liang-Barsky clipping keeps coastlines from crossing map borders."""
    x0, y0 = a
    x1, y1 = b
    dx, dy = x1 - x0, y1 - y0
    lo, hi = 0.0, 1.0
    for p, q in ((-dx, x0-LON_MIN), (dx, LON_MAX-x0),
                 (-dy, y0-LAT_MIN), (dy, LAT_MAX-y0)):
        if abs(p) < 1e-12:
            if q < 0:
                return None
            continue
        u = q / p
        if p < 0:
            lo = max(lo, u)
        else:
            hi = min(hi, u)
        if lo > hi:
            return None
    return ((x0 + lo*dx, y0 + lo*dy), (x0 + hi*dx, y0 + hi*dy))


def source_lines():
    paths = []
    for part in range(1, 4):
        source = (ROOT / f'src/lib/coastline110mPart{part}.js').read_text()
        match = re.search(r'export const coastline110mPart\d+\s*=\s*(\[.*\]);', source, re.S)
        if not match:
            raise ValueError(f'Natural Earth source part {part} missing')
        paths.extend(json.loads(match.group(1)))
    return paths


def make_svg():
    segments = []
    for line in source_lines():
        for a, b in zip(line, line[1:]):
            clipped = clip_segment(a, b)
            if clipped is None:
                continue
            (x0, y0), (x1, y1) = [project(*p) for p in clipped]
            segments.append(f'M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}')
    if len(segments) < 4:
        raise ValueError('Regional coastline unexpectedly missing')
    coast = ' '.join(segments)
    grid = []
    for lon in (-44, -42, -40, -38, -36, -34):
        x, _ = project(lon, LAT_MAX)
        grid.append(f'<path d="M{x:.0f} {Y0:.0f}V{Y1:.0f}"/>')
    for lat in (-8, -11, -14, -17):
        _, y = project(LON_MIN, lat)
        grid.append(f'<path d="M{X0:.0f} {y:.0f}H{X1:.0f}"/>')
    cx, cy = project(CONDE_LON, CONDE_LAT)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" role="img" aria-labelledby="map-title map-desc">
<title id="map-title">Conde, Bahia: localização aproximada da sede municipal</title>
<desc id="map-desc">Mapa de contexto com litoral generalizado do Nordeste brasileiro, grade de latitude e longitude e marcador na sede aproximada de Conde. Não representa local de queda ou evento de 1963.</desc>
<rect width="800" height="500" rx="12" fill="#eaf5f8"/>
<rect x="55" y="55" width="690" height="375" fill="#d2eef5" stroke="#63899a" stroke-width="1.5"/>
<g stroke="#89b9c7" stroke-width="1" stroke-dasharray="4 7">{''.join(grid)}</g>
<g fill="none" stroke="#44615a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="{coast}"/></g>
<g fill="#173b47" font-family="system-ui, sans-serif">
<text x="58" y="35" font-size="19" font-weight="700">Conde no litoral da Bahia</text>
<text x="66" y="76" font-size="14">Interior do Brasil</text>
<text x="620" y="396" font-size="14">Oceano Atlântico</text>
<text x="238" y="298" font-size="20" opacity="0.75">Bahia</text>
<text x="56" y="456" font-size="13">45° O</text>
<text x="707" y="456" font-size="13">33° O</text>
<text x="7" y="61" font-size="13">5° S</text>
<text x="7" y="428" font-size="13">20° S</text>
</g>
<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="#fff" opacity="0.92"/>
<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="#b32236" stroke="#fff" stroke-width="2"/>
<path d="M{cx+10:.1f},{cy-7:.1f} l14,-19" fill="none" stroke="#621b2b" stroke-width="2"/>
<text x="{cx+28:.1f}" y="{cy-31:.1f}" font-family="system-ui, sans-serif" font-size="17" font-weight="700" fill="#621b2b">Conde (sede aprox.)</text>
<text x="56" y="483" font-family="system-ui, sans-serif" font-size="12" fill="#38545e">Costa: Natural Earth 1:110m (domínio público), simplificada. Não é carta local.</text>
</svg>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='verify tracked SVG matches pinned geometry')
    args = parser.parse_args()
    svg = make_svg()
    if len(svg.encode()) > 20_000:
        raise ValueError('SVG exceeds 20KB file policy')
    if args.check:
        if not OUT.exists() or OUT.read_text() != svg:
            sys.exit('FAIL: static SVG not regenerated from pinned Natural Earth sources')
        print('PASS: offline map matches pinned coastline, 20KB gate')
    else:
        OUT.write_text(svg)
        print(f'WROTE {OUT} ({len(svg.encode())} bytes)')


if __name__ == '__main__':
    main()
