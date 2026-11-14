#!/usr/bin/env python3
"""Source-locked retrospective Baker-Nunn budget, NOT 1963 calibration."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/constraints/sao_baker_nunn_1973_error_budget_G70.json"
PDF_SHA256 = "10f2d85593af7be543326471f8c1eaf234aefc0565515cd4ff059edad20922c8"
PDF_SIZE = 12337725
PDF_URL = "https://ntrs.nasa.gov/api/citations/19740019249/downloads/19740019249.pdf"
RATE_BINS = [
    (32, 0, 250, 1.8, 1.8, 1.8, 1.8),
    (16, 250, 500, 1.8, 1.8, 2.1, 1.8),
    (8, 500, 1000, 1.9, 1.8, 2.3, 1.8),
    (4, 1000, 2000, 1.9, 1.8, 2.7, 1.8),
    (2, 2000, None, 2.0, 1.8, 3.7, 1.8),
]
TABLE_KEYS = ("cycle_s", "rate_min", "rate_max", "vlf_along",
              "vlf_across", "vhf_along", "vhf_across")


def check_ledger(record: dict) -> dict:
    """Fail closed on automatic promotion of a generic budget to a holdout."""
    if not isinstance(record, dict) or set(record) != {
        "schema", "source", "clock", "table_1", "activation"
    } or record["schema"] != "CASTOR_G70_SAO_RETROSPECTIVE_ERROR_BUDGET_V1":
        raise ValueError("Unexpected G70 ledger schema")
    src = record["source"]
    if not isinstance(src, dict) or any((
        src.get("pdf_sha256") != PDF_SHA256,
        src.get("pdf_bytes") != PDF_SIZE,
        src.get("url") != PDF_URL,
        src.get("publication_date") != "1973-11-28",
        src.get("nasa_ntrs_id") != "19740019249",
        src.get("pdf_page_numbers_one_based") != [35, 36],
        src.get("printed_page_numbers") != [25, 26],
        src.get("evidence_class") != "1973_RETROSPECTIVE_NOT_1963_INSTRUMENT_RECORD",
    )):
        raise ValueError("Source identity or retrospective status changed")
    clock = record["clock"]
    if not isinstance(clock, dict) or any((
        clock.get("historical_scope") != "SAO_BAKER_NUNN_STATIONS_BEFORE_1965",
        type(clock.get("observation_epoch_rms_s_approx")) is not float,
        clock.get("observation_epoch_rms_s_approx") != 0.001,
        "Norrman" not in clock.get("clock_and_sync", ""),
        "EECo" not in clock.get("replacement_note", ""),
        "Retrospective" not in clock.get("interpretation", "")
    )):
        raise ValueError("Retrospective clock scope or units changed")
    table = record["table_1"]
    if not isinstance(table, dict) or any((
        table.get("printed_page") != 26,
        table.get("units_rate") != "arcsec/s",
        table.get("units_error") != "arcsec",
        table.get("scope") != "RETROSPECTIVE_GENERALIZED_BAKER_NUNN_BUDGET_NOT_SENSOR_EVENT"
    )):
        raise ValueError("Invalid table source or units")
    rows = table.get("rows")
    if not isinstance(rows, list) or len(rows) != len(RATE_BINS):
        raise ValueError("Five published rate bins required")
    for row, expected in zip(rows, RATE_BINS):
        if not isinstance(row, dict) or set(row) != set(TABLE_KEYS):
            raise ValueError("Wrong table fields")
        for field, original in zip(TABLE_KEYS, expected):
            if type(row[field]) is not type(original) or row[field] != original:
                raise ValueError("Retrospective table altered or units confused")
    gate = record["activation"]
    null_fields = (
        "station_crosswalk_1963", "norad_527_528_529_exposure_ids",
        "instrumental_utc_epochs", "observational_covariance_for_g64",
        "historical_likelihood", "impact_location_or_probability"
    )
    if not isinstance(gate, dict) or set(gate) != {
        "state", *null_fields, "independent_1963_holdout",
        "historical_orbital_domain_reduction"
    } or gate["state"] != "CANDIDATE_NOT_ACTIVATED" or (
        gate["independent_1963_holdout"] != "NOT_RUN" or
        gate["historical_orbital_domain_reduction"] is not False
    ) or any(gate[k] is not None for k in null_fields):
        raise ValueError("Historical parameters cannot be activated by this source")
    return record


def check_pdf(path: Path) -> None:
    """Authenticate exact PDF bytes; an archive URL is not proof of content."""
    raw = path.read_bytes()
    if (len(raw) != PDF_SIZE or not raw.startswith(b"%PDF-") or
            hashlib.sha256(raw).hexdigest() != PDF_SHA256):
        raise ValueError("SAO source bytes mismatch")


def conditional_clock_displacement_arcsec(rate_arcsec_s: float,
                                           clock_rms_s: float) -> dict:
    """Dimensional sensitivity only: omega [arcsec/s] * dt [s]."""
    for v in (rate_arcsec_s, clock_rms_s):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or (
                not math.isfinite(v) or v < 0):
            raise ValueError("Expected finite nonnegative rate and seconds")
    displacement = float(rate_arcsec_s) * float(clock_rms_s)
    if not math.isfinite(displacement):
        raise ValueError("Angular displacement overflow")
    return {
        "conditional_clock_component_arcsec": displacement,
        "historical_528_sigma_arcsec": None,
        "covariance_activation": "NOT_AUTHORIZED_BY_RETROSPECTIVE_BUDGET"
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--source-pdf", type=Path)
    args = parser.parse_args()
    data = check_ledger(json.loads(args.ledger.read_text(encoding="utf-8")))
    if args.source_pdf:
        check_pdf(args.source_pdf)
    print(json.dumps({
        "source_ntrs": data["source"]["nasa_ntrs_id"],
        "pdf_verified": args.source_pdf is not None,
        "clock_rms_s_approx": .001,
        "rate_bin_count": len(data["table_1"]["rows"]),
        "conditional_250_arcsec_s": conditional_clock_displacement_arcsec(250, .001),
        "historical_holdout": "NOT_RUN",
        "state": "CANDIDATE_NOT_ACTIVATED"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
