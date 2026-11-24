#!/usr/bin/env python3
"""Replay date sensitivity and observer geometry for the CORONA 1005 control."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import sys

import pyarrow as pa
from pyarrow.parquet import read_table
from sgp4.api import Satrec, WGS72, jday

from c241_637_regime_holdout import digest
from c241_king_hele_day_holdout import evaluate, strict_training

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "formal" / "scripts"))
from check_528_optical_visibility_oct_nov_1963 import gmst_rad, station_ecef

SOURCE_SHA = "bf86a12ff26af0cd56e712e1d5ac80036766b1174b42f86bc0481efd90c592e4"
SOURCE_URL = (
    "https://huggingface.co/datasets/oxzoid/space-track-tle-history"
    "/resolve/main/data/tle_1964.parquet"
)
NORAD = 796
DAY = datetime(1964, 5, 26, tzinfo=timezone.utc)
CLOCKS = {
    "CIA_0006_IF_GMT": DAY + timedelta(minutes=6),
    "MOLCZAN_0409_UTC_REFERENCE_EVENT_UNVERIFIED": DAY + timedelta(hours=4, minutes=9),
    "CIA_0006_IF_VENEZUELAN_CIVIL": DAY + timedelta(hours=4, minutes=36),
}
SITE = (10.64232, -71.61089, 0.002)
LEAD_DAYS = (14, 10, 6, 3, 1)


def read_epochs(path: Path) -> list[dict]:
    if digest(path) != SOURCE_SHA:
        raise ValueError("1964 Parquet SHA-256 mismatch")
    columns = ["norad_id", "epoch", "mean_motion", "eccentricity", "inclination",
               "raan", "arg_perigee", "mean_anomaly", "bstar", "intl_designator"]
    table = read_table(path, columns=columns, filters=[("norad_id", "=", NORAD)])
    if table.schema.field("epoch").type != pa.timestamp("us", tz="UTC"):
        raise ValueError("unexpected epoch type or time zone")
    # Cast only after checking UTC, for Windows environments without tzdata.
    table = table.set_column(1, "epoch", table["epoch"].cast(pa.timestamp("us")))
    rows = table.sort_by("epoch").to_pylist()
    if len(rows) != 11 or {r["intl_designator"] for r in rows} != {"64022  A"}:
        raise ValueError("unexpected CORONA 1005 row count or designator")
    for index, row in enumerate(rows, start=1):
        row["epoch"] = row["epoch"].replace(tzinfo=timezone.utc)
        if not datetime(1964, 4, 27, tzinfo=timezone.utc) <= row["epoch"] < DAY:
            raise ValueError("epoch outside pre-event mission span")
        row["source_row"] = index  # ordinal within the sorted NORAD 796 subset
    strict_training(rows, DAY)
    return rows


def jd_parts(t: datetime) -> tuple[float, float]:
    return jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond / 1e6)


def clock_geometry(row: dict) -> dict:
    epoch_jd, epoch_fraction = jd_parts(row["epoch"])
    sat = Satrec()
    sat.sgp4init(
        WGS72, "i", NORAD, (epoch_jd - 2433281.5) + epoch_fraction,
        row["bstar"], 0.0, 0.0, row["eccentricity"], math.radians(row["arg_perigee"]),
        math.radians(row["inclination"]), math.radians(row["mean_anomaly"]),
        row["mean_motion"] * math.tau / 1440, math.radians(row["raan"]),
    )
    observer, enu = station_ecef(*SITE)
    results = {}
    for clock, instant in CLOCKS.items():
        jd, fraction = jd_parts(instant)
        error, position, _ = sat.sgp4(jd, fraction)
        sample = {"utc": instant.isoformat(), "sgp4_error": error}
        if error == 0:
            theta = gmst_rad(jd + fraction)
            c, s = math.cos(theta), math.sin(theta)
            x, y, z = position
            ecef = (c*x + s*y, -s*x + c*y, z)
            displacement = [value - origin for value, origin in zip(ecef, observer)]
            east, north, up = enu @ displacement
            sample.update(
                elevation_deg=round(math.degrees(math.atan2(up, math.hypot(east, north))), 3),
                slant_range_km=round(math.hypot(east, north, up), 1),
            )
        results[clock] = sample
    return results


def report(rows: list[dict]) -> dict:
    trials = []
    for lead in LEAD_DAYS:
        cutoff = DAY - timedelta(days=lead)
        training = strict_training(rows, cutoff)
        trial = evaluate(rows, cutoff.isoformat(), DAY.date().isoformat(), NORAD)
        trial["day_lead_hours"] = lead * 24
        trial["clock_geometry"] = clock_geometry(training[-1])
        trials.append(trial)
    return {
        "schema": "conde.c241-maracaibo-1005-retrospective/v1",
        "source": {"url": SOURCE_URL, "sha256": SOURCE_SHA, "catalogue_epochs": len(rows),
                   "bstar_all_zero": all(r["bstar"] == 0 for r in rows),
                   "epoch_does_not_establish_publication_time": True,
                   "source_row_definition": "1-based ordinal within sorted NORAD 796 rows"},
        "site": {"gazetteer": "https://www.geonames.org/3633009",
                 "latitude_deg": SITE[0], "longitude_deg": SITE[1], "altitude_km": SITE[2]},
        "assumptions": {"retrospective": True, "cutoff_is_exclusive": True,
                        "clock_branches_are_unverified": True, "earth_rotation_ut1_approx_utc": True,
                        "geometric_line_of_sight_only": True, "state_is_vehicle_not_fragment": True},
        "trials": trials,
        "inference": {"calibrated_terminal_holdouts": 0, "terminal_time_sigma_hours": None,
                      "historical_prediction_error": None, "landing_location_error": None},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parquet", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = report(read_epochs(args.parquet))
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
