#!/usr/bin/env python3
"""Source-locked, descriptive Telstar prediction residuals (NOT 528 sensor sigma)."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "research/observations/telstar_1962_table_vii_C241.csv"
OUT = ROOT / "research/statistics/telstar_1962_prediction_benchmark_C241.json"
CSV_SHA256 = "50c09ca2ac44f48b037e2efa5e4ad6c96740d6ca10f4f0189684a4845ac7d061"
PDF_SHA256 = "98cbd80eb06d381df2d4e78c6c92a6d4436ec3ea3f55b2c4e92baf6640a776b9"
PDF_BYTES = 1148397
COUNTS = {124: 8, 133: 7, 143: 7, 151: 8, 160: 8}
HEADERS = ["utc", "pass_id", "az_observed_deg", "az_predicted_deg",
           "el_observed_deg", "el_predicted_deg"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_rows(raw: bytes | None = None) -> list[dict]:
    if raw is None:
        raw = CSV.read_bytes()
    if sha(raw) != CSV_SHA256:
        raise ValueError("transcribed Table VII bytes changed; re-audit facsimile")
    reader = csv.DictReader(raw.decode("utf-8").splitlines())
    if reader.fieldnames != HEADERS:
        raise ValueError("invalid column contract")
    rows = []
    previous = None
    for row in reader:
        if None in row or set(row) != set(HEADERS):
            raise ValueError("missing or additional CSV field")
        try:
            timestamp = datetime.strptime(row["utc"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
            pass_id = int(row["pass_id"])
            coordinates = [Decimal(row[c]) for c in HEADERS[2:]]
        except (ValueError, InvalidOperation) as exc:
            raise ValueError("malformed time, pass or decimal") from exc
        if not (datetime(1962, 7, 23, tzinfo=timezone.utc) <= timestamp
                < datetime(1962, 7, 28, tzinfo=timezone.utc)):
            raise ValueError("not original July 1962 Telstar sample")
        if previous is not None and timestamp <= previous:
            raise ValueError("repeated or unordered observation epoch")
        previous = timestamp
        if pass_id not in COUNTS:
            raise ValueError("unexpected tracking pass")
        if any(not x.is_finite() or x.as_tuple().exponent != -2 for x in coordinates):
            raise ValueError("loss of published two-decimal print resolution")
        az_o, az_p, el_o, el_p = coordinates
        if not (0 <= az_o < 360 and 0 <= az_p < 360
                and -90 <= el_o <= 90 and -90 <= el_p <= 90):
            raise ValueError("invalid pointing angles")
        rows.append({"utc": row["utc"], "pass_id": pass_id,
                     "az_obs": az_o, "az_pred": az_p,
                     "el_obs": el_o, "el_pred": el_p})
    from collections import Counter
    if Counter(r["pass_id"] for r in rows) != COUNTS or len(rows) != 38:
        raise ValueError("incorrect pass memberships")
    if not any(r["pass_id"] == 143 and r["utc"].startswith("1962-07-26T")
               for r in rows):
        raise ValueError("midnight-crossing pass lost")
    return rows


def circular_difference_deg(a: float, b: float) -> float:
    """Shortest a-b angular difference in degrees, including 0/360 seam."""
    return (a - b + 180.0) % 360.0 - 180.0


def sky_separation_deg(az_o: float, az_p: float, el_o: float, el_p: float) -> float:
    """Exact great-circle LOS angle, avoiding flat azimuth error at high elevation."""
    eo, ep = math.radians(el_o), math.radians(el_p)
    da = math.radians(circular_difference_deg(az_p, az_o))
    hav = math.sin((ep - eo) / 2)**2 + math.cos(eo) * math.cos(ep) * math.sin(da / 2)**2
    return math.degrees(2 * math.asin(math.sqrt(max(0.0, min(1.0, hav)))))


def pass_deletion_sensitivity(rows: list[dict]) -> dict:
    """Five fixed-sample deletion diagnostics; NOT out-of-sample predictive CV.

    Excluding a pass recomputes a descriptive aggregate; there is no refit,
    held-out forecast, independence claim, or uncertainty coverage estimate.
    """
    per = {}
    for row in rows:
        separation = sky_separation_deg(*(float(row[k]) for k in
            ("az_obs", "az_pred", "el_obs", "el_pred")))
        per.setdefault(row["pass_id"], []).append(separation**2)
    if set(per) != set(COUNTS) or any(len(per[k]) != COUNTS[k] for k in COUNTS):
        raise ValueError("pass-membership contract changed")
    all_count = sum(len(x) for x in per.values())
    total_sq = sum(sum(x) for x in per.values())
    deleted = []
    for pass_id in COUNTS:
        remaining_n = all_count - len(per[pass_id])
        remaining_sq = total_sq - sum(per[pass_id])
        deleted.append({"excluded_pass_id": pass_id,
                        "remaining_rows": remaining_n,
                        "remaining_passes": len(COUNTS) - 1,
                        "descriptive_los_rms_deg": round(math.sqrt(remaining_sq / remaining_n), 7)})
    vals = [r["descriptive_los_rms_deg"] for r in deleted]
    return {
        "classification": "PASS_BLOCK_DELETION_SENSITIVITY_NOT_CROSS_VALIDATION",
        "unit_of_deletion": "complete_tracking_pass",
        "refits_prediction_model": False,
        "prospective_or_blind_holdout": False,
        "estimates_population_uncertainty": False,
        "assumes_independent_passes": False,
        "passes": deleted,
        "min_deletion_rms_deg": min(vals),
        "max_deletion_rms_deg": max(vals),
        "rms_range_deg": round(max(vals)-min(vals), 7),
    }


def summarize(rows: list[dict]) -> dict:
    per_pass = []
    all_separations = []
    for pass_id in COUNTS:
        subset = [r for r in rows if r["pass_id"] == pass_id]
        sep = [sky_separation_deg(*(float(r[k]) for k in
               ("az_obs", "az_pred", "el_obs", "el_pred"))) for r in subset]
        all_separations.extend(sep)
        per_pass.append({
            "pass_id": pass_id, "count": len(sep),
            "start_utc": subset[0]["utc"], "end_utc": subset[-1]["utc"],
            "descriptive_los_rms_deg": round(math.sqrt(sum(s*s for s in sep) / len(sep)), 7),
            "descriptive_los_max_deg": round(max(sep), 7),
        })
    return {
        "schema": "conde.historical-prediction-pairs/v1",
        "classification": "EMPIRICAL_COMPARISON_OTHER_SATELLITE_NOT_528_CALIBRATION",
        "source": {
            "paper": "Claus et al., Orbit Determination and Prediction, and Computer Programs",
            "publisher": "Bell System Technical Journal",
            "publication_year": 1963,
            "ntrs_id": "19640000981",
            "url": "https://ntrs.nasa.gov/api/citations/19640000981/downloads/19640000981.pdf",
            "pdf_sha256": PDF_SHA256, "pdf_bytes": PDF_BYTES,
            "table": "VII", "pdf_page_index_zero_based": 23,
            "printed_page": 1380,
        },
        "observations": {"object": "Telstar 1 (1962)", "site": "Andover",
                         "kind": "published observed versus predicted azimuth/elevation",
                         "row_count": len(rows), "pass_count": len(COUNTS),
                         "csv_sha256": CSV_SHA256, "units": "degrees"},
        "method": {
            "angle": "great-circle angular separation of observed and predicted sightlines",
            "predictions": "paper reports five-day lookahead from preceding five days of tracking",
            "individual_prediction_horizon": None,
            "fit_epochs_and_raw_tracking": None,
            "print_resolution_deg": "0.01",
            "rounding_rule_verified": False,
            "measurements_are_independent": False,
            "rows_are_independent_realizations": False,
        },
        "passes": per_pass,
        "pass_deletion_sensitivity": pass_deletion_sensitivity(rows),
        "all_rows_descriptive_los_rms_deg": round(
            math.sqrt(sum(s*s for s in all_separations)/len(all_separations)), 7),
        "all_rows_descriptive_los_max_deg": round(max(all_separations), 7),
        "eligibility": {
            "empirical_prediction_residuals_for_telstar": True,
            "independent_tracking_network_from_norad_528": None,
            "sensor_sigma_for_norad_528": None,
            "orbit_covariance_for_norad_528": None,
            "terminal_timing_distribution_for_norad_528": None,
            "calibrated_historical_528_likelihood": False,
            "historic_528_mcmc": "NOT_RUN",
            "active_conde_geographic_constraint": False,
        },
        "limits": [
            "Single named tracking site; five passes and 38 serial measurements are not 38 independent trials",
            "Retrospective facsimile inspection; not a newly blind prospective holdout",
            "Print rounding, individual forecast horizons and tracking biases are not calibrated here",
            "Telstar 1962 does not transfer instrument-specific accuracy to NORAD 528",
        ],
    }


def verify_pdf(path: Path) -> None:
    blob = path.read_bytes()
    if len(blob) != PDF_BYTES or sha(blob) != PDF_SHA256:
        raise ValueError("NASA source PDF custody failed")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-pdf", type=Path)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    if args.source_pdf:
        verify_pdf(args.source_pdf)
    report = (json.dumps(summarize(load_rows()), sort_keys=True, indent=2)+"\n").encode()
    if args.check:
        if not OUT.is_file() or OUT.read_bytes() != report:
            raise SystemExit("descriptive historical benchmark certificate drift")
    else:
        OUT.write_bytes(report)
        print(report.decode(), end="")


if __name__ == "__main__":
    main()
