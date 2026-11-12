#!/usr/bin/env python3
"""Audit each IIIF JPEG tile of UWM agdm/10814 without claiming original JP2 fixity.

Capture uses a bounded public read (no contact with staff, no upload), then
writes a compact JSON snapshot. CI validation is offline and adversarial.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import urllib.request

CATALOG = "https://collections.lib.uwm.edu/digital/collection/agdm/id/10814/"
IMAGE_INFO = "https://collections.lib.uwm.edu/digital/iiif/agdm/10814/info.json"
PRESENTATION = "https://collections.lib.uwm.edu/iiif/info/agdm/10814/manifest.json"
BASE = "https://collections.lib.uwm.edu/digital/iiif/agdm/10814/"
USER_AGENT = "Conde-Lontra-IIIF-archival-integrity/1.0"
WIDTH = 9603
HEIGHT = 7783
TILE = 1024


def grid(width=WIDTH, height=HEIGHT, tile=TILE):
    """Row-major non-overlapping coverage of a native pixel canvas."""
    if not all(isinstance(v, int) and v > 0 for v in (width, height, tile)):
        raise ValueError("positive integer width/height/tile required")
    return [
        (x, y, min(tile, width - x), min(tile, height - y))
        for y in range(0, height, tile)
        for x in range(0, width, tile)
    ]


def url_for(tile):
    x, y, w, h = tile
    return f"{BASE}{x},{y},{w},{h}/{w},/0/default.jpg"


def jpeg_dimensions(data):
    """Parse SOF metadata, not decoded pixels; bounds errors fail closed."""
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("not a JPEG SOI")
    at = 2
    while at < len(data):
        if data[at] != 255:
            raise ValueError("invalid JPEG marker boundary")
        while at < len(data) and data[at] == 255:
            at += 1
        if at >= len(data):
            break
        kind = data[at]
        at += 1
        if kind in (0xD8, 0xD9, 0x01) or 0xD0 <= kind <= 0xD7:
            continue
        if at + 2 > len(data):
            break
        size = int.from_bytes(data[at:at+2], "big")
        if size < 2 or at + size > len(data):
            raise ValueError("invalid JPEG segment length")
        if kind in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if size < 7:
                raise ValueError("short JPEG SOF segment")
            return (int.from_bytes(data[at+5:at+7], "big"),
                    int.from_bytes(data[at+3:at+5], "big"))
        at += size
    raise ValueError("no JPEG frame header found")


def get(url: str, timeout: float = 25.0):
    if not (url.startswith(BASE) or url in (IMAGE_INFO, PRESENTATION)):
        raise ValueError("non-custodial URL refused")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        if res.status != 200:
            raise ValueError(f"unexpected HTTP {res.status}: {url}")
        data = res.read(4_000_001)
        if len(data) > 4_000_000:
            raise ValueError("individual response over 4 MB; not a bounded tile")
        return data, res.headers.get("Content-Type", "").split(";")[0].lower()


def get_tile(index, tile):
    data, mime = get(url_for(tile))
    if mime != "image/jpeg":
        raise ValueError(f"tile {index}: wrong Content-Type {mime}")
    if jpeg_dimensions(data) != tile[2:]:
        raise ValueError(f"tile {index}: wrong JPEG pixel dimensions")
    return index, hashlib.sha256(data).hexdigest(), len(data)


def capture(max_workers=2):
    if not 1 <= max_workers <= 3:
        raise ValueError("limit to 1–3 parallel public requests")
    info_raw, info_type = get(IMAGE_INFO)
    pres_raw, pres_type = get(PRESENTATION)
    if info_type != "application/json" or pres_type != "application/json":
        raise ValueError("IIIF JSON Content-Type mismatch")
    info = json.loads(info_raw)
    pres = json.loads(pres_raw)
    if (info.get("width"), info.get("height")) != (WIDTH, HEIGHT):
        raise ValueError("IIIF image canvas has changed")
    if info.get("tiles") != [{"scaleFactors": [1, 2, 4, 8, 16], "width": TILE}]:
        raise ValueError("unexpected IIIF image tile configuration")
    canvases = pres["sequences"][0]["canvases"]
    if len(canvases) != 1 or (canvases[0]["width"], canvases[0]["height"]) != (WIDTH, HEIGHT):
        raise ValueError("presentation canvas differs from image info")
    declared = canvases[0]["images"][0]["resource"]["service"]["tiles"][0]["width"]
    cells = grid()
    outputs = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        jobs = [pool.submit(get_tile, i, tile) for i, tile in enumerate(cells)]
        for f in as_completed(jobs):
            i, sha, size = f.result()
            outputs[i] = [sha, size]
    if set(outputs) != set(range(len(cells))):
        raise ValueError("incomplete tile coverage")
    obj = {
        "schema": "conde.uwm-iiif-tile-custody/v1",
        "source": CATALOG,
        "contentdm_collection": "agdm",
        "contentdm_item_id": "10814",
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "iiif_image_info": IMAGE_INFO,
        "iiif_presentation_manifest": PRESENTATION,
        "iiif_image_info_sha256": hashlib.sha256(info_raw).hexdigest(),
        "iiif_manifest_sha256": hashlib.sha256(pres_raw).hexdigest(),
        "image_info_tiles_width": TILE,
        "presentation_service_tiles_width": declared,
        "width_px": WIDTH,
        "height_px": HEIGHT,
        "grid_order": "row-major, x-fastest; origin top-left",
        "row_count": (HEIGHT + TILE - 1) // TILE,
        "column_count": (WIDTH + TILE - 1) // TILE,
        "tile_api_pattern": BASE + "{x},{y},{width},{height}/{width},/0/default.jpg",
        "tile_hashes_and_lengths_row_major": [outputs[i] for i in range(len(cells))],
        "retrieval_scope": "Entire IIIF rendered JPEG canvas by tile; no original JP2 downloaded",
        "original_jp2_sha256": None,
        "original_jp2_full_fixity": False,
        "legal_boundary_1963": None,
        "orbital_constraint": "NOT_ACTIVATED",
        "limitations": [
            "Each SHA-256 covers an HTTP JPEG derivative response, not the JP2 master.",
            "JPEG frame dimensions checked; no pixel decode or visual inspection of every tile.",
            "Different IIIF service tile widths are recorded, not silently conflated.",
            "A complete set of JPEG tile responses does not authenticate printed dates, legal municipal boundaries, or OCR.",
            "Live CDN data could change; checksums are a capture snapshot, not a permanent assertion.",
        ],
    }
    validate(obj)
    return obj


def validate(obj):
    if obj.get("schema") != "conde.uwm-iiif-tile-custody/v1":
        raise ValueError("wrong schema")
    if obj.get("contentdm_item_id") != "10814":
        raise ValueError("wrong object")
    if obj.get("width_px") != WIDTH or obj.get("height_px") != HEIGHT:
        raise ValueError("canvas dimensions changed")
    if obj.get("image_info_tiles_width") != TILE:
        raise ValueError("tile width changed")
    if obj.get("presentation_service_tiles_width") != WIDTH:
        raise ValueError("manifest tile-width discrepancy not retained")
    cells = grid()
    hashes = obj.get("tile_hashes_and_lengths_row_major")
    if not isinstance(hashes, list) or len(hashes) != len(cells):
        raise ValueError("incomplete row-major tile list")
    if obj.get("row_count") != 8 or obj.get("column_count") != 10:
        raise ValueError("grid dimensions changed")
    if len(set(x[0] for x in hashes)) != len(hashes):
        raise ValueError("duplicate tile content hash: possible reused/incorrect region")
    for sha, size in hashes:
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
            raise ValueError("invalid tile digest")
        if not isinstance(size, int) or not 100 < size <= 4_000_000:
            raise ValueError("missing/truncated tile response")
    for label in ("iiif_image_info_sha256", "iiif_manifest_sha256"):
        if not re.fullmatch(r"[0-9a-f]{64}", obj.get(label, "")):
            raise ValueError("invalid JSON snapshot checksum")
    if obj.get("original_jp2_sha256") is not None or obj.get("original_jp2_full_fixity") is not False:
        raise ValueError("derivative coverage misrepresented as JP2 integrity")
    if obj.get("legal_boundary_1963") is not None or obj.get("orbital_constraint") != "NOT_ACTIVATED":
        raise ValueError("unjustified legal/orbital claim")
    return len(cells)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, help="Read every bounded IIIF JPEG tile and write JSON")
    parser.add_argument("--verify", type=Path, help="Offline structural validation of captured snapshot")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if bool(args.capture) == bool(args.verify):
        parser.error("choose exactly one of --capture or --verify")
    if args.capture:
        snapshot = capture(args.workers)
        args.capture.parent.mkdir(parents=True, exist_ok=True)
        args.capture.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("CAPTURED", validate(snapshot), "verified JPEG tiles")
    else:
        obj = json.loads(args.verify.read_text(encoding="utf-8"))
        print("STRUCTURAL_COVERAGE_VALID", validate(obj), "tiles; JP2 master remains unverified")
