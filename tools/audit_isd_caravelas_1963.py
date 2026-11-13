#!/usr/bin/env python3
"""Audit 1963 NOAA ISD surface rows for Caravelas, without Conde extrapolation."""
from __future__ import annotations
import argparse
import base64
import gzip
import hashlib
import json
import statistics
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/meteorology/isd_caravelas_19631107_09.zlib.b64"
REPORT = ROOT / "research/meteorology/isd_caravelas_19631107_09.json"
GRAPH = ROOT / "research/constraints/isd_caravelas_surface_1963.json"
SOURCE_SHA256 = "c4a0b2f625e8febcd03c4b6ca6ac37b91c9d38423a2ccddd6f0cd7a7712e7e05"
WINDOW_SHA256 = "c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000"
DATES = tuple(f"1963110{d}" for d in (7, 8, 9))
VARIABLES = {"wind_speed_m_s": (65, 69, 69), "temperature_degC": (87, 92, 92),
             "dewpoint_degC": (93, 98, 98), "sea_level_pressure_hPa": (99, 104, 104)}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def window_from_gz(data: bytes) -> bytes:
    if sha(data) != SOURCE_SHA256:
        raise ValueError("full original NOAA gzip archive hash mismatch")
    lines = gzip.decompress(data).splitlines(keepends=True)
    return b"".join(row for row in lines if row[15:23].decode("ascii") in DATES)

def load_snapshot() -> bytes:
    data = zlib.decompress(base64.b64decode(DATA.read_bytes().strip(), validate=True))
    if sha(data) != WINDOW_SHA256:
        raise ValueError("pinned 72-hour excerpt hash mismatch")
    return data

def parse(data: bytes) -> dict:
    if sha(data) != WINDOW_SHA256:
        # The parser can also be called on intentionally modified data for adversarial tests.
        if not data:
            raise ValueError("empty ISD series")
    lines = data.splitlines(keepends=True)
    seen, perday = set(), {d: [] for d in DATES}
    for row in lines:
        if not row.endswith(b"\n") or len(row) < 105:
            raise ValueError("truncated ISD row")
        if row[4:15] != b"83497099999" or row[28:41] != b"-17633-039250":
            raise ValueError("station or retrospective position mismatch")
        ts = row[15:27].decode("ascii")
        if ts in seen or ts[0:8] not in DATES or ts[10:12] != "00" or not 0 <= int(ts[8:10]) < 24:
            raise ValueError("duplicate/missing/wrong station-hour timestamp")
        seen.add(ts)
        if row[63:64] != b"1":
            raise ValueError("wind direction quality flag differs from pinned snapshot")
        measured = {}
        for key, (start, end, quality_index) in VARIABLES.items():
            segment = row[start:end]
            if row[quality_index:quality_index+1] != b"1" or not segment.lstrip(b"+-").isdigit():
                raise ValueError("unknown or degraded ISD quality flag / value: " + key)
            value = int(segment)/10
            if abs(value) > 2000:
                raise ValueError("ISD missing sentinel or out-of-scale value: " + key)
            measured[key] = value
        direction = int(row[60:63])
        if direction not in range(0, 361):
            raise ValueError("invalid wind direction")
        measured["wind_direction_deg_meteorological"] = direction
        perday[ts[:8]].append(measured)
    if len(lines) != 72 or any(len(v) != 24 for v in perday.values()):
        raise ValueError("three complete nominal days not present")
    if seen != {f"{d}{hour:02d}00" for d in DATES for hour in range(24)}:
        raise ValueError("missing or shifted UTC-hour coverage")
    daily = {}
    for date, vals in perday.items():
        daily[f"{date[:4]}-{date[4:6]}-{date[6:8]}"] = {
            "rows": len(vals),
            "surface": {k: {"min": min(v[k] for v in vals), "mean": round(statistics.mean(v[k] for v in vals), 3),
                            "max": max(v[k] for v in vals)} for k in VARIABLES},
        }
    return {"schema": "conde.isd-caravelas-hourly-1963/v1", "observation_interval_utc": ["1963-11-07T00:00:00Z", "1963-11-09T23:00:00Z"],
            "station": {"usaf": "834970", "wban": "99999", "archive_name": "CARAVELAS", "archive_latitude": -17.633,
                        "archive_longitude": -39.250, "position_epoch_in_1963_verified": None},
            "source": {"url": "https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz",
                       "format": "NOAA ISD fixed-width (retrospectively compiled, not 1963 facsimile)",
                       "full_gzip_sha256": SOURCE_SHA256, "excerpt_sha256": WINDOW_SHA256,
                       "full_archive_1963_observation_rows": 8532, "excerpt_rows": 72,
                       "independence": "different surface station from Recife upper-air; upstream institutional lineage not established"},
            "quality": {"is_digital_qc_code_1": True, "qc_1_is_not_calibrated_instrument_error": True,
                        "instrument_identity_1963": None, "measurement_uncertainty": None,
                        "station_specific_transfer_uncertainty_to_conde": None},
            "daily": daily,
            "interpretation": {"classification": "ARCHIVED_SURFACE_OBSERVATIONS_WITH_RETROSPECTIVE_STATION_METADATA",
                               "relation_to_conde": "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION",
                               "numeric_constraint_on_conde": None,
                               "physical_reference": "surface weather at Caravelas, not high-altitude density or winds in Conde"}}

def check(full_gz: Path | None = None) -> dict:
    data = load_snapshot()
    if full_gz is not None and window_from_gz(full_gz.read_bytes()) != data:
        raise ValueError("extracted raw window does not match full NOAA gzip file")
    report = parse(data)
    if json.loads(REPORT.read_text()) != report:
        raise ValueError("ISD published diagnostics differ from pinned rows")
    graph = json.loads(GRAPH.read_text())
    if (graph["source"]["excerpt_sha256"] != WINDOW_SHA256 or
            graph["status"] != "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION" or
            graph["active_conde_constraint"] is not None or
            graph["uncertainty_m_s"] is not None):
        raise ValueError("graph unexpectedly promotes uncalibrated data to a hard constraint")
    return report

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--verify-full-gz", type=Path)
    opts = ap.parse_args()
    if opts.check:
        print(json.dumps({"checked": True, "rows": check(opts.verify_full_gz)["source"]["excerpt_rows"]}))
    else:
        print(json.dumps(parse(load_snapshot()), indent=2, ensure_ascii=False))
