#!/usr/bin/env python3
"""G39: test NASA SSR cross-field inconsistency against a pinned secondary TLE mirror.

Publication/report date is NOT an observation epoch. Mirrors may share a NORAD
source with NASA. The screen is not a measured orbit, trajectory, or holdout.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path

try:
    from tools.ssr_crossfield_screen_g37 import build as validate_nasa
except ModuleNotFoundError as exc:
    if exc.name != "tools":
        raise
    from ssr_crossfield_screen_g37 import build as validate_nasa

ROOT = Path(__file__).resolve().parents[1]
NASA = ROOT / "research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json"
SNAP = ROOT / "research/tle_custody/CASTOR-G39_mirror_selection.json"
OUT = ROOT / "research/constraints/CASTOR-G39_ssr_mirror_period_screen.json"
EXPECTED_CSV_SHA256 = "3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231"
EXPECTED_PARQUET_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
IDS = {"1963-003A": "527", "1963-003B": "528", "1963-003C": "529"}
GM = 398600.4418
R_EARTH = 6378.137


def instant(s: str) -> datetime:
    if not isinstance(s, str) or not s.endswith("Z"):
        raise ValueError("UTC Z epoch required")
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def source_candidates(csv_bytes: bytes, cutoffs: dict) -> list[dict]:
    if hashlib.sha256(csv_bytes).hexdigest() != EXPECTED_CSV_SHA256:
        raise ValueError("unverified secondary CSV checksum")
    rows = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8"))))
    required = {"source_row", "norad_id", "epoch", "mean_motion"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("secondary schema changed")
    candidates = []
    for ntrs, designator, cutoff in cutoffs:
        obj = IDS[designator]
        before = [r for r in rows if r["norad_id"] == obj and instant(r["epoch"]) <= cutoff]
        if not before:
            raise ValueError("no preceding mirror epoch")
        latest_epoch = max(instant(r["epoch"]) for r in before)
        tied = [r for r in before if instant(r["epoch"]) == latest_epoch]
        if len({r["mean_motion"] for r in tied}) != 1:
            raise ValueError("conflicting latest-epoch mean motions")
        # Exact row index disambiguates duplicate numerical copies.
        r = min(tied, key=lambda x: int(x["source_row"]))
        candidates.append({
            "ntrs_id": ntrs, "designator": designator,
            "source_row": int(r["source_row"]),
            "norad_id": obj, "epoch": r["epoch"], "mean_motion_rev_day": r["mean_motion"],
        })
    return candidates


def evaluate(ledger: dict, snapshot: dict, csv_bytes: bytes | None = None) -> dict:
    validated = validate_nasa(ledger)  # checks edition, page, identity, document SHA
    if len(validated["cells"]) != 7:
        raise ValueError("NASA row count changed")
    if snapshot.get("id") != "CASTOR-G39-MIRROR-SELECTION":
        raise ValueError("unknown snapshot")
    if (snapshot.get("source_csv_sha256") != EXPECTED_CSV_SHA256 or
            snapshot.get("source_parquet_sha256") != EXPECTED_PARQUET_SHA256):
        raise ValueError("mirror source changed")
    cutoffs = []
    source_map = {}
    for s in ledger["sources"]:
        as_of = instant(s["as_of_utc"])  # documentary cutoff only
        source_map[s["ntrs_id"]] = s
        for r in s["rows"]:
            cutoffs.append((s["ntrs_id"], r["designator"], as_of))
    pinned = snapshot.get("selected")
    if not isinstance(pinned, list) or len(pinned) != len(cutoffs):
        raise ValueError("mirror selected records missing")
    if csv_bytes is not None and source_candidates(csv_bytes, cutoffs) != pinned:
        raise ValueError("frozen mirror candidate selection differs from verified CSV")
    by_key = {}
    seen_rows = set()
    for row in pinned:
        key = (row["ntrs_id"], row["designator"])
        if key in by_key or key not in {(a, b) for a, b, _ in cutoffs}:
            raise ValueError("duplicate or invented linked source")
        if row["norad_id"] != IDS[row["designator"]]:
            raise ValueError("NORAD identity mismatch")
        if not isinstance(row["source_row"], int) or row["source_row"] in seen_rows:
            raise ValueError("mirror source row conflict")
        seen_rows.add(row["source_row"])
        if not math.isfinite(float(row["mean_motion_rev_day"])) or float(row["mean_motion_rev_day"]) <= 0:
            raise ValueError("mean motion not finite positive")
        if instant(row["epoch"]) > instant(source_map[row["ntrs_id"]]["as_of_utc"]):
            raise ValueError("future observation used")
        by_key[key] = row
    if len(by_key) != len(cutoffs):
        raise ValueError("some NASA rows lack mirror source")
    comparisons = []
    for source in ledger["sources"]:
        for cell in source["rows"]:
            row = by_key[(source["ntrs_id"], cell["designator"])]
            lag = (instant(source["as_of_utc"]) - instant(row["epoch"])).total_seconds() / 86400
            n = float(row["mean_motion_rev_day"])
            mirror_period = 1440 / n
            a = (GM / (2 * math.pi * n / 86400) ** 2) ** (1 / 3)
            altitude_proxy = a - R_EARTH
            compiled_altitude = (cell["apogee_km"] + cell["perigee_km"]) / 2
            if not all(math.isfinite(v) for v in (lag, mirror_period, altitude_proxy, compiled_altitude)):
                raise ValueError("nonfinite derived output")
            comparisons.append({
                "ntrs_id": source["ntrs_id"],
                "document_publication_NOT_instrument_epoch": source["published"],
                "report_cutoff_NOT_instrument_epoch": source["as_of_utc"],
                "object": cell["designator"], "norad": row["norad_id"],
                "mirror_source_row": row["source_row"], "mirror_epoch_utc_SECONDARY": row["epoch"],
                "mirror_age_at_report_cutoff_days": round(lag, 6),
                "mirror_epoch_is_coeval_with_nasa_fields": "UNKNOWN",
                "printed_period_min": float(cell["period_min"]),
                "mirror_mean_motion_rev_day": n,
                "mirror_period_proxy_min_NOT_osculating": round(mirror_period, 7),
                "printed_minus_mirror_period_seconds": round(60 * (float(cell["period_min"]) - mirror_period), 4),
                "printed_mean_apsidal_height_km": compiled_altitude,
                "mirror_kepler_altitude_proxy_km_NOT_observation": round(altitude_proxy, 4),
                "printed_height_minus_mirror_proxy_km": round(compiled_altitude - altitude_proxy, 4),
                "recency_bucket_only": "WITHIN_2_DAYS" if lag <= 2 else ("WITHIN_7_DAYS" if lag <= 7 else "OLDER_THAN_7_DAYS"),
                "independent_instrumental_cross_validation": False,
            })
    dec = {r["norad"]: r for r in comparisons if r["document_publication_NOT_instrument_epoch"] == "1963-12-31"}
    nov = {r["norad"]: r for r in comparisons if r["document_publication_NOT_instrument_epoch"] == "1963-11-30"}
    if set(dec) != {"527", "529"} or "529" not in nov:
        raise ValueError("expected December and November controls")
    return {
        "id": "CASTOR-G39-SSR-SECONDARY-PERIOD-CROSSCHECK",
        "status": "SECONDARY_SAME_LINEAGE_DIAGNOSTIC_NO_INSTRUMENT_HOLDOUT",
        "depends_on": ["C241-L18", "CASTOR-G37-DEC31-SSR-CROSSFIELD", "CASTOR-G38-DEC31-PRINTED-NODAL-J2", "C241-L2"],
        "nasa_source": str(NASA.relative_to(ROOT)),
        "mirror_selection_source": str(SNAP.relative_to(ROOT)),
        "mirror_original_kind": "MODERN_NUMERIC_PARQUET_COPY_NOT_ORIGINAL_TLE",
        "parquet_sha256": EXPECTED_PARQUET_SHA256,
        "csv_sha256": EXPECTED_CSV_SHA256,
        "comparison_conventions": {
            "mirror_T_min": "1440 / mean_motion_rev_day",
            "mirror_a_km": "(mu/(2*pi*n/86400)^2)^(1/3)",
            "printed_mean_alt_km": "(apogee_km+perigee_km)/2",
            "caution": "SGP4 mean motion is not osculating Kepler motion; report cutoff is not measurement time, and NASA and mirror may share input tracking",
            "instrumental_sigma": None,
            "elements_are_coepoch": None,
            "physically_calibrated_dynamics": False,
        },
        "comparisons": comparisons,
        "december_529_vs_november_529": {
            "december_printed_vs_mirror_period_s": dec["529"]["printed_minus_mirror_period_seconds"],
            "december_printed_vs_mirror_altitude_proxy_km": dec["529"]["printed_height_minus_mirror_proxy_km"],
            "november_printed_vs_mirror_altitude_proxy_km": nov["529"]["printed_height_minus_mirror_proxy_km"],
            "december_source_row": dec["529"]["mirror_source_row"],
            "hypothesis_of_lagged_altitudes": "UNRESOLVED_CANDIDATE_NOT_PROVED",
            "instrumental_origin_determined": False,
        },
        "source_raw_1963_instrument_observations": 0,
        "independent_historical_527_529_holdout": "NOT_RUN",
        "activated_historical_orbital_restriction": False,
        "time_location_probability_of_conde_impact": "NOT_DETERMINED",
    }


def render(ledger: dict, snap: dict, csv_bytes: bytes | None = None) -> str:
    return json.dumps(evaluate(ledger, snap, csv_bytes), indent=2, ensure_ascii=False) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--csv", type=Path, help="full, SHA-pinned historical secondary CSV; replay candidate selection")
    args = parser.parse_args()
    content = render(json.loads(NASA.read_text()), json.loads(SNAP.read_text()),
                     args.csv.read_bytes() if args.csv else None)
    if args.write:
        OUT.write_text(content, encoding="utf-8")
    elif OUT.read_text(encoding="utf-8") != content:
        raise SystemExit("G39 reproducibility check failed")
    print("G39: seven rows; "+("full SHA-pinned CSV selection replay PASS" if args.csv else "frozen selection only")+"; no independent instrument holdout")


if __name__ == "__main__":
    main()
