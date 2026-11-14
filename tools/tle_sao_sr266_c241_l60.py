#!/usr/bin/env python3
"""Custody and dependency audit for SAO Special Report 266, not 528 data."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/sao_sr266_synthetic_1963_C241-L60.json"
SOURCE_SHA = "287158c6a3044a1d088cb5addf4635af6921222abf21a917b08bbe81c967f9b6"
SOURCE_BYTES = 10985789
TARGETS = ("60 09 2", "60 13 1", "61 04 1", "61 28 1", "62 20 1", "62 60 1",
           "62 68 1", "63 30 1", "63 30 4", "63 53 1", "64 38 1", "65 34 3")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf8"))


def validate(m: dict) -> dict:
    s, p, t = m["source"], m["published_dataset"], m["target_527_528_529"]
    require(m["id"] == "C241-L60", "ledger ID mismatch")
    require(m["kind"] == "HISTORICAL_SAO_SYNTHETIC_OBSERVATION_DEPENDENCY", "ledger kind")
    require(s["ntrs_id"] == "19690000806" and s["publication_date"] == "1968-01-26", "source metadata")
    require(s["sha256"] == SOURCE_SHA and s["bytes"] == SOURCE_BYTES and s["pdf_pages"] == 71, "source digest")
    require(s["url"] == "https://ntrs.nasa.gov/api/citations/19690000806/downloads/19690000806.pdf", "source URL")
    require(s["pages_pdf_zero_based"] == {"method": 8, "interpolation": 9, "quality": 13, "table1": 15}, "page provenance")
    require(p["observation_period"] == ["1961-06", "1965-10"], "time scope")
    require(p["table1_target_count"] == 12 and tuple(p["table1_designations"]) == TARGETS, "table 1 identities")
    require(p["includes_1963_003"] is False, "inferred 528 in table")
    require(p["scope"] == "ONLY_TABLE1_TARGETS_NOT_ALL_SAO_OR_NORAD_TRACKING", "negative inference")
    require(p["method"] == "DERIVED_LEAST_SQUARES_POLYNOMIAL_AND_INTERPOLATION_FROM_OVERLAPPING_BAKER_NUNN_SEQUENCES", "derived method")
    require((p["stations_per_synthetic_pair_min"], p["raw_frames_per_station_min"],
             p["raw_frames_per_station_max"]) == (2, 4, 10), "sensor/sample method")
    require(p["time_scale"] == "A.S._ATOMIC_TIME_NOT_UTC", "invented UTC")
    require(p["direction_frame"] == "HISTORIC_FIXED_EARTH_REFERENCE_NOT_TEME", "invented TEME")
    require(p["timing_uncertainty_msec_context"] == [0.3, 5.0], "instrument time uncertainty")
    require(p["synthetic_rejection_threshold_arcsec"] == 2.0, "synthetic selection threshold")
    require(p["independence_policy"] == "DERIVED_ROWS_SHARE_INPUT_SENSOR_OBSERVATIONS; DO_NOT_COUNT_AS_NEW_RAW_MEASUREMENTS",
            "duplicated sensor")
    for key in ("raw_observations", "object_station_link", "instrumental_epoch_utc",
                "orbital_covariance", "reentry_location"):
        require(t[key] is None, "invented target data: " + key)
    for key in ("independent_raw_measurements_added", "physical_constraints_activated"):
        require(type(t[key]) is int and t[key] == 0, "invented target constraint: " + key)
    return {"id": "C241-L60", "status": "CONTEXT_ONLY_NOT_528", "table1_targets": 12,
            "independent_528_measurements_added": 0, "physical_constraints": 0}


def inspect_pdf(raw: bytes) -> dict:
    require(len(raw) == SOURCE_BYTES and hashlib.sha256(raw).hexdigest() == SOURCE_SHA,
            "source bytes drifted: investigate original, never repin silently")
    from pypdf import PdfReader
    pdf = PdfReader(io.BytesIO(raw))
    require(len(pdf.pages) == 71, "PDF pagination drifted")
    method = pdf.pages[8].extract_text() or ""
    overlap = pdf.pages[9].extract_text() or ""
    quality = pdf.pages[13].extract_text() or ""
    table1 = pdf.pages[15].extract_text() or ""
    require("synthetic simultaneous" in method.lower() and "least-squar" in method.lower(),
            "method page drifted")
    require("minimum of 4" in overlap and "maximum of 10" in overlap, "overlap frames drifted")
    require("2 arcsec" in quality and "A. S" in quality, "error/time page drifted")
    require(len(table1) > 500, "rotated table 1 page missing")
    return {"pdf_bytes": len(raw), "pages": len(pdf.pages), "sha256": SOURCE_SHA,
            "pages_inspected": [8, 9, 13, 15],
            "table1_reading": "VISUALLY_VERIFIED_ORIGINAL_ROTATED_SCAN"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path)
    args = p.parse_args()
    result = validate(load())
    if args.pdf:
        result["replay"] = inspect_pdf(args.pdf.read_bytes())
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
