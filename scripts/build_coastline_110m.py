#!/usr/bin/env python3
"""Build static, tile-free Natural Earth coastline chunks from a pinned GeoJSON.

Usage: download the pinned source URL noted below and run:
 python3 scripts/build_coastline_110m.py /path/to/ne_110m_coastline.geojson
Never use this generator in the production browser or CI network path.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

SOURCE_REV = 'ca96624a56bd078437bca8184e78163e5039ad19'
SOURCE_URL = (f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/'
              f'{SOURCE_REV}/geojson/ne_110m_coastline.geojson')
SOURCE_SHA256 = '851f581ff5ffb844deed8ae1a9ce22e3c4bb3d74fa342cadb5d8e39b41ae7c3c'
EPSILON_DEGREES = 0.3
MAX_BYTES = 14_500
DEST = Path('src/lib')


def segment_at_antimeridian(points):
    segments = [[points[0]]]
    for point in points[1:]:
        if abs(point[0] - segments[-1][-1][0]) > 180:
            if len(segments[-1]) < 2:
                segments.pop()
            segments.append([point])
        else:
            segments[-1].append(point)
    return [part for part in segments if len(part) >= 2]


def perpendicular_distance(point, start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    if dx == dy == 0:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    t = max(0, min(1, ((point[0] - start[0]) * dx +
                       (point[1] - start[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(point[0] - (start[0] + t * dx),
                      point[1] - (start[1] + t * dy))


def simplify(points):
    if len(points) <= 2:
        return points
    distances = [perpendicular_distance(point, points[0], points[-1])
                 for point in points[1:-1]]
    greatest = max(distances)
    if greatest <= EPSILON_DEGREES:
        return [points[0], points[-1]]
    split = distances.index(greatest) + 1
    return simplify(points[:split + 1])[:-1] + simplify(points[split:])


def render(part, index):
    name = f'coastline110mPart{index}'
    note = ('// Natural Earth 1:110m coastline, public domain; offline derivative.\n'
            f'// Source: {SOURCE_URL}\n'
            f'// SHA-256 raw GeoJSON: {SOURCE_SHA256}; RDP <= {EPSILON_DEGREES} deg.\n')
    return note + f'export const {name} = ' + json.dumps(part, separators=(',', ':')) + ';\n'


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Usage: build_coastline_110m.py ne_110m_coastline.geojson')
    raw = Path(sys.argv[1]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise SystemExit('Source mismatch: expected pinned SHA-256, refusing rebuild')
    features = json.loads(raw)['features']
    if len(features) != 134 or any(f['geometry']['type'] != 'LineString' for f in features):
        raise SystemExit('Unexpected coastline source structure')
    outlines = []
    for feature in features:
        for segment in segment_at_antimeridian(feature['geometry']['coordinates']):
            outline = [[round(coord, 2) for coord in point] for point in simplify(segment)]
            if len(outline) >= 2:
                outlines.append(outline)

    chunks, current = [], []
    for outline in outlines:
        if current and len(render(current + [outline], len(chunks) + 1).encode()) > MAX_BYTES:
            chunks.append(current)
            current = []
        current.append(outline)
    if current:
        chunks.append(current)
    if not (2 <= len(chunks) <= 8):
        raise SystemExit(f'Unexpected chunk count: {len(chunks)}')
    for index, chunk in enumerate(chunks, 1):
        target = DEST / f'coastline110mPart{index}.js'
        content = render(chunk, index)
        if len(content.encode()) > MAX_BYTES:
            raise SystemExit(f'Oversized chunk: {target}')
        target.write_text(content)
        print(f'{target}: {len(chunk)} lines, {len(content.encode())} bytes')
    print(f'{len(outlines)} segments; {sum(map(len, outlines))} vertices; {len(chunks)} chunks')


if __name__ == '__main__':
    main()
