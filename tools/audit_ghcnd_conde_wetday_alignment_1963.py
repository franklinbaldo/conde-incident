"""Pinned, source-audited wet-day date-alignment sensitivity (Conde, 1963).

Only tests comparability of *archival daily labels* across nearby gauges.
It does not infer the instrument observation hour, weather over the
incident site, or any trajectory/reentry parameter.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
import math
from pathlib import Path

import audit_ghcnd_conde_rain_1963 as original

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research/meteorology/ghcnd_conde_wetday_alignment_1963.json"
LAGS = (-2, -1, 0, 1, 2)
CONDE = "BR048346820"


def read_year(data: bytes, station_id: str):
    """One 1963 PRCP row per month; preserve QC failures separately."""
    rows, days, rejected = set(), {}, []
    for raw in data.decode("ascii").splitlines():
        if len(raw) != 269:
            raise ValueError("not fixed-width .dly")
        if raw[:11] != station_id:
            raise ValueError("station mismatch")
        if raw[11:15] != "1963" or raw[17:21] != "PRCP":
            continue
        month = int(raw[15:17])
        if month in rows:
            raise ValueError("duplicate PRCP month")
        rows.add(month)
        for idx in range(31):
            item = raw[21+8*idx:29+8*idx]
            try:
                when = date(1963, month, idx+1)
            except ValueError:
                if int(item[:5]) != -9999:
                    raise ValueError("data on nonexistent calendar date")
                continue
            value = int(item[:5])
            mflag, qflag, sflag = item[5:]
            if value == -9999:
                continue
            if value < 0 or sflag != "I":
                raise ValueError("invalid non-missing value or unexpected source")
            if mflag.strip():
                raise ValueError("unhandled measurement convention")
            if qflag.strip():
                rejected.append({"date": when.isoformat(), "raw_eight_chars": item, "quality_flag": qflag})
                continue
            if when in days:
                raise ValueError("duplicate date")
            days[when] = value / 10
    if not rows:
        raise ValueError("1963 PRCP unavailable")
    return days, rejected


def phi(a, b):
    """Matthews/phi coefficient for two binary wet-day vectors."""
    if not a or len(a) != len(b):
        raise ValueError("aligned nonempty vectors required")
    tp = sum(x and y for x, y in zip(a, b))
    fn = sum(x and not y for x, y in zip(a, b))
    fp = sum(not x and y for x, y in zip(a, b))
    tn = len(a) - tp - fn - fp
    denom = math.sqrt((tp+fn)*(tp+fp)*(tn+fn)*(tn+fp))
    return {"joint_wet_days": tp, "conde_only_wet": fn, "peer_only_wet": fp,
            "joint_dry_days": tn,
            "phi": round((tp*tn-fn*fp)/denom, 4) if denom else None}


def lag_scan(conde, peer, dates, lag_set=LAGS):
    """Same reference dates for every shift to avoid support cherry-picking."""
    common = sorted(t for t in dates if t in conde and
                    all(t + timedelta(days=k) in peer for k in lag_set))
    if not common:
        return {"overlap_days_fixed": 0, "lag_results": [], "strongest_lag_days": None}
    a = [conde[t] > 0 for t in common]
    results = []
    for lag in lag_set:
        b = [peer[t+timedelta(days=lag)] > 0 for t in common]
        results.append({"peer_label_minus_conde_label_days": lag, **phi(a, b)})
    valid = [x for x in results if x["phi"] is not None]
    # Descriptive maximum only: no inference that a gauge clock is offset.
    best = sorted(valid, key=lambda x: (-x["phi"], abs(x["peer_label_minus_conde_label_days"]),
                                        x["peer_label_minus_conde_label_days"]))[0] if valid else None
    return {"overlap_days_fixed": len(common), "lag_results": results,
            "strongest_lag_days": best["peer_label_minus_conde_label_days"] if best else None}


def audit(source_dir: Path):
    archival = json.loads((ROOT/"research/meteorology/ghcnd_conde_precip_19631107_09.json").read_text())
    stations = {s["id"]: s for s in archival["stations"]}
    if set(stations) != set(original.IDS):
        raise ValueError("archival baseline differs from pinned original sources")
    series, exceptions = {}, {}
    for sid in original.IDS:
        data = original.checked_bytes(source_dir, sid+".dly")  # SHA-256 of entire original file
        if stations[sid]["whole_file_sha256"] != original.SHA[sid+".dly"]:
            raise ValueError("baseline source hash disagreement")
        series[sid], exceptions[sid] = read_year(data, sid)
        for d in (7, 8, 9):
            expected = stations[sid]["daily"][d-7]["precipitation_mm"]
            if series[sid].get(date(1963, 11, d)) != expected:
                raise ValueError("November 7-9 baseline regression")
    conde = series[CONDE]
    comparisons = []
    all_days = sorted(conde)
    for sid in original.IDS:
        if sid == CONDE:
            continue
        peer = series[sid]
        full = lag_scan(conde, peer, all_days)
        first = lag_scan(conde, peer, [d for d in all_days if d.month <= 6])
        second = lag_scan(conde, peer, [d for d in all_days if d.month > 6])
        comparisons.append({
            "station_id": sid, "station": stations[sid]["station"],
            "distance_to_modern_municipality_reference_km": stations[sid]["approx_distance_to_modern_bbox_midpoint_km"],
            "observed_1963_days_after_QC": len(peer),
            "wet_days_after_QC": sum(v > 0 for v in peer.values()),
            "excluded_QC_flagged_days": exceptions[sid],
            "full_year": full,
            "jan_jun": {"overlap_days_fixed": first["overlap_days_fixed"], "strongest_lag_days": first["strongest_lag_days"]},
            "jul_dec": {"overlap_days_fixed": second["overlap_days_fixed"], "strongest_lag_days": second["strongest_lag_days"]},
        })
    comparisons.sort(key=lambda o: (o["distance_to_modern_municipality_reference_km"], o["station_id"]))
    controls = {}
    for d in (8, 13, 14):
        t = date(1963,11,d)
        controls[t.isoformat()] = {
            "reported_positive": [
                {"station_id": sid, "value_mm": series[sid][t]}
                for sid in original.IDS if t in series[sid] and series[sid][t] > 0
            ],
            "present": sum(t in series[sid] for sid in original.IDS),
            "missing": [sid for sid in original.IDS if t not in series[sid]]
        }
    return {
        "schema": "conde.ghcnd-wetday-alignment-1963/v1",
        "id": "MET-GHCND-CONDE-1963-WETDAY-ALIGNMENT-01",
        "baseline_evidence": "MET-GHCND-CONDE-19631107-09-01",
        "source_url": "https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/",
        "fixed_source_digests": {sid+".dly": original.SHA[sid+".dly"] for sid in original.IDS},
        "variable": "binary wet-day PRCP>0 mm; no hour specified",
        "threshold_mm": 0,
        "lag_definition": "peer label at Conde date + lag, NOT physical transport time",
        "lag_candidates_days": list(LAGS),
        "conde": {"station_id": CONDE, "valid_1963_days": len(conde),
                  "positive_1963_days": sum(v > 0 for v in conde.values())},
        "comparisons": comparisons,
        "november_controls": controls,
        "not_proved": {
            "station_independence": None, "actual_1963_observation_clock": None,
            "spatial_rainfall_homogeneity": None, "weather_at_incident_hour": None,
            "wind_or_drag": None, "fall_geography": None,
        },
        "status": "CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = audit(args.source_dir)
    if args.check:
        if json.loads(OUT.read_text()) != result:
            raise SystemExit("FAIL: source-audited output differs from pinned manifest")
        print("PASS: 11 original station SHA, QC filtering, 1963 alignment and fixed support")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
