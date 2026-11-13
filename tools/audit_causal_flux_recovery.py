#!/usr/bin/env python3
"""C241-P33: recover actual archived F10.7 days, not historical release vintages."""
import argparse
import csv
import datetime as dt
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from audit_causal_flux_backfill import ROOT, SOURCE, audit_bytes_causal, causal_window

EXTRACT = ROOT / "research/meteorology/f107_1963_08_18_09_26_nrc_extract.txt"
CERT = ROOT / "research/constraints/C241-P33_real_solar_flux_backfill.json"
FULL_SHA = "60c51e8878dc70561e615b5cefb26315c201116fe4560799ec19237bed691c61"
EXTRACT_SHA = "26ee76e557dbe1ecf4eca35fa23e5f230b052c24bad15e21ffad3f408ca13351"
WINDOW_START = dt.date(1963, 8, 18)
WINDOW_END = dt.date(1963, 9, 26)
DAYS = (WINDOW_END - WINDOW_START).days + 1


def extract_data(raw: bytes, expected_sha: str = EXTRACT_SHA):
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise ValueError("SOURCE_BYTES_HASH_MISMATCH")
    try:
        content = raw.decode("ascii")
    except UnicodeError as exc:
        raise ValueError("NON_ASCII_EXTRACT") from exc
    data = {}
    rows = csv.reader(content.splitlines(), skipinitialspace=True)
    for fields in rows:
        if len(fields) != 8:
            raise ValueError("INVALID_NRC_COLUMNS")
        try:
            year, month, day = (int(fields[i]) for i in (2, 3, 4))
            date = dt.date(year, month, day)
            # NRC columns: JD, rotation, year, month, day, observed, adjusted, URSI-D
            values = tuple(Decimal(fields[i].strip()) for i in (5, 6, 7))
        except (ValueError, ArithmeticError) as exc:
            raise ValueError("INVALID_NRC_VALUE") from exc
        if date in data:
            raise ValueError("DUPLICATE_DATE")
        if not all(v.is_finite() and v > 0 for v in values):
            raise ValueError("NONPOSITIVE_OR_NONFINITE_FLUX")
        data[date] = values
    expected = {WINDOW_START + dt.timedelta(days=i) for i in range(DAYS)}
    if set(data) != expected:
        raise ValueError("MISSING_OR_EXTRA_DATE")
    return data


def verify_full_archive(full: bytes, extract: bytes):
    if hashlib.sha256(full).hexdigest() != FULL_SHA:
        raise ValueError("FULL_SOURCE_BYTES_HASH_MISMATCH")
    archive_lines = {line.rstrip(b"\r\n") for line in full.splitlines()}
    raw_lines = {line.rstrip(b"\r\n") for line in extract.splitlines()}
    if not raw_lines <= archive_lines:
        raise ValueError("EXTRACT_NOT_IN_ARCHIVE")
    return True


def audit(extract: bytes, parent_source: bytes):
    backfill = extract_data(extract)
    p32 = audit_bytes_causal(parent_source)
    parent = json.loads(parent_source)
    source = parent["source_documents"]["F107"]
    if source["sha256"] != FULL_SHA or source["bytes"] != 1184761:
        raise ValueError("DIFFERENT_SOURCE_LINEAGE")
    dated = {
        dt.date.fromisoformat(k): Decimal(str(v["observed_sfu"]))
        for k, v in parent["raw_series"]["F107_observed_daily"].items()
    }
    if set(dated) & set(backfill):
        raise ValueError("BACKFILL_OVERLAPS_ORIGINAL")
    observed = {**dated, **{k: v[0] for k, v in backfill.items()}}
    rows = []
    for previous in p32["rows"]:
        epoch = dt.datetime.fromisoformat(
            previous["model_evaluation_utc_not_event_time"].replace("Z", "+00:00")
        )
        dates = causal_window(epoch)
        if any(day not in observed for day in dates):
            raise ValueError("INCOMPLETE_81_DAY_WINDOW")
        total = sum((observed[d] for d in dates), Decimal(0))
        rows.append({
            "model_evaluation_utc_not_event_time": previous["model_evaluation_utc_not_event_time"],
            "trailing_81_observed_sfu": str(total / Decimal(81)),
            "window_days": len(dates),
            "backfilled_dates_used": sum(d in backfill for d in dates),
            "missing_after_backfill": 0,
            "historical_release_timestamp_audited": False,
            "prospective_eligible": False,
            "standard_centered_f107a_replaced": False,
            "historical_orbit_inference": "NOT_RUN",
        })
    return {
        "schema": "conde.c241-p33-real-f107-backfill/v1",
        "source_archive_url": source["url"],
        "source_archive_sha256": FULL_SHA,
        "source_archive_bytes": source["bytes"],
        "extract_path": str(EXTRACT.relative_to(ROOT)),
        "extract_sha256": hashlib.sha256(extract).hexdigest(),
        "parent_extract_sha256": hashlib.sha256(parent_source).hexdigest(),
        "observed_column": "Obs.",
        "units": "solar_flux_unit",
        "backfilled_records": len(backfill),
        "same_documentary_lineage_as_parent": True,
        "finding": "81 historical daily values are computable retrospectively, but no release-time proof or calibrated prospective model follows.",
        "release_vintage": "UNKNOWN",
        "causal_forecast_score": "NOT_RUN",
        "physical_constraint": "CONNECTED_PENDING_CALIBRATION",
        "rows": rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    p.add_argument("--full-archive", type=Path, help="Optional external 1947–1996 archive, SHA-pinned; verifies raw lines")
    args = p.parse_args()
    extracted = EXTRACT.read_bytes()
    if args.full_archive:
        verify_full_archive(args.full_archive.read_bytes(), extracted)
    payload = json.dumps(audit(extracted, SOURCE.read_bytes()), indent=2, ensure_ascii=False) + "\n"
    if args.write:
        CERT.write_text(payload)
        print("WROTE C241-P33", CERT)
    elif args.check:
        if CERT.read_text() != payload:
            raise SystemExit("STALE_C241_P33_CERTIFICATE")
        print("PASS C241-P33 real 40-day F10.7 backfill; as-of eligibility remains NOT_RUN")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
