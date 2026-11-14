#!/usr/bin/env python3
"""C241: archive-search triage of 1963 reentry controls, NOT reentry calibration.

The 1963 Parquet is a single secondary lineage. The calendar dates for new
candidates come from *secondary leads*, not independent terminal observations.
No event likelihood, terminal sigma, posterior or geographic constraint is made.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime, time, timezone
import json
import math
from pathlib import Path

from c241_637_regime_holdout import SOURCE_SHA256, SOURCE_URL, digest

COLUMNS = ("norad_id", "epoch", "mean_motion", "eccentricity",
           "inclination", "raan", "intl_designator")
# Archival leads found after looking at the 1963 catalogue; NOT a blind cohort.
# KeepTrack dates are useful search clues, not independently authenticated
# terminal instants. NASA / AF IN source statuses are deliberately distinct.
CASES = {
    292: ("1963-11-26", "https://keeptrack.space/satellite/00292",
          "SECONDARY_DECAY_DAY_LEAD", "CANDIDATE"),
    308: ("1963-10-30", "https://keeptrack.space/satellite/00308",
          "SECONDARY_DECAY_DAY_LEAD", "CANDIDATE"),
    565: ("1963-11-24", "https://keeptrack.space/satellite/565",
          "SECONDARY_DECAY_DAY_LEAD", "CANDIDATE"),
    668: ("1963-10-12", "https://keeptrack.space/satellite/00668",
          "SECONDARY_DECAY_DAY_LEAD", "CANDIDATE"),
    637: ("1963-11-07", "https://ntrs.nasa.gov/",
          "NASA_SSR_CALENDAR_DAY_TZ_UNVERIFIED", "KNOWN_CONTROL"),
    688: ("1963-11-12", "https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/08.pdf",
          "AF_IN_23784_INTERVAL_2210_2400Z", "INCOMPLETE_CONTROL"),
    528: ("1963-11-08", "https://ntrs.nasa.gov/",
          "NASA_SSR_CALENDAR_DAY_TZ_UNVERIFIED", "TARGET_NOT_CONTROL"),
}
# Counts are assertions against this particular pinned artefact, NOT independent
# observation counts. An alternate source must use a different contract.
EXPECTED_DISTINCT = {292: 53, 308: 52, 565: 31, 668: 10,
                     637: 25, 688: 1, 528: 45}
EXPECTED_RAW = {292: 53, 308: 52, 565: 31, 668: 10,
                637: 25, 688: 1, 528: 45}
EARTH_MU = 398600.4418  # km^3/s^2, conventional Kepler proxy
EARTH_RADIUS = 6378.137  # km, conventional equatorial radius


def parsed_row(row: dict, index: int) -> dict:
    if type(row.get("norad_id")) is not int or row["norad_id"] not in CASES:
        raise ValueError("bad candidate ID")
    epoch = row.get("epoch")
    if (not isinstance(epoch, datetime) or epoch.utcoffset() is None
            or epoch.utcoffset().total_seconds() != 0 or epoch.year != 1963):
        raise ValueError("non-1963 or non-UTC epoch")
    name = row.get("intl_designator")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("missing designator")
    fields = {}
    for key in ("mean_motion", "eccentricity", "inclination", "raan"):
        value = row.get(key)
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError("bad numerical field: " + key)
        fields[key] = float(value)
    if not (fields["mean_motion"] > 0 and 0 <= fields["eccentricity"] < 1
            and 0 <= fields["inclination"] <= 180 and 0 <= fields["raan"] < 360):
        raise ValueError("invalid orbital element")
    return {"norad_id": row["norad_id"], "epoch": epoch, "source_row": index,
            "intl_designator": name, **fields}


def collect_pinned(path: Path) -> dict[int, list[dict]]:
    if digest(path) != SOURCE_SHA256:
        raise ValueError("SHA-256 mismatch: historical source changed")
    import pyarrow.parquet as pq
    parquet = pq.ParquetFile(path)
    if not set(COLUMNS).issubset(parquet.schema_arrow.names):
        raise ValueError("missing pinned schema columns")
    groups = defaultdict(list)
    row_idx = 0
    for batch in parquet.iter_batches(batch_size=64, columns=list(COLUMNS)):
        for raw in batch.to_pylist():
            if raw["norad_id"] in CASES:
                groups[raw["norad_id"]].append(parsed_row(raw, row_idx))
            row_idx += 1
    if row_idx != 4567:
        raise ValueError("pinned source row count drift")
    return groups


def unique_epochs(rows: list[dict], sid: int) -> list[dict]:
    by_epoch = {}
    designators = set()
    for rec in rows:
        if rec["norad_id"] != sid:
            raise ValueError("cross-object contamination")
        designators.add(rec["intl_designator"].strip())
        old = by_epoch.get(rec["epoch"])
        if old is None:
            by_epoch[rec["epoch"]] = rec
        elif any(rec[k] != old[k] for k in ("mean_motion", "eccentricity",
                                            "inclination", "raan", "intl_designator")):
            raise ValueError("conflicting same-epoch records")
    if len(designators) != 1:
        raise ValueError("designator changed within NORAD ID")
    return sorted(by_epoch.values(), key=lambda rec: rec["epoch"])


def perigee_proxy(row: dict) -> float:
    mean_motion_rad_s = row["mean_motion"] * math.tau / 86400.0
    a = (EARTH_MU / (mean_motion_rad_s ** 2)) ** (1 / 3)
    return a * (1 - row["eccentricity"]) - EARTH_RADIUS


def screen(groups: dict[int, list[dict]], *, pin_counts: bool) -> dict:
    if set(groups) != set(CASES):
        raise ValueError("candidate object set drift")
    controls = []
    for sid, (terminal_day, url, grade, role) in CASES.items():
        raw = groups[sid]
        epochs = unique_epochs(raw, sid)
        if not epochs:
            raise ValueError("missing candidate epochs")
        if pin_counts and (len(raw) != EXPECTED_RAW[sid] or
                           len(epochs) != EXPECTED_DISTINCT[sid]):
            raise ValueError("pinned candidate row/epoch count drift")
        # Solely a counterfactual UTC-day cutoff; the documentary date
        # convention is not authenticated by this screening exercise.
        boundary = datetime.combine(date.fromisoformat(terminal_day),
                                    time.min, tzinfo=timezone.utc)
        prior = [rec for rec in epochs if rec["epoch"] < boundary]
        if not prior:
            raise ValueError("no orbital data before assumed UTC day")
        last = prior[-1]
        # Any record at/after a presumed event must not silently enter fit.
        excluded = len(epochs) - len(prior)
        status = "SLOPE_ALGEBRAICALLY_ESTIMABLE" if len(prior) >= 2 else "ONE_EPOCH_NO_SLOPE"
        controls.append({
            "norad": sid, "role": role, "international_designator": last["intl_designator"],
            "reported_terminal_calendar_day": terminal_day, "reported_terminal_source": url,
            "terminal_evidence_grade": grade,
            "terminal_date_utc_convention_verified": False if grade != "AF_IN_23784_INTERVAL_2210_2400Z" else True,
            "catalogue_raw_rows": len(raw), "catalogue_unique_epochs": len(epochs),
            "conditional_pre_day_epoch_count": len(prior),
            "excluded_at_or_after_assumed_utc_boundary": excluded,
            "latest_pre_day_epoch_utc": last["epoch"].isoformat(),
            "latest_pre_day_source_row": last["source_row"],
            "last_mean_motion_rev_day": round(last["mean_motion"], 8),
            "last_kepler_perigee_proxy_km_NOT_OBSERVED": round(perigee_proxy(last), 3),
            "within_object_local_secant": status,
            "instrumental_lineages_independently_authenticated": 0,
            "terminal_time_error_calibrated": False,
            "terminal_holdout_ready": False,
        })
    # Rank archive retrieval only, not likelihood or historical certainty.
    # Compare only proposed new controls, keeping target and known controls out.
    priority = sorted((v for v in controls if v["role"] == "CANDIDATE"),
                      key=lambda v: (-v["conditional_pre_day_epoch_count"], v["norad"]))
    return {
        "schema": "conde.c241-1963-reentry-control-search/v1",
        "source": {"url": SOURCE_URL, "sha256": SOURCE_SHA256,
                   "lineage": "ONE_SECONDARY_SPACE_TRACK_MIRROR"},
        "design": {"selection": "POST_INSPECTION_RETROSPECTIVE_ARCHIVE_SEARCH",
                   "candidate_decay_days": "SECONDARY_LEADS_UNVERIFIED_AS_INDEPENDENT_TERMINAL_TIMES",
                   "comparison_date_convention": "HYPOTHETICAL_UTC_DAY_EXCLUSIVE",
                   "orbit_fields": "CATALOGUE_ELEMENTS_NOT_TRACKING_INSTRUMENT_READINGS",
                   "repeated_epoch_counts_as_new_observation": False},
        "cases": controls,
        "archive_search_priority_norad": [v["norad"] for v in priority],
        "inference": {"active_constraint_528": False,
                      "historical_mcmc": "NOT_RUN",
                      "reentry_time_sigma_hours": None,
                      "mass_528_posterior": None, "impact_probability": None,
                      "impact_geography": None,
                      "reason": "NO_INDEPENDENTLY_CALIBRATED_TERMINAL_TIMES_OR_INSTRUMENT_ERRORS"},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    payload = screen(collect_pinned(args.parquet), pin_counts=args.check)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    print("C241 archive screen: candidates",
          payload["archive_search_priority_norad"],
          "; calibrated reentry holdouts = 0; MCMC NOT_RUN")


if __name__ == "__main__":
    main()
