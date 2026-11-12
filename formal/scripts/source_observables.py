#!/usr/bin/env python3
"""C179/C151 SI observables from a pinned primary/secondary-source matrix.

This is a *small, standalone extraction* from Polvo's larger draft #17.
No external packages, no physical fit, no geographic propagation to Conde.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

MATRIX_BLOB_SHA1 = "a7978c3a75a153b16ab70118a92c434bba674cb7"
TLE_SOURCE = "https://www.itau.magnetic-declination.com/satellite/?s=528"
RECIFE_SOURCE = "https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip"
WIND_LEVELS_M_APPROX = {850: 1560, 700: 3200, 500: 5900, 300: 9700, 250: 11000}
WIND_RE = re.compile(r"(\d{3}) hPa\s+(\d{1,3})°/(\d+)m·s⁻¹")
MU_KM3_S2 = 398600.4418
R_E_KM = 6378.137


def pinned_rows(path: Path) -> dict[str, str]:
    data = path.read_bytes()
    raw = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    if hashlib.sha1(raw).hexdigest() != MATRIX_BLOB_SHA1:
        raise ValueError("matrix changed: revalidate sources, do not silently recalculate")
    rows: dict[str, list[str]] = {"C151": [], "C179": []}
    for line in data.decode("utf-8").splitlines():
        for name in rows:
            if re.match(rf"^\|\s*\*\*{name}\*\*\s*\|", line):
                rows[name].append(line)
    if any(len(v) != 1 for v in rows.values()):
        raise ValueError("missing or duplicated occurrence of C151/C179")
    return {name: found[0] for name, found in rows.items()}


def entry_orbit(c179: str) -> dict:
    def number(label: str, pattern: str) -> float:
        m = re.search(pattern, c179)
        if not m:
            raise ValueError("missing sourced 528 field " + label)
        return float(m.group(1).replace(",", "."))

    # Values are the transcribed AFSPC-mirror values in the frozen matrix.
    n = number("mean motion", r"movimento médio\s+([\d,]+) rev/dia")
    inclination = number("inclination", r"inclinação\s+([\d,]+)°")
    raan = number("RAAN", r"nó\s+([\d,]+)°")
    eccentricity = number("eccentricity", r"excentricidade\s+([\d,]+)")
    if not 0 <= raan < 360 or not 0 <= eccentricity < 1 or not 0 <= inclination <= 180 or n <= 0:
        raise ValueError("incompatible transcribed orbital elements")
    n_rads = 2 * math.pi * n / 86400
    semimajor_km = (MU_KM3_S2 / (n_rads * n_rads)) ** (1 / 3)
    perigee_km = semimajor_km * (1 - eccentricity) - R_E_KM
    j2 = 1.08262668e-3
    j2_raan_deg_day = (-1.5 * j2 * n_rads *
                       (R_E_KM / (semimajor_km * (1 - eccentricity ** 2))) ** 2 *
                       math.cos(math.radians(inclination)) * 86400 * 180 / math.pi)
    return {
        "source_id": "C179#1", "source_type": "AFSPC_SECONDARY_MIRROR",
        "source_url": TLE_SOURCE, "epoch_utc_to_seconds": "1963-10-27T14:40:16Z",
        "mean_motion_rev_day": n, "inclination_deg": inclination,
        "raan_deg_printed": raan, "eccentricity": eccentricity,
        "derived_mean_motion_rad_s": n_rads,
        "derived_semimajor_axis_km_kepler_proxy": semimajor_km,
        "derived_perigee_altitude_km_kepler_proxy": perigee_km,
        "derived_j2_raan_rate_deg_day_first_order": j2_raan_deg_day,
        "model": "TLE_MEAN_ELEMENTS_AS_KEPLER_PROXY_NOT_OSCULATING",
    }


def winds(recife_c151: str) -> list[dict]:
    observed: list[dict] = []
    for p, direction, speed in WIND_RE.findall(recife_c151):
        p, direction, speed = int(p), int(direction), int(speed)
        if p not in WIND_LEVELS_M_APPROX or not 0 <= direction <= 360:
            raise ValueError("unexpected level/direction")
        azimuth_from = math.radians(direction)
        observed.append({
            "pressure_hpa": p, "pressure_pa": p * 100,
            "approx_altitude_m": WIND_LEVELS_M_APPROX[p],
            "direction_from_deg": direction, "speed_m_s": speed,
            "derived_east_m_s": -speed * math.sin(azimuth_from),
            "derived_north_m_s": -speed * math.cos(azimuth_from),
            "source_id": "C151#1",
        })
    if [w["pressure_hpa"] for w in observed] != [850, 700, 500, 300, 250]:
        raise ValueError("missing or changed NOAA IGRA Recife wind levels")
    return observed


def illustrative_descent(wind: list[dict], assumed_downward_m_s: float) -> dict:
    if not math.isfinite(assumed_downward_m_s) or assumed_downward_m_s <= 0:
        raise ValueError("assumed vertical descent must be finite positive m/s")
    ordered = sorted(wind, key=lambda w: w["approx_altitude_m"])
    east = north = seconds = 0.0
    for low, high in zip(ordered, ordered[1:]):
        dt = (high["approx_altitude_m"] - low["approx_altitude_m"]) / assumed_downward_m_s
        seconds += dt
        east += 0.5 * (low["derived_east_m_s"] + high["derived_east_m_s"]) * dt
        north += 0.5 * (low["derived_north_m_s"] + high["derived_north_m_s"]) * dt
    return {
        "assumed_descent_m_s_NOT_OBSERVED": assumed_downward_m_s,
        "sampled_altitude_m_approx": [ordered[0]["approx_altitude_m"],
                                     ordered[-1]["approx_altitude_m"]],
        "derived_time_s": seconds, "derived_east_m": east, "derived_north_m": north,
        "derived_magnitude_m": math.hypot(east, north),
        "status": "RECIFE_WIND_CONDITIONAL_SENSITIVITY_NOT_CONDE_NOT_GROUND",
    }


def crosswalk(matrix: Path, assumed_downward_m_s: float) -> dict:
    rows = pinned_rows(matrix)
    w = winds(rows["C151"])
    return {
        "schema": "conde.source-observables/v1",
        "matrix_git_blob_sha1": MATRIX_BLOB_SHA1,
        "orbital": entry_orbit(rows["C179"]),
        "recife_nominal_1963_11_08_12UTC": {
            "source_id": "C151#1",
            "source_type": "NOAA_NCEI_IGRA_NCDC6301_ONE_STATION",
            "source_url": RECIFE_SOURCE,
            "nominal_utc": "1963-11-08T12:00:00Z",
            "actual_balloon_release_time": "NOT_RECORDED",
            "winds": w,
        },
        "illustrative_only": illustrative_descent(w, assumed_downward_m_s),
        "interpretation": "No geolocated 1963 Conde weather; no NORAD 528 domain reduction or holdout run.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--matrix", type=Path, required=True)
    p.add_argument("--assumed-descent-mps", type=float, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = crosswalk(args.matrix, args.assumed_descent_mps)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "source_ids": ["C179#1", "C151#1"],
        "weather": "RECIFE_ONLY", "historical_domain_reduction": "NOT_RUN",
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
