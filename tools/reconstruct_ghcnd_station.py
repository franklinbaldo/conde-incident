#!/usr/bin/env python3
"""Reconstitute byte-exact full BR048158910.dly captured 13 Nov 2026.

Original 348,840-byte GHCN-Daily source, not generated or synthetic data.
Content is gzip-base64 split into <=20 kB Git-tracked pieces, without LFS.
"""
import argparse
import base64
import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = [ROOT / 'research/meteorology' / f'BR048158910-dly-captured-20261113.part{i:02d}.b64'
         for i in range(1, 4)]
SHA256 = '327a5c3f0f326a36214d7c2d37e9ecee82f676f8a6bf6e14056d82fe88673d03'
ORIGINAL_BYTES = 348840


def recover(output: Path, parts=PARTS):
    encoded = ''.join(p.read_text(encoding='ascii').strip() for p in parts)
    original = gzip.decompress(base64.b64decode(encoded, validate=True))
    if len(original) != ORIGINAL_BYTES or hashlib.sha256(original).hexdigest() != SHA256:
        raise ValueError('NOAA BR048158910 full 2026-11-13 source SHA-256 mismatch')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(original)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    recover(args.output)
    print('GHCNd BR048158910: byte-exact 2026-11-13 original source PASS')


if __name__ == '__main__':
    main()
