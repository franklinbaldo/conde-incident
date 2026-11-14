#!/usr/bin/env python3
"""Recreate byte-exact 2026-11-13 NOAA inventory from authenticated 2026-10-25 Wayback snapshot."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELTA = ROOT / 'research/meteorology/ghcnd-inventory-wayback-to-pinned.b64'
ARCHIVE_SHA = 'c33ec006c4f35d0371e6f9ccfe3f656ae9de0b6f0f122794da07df7c971c48b5'
PINNED_SHA = '3d7378c3ecad6841340b47392f10b391c42a5f47369765e6bb032704d2301125'
WAYBACK_URL = ('https://web.archive.org/web/20261025021909id_/'
               'https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt')


def sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def recover(archive: Path, output: Path, delta_path: Path = DELTA):
    if sha256(archive) != ARCHIVE_SHA:
        raise ValueError('Wayback source SHA-256 mismatch (whole archive)')
    delta = json.loads(gzip.decompress(base64.b64decode(delta_path.read_bytes())))
    if (delta.get('schema') != 'conde.ghcnd-inventory-delta/v1'
            or delta.get('from_sha256') != ARCHIVE_SHA
            or delta.get('to_sha256') != PINNED_SHA):
        raise ValueError('unexpected inventory patch contract')
    bumps = set(delta['year_2025_to_2026'])
    changes = delta['replace']
    if (len(bumps) != len(delta['year_2025_to_2026'])
            or not all(isinstance(x, int) and x > 0 for x in bumps)
            or not all(isinstance(x, list) and len(x) == 3 for x in changes)):
        raise ValueError('duplicate or malformed edit positions')
    consumed_bumps = set()
    position = 0
    next_allowed = 0

    def copy_line(source, dest):
        nonlocal position
        raw = source.readline()
        if not raw:
            raise ValueError('patch references line after end of archive')
        position += 1
        if position in bumps:
            if not raw.endswith(b'2025\n'):
                raise ValueError('year transition was not 2025')
            raw = raw[:-5] + b'2026\n'
            consumed_bumps.add(position)
        dest.write(raw)

    output.parent.mkdir(parents=True, exist_ok=True)
    with archive.open('rb') as source, output.open('wb') as dest:
        for change in changes:
            start, count, added = change
            if (not isinstance(start, int) or not isinstance(count, int)
                    or count < 0 or start < 0 or start < next_allowed
                    or not isinstance(added, list)
                    or not all(isinstance(row, str) and '\n' not in row and '\r' not in row
                               and row.isascii() for row in added)):
                raise ValueError('overlapping or invalid edit')
            copy_through = start if count == 0 else start - 1
            if copy_through < position:
                raise ValueError('edits not in ascending order')
            while position < copy_through:
                copy_line(source, dest)
            for _ in range(count):
                if not source.readline():
                    raise ValueError('patch deletion beyond end of archive')
                position += 1
                if position in bumps:
                    raise ValueError('bump overlaps deleted line')
            for row in added:
                dest.write(row.encode('ascii') + b'\n')
            next_allowed = position + 1
        for raw in source:
            position += 1
            if position in bumps:
                if not raw.endswith(b'2025\n'):
                    raise ValueError('year transition was not 2025')
                raw = raw[:-5] + b'2026\n'
                consumed_bumps.add(position)
            dest.write(raw)
    if consumed_bumps != bumps or sha256(output) != PINNED_SHA:
        raise ValueError('reconstructed 2026-11-13 source SHA-256 mismatch')
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    recover(args.archive, args.output)
    print('GHCNd inventory: byte-exact 2026-11-13 pinned source PASS')


if __name__ == '__main__':
    main()
