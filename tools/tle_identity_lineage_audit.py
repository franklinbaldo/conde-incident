#!/usr/bin/env python3
"""C241-T8: source-traceable NORAD/COSPAR identity join, NOT a debris identification.

Compares a pinned numeric Parquet-derived CSV, the single literal TLE
secondary mirror, and attributed catalog label transcriptions. A common
launch designator is NOT physical fragment identity, material or size.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from tle_literal_layout import audit_literal_file

CSV_SHA256 = "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231"
PARQUET_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
EXPECTED = {527: "1963-003A", 528: "1963-003B", 529: "1963-003C"}
COUNTS = {527: 21, 528: 45, 529: 57}
UNIQUE_EPOCHS = {527: 20, 528: 45, 529: 54}
SECONDARY_NAMES = {527: "FTV 2313", 528: "FTV 2313 DEB", 529: "FTV 2313 DEB"}
SOURCE_URL = "https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/4b4fb3a/data/tle_1963.parquet"


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_designator(raw):
    """Read notation ONLY, preserving the original string separately.

    Accepts 2-digit TLE-like year 63 or a 4-digit catalog year 1963.
    Rejects 1963-030B, 1963-003AB, unrelated launches and empty pieces.
    """
    if not isinstance(raw, str):
        raise ValueError("international designator must be textual")
    match = re.fullmatch(r"\s*(?:63|1963)[ -]?003[ -]*([A-Z])\s*", raw)
    if match is None:
        raise ValueError("unrecognized 1963-003 COSPAR designator: " + repr(raw))
    return "1963-003" + match.group(1)


def check_catalog_ledger(ledger):
    if ledger.get("schema_version") != 1 or ledger.get("classification") != \
            "TRANSCRIBED_CATALOG_LABELS_NOT_INSTRUMENTAL_RECORDS":
        raise ValueError("identity catalog transcription classification changed")
    sources = ledger.get("sources")
    if not isinstance(sources, dict) or set(sources) != {
            "itau_527", "itau_528", "itau_529", "keeptrack_528", "keeptrack_529"}:
        raise ValueError("catalog source inventory missing or expanded without review")
    for key, row in sources.items():
        ident = int(key.split("_")[1])
        if (row["catalog"] != ident or
                row["international_designator"] != EXPECTED[ident] or
                row["display_name"] != SECONDARY_NAMES[ident] or
                row["launch_day"] != "1963-01-16" or
                not row["url"].startswith("https://") or
                row["kind"] not in ("MODERN_SECONDARY_CATALOG",
                                    "MODERN_SECONDARY_AGGREGATOR")):
            raise ValueError("source transcription mismatch: " + key)
        if ident in (528, 529) and "debris" not in row["catalog_class"]:
            raise ValueError("source lost the secondary debris label: " + key)
    nasa = ledger.get("primary_date_only_record", {})
    if (nasa.get("document_id") != "NASA NTRS 19640001198" or
            nasa.get("catalog_designator_printed") != "1963 3B" or
            nasa.get("decay_day") != "1963-11-08" or
            nasa.get("extraction_status") !=
            "VISUALLY_REINSPECTED_PDF_PAGE_9_PRINTED_8_2026-11-12"):
        raise ValueError("NASA document must remain a date-only attributed claim")
    p = ledger.get("provenance", {})
    if any(p.get(name) is not False for name in (
            "independent_radar_observations_demonstrated",
            "original_1963_line1_line2_for_all_epochs",
            "original_fragment_engineering_record")):
        raise ValueError("cannot promote secondary labels to primary physical identity")
    return True


def audit_identity(raw_rows, ledger, literal_report, *, csv_sha):
    check_catalog_ledger(ledger)
    if literal_report["catalog"] != 528 or literal_report["epoch_raw"] != "63300.61129783":
        raise ValueError("secondary literal 528 catalog or epoch changed")
    # Check line-1 launch/piece transcription, not just catalog number/RAAN.
    first_line = literal_report["line1_intl_designator_literal"]
    if normalize_designator(first_line) != EXPECTED[528]:
        raise ValueError("secondary literal TLE launch designator mismatch")
    if literal_report["source"]["format"] != \
            "secondary_literal_tle_not_instrumental_original":
        raise ValueError("literal mirror is not primary")
    by_id = defaultdict(list)
    sources = set()
    for raw in raw_rows:
        try:
            sat = int(raw["norad_id"])
            row_index = int(raw["source_row"])
            if sat not in EXPECTED or str(sat) != raw["norad_id"]:
                raise ValueError("unexpected NORAD number")
            if row_index < 0 or row_index in sources:
                raise ValueError("source_row duplicate")
            sources.add(row_index)
            designator_raw = raw["intl_designator"]
            designator = normalize_designator(designator_raw)
            if designator != EXPECTED[sat]:
                raise ValueError("NORAD/COSPAR identity conflict at row " + str(row_index))
            epoch = raw["epoch"]
            if not isinstance(epoch, str) or not epoch.startswith("1963-") or \
                    not epoch.endswith("Z"):
                raise ValueError("epoch outside 1963 UTC")
        except (KeyError, TypeError) as exc:
            raise ValueError("missing required catalog fields") from exc
        by_id[sat].append((row_index, epoch, designator_raw))
    counts = {sid: len(by_id[sid]) for sid in EXPECTED}
    distinct = {sid: len({r[1] for r in by_id[sid]}) for sid in EXPECTED}
    if counts != COUNTS or distinct != UNIQUE_EPOCHS:
        raise ValueError("pinned CSV object/epoch counts changed")
    return {
        "record_id": "C241-L10",
        "constraint_graph": {
            "edge": "C241-L10:NORAD_COSPAR_catalog_join",
            "state": "CONNECTED_PENDING_CALIBRATION",
            "independence": "NOT_ESTABLISHED",
            "physical_frame": None,
            "measurement_sigma": None,
            "lean_4_35_physical_predicate": "NOT_PROMOTED",
            "parameter_domain_reduction": "NOT_COMPUTED",
        },
        "classification": "CATALOG_IDENTITY_CONSISTENCY_NOT_ENGINEERING_IDENTITY",
        "source": {
            "parquet_url": SOURCE_URL,
            "parquet_sha256": PARQUET_SHA256,
            "derived_csv_sha256": csv_sha,
            "literal_528_sha256": literal_report["source"]["sha256"],
            "catalog_transcription_date_utc": ledger["capture_date_utc"],
            "catalog_sources": {name: row["url"] for name, row in ledger["sources"].items()},
            "nasa_date_only": ledger["primary_date_only_record"],
        },
        "catalog_join": {
            str(sid): {
                "cospar": EXPECTED[sid],
                "secondary_display_name": SECONDARY_NAMES[sid],
                "rows": counts[sid],
                "unique_epochs": distinct[sid],
                "source_rows": sorted(x[0] for x in by_id[sid]),
                "literal_designator_spellings": dict(sorted(Counter(
                    x[2] for x in by_id[sid]).items())),
                "catalog_label_only": True,
            } for sid in EXPECTED
        },
        "literal_528_cospar": normalize_designator(first_line),
        "ledger_status": "TRANSCRIPTION_AT_DATE_NOT_ARCHIVED_SOURCE_BYTES",
        "shared_launch_identity": "1963-003",
        "not_demonstrated": [
            "individual fragment dimensions", "component serial number",
            "debris material", "mass", "separation mechanism",
            "sensor independence", "1963 TLE primary source",
            "historical orbit frame and uncertainties",
            "terminal reentry time/place", "impact at Conde",
            "source of legacy RAAN 284.1520 degrees",
        ],
        "physical_component_identity_528": "NOT_RECOVERED",
        "lean_physical_premise": "NOT_PROMOTED",
        "physical_simulation_and_holdout": "NOT_RUN",
        "status_for_conde": "INDETERMINATE",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--pair", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    sha = file_sha256(args.csv)
    if sha != CSV_SHA256:
        raise SystemExit("CSV SHA256 mismatch: " + sha)
    with args.csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    pair = audit_literal_file(args.pair)
    # The full syntax auditor already pins literal bytes and checksums.
    pair["line1_intl_designator_literal"] = args.pair.read_text(
        encoding="ascii").splitlines()[0][9:17]
    report = audit_identity(rows, ledger, pair, csv_sha=sha)
    report["catalog_ledger_sha256"] = file_sha256(args.ledger)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(
        report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps({
        "counts": {k: v["rows"] for k, v in report["catalog_join"].items()},
        "cospar": {k: v["cospar"] for k, v in report["catalog_join"].items()},
        "physical_identity": report["physical_component_identity_528"],
        "frame": "NOT_VERIFIED",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
