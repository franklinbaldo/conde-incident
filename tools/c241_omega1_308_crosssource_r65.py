#!/usr/bin/env python3
"""C241 R65: cross-source numerical fingerprint, never an identity assertion.

Printed NASA SSR is a catalogue summary, and secondary historical TLEs are
not known to be independent observations. This produces diagnostics only.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path

from c241_1963_terminal_control_screen import EARTH_MU, EARTH_RADIUS
from c241_637_regime_holdout import SOURCE_SHA256, SOURCE_URL

SSR_SHA = "fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2"
CUTOFF = datetime.fromisoformat("1963-10-15T12:00:00+00:00")
SSR_EXPECTED = {"printed_name": "OMEGA 1", "source_country": "US",
                "launch_day_month": "18 JUN", "nodal_period_minutes": "89.7",
                "inclination_degrees": "82.15", "apogee_km": 263,
                "perigee_km": 254, "catalog_number_printed": None}


def verify_ssr(record: dict) -> None:
    if record.get("id") != "C241-L68":
        raise ValueError("incorrect SSR record")
    s = record.get("source", {})
    if (s.get("pdf_sha256") != SSR_SHA or s.get("report_as_of_utc") != "1963-10-15T12:00:00Z"
            or s.get("ntrs_id") != "19640000428" or s.get("family") != "NASA_GSFC_SSR_NORAD_SHARED"):
        raise ValueError("SSR provenance/as-of mismatch")
    if record.get("row") != {**SSR_EXPECTED, "table_heading": "OBJECTS IN ORBIT", "section": "1962 LAUNCHES"}:
        raise ValueError("SSR printed row drift")
    limitations = record.get("limits", {})
    expected = {"row_is_instrumental_observation": False,
                "as_of_is_instrumental_epoch": False,
                "source_independent_of_nasa_1963_1977_catalog_family": False,
                "norad_308_identification_from_this_row": None,
                "independent_instrumental_observations_added": 0,
                "terminal_event_utc": None, "terminal_sigma_seconds": None,
                "active_constraint_528": False, "historical_mcmc": "NOT_RUN"}
    if any(limitations.get(k, object()) != v for k, v in expected.items()):
        raise ValueError("SSR evidence limitations promoted")


def valid_epoch(rec: dict) -> datetime:
    t = rec.get("epoch")
    if (not isinstance(t, datetime) or t.utcoffset() is None
            or t.utcoffset().total_seconds() != 0 or t.year != 1963):
        raise ValueError("bad epoch/UTC")
    return t


def compare(record: dict, rows: list[dict]) -> dict:
    verify_ssr(record)
    seen = {}
    for row in rows:
        if type(row.get("norad_id")) is not int or row["norad_id"] != 308:
            raise ValueError("wrong NORAD")
        epoch = valid_epoch(row)
        if row.get("intl_designator") != "62024  A":
            raise ValueError("TLE designator drift")
        for key in ("mean_motion", "eccentricity", "inclination"):
            x = row.get(key)
            if isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x):
                raise ValueError("bad orbital data " + key)
        if not (row["mean_motion"] > 0 and 0 <= row["eccentricity"] < 1
                and 0 <= row["inclination"] <= 180):
            raise ValueError("orbital element range")
        vals = (float(row["mean_motion"]), float(row["eccentricity"]),
                float(row["inclination"]))
        if epoch in seen and seen[epoch] != vals:
            raise ValueError("conflicting duplicate epoch")
        seen[epoch] = vals
    prior = sorted(t for t in seen if t < CUTOFF)
    if not prior:
        raise ValueError("no pre-cutoff catalogue epoch")
    t = prior[-1]
    n, e, inc = seen[t]
    a = (EARTH_MU / (n * math.tau / 86400) ** 2) ** (1 / 3)
    derived = {"period_minutes_from_mean_motion": 1440 / n,
               "inclination_degrees": inc,
               "kepler_apogee_proxy_km": a * (1 + e) - EARTH_RADIUS,
               "kepler_perigee_proxy_km": a * (1 - e) - EARTH_RADIUS}
    printed = {"nodal_period_minutes": 89.7, "inclination_degrees": 82.15,
               "apogee_km": 263, "perigee_km": 254}
    diff = {"period_minutes": derived["period_minutes_from_mean_motion"] - printed["nodal_period_minutes"],
            "inclination_degrees": inc - printed["inclination_degrees"],
            "apogee_proxy_km": derived["kepler_apogee_proxy_km"] - printed["apogee_km"],
            "perigee_proxy_km": derived["kepler_perigee_proxy_km"] - printed["perigee_km"]}
    return {
        "schema": "conde.c241-omega1-308-numeric-fingerprint-r65/v1",
        "sources": {"primary_ssr": record["source"]["pdf_url"],
                    "primary_ssr_sha256": SSR_SHA, "secondary_tle": SOURCE_URL,
                    "secondary_tle_sha256": SOURCE_SHA256,
                    "lineage_independence_established": False},
        "printed_row": {"name": "OMEGA 1", "norad_id_printed": None,
                        **printed, "report_as_of_utc_NOT_OBSERVATION": "1963-10-15T12:00:00Z"},
        "candidate": {"norad_id": 308, "selection": "RETROSPECTIVE_CROSS_EDITION_ALIAS",
                      "raw_rows": len(rows), "unique_epochs": len(seen),
                      "pre_cutoff_epochs": len(prior), "excluded_at_or_after_cutoff": len(seen) - len(prior),
                      "last_pre_cutoff_epoch_utc": t.isoformat().replace("+00:00", "Z"),
                      "lag_from_report_cutoff_hours": round((CUTOFF - t).total_seconds() / 3600, 9),
                      **{k: round(v, 9) for k, v in derived.items()}},
        "difference_candidate_minus_printed": {k: round(v, 9) for k, v in diff.items()},
        "comparison_caveats": {
            "nodal_period_equals_tle_kepler_period": False,
            "ssr_printed_elements_same_instrument_epoch_as_tle": False,
            "apogee_perigee_kepler_proxy_equals_ssr_definition": False,
            "printed_decimals_instrument_sigma": False,
            "direct_1963_OMEGA1_to_NORAD308_identification": False,
            "numerical_fingerprint_proves_identity": False,
            "candidate_cohort_exhaustive": False},
        "inference": {"active_constraint_528": False, "historical_mcmc": "NOT_RUN",
                      "terminal_sigma_hours": None, "identity_probability": None,
                      "impact_probability": None, "impact_geography": None}
    }


def pinned_rows(parquet_path: Path) -> list[dict]:
    digest = hashlib.sha256(parquet_path.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError("pinned secondary archive SHA mismatch")
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(parquet_path)
    fields = ["norad_id", "epoch", "mean_motion", "eccentricity", "inclination", "intl_designator"]
    if not set(fields).issubset(pf.schema_arrow.names):
        raise ValueError("secondary archive schema drift")
    rows, total = [], 0
    for batch in pf.iter_batches(batch_size=64, columns=fields):
        for row in batch.to_pylist():
            total += 1
            if row["norad_id"] == 308:
                rows.append(row)
    if total != 4567 or len(rows) != 52:
        raise ValueError("secondary archive count drift")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ssr", type=Path, required=True)
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    result = compare(json.loads(a.ssr.read_text(encoding="utf-8")), pinned_rows(a.parquet))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("R65: numerical fingerprint only; independent calibration=0; MCMC NOT_RUN")


if __name__ == "__main__":
    main()
