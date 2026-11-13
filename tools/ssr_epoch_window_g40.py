#!/usr/bin/env python3
"""G40: sensitivity of NASA/secondary period comparisons to UNVERIFIED epoch choice.

The NASA publication cutoff is not an instrumental epoch. A secondary numeric
mirror can share provenance with NASA: this is a documentary sensitivity test,
not a historical holdout, drag model, clock estimate or reentry localization.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

try:
    from tools import ssr_secondary_period_g39 as g39
except ModuleNotFoundError as exc:
    if exc.name != "tools":
        raise
    import ssr_secondary_period_g39 as g39

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/constraints/CASTOR-G40_ssr_epoch_window_sensitivity.json"
WINDOWS_DAYS = (2, 7, 14, 30)


def parse_verified_csv(raw: bytes) -> list[dict]:
    if hashlib.sha256(raw).hexdigest() != g39.EXPECTED_CSV_SHA256:
        raise ValueError("source CSV SHA256 differs from pinned C241-L2 derivative")
    try:
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8", errors="strict"))))
    except UnicodeError as exc:
        raise ValueError("CSV must be UTF-8") from exc
    required = {"source_row", "norad_id", "epoch", "mean_motion"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("missing secondary source columns")
    seen_row = set()
    seen_epoch = {}
    clean = []
    for r in rows:
        if not set(required).issubset(r):
            raise ValueError("incomplete row")
        source_row = int(r["source_row"])
        obj = r["norad_id"]
        instant = g39.instant(r["epoch"])
        n = float(r["mean_motion"])
        if source_row in seen_row or obj not in g39.IDS.values():
            raise ValueError("duplicate source_row or unexpected NORAD")
        if not math.isfinite(n) or n <= 0:
            raise ValueError("mean motion not finite/positive")
        seen_row.add(source_row)
        key = (obj, instant)
        if key in seen_epoch and seen_epoch[key] != n:
            raise ValueError("conflicting same-epoch mean motions")
        seen_epoch[key] = n
        clean.append({"row": source_row, "norad": obj, "epoch": instant, "n": n})
    return clean


def window_stats(rows: list[dict], obj: str, cutoff, printed_period: float,
                 printed_mean_alt: float, width_days: int) -> dict:
    """Date-bounded descriptive extrema. Never fit or extrapolate to report date."""
    if width_days <= 0 or not math.isfinite(printed_period) or not math.isfinite(printed_mean_alt):
        raise ValueError("invalid window/printed datum")
    candidates = [r for r in rows if r["norad"] == obj and
                  0 <= (cutoff-r["epoch"]).total_seconds() / 86400 <= width_days]
    # Repeated identical epochs are copies, not independent observations.
    distinct = {}
    for r in candidates:
        key = r["epoch"]
        if key in distinct and distinct[key]["n"] != r["n"]:
            raise ValueError("same-epoch source disagreement")
        if key not in distinct or r["row"] < distinct[key]["row"]:
            distinct[key] = r
    candidates = list(distinct.values())
    result = {"max_lookback_days_NOT_instrument_age": width_days,
              "distinct_secondary_epochs": len(candidates),
              "printed_minus_mirror_period_seconds_range": None,
              "printed_height_minus_mirror_kepler_proxy_km_range": None}
    if not candidates:
        return result
    seconds = [60 * (printed_period - 1440 / r["n"]) for r in candidates]
    heights = [
        printed_mean_alt - ((g39.GM / (2 * math.pi * r["n"] / 86400) ** 2) ** (1 / 3) - g39.R_EARTH)
        for r in candidates
    ]
    if not all(map(math.isfinite, seconds + heights)):
        raise ValueError("derived proxy nonfinite")
    result["printed_minus_mirror_period_seconds_range"] = [round(min(seconds), 4), round(max(seconds), 4)]
    result["printed_height_minus_mirror_kepler_proxy_km_range"] = [round(min(heights), 4), round(max(heights), 4)]
    return result


def evaluate(ledger: dict, snapshot: dict, raw: bytes) -> dict:
    # Checks seven source-locked NASA rows, hash-pinned full CSV and frozen
    # nearest-prior selections from G39 before computing anything new.
    report = g39.evaluate(ledger, snapshot, raw)
    rows = parse_verified_csv(raw)
    results = []
    for base in report["comparisons"]:
        obj = base["norad"]
        cutoff = g39.instant(base["report_cutoff_NOT_instrument_epoch"])
        period = base["printed_period_min"]
        altitude = base["printed_mean_apsidal_height_km"]
        result = {
            "ntrs_id": base["ntrs_id"],
            "object": base["object"],
            "norad_id": obj,
            "publication_date_NOT_observation_epoch": base["document_publication_NOT_instrument_epoch"],
            "editorial_cutoff_NOT_observation_epoch": base["report_cutoff_NOT_instrument_epoch"],
            "g39_latest_prior_source_row": base["mirror_source_row"],
            "g39_latest_prior_age_days": base["mirror_age_at_report_cutoff_days"],
            "windows": [window_stats(rows, obj, cutoff, period, altitude, w) for w in WINDOWS_DAYS],
        }
        results.append(result)
    return {
        "id": "CASTOR-G40-SSR-EPOCH-WINDOW-SENSITIVITY",
        "status": "SECONDARY_DOCUMENTARY_EPOCH_CHOICE_SENSITIVITY_NOT_HISTORICAL_FIT",
        "dependencies": ["C241-L18", "C241-L2", "CASTOR-G39-SSR-SECONDARY-PERIOD-CROSSCHECK"],
        "source_parquet_sha256": g39.EXPECTED_PARQUET_SHA256,
        "source_csv_sha256": g39.EXPECTED_CSV_SHA256,
        "metric": "For EVERY eligible prior secondary epoch within each lookback window, descriptive min/max of NASA printed minus 1440/n and of NASA printed mean altitude minus Kepler proxy from n",
        "source_independence": "UNKNOWN_SHARED_NORAD_LINEAGE",
        "reported_epochs_are_instrument_epochs": False,
        "secondary_epochs_are_authenticated_raw_instrument_observations": False,
        "window_width_is_uncertainty_calibration": False,
        "source_epoch_lag_is_publication_latency": "NOT_ESTABLISHED",
        "instrument_sigma_and_covariance": None,
        "physical_constraint_activated": False,
        "norad_527_529_historical_holdouts": "NOT_RUN",
        "conde_impact_time_position_probability": "NOT_DETERMINED",
        "results": results,
    }


def render(ledger: dict, snapshot: dict, raw: bytes) -> str:
    return json.dumps(evaluate(ledger, snapshot, raw), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path, help="verified C241-L2 derived CSV")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = render(json.loads(g39.NASA.read_text()), json.loads(g39.SNAP.read_text()),
                   args.csv.read_bytes())
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != value:
            raise SystemExit("G40 certificate drift")
    else:
        OUT.write_text(value, encoding="utf-8")
    print("G40 seven cells; four dated windows each; raw CSV SHA256 verified; no instrumental inference")


if __name__ == "__main__":
    main()
