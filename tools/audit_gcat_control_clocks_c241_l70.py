#!/usr/bin/env python3
"""C241-L70: keep payload-operation dates distinct from catalog decay days.

Reuses the exact GCAT full-TSV snapshot already pinned in C241-P29.
No tracking data, new instrumental epochs, or physical inference.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/gcat_control_clocks_C241-L70.json"
EXPECTED = {
    "637": ("1963-035A", "1963 Sep 1", "1963 Nov 7", "A00384"),
    "668": ("1963-037A", "1963 Oct 4", "1963 Oct 12", "A00391"),
}
INTERPRETATION = {
    "operational_dates_are_not_decay_dates": True,
    "common_catalog_snapshot_not_independent_measurements": True,
    "terminal_hour_recovered": False,
    "extra_norad_528_constraints": 0,
    "physical_domain_effect": "THETA_UNCHANGED",
}


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("C241-L70: " + reason)


def day(value: str) -> datetime:
    require(bool(re.fullmatch(r"\d{4}\s+[A-Z][a-z]{2}\s+\d{1,2}", value)),
            "not a day-only catalog date")
    return datetime.strptime(" ".join(value.split()), "%Y %b %d")


def parse_row(header: str, entry: dict, number: str, kind: str) -> dict:
    line = entry["line"]
    require(hashlib.sha256(line.encode("utf-8")).hexdigest() == entry["sha256"],
            f"{kind} {number}: row digest mismatch")
    keys = header.lstrip("#").split("\t")
    cells = line.split("\t")
    require(len(keys) == len(set(keys)) == len(cells), f"{kind} field count")
    row = dict(zip(keys, (cell.strip() for cell in cells)))
    require(row["JCAT"] == f"S{int(number):05d}", f"{kind} object identity")
    return row


def audit(ledger: dict, base: dict) -> dict:
    require(ledger.get("schema") == "conde.gcat-control-clocks/v1", "schema")
    require(ledger["snapshot_ledger"] ==
            "research/tle_custody/gcat_time_axes_527_529_C241-P29.json",
            "parent snapshot reference")
    require(ledger["snapshot_gcat_version"] == base["gc_version"]
            and ledger["snapshot_captured_utc"] == base["capture_date_utc"],
            "snapshot/version mismatch")
    require(base["gc_version"] == "GCAT 1.8.9, Data Update 2026 Nov 13",
            "unexpected baseline version")
    for kind in ("payload", "object"):
        require(ledger["sources"][kind] == base["sources"][kind]["url"],
                f"{kind}: source URL mismatch")
        require(base["sources"][kind]["bytes_full_tsv"] > 100000
                and re.fullmatch(r"[0-9a-f]{64}",
                                 base["sources"][kind]["sha256_full_tsv"]) is not None,
                f"{kind}: parent full-source custody missing")
    require(ledger["sources"]["field_definitions"].endswith("/cat/pcols.html"),
            "payload field definitions not pinned")
    require(set(ledger["objects"]) == set(EXPECTED), "missing/extra controls")
    require(ledger["interpretation"] == INTERPRETATION, "epistemic promotion")
    answer = {}
    for number, item in ledger["objects"].items():
        piece, operations, decay, parent = EXPECTED[number]
        require(item["piece"] == piece and item["parent"] == parent,
                f"{number}: object crosswalk/parent changed")
        require(item["operational_day"] == operations
                and item["catalog_decay_day"] == decay,
                f"{number}: date classification changed")
        for field in ("terminal_epoch_utc", "sensor_id",
                      "terminal_uncertainty_seconds", "impact_location"):
            require(item[field] is None, f"{number}: invented {field}")
        require(item["physical_activation"] is False, f"{number}: physical activation")
        payload = parse_row(base["sources"]["payload"]["header"], item["payload"],
                            number, "payload")
        orbital = parse_row(base["sources"]["object"]["header"], item["object"],
                            number, "object")
        require(payload["Piece"] == orbital["Piece"] == piece,
                f"{number}: COSPAR mismatch")
        require("DDate" not in payload and "TDate" not in orbital,
                f"{number}: mixed catalog namespaces")
        require(all(" ".join(payload[key].split()) == operations
                    for key in ("TLast", "TOp", "TDate")),
                f"{number}: payload-operation day changed")
        require(" ".join(orbital["DDate"].split()) == decay,
                f"{number}: catalog decay day changed")
        require(orbital["Satcat"] == f"{int(number):05d}"
                and orbital["Parent"] == parent
                and orbital["ExpandedStatus"].startswith("Reentered attached to " + parent),
                f"{number}: orbital status/identity changed")
        require(day(payload["TDate"]) < day(orbital["DDate"]),
                f"{number}: operation not before decay")
        answer[number] = {"operation_end": operations,
                          "catalog_decay": decay, "terminal_epoch_utc": None}
    return {"status": "PASS_SNAPSHOT_ONLY", "objects": answer,
            "new_instrumental_measurements": 0, "theta": "UNCHANGED"}


def replay(ledger: dict, base: dict, directory: Path) -> None:
    """Check both original complete TSV files and the four recorded rows."""
    for kind, name in (("payload", "psatcat.tsv"), ("object", "currentcat.tsv")):
        raw = (directory / name).read_bytes()
        source = base["sources"][kind]
        require(len(raw) == source["bytes_full_tsv"]
                and hashlib.sha256(raw).hexdigest() == source["sha256_full_tsv"],
                f"{kind}: complete TSV digest/bytes mismatch")
        lines = raw.decode("utf-8").splitlines()
        require(lines[0] == source["header"], f"{kind}: header mismatch")
        for number, item in ledger["objects"].items():
            matches = [line for line in lines[1:]
                       if line.split("\t", 1)[0].strip() == f"S{int(number):05d}"]
            require(len(matches) == 1 and matches[0] == item[kind]["line"],
                    f"{kind} {number}: row missing/different")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--replay-source-dir", type=Path)
    args = parser.parse_args()
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    base = json.loads((ROOT / ledger["snapshot_ledger"]).read_text(encoding="utf-8"))
    result = audit(ledger, base)
    if args.replay_source_dir:
        replay(ledger, base, args.replay_source_dir)
    if args.check:
        print("PASS C241-L70: 637/668 operational and orbital dates separated; no UTC or physical activation")
    else:
        print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
