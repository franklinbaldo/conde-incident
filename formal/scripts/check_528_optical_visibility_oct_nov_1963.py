#!/usr/bin/env python3
"""
Reproducible exploratory SGP4 optical visibility and B* decay-sensitivity check
for NORAD 528 (1963-003B) between 1963-10-27 14:40:16 UTC and 1963-11-08 23:59:59 UTC.

Uses the secondary mirror TLE in research/tle_custody/mirror_528_1963-10-27.tle
(RAAN 198.5261 deg at epoch 63300.61129783, B* = 0).

Caveat: SGP4 extrapolated ~12 days does not determine terminal entry time or location;
this check evaluates macroscopic solar-illumination geometry and along-track sensitivity
conditional on the secondary TLE plane (RAAN 198.5261 deg).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from sgp4.api import Satrec, jday

REPO_ROOT = Path(__file__).resolve().parents[2]
TLE_PATH = REPO_ROOT / "research" / "tle_custody" / "mirror_528_1963-10-27.tle"
OUT_JSON = REPO_ROOT / "research" / "constraints" / "optical_visibility_528_19631027_1108.json"

RE_KM = 6378.137
F_WGS84 = 1.0 / 298.257223563
E2_WGS84 = F_WGS84 * (2.0 - F_WGS84)

STATIONS = {
    "Durban": {"lat_deg": -29.88, "lon_deg": 31.02, "alt_km": 0.05},
    "Slough": {"lat_deg": 51.48, "lon_deg": -0.56, "alt_km": 0.02},
    "Baja": {"lat_deg": 46.18, "lon_deg": 18.96, "alt_km": 0.10},
    "Meudon": {"lat_deg": 48.80, "lon_deg": 2.23, "alt_km": 0.16},
}


def tle_checksum(line: str) -> int:
    total = 0
    for ch in line[:68]:
        if ch.isdigit():
            total += int(ch)
        elif ch == "-":
            total += 1
    return total % 10


def format_bstar_field(bstar: float) -> str:
    if abs(bstar) < 1e-12:
        return "+00000-0"
    sign = "-" if bstar < 0 else " "
    val = abs(bstar)
    exp = int(math.floor(math.log10(val))) + 1
    mant = int(round(val / (10.0 ** exp) * 1e5))
    if mant >= 100000:
        mant //= 10
        exp += 1
    exp_sign = "+" if exp >= 0 else "-"
    return f"{sign}{mant:05d}{exp_sign}{abs(exp):1d}"


def make_sat_with_bstar(line1: str, line2: str, bstar: float | None) -> tuple[Satrec, str]:
    if bstar is None:
        return Satrec.twoline2rv(line1, line2), line1
    b_field = format_bstar_field(bstar)
    new_l1 = line1[:53] + b_field + line1[61:68]
    new_l1 = new_l1 + str(tle_checksum(new_l1))
    return Satrec.twoline2rv(new_l1, line2), new_l1


def gmst_rad(jd_ut1: float) -> float:
    t_cent = (jd_ut1 - 2451545.0) / 36525.0
    gmst_sec = (
        67310.54841
        + (876600.0 * 3600.0 + 8640184.812866) * t_cent
        + 0.093104 * t_cent * t_cent
        - 6.2e-6 * t_cent * t_cent * t_cent
    )
    return math.radians((gmst_sec / 240.0) % 360.0)


def sun_eci_unit(jd: float) -> tuple[np.ndarray, float, float]:
    n = jd - 2451545.0
    mean_lon = (280.460 + 0.9856474 * n) % 360.0
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = math.radians(mean_lon + 1.915 * math.sin(g) + 0.020 * math.sin(2.0 * g))
    eps = math.radians(23.439 - 0.0000004 * n)
    x = math.cos(lam)
    y = math.cos(eps) * math.sin(lam)
    z = math.sin(eps) * math.sin(lam)
    ra = math.degrees(math.atan2(y, x)) % 360.0
    dec = math.degrees(math.asin(z))
    return np.array([x, y, z]), ra, dec


def station_ecef(lat_deg: float, lon_deg: float, alt_km: float) -> tuple[np.ndarray, np.ndarray]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    sin_lat, cos_lat = math.sin(lat), math.cos(lat)
    sin_lon, cos_lon = math.sin(lon), math.cos(lon)
    n_rad = RE_KM / math.sqrt(1.0 - E2_WGS84 * sin_lat * sin_lat)
    r_ecef = np.array([
        (n_rad + alt_km) * cos_lat * cos_lon,
        (n_rad + alt_km) * cos_lat * sin_lon,
        (n_rad * (1.0 - E2_WGS84) + alt_km) * sin_lat,
    ])
    r_enu = np.array([
        [-sin_lon, cos_lon, 0.0],
        [-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat],
        [cos_lat * cos_lon, cos_lat * sin_lon, sin_lat],
    ])
    return r_ecef, r_enu


def is_sunlit(r_eci: np.ndarray, s_hat: np.ndarray) -> bool:
    proj = float(np.dot(r_eci, s_hat))
    if proj > 0.0:
        return True
    perp = r_eci - proj * s_hat
    return float(np.linalg.norm(perp)) > RE_KM


def decay_time_utc(line1: str, line2: str, bstar: float, t_start: datetime, max_days: float = 16.0) -> datetime | None:
    sat, _ = make_sat_with_bstar(line1, line2, bstar)
    steps = int(max_days * 24 * 60)
    for m in range(0, steps + 1, 5):
        t = t_start + timedelta(minutes=m)
        jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond * 1e-6)
        err, r, _ = sat.sgp4(jd, fr)
        if err != 0 or (math.sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2) - RE_KM) < 120.0:
            for m2 in range(max(0, m - 5), m + 1):
                t2 = t_start + timedelta(minutes=m2)
                jd2, fr2 = jday(t2.year, t2.month, t2.day, t2.hour, t2.minute, t2.second)
                e2, r2, _ = sat.sgp4(jd2, fr2)
                if e2 != 0 or (math.sqrt(r2[0] ** 2 + r2[1] ** 2 + r2[2] ** 2) - RE_KM) < 120.0:
                    return t2
            return t
    return None


def solve_bstar_for_decay(line1: str, line2: str, t_start: datetime, t_target: datetime) -> tuple[float, datetime | None]:
    lo, hi = 1e-5, 0.05
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        td = decay_time_utc(line1, line2, mid, t_start)
        if td is None or td > t_target:
            lo = mid
        else:
            hi = mid
    b_sol = 0.5 * (lo + hi)
    return b_sol, decay_time_utc(line1, line2, b_sol, t_start)


def scan_station_visibility(sat: Satrec, t_start: datetime, t_end: datetime, step_s: int = 10) -> dict:
    st_geom = {
        name: station_ecef(cfg["lat_deg"], cfg["lon_deg"], cfg["alt_km"])
        for name, cfg in STATIONS.items()
    }
    n_steps = int((t_end - t_start).total_seconds() // step_s) + 1
    active = {name: None for name in STATIONS}
    passes = {name: [] for name in STATIONS}

    for k in range(n_steps):
        t = t_start + timedelta(seconds=k * step_s)
        jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond * 1e-6)
        err, r, _ = sat.sgp4(jd, fr)
        if err != 0:
            break
        r_eci = np.array(r, dtype=float)
        alt_km = float(np.linalg.norm(r_eci)) - RE_KM
        if alt_km < 120.0:
            break

        theta = gmst_rad(jd + fr)
        c, s = math.cos(theta), math.sin(theta)
        r_ecef = np.array([c * r_eci[0] + s * r_eci[1], -s * r_eci[0] + c * r_eci[1], r_eci[2]])

        s_hat_eci, _, _ = sun_eci_unit(jd + fr)
        s_hat_ecef = np.array([
            c * s_hat_eci[0] + s * s_hat_eci[1],
            -s * s_hat_eci[0] + c * s_hat_eci[1],
            s_hat_eci[2],
        ])
        sunlit = is_sunlit(r_eci, s_hat_eci)

        for name, (st_r, r_enu) in st_geom.items():
            enu = r_enu @ (r_ecef - st_r)
            rng = float(np.linalg.norm(enu))
            el_deg = math.degrees(math.asin(enu[2] / rng))
            if el_deg >= 10.0:
                sun_enu = r_enu @ s_hat_ecef
                sun_el = math.degrees(math.asin(max(-1.0, min(1.0, float(sun_enu[2])))))
                cur = active[name]
                if cur is None:
                    cur = {
                        "dark6": False,
                        "vis6": False,
                        "vis0": False,
                        "sunlit": False,
                        "min_sun_el_when_sunlit": 999.0,
                    }
                    active[name] = cur
                if sun_el <= -6.0:
                    cur["dark6"] = True
                if sunlit:
                    cur["sunlit"] = True
                    if sun_el < cur["min_sun_el_when_sunlit"]:
                        cur["min_sun_el_when_sunlit"] = sun_el
                    if sun_el <= 0.0:
                        cur["vis0"] = True
                    if sun_el <= -6.0:
                        cur["vis6"] = True
            elif active[name] is not None:
                passes[name].append(active[name])
                active[name] = None

    for name in STATIONS:
        if active[name] is not None:
            passes[name].append(active[name])

    summary = {}
    for name, ps in passes.items():
        mins = [p["min_sun_el_when_sunlit"] for p in ps if p["sunlit"]]
        summary[name] = {
            "passes_el_ge_10": len(ps),
            "passes_dark_sun_le_minus6": sum(1 for p in ps if p["dark6"]),
            "visible_passes_sun_le_minus6": sum(1 for p in ps if p["vis6"]),
            "visible_passes_sun_le_0": sum(1 for p in ps if p["vis0"]),
            "min_sun_el_deg_when_sunlit": round(min(mins), 2) if mins else None,
        }
    return summary


def arg_lat_rad(r: tuple[float, float, float], v: tuple[float, float, float]) -> float:
    r_vec = np.array(r, dtype=float)
    v_vec = np.array(v, dtype=float)
    h_vec = np.cross(r_vec, v_vec)
    n_vec = np.cross(np.array([0.0, 0.0, 1.0]), h_vec)
    n_hat = n_vec / np.linalg.norm(n_vec)
    r_hat = r_vec / np.linalg.norm(r_vec)
    q_hat = np.cross(h_vec / np.linalg.norm(h_vec), n_hat)
    return math.atan2(float(np.dot(r_hat, q_hat)), float(np.dot(r_hat, n_hat)))


def compute_along_track_shift(sat_nom: Satrec, sat_b2: Satrec, t_start: datetime) -> list[dict]:
    sample_minutes = {1440, 2880, 5760, 8640, 11520, 14400, 15840, 17040}
    u_nom_prev = None
    u_b2_prev = None
    cum_nom = 0.0
    cum_b2 = 0.0
    rows = []

    for m in range(0, 12 * 1440, 5):
        t = t_start + timedelta(minutes=m)
        jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
        en, rn, vn = sat_nom.sgp4(jd, fr)
        eb, rb, vb = sat_b2.sgp4(jd, fr)
        if en != 0 or eb != 0:
            break
        un = arg_lat_rad(rn, vn)
        ub = arg_lat_rad(rb, vb)
        if u_nom_prev is not None:
            cum_nom += (un - u_nom_prev + math.pi) % (2.0 * math.pi) - math.pi
            cum_b2 += (ub - u_b2_prev + math.pi) % (2.0 * math.pi) - math.pi
        u_nom_prev, u_b2_prev = un, ub
        if m in sample_minutes:
            drev = (cum_b2 - cum_nom) / (2.0 * math.pi)
            dt_min = drev * (1440.0 / 15.8)
            alt_b2 = float(np.linalg.norm(np.array(rb))) - RE_KM
            rows.append({
                "days_since_epoch": round(m / 1440.0, 2),
                "utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "b2_alt_km": round(alt_b2, 1),
                "phase_lead_revs": round(drev, 3),
                "approx_dt_min": round(dt_min, 1),
            })
    return rows


def run_analysis() -> dict:
    raw_bytes = TLE_PATH.read_bytes()
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    lines = [ln.strip() for ln in raw_bytes.decode("utf-8").splitlines() if ln.strip()]
    l1, l2 = lines[0], lines[1]

    t_epoch = datetime(1963, 1, 1, tzinfo=timezone.utc) + timedelta(days=300 - 1 + 0.61129783)
    t_end = datetime(1963, 11, 8, 23, 59, 59, tzinfo=timezone.utc)
    sat_nom, _ = make_sat_with_bstar(l1, l2, None)

    plane_vs_sun = []
    for d in range(0, 13):
        t = t_epoch + timedelta(days=d)
        if t > t_end:
            break
        jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
        err, r, v = sat_nom.sgp4(jd, fr)
        if err != 0:
            break
        r_v, v_v = np.array(r), np.array(v)
        h_v = np.cross(r_v, v_v)
        raan = math.degrees(math.atan2(h_v[0], -h_v[1])) % 360.0
        _, sra, sdec = sun_eci_unit(jd + fr)
        diff = ((raan - sra + 180.0) % 360.0) - 180.0
        plane_vs_sun.append({
            "utc": t.strftime("%Y-%m-%dT%H:%MZ"),
            "alt_km": round(float(np.linalg.norm(r_v)) - RE_KM, 1),
            "raan_deg": round(raan, 2),
            "sun_ra_deg": round(sra, 2),
            "raan_minus_sun_ra_deg": round(diff, 2),
            "sun_dec_deg": round(sdec, 2),
        })

    targets = {
        "B1_early_Nov8": datetime(1963, 11, 8, 0, 0, tzinfo=timezone.utc),
        "B2_mid_Nov8": datetime(1963, 11, 8, 12, 0, tzinfo=timezone.utc),
        "B3_late_Nov8": datetime(1963, 11, 8, 23, 59, tzinfo=timezone.utc),
    }
    scenarios = {
        "Nominal_Bstar_0": {
            "bstar": 0.0,
            "tle_bstar_field": "+00000-0",
            "sgp4_decay_utc": None,
            "stations": scan_station_visibility(sat_nom, t_epoch, t_end, step_s=10),
        }
    }
    sat_b2 = None
    for label, targ in targets.items():
        b_val, t_dec = solve_bstar_for_decay(l1, l2, t_epoch, targ)
        sat_b, _ = make_sat_with_bstar(l1, l2, b_val)
        if label == "B2_mid_Nov8":
            sat_b2 = sat_b
        scenarios[label] = {
            "bstar": round(b_val, 6),
            "tle_bstar_field": format_bstar_field(b_val),
            "sgp4_decay_utc": t_dec.strftime("%Y-%m-%dT%H:%M:%SZ") if t_dec else None,
            "stations": scan_station_visibility(sat_b, t_epoch, t_end, step_s=10),
        }

    along_track = compute_along_track_shift(sat_nom, sat_b2, t_epoch)

    return {
        "experiment_id": "EXP-OPTICAL-VISIBILITY-528-19631027-1108",
        "verification_status": "EXPLORATORY_SGP4_GEOMETRIC_CHECK",
        "epistemic_scope": (
            "Conditional on secondary mirror TLE mirror_528_1963-10-27.tle (RAAN 198.5261 deg). "
            "SGP4 extrapolated 12 days does not determine terminal entry time or location."
        ),
        "tle_source": {
            "path": "research/tle_custody/mirror_528_1963-10-27.tle",
            "sha256": sha256,
            "epoch_utc": t_epoch.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "line1": l1,
            "line2": l2,
        },
        "window_utc": {
            "start": t_epoch.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": t_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "step_seconds": 10,
            "elevation_threshold_deg": 10.0,
            "twilight_thresholds_deg": [-6.0, 0.0],
        },
        "stations": STATIONS,
        "orbital_plane_vs_sun_nominal": plane_vs_sun,
        "scenarios": scenarios,
        "along_track_lead_B2_vs_nominal": along_track,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check NORAD 528 optical visibility (27 Oct - 8 Nov 1963).")
    parser.add_argument("--write", action="store_true", help="Write JSON output to research/constraints/.")
    args = parser.parse_args()

    result = run_analysis()
    if args.write:
        OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {OUT_JSON} ({OUT_JSON.stat().st_size} bytes)")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
