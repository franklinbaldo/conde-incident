#!/usr/bin/env python3
"""C241-L68: October 1963 NASA printed Omega 1 row; no terminal orbit inference."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/tle_custody/nasa_ssr_omega1_oct15_C241-L68.json"
SHA = "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2"
SOURCE = {
    "title": "NASA/Goddard Satellite Situation Report, volume 3 number 20",
    "publication_date": "1963-10-15",
    "report_as_of_utc": "1963-10-15T12:00:00Z",
    "ntrs_id": "19640000428",
    "pdf_url": "https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf",
    "pdf_sha256": SHA,
    "pdf_bytes": 286417,
    "pdf_pages": 9,
    "pdf_page_1based": 5,
    "printed_page": 3,
    "family": "NASA_GSFC_SSR_NORAD_SHARED",
}
ROW = {
    "table_heading": "OBJECTS IN ORBIT",
    "section": "1962 LAUNCHES",
    "printed_name": "OMEGA 1",
    "source_country": "US",
    "launch_day_month": "18 JUN",
    "nodal_period_minutes": "89.7",
    "inclination_degrees": "82.15",
    "apogee_km": 263,
    "perigee_km": 254,
    "catalog_number_printed": None,
}
LIMITS = {
    "row_is_instrumental_observation": False,
    "as_of_is_instrumental_epoch": False,
    "source_independent_of_nasa_1963_1977_catalog_family": False,
    "norad_308_identification_from_this_row": None,
    "physical_survival_at_report_cutoff_proven": False,
    "independent_instrumental_observations_added": 0,
    "terminal_event_utc": None,
    "terminal_sigma_seconds": None,
    "sensor": None,
    "station": None,
    "active_constraint_528": False,
    "historical_mcmc": "NOT_RUN",
    "impact_location": None,
}
EXPECTED = {
    "id": "C241-L68",
    "kind": "NASA_SSR_OCT1963_OMEGA1_PRINTED_CATALOG_ROW",
    "source": SOURCE,
    "row": ROW,
    "related": ["C241-L12", "C241-L64", "C241-L65", "C241-L66", "C241-L67"],
    "limits": LIMITS,
}


def fail_if_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def validate(record):
    if type(record) is not dict or record != EXPECTED:
        raise ValueError("C241-L68 changed printed row, custodian, or no-inference gate")
    for key in EXPECTED:
        if type(record[key]) is not type(EXPECTED[key]):
            raise ValueError("C241-L68 type mismatch: " + key)
    for group in ("source", "row", "limits"):
        for key, value in EXPECTED[group].items():
            if type(record[group][key]) is not type(value):
                raise ValueError("C241-L68 nested type mismatch: " + group + "." + key)
    return True


def validate_pdf(pdf_bytes):
    if len(pdf_bytes) != SOURCE["pdf_bytes"] or not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("PDF wrong size or signature")
    if hashlib.sha256(pdf_bytes).hexdigest() != SHA:
        raise ValueError("PDF failed SHA-256 custody check")
    return True


def adversarial(record, pdf_bytes=None):
    mutations = [
        ("id", lambda r: r.update(id="C241-L69")),
        ("source SHA", lambda r: r["source"].update(pdf_sha256="0" * 64)),
        ("as-of", lambda r: r["source"].update(report_as_of_utc="1963-10-15T00:00:00Z")),
        ("label", lambda r: r["row"].update(printed_name="OMEGA 2")),
        ("period", lambda r: r["row"].update(nodal_period_minutes="89.70")),
        ("apogee", lambda r: r["row"].update(apogee_km=264)),
        ("NORAD", lambda r: r["row"].update(catalog_number_printed=308)),
        ("observation epoch", lambda r: r["limits"].update(as_of_is_instrumental_epoch=True)),
        ("survival", lambda r: r["limits"].update(physical_survival_at_report_cutoff_proven=True)),
        ("UTC", lambda r: r["limits"].update(terminal_event_utc="1963-10-29T09:45:06Z")),
        ("sigma", lambda r: r["limits"].update(terminal_sigma_seconds=1.0)),
        ("active 528", lambda r: r["limits"].update(active_constraint_528=True)),
    ]
    for name, mutate in mutations:
        candidate = copy.deepcopy(record)
        mutate(candidate)
        try:
            validate(candidate)
        except ValueError:
            pass
        else:
            raise RuntimeError("negative control failed: " + name)
    if pdf_bytes is not None:
        corrupted = bytearray(pdf_bytes)
        corrupted[-20] ^= 1
        try:
            validate_pdf(corrupted)
        except ValueError:
            pass
        else:
            raise RuntimeError("negative control failed: corrupted PDF")
    return len(mutations) + (1 if pdf_bytes is not None else 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, help="Full original NASA NTRS PDF")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    record = json.loads(DATA.read_text(encoding="utf-8"), object_pairs_hook=fail_if_duplicate_keys)
    validate(record)
    content = args.pdf.read_bytes() if args.pdf is not None else None
    if content is not None:
        validate_pdf(content)
    count = adversarial(record, content) if args.self_test else 0
    print("C241-L68 PASS | original PDFs verified:", int(content is not None),
          "| negative mutants rejected:", count, "| independent observations: 0")


if __name__ == "__main__":
    main()
