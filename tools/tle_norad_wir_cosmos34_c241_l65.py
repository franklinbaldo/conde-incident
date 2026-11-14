#!/usr/bin/env python3
"""C241-L65. NORAD 1964 Z-labelled apparent de-orbit is not a 1963 decay clock."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "research/tle_custody/norad_wir_cosmos34_1964_C241-L65.json"
PDF_SHA256 = "2063f4f8d9082c55990dd4be91b8eb096333143230b6f726639fc58bef7251c5"
PDF_BYTES = 30133149
PDF_URL = "https://www.archives.gov/files/declassification/iscap/pdf/2009-068-doc35.pdf"


def no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate key: " + key)
        obj[key] = value
    return obj


def load(path=RECORD_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=no_duplicates)


EXPECTED = {
  "id": "C241-L65",
  "kind": "NORAD_1964_INTELLIGENCE_DEORBIT_WINDOW_CONTEXT_ONLY",
  "source": {
    "publisher": "North American Air Defense Command (NORAD)",
    "publication": "Weekly Intelligence Review 29/64",
    "published_on": "1964-07-17",
    "url": "https://www.archives.gov/files/declassification/iscap/pdf/2009-068-doc35.pdf",
    "source_class": "ORIGINAL_NORAD_REPORT_RELEASED_BY_NARA_ISCAP",
    "declassification_record": "ISCAP 2009-068 document 35",
    "pdf_bytes": 30133149,
    "pdf_sha256": "2063f4f8d9082c55990dd4be91b8eb096333143230b6f726639fc58bef7251c5",
    "pdf_pages": 10,
    "pdf_page_one_indexed": 4,
    "printed_page": 6,
    "visually_checked_on": "2026-11-14"
  },
  "report": {
    "object_name_as_printed": "Cosmos 34",
    "launch_printed": "about 1100Z, 1 July",
    "event_printed": "apparently de-orbited sometime between 0931-0936Z, 9 July",
    "event_date": "1964-07-09",
    "start_as_printed": "0931Z",
    "end_as_printed": "0936Z",
    "printed_interval_minutes": 5,
    "qualifier": "apparently",
    "described_revolution": 127,
    "sensor": None,
    "instrument_observation_id": None,
    "observation_epoch": None,
    "estimation_method": None,
    "time_uncertainty_sigma_seconds": None
  },
  "interpretation": {
    "evidence_type": "NORAD_INTELLIGENCE_ASSESSMENT_NOT_SENSOR_LOG",
    "event_type": "APPARENT_DEORBIT_NOT_NATURAL_DECAY_CALIBRATION",
    "same_event_as_1963_norad_308": False,
    "same_event_as_1963_norad_528": False,
    "permits_five_minute_sigma_for_528": False,
    "permits_utc_terminal_point_for_528": False,
    "original_independent_measurements_528": 0,
    "activated_orbital_constraints_528": 0,
    "conditional_value": "Show that one 1964 NORAD narrative printed a Z-labelled de-orbit estimate; no proof of typical 1963 date accuracy or automatic decay clock",
    "related_primary": "C241-L24 NORAD/GSFC 1962 release memorandum; C241-L64 NASA SSR 1963 date-only catalogue",
    "note": "1964 source is neither a 1963 object observation nor a new terminal calibration sample"
  }
}


def require_exact(got, wanted, position="root"):
    if type(got) is not type(wanted):
        raise ValueError(position + ": changed field type")
    if isinstance(wanted, dict):
        if set(got) != set(wanted):
            raise ValueError(position + ": unexpected or missing key")
        for key, value in wanted.items():
            require_exact(got[key], value, position + "." + key)
    elif isinstance(wanted, list):
        if len(got) != len(wanted):
            raise ValueError(position + ": changed length")
        for i, value in enumerate(wanted):
            require_exact(got[i], value, position + "[" + str(i) + "]")
    elif got != wanted:
        raise ValueError(position + ": changed historical source or epistemic limit")


def verify_record(record):
    require_exact(record, EXPECTED)
    if record["report"]["sensor"] is not None or record["report"]["time_uncertainty_sigma_seconds"] is not None:
        raise ValueError("uncalibrated source cannot acquire a fictitious sensor or sigma")
    if record["interpretation"]["activated_orbital_constraints_528"] != 0:
        raise ValueError("1964 estimate cannot constrain a 1963 orbit")
    return {"id": "C241-L65", "event": "1964-07-09", "inference": "CONTEXT_ONLY", "observations_528": 0}


def verify_pdf(path):
    source = Path(path)
    size = 0
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        if stream.read(5) != b"%PDF-":
            raise ValueError("not a PDF")
        stream.seek(0)
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    if size != PDF_BYTES or digest.hexdigest() != PDF_SHA256:
        raise ValueError("PDF bytes/sha256 mismatch")
    return {"pdf_sha256": PDF_SHA256, "pdf_bytes": size}


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--record", type=Path, default=RECORD_PATH)
    argp.add_argument("--pdf", type=Path)
    args = argp.parse_args()
    outcome = verify_record(load(args.record))
    if args.pdf:
        outcome.update(verify_pdf(args.pdf))
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
