#!/usr/bin/env python3
"""Reproducible APPLAUSE DR4 1963 sky-plate SGP4 cross-match and Radon streak search.

Supports:
  --scan-tap      Query APPLAUSE DR4 TAP/ADQL across Jan 17 - Nov 8, 1963 solved plates
                  and cross-match NORAD 527, 528, 529, 637 from a verified 1963 TLE parquet.
  --analyze-fits  Run exact Gaia EDR3 WCS projection + Radon/glint streak search with
                  null control on Boyden plate 27600 (000011_1963_h.fits).
  --check-json    Offline verification of the committed JSON artifact invariants.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

RE_KM = 6378.137
TAP_URL = "https://www.plate-archive.org/tap/sync"
PARQUET_SHA256 = "c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09"
PLATE_27600_FITS_URL = (
    "https://www.plate-archive.org/files/DR4/scans/Bamberg-South/000011_1963_h.fits"
)
PLATE_27600_SHA256 = "9526acc0f1f743befdc46502ee8c3c4399815ffee755ff31b48bff4cad959f0c"
DEFAULT_JSON = pathlib.Path("research/constraints/applause_dr4_1963_plate_search.json")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def gmst_rad(jd: float) -> float:
    t = (jd - 2451545.0) / 36525.0
    sec = (
        67310.54841
        + (876600.0 * 3600.0 + 8640184.812866) * t
        + 0.093104 * t * t
        - 6.2e-6 * t * t * t
    )
    return (sec % 86400.0) * (2.0 * math.pi / 86400.0)


def sun_eci_unit(jd: float) -> tuple[float, float, float]:
    n = jd - 2451545.0
    lam_m = math.radians((280.460 + 0.9856474 * n) % 360.0)
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = lam_m + math.radians(1.915 * math.sin(g) + 0.020 * math.sin(2.0 * g))
    eps = math.radians(23.439 - 0.0000004 * n)
    return (math.cos(lam), math.cos(eps) * math.sin(lam), math.sin(eps) * math.sin(lam))


def tap_query(adql: str) -> list[dict[str, str]]:
    data = urllib.parse.urlencode(
        {"REQUEST": "doQuery", "LANG": "ADQL", "QUERY": adql}
    ).encode("utf-8")
    with urllib.request.urlopen(TAP_URL, data=data, timeout=90) as resp:
        xml_bytes = resp.read()
    root = ET.fromstring(xml_bytes)
    ns = {"v": "http://www.ivoa.net/xml/VOTable/v1.3"}
    fields = [f.attrib["name"] for f in root.findall(".//v:FIELD", ns)]
    rows = []
    for tr in root.findall(".//v:TR", ns):
        vals = [td.text or "" for td in tr.findall("v:TD", ns)]
        rows.append(dict(zip(fields, vals)))
    return rows


def scan_tap(parquet_path: pathlib.Path, max_dt_days: float = 35.0) -> dict[str, Any]:
    import numpy as np
    import pyarrow.parquet as pq
    from sgp4.api import Satrec, WGS72, jday

    actual_sha = sha256_file(parquet_path)
    if actual_sha != PARQUET_SHA256:
        raise ValueError(f"Parquet SHA-256 mismatch: {actual_sha} != {PARQUET_SHA256}")

    tbl = pq.read_table(parquet_path).to_pylist()
    sat_models: dict[str, list[tuple[Satrec, float]]] = {
        k: [] for k in ("527", "528", "529", "637")
    }
    for row in tbl:
        nid = str(row["norad_id"])
        if nid not in sat_models:
            continue
        ep = row["epoch"]
        if isinstance(ep, str):
            ep = dt.datetime.fromisoformat(ep)
        jd_e, fr_e = jday(
            ep.year, ep.month, ep.day, ep.hour, ep.minute, ep.second + ep.microsecond / 1e6
        )
        s = Satrec()
        s.sgp4init(
            WGS72,
            "i",
            int(nid),
            (jd_e + fr_e) - 2433281.5,
            float(row.get("bstar") or 0.0),
            float(row.get("mean_motion_dot") or 0.0) * 2.0 * math.pi / 2073600.0,
            0.0,
            float(row["eccentricity"]),
            math.radians(float(row["arg_perigee"])),
            math.radians(float(row["inclination"])),
            math.radians(float(row["mean_anomaly"])),
            float(row["mean_motion"]) * 2.0 * math.pi / 1440.0,
            math.radians(float(row["raan"])),
        )
        sat_models[nid].append((s, jd_e + fr_e))

    adql = """
    SELECT TOP 5000 ex.archive_id, ex.plate_id, ex.exposure_id, ex.ut_start,
           ex.jd_start, ex.jd_end, ex.jd_mid, ex.exptime,
           sol.ra_icrs, sol.dec_icrs, sol.fov1, sol.fov2,
           pl.observatory, pl.ota_aperture, pl.site_latitude, pl.site_longitude
    FROM applause_dr4.exposure AS ex
    JOIN applause_dr4.plate AS pl ON ex.plate_id = pl.plate_id
    JOIN applause_dr4.solution AS sol ON sol.plate_id = ex.plate_id
    WHERE ex.jd_mid BETWEEN 2438046.5 AND 2438342.5
      AND sol.solution_num = 1
    """
    rows = tap_query(adql)
    exposures = []
    by_arch: dict[str, int] = {}
    for r in rows:
        try:
            ra = float(r["ra_icrs"])
            dec = float(r["dec_icrs"])
            fov1 = float(r["fov1"])
            fov2 = float(r["fov2"])
            lat = float(r["site_latitude"])
            lon = float(r["site_longitude"])
            if r["jd_start"] and r["jd_end"]:
                jd_s, jd_e = float(r["jd_start"]), float(r["jd_end"])
            elif r["jd_start"] and r["exptime"]:
                jd_s = float(r["jd_start"])
                jd_e = jd_s + float(r["exptime"]) / 86400.0
            elif r["jd_mid"] and r["exptime"]:
                jm = float(r["jd_mid"])
                half = 0.5 * float(r["exptime"]) / 86400.0
                jd_s, jd_e = jm - half, jm + half
            else:
                continue
        except ValueError:
            continue
        if r["archive_id"] == "208" and lat < 20.0 and lon > 40.0:
            lat, lon = lon, lat
        if jd_e <= jd_s or (jd_e - jd_s) > 0.25:
            continue
        r["_jd_s"], r["_jd_e"] = jd_s, jd_e
        r["_fov_r"] = 0.5 * math.hypot(fov1, fov2) + 0.3
        r["_lat"], r["_lon"] = math.radians(lat), math.radians(lon)
        ra_r, dec_r = math.radians(ra), math.radians(dec)
        r["_pvec"] = np.array(
            [math.cos(dec_r) * math.cos(ra_r), math.cos(dec_r) * math.sin(ra_r), math.sin(dec_r)]
        )
        exposures.append(r)
        by_arch[r["archive_id"]] = by_arch.get(r["archive_id"], 0) + 1

    sunlit_hits: dict[str, list[dict[str, Any]]] = {k: [] for k in sat_models}
    for nid, models in sat_models.items():
        for ex in exposures:
            jd_mid = 0.5 * (ex["_jd_s"] + ex["_jd_e"])
            sat, ep = min(models, key=lambda m: abs(m[1] - jd_mid))
            dt_tle = jd_mid - ep
            if abs(dt_tle) > max_dt_days:
                continue
            dur_s = (ex["_jd_e"] - ex["_jd_s"]) * 86400.0
            jds = np.linspace(ex["_jd_s"], ex["_jd_e"], max(2, int(dur_s / 10.0) + 1))
            clat, slat = math.cos(ex["_lat"]), math.sin(ex["_lat"])
            best = None
            for jd in jds:
                jd_i = math.floor(jd)
                err, r_eci, _ = sat.sgp4(jd_i, jd - jd_i)
                if err != 0:
                    continue
                r_vec = np.array(r_eci)
                th = gmst_rad(float(jd)) + ex["_lon"]
                obs = RE_KM * np.array([clat * math.cos(th), clat * math.sin(th), slat])
                rho = r_vec - obs
                dist = float(np.linalg.norm(rho))
                u = rho / dist
                el = math.degrees(math.asin(max(-1.0, min(1.0, float(np.dot(u, obs / RE_KM))))))
                if el < 5.0:
                    continue
                sep = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(u, ex["_pvec"]))))))
                if sep <= ex["_fov_r"]:
                    sun_u = np.array(sun_eci_unit(float(jd)))
                    proj = float(np.dot(r_vec, sun_u))
                    sunlit = not (
                        proj < 0.0 and (float(np.dot(r_vec, r_vec)) - proj * proj) < RE_KM * RE_KM
                    )
                    if sunlit and (best is None or sep < best["sep_deg"]):
                        best = {
                            "archive_id": ex["archive_id"],
                            "plate_id": ex["plate_id"],
                            "ut_start": ex["ut_start"],
                            "sep_deg": round(sep, 3),
                            "el_deg": round(el, 2),
                            "range_km": round(dist, 1),
                            "dt_tle_days": round(dt_tle, 3),
                        }
            if best is not None:
                sunlit_hits[nid].append(best)
    return {"total_exposures": len(exposures), "by_archive": by_arch, "sunlit_hits": sunlit_hits}


def analyze_plate_27600(fits_path: pathlib.Path) -> dict[str, Any]:
    import numpy as np
    from astropy.io import fits
    from scipy.ndimage import map_coordinates, median_filter

    actual_sha = sha256_file(fits_path)
    if actual_sha != PLATE_27600_SHA256:
        raise ValueError(f"FITS SHA-256 mismatch: {actual_sha} != {PLATE_27600_SHA256}")

    # Exact Gaia EDR3 WCS track endpoints for NORAD 528 (TLE 1963-06-12 00:43:50 UTC)
    x0, y0 = 3519.6, 14555.7
    x1, y1 = 252.2, 322.3
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    vx, vy = -uy, ux

    with fits.open(fits_path, memmap=False) as hdul:
        data = hdul[0].data
    ny, nx = data.shape

    def run_strip(x_shift: float) -> dict[str, float]:
        u_arr = np.arange(800, int(length) - 800, 2, dtype=np.float32)
        v_arr = np.arange(-600, 601, 1, dtype=np.float32)
        u_grid, v_grid = np.meshgrid(u_arr, v_arr, indexing="ij")
        x_grid = x0 + x_shift + u_grid * ux + v_grid * vx
        y_grid = y0 + u_grid * uy + v_grid * vy
        ok = (
            (x_grid.min(axis=1) >= 10)
            & (x_grid.max(axis=1) < nx - 10)
            & (y_grid.min(axis=1) >= 10)
            & (y_grid.max(axis=1) < ny - 10)
        )
        x_grid, y_grid, u_valid = x_grid[ok], y_grid[ok], u_arr[ok]
        xmin, xmax = int(x_grid.min()) - 2, int(x_grid.max()) + 3
        ymin, ymax = int(y_grid.min()) - 2, int(y_grid.max()) + 3
        patch = data[ymin:ymax, xmin:xmax].astype(np.float32)
        sig = -map_coordinates(patch, [y_grid - ymin, x_grid - xmin], order=1, mode="nearest")
        sig -= np.median(sig, axis=1, keepdims=True)
        mad = float(np.median(np.abs(sig))) * 1.4826
        sig_clip = np.clip(sig, -3.0 * mad, 3.0 * mad)
        prof = np.mean(sig_clip, axis=0)
        prof = prof - median_filter(prof, size=61)
        prof = np.convolve(prof, np.ones(3) / 3.0, mode="same")
        pstd = float(np.median(np.abs(prof - np.median(prof)))) * 1.4826
        snr = (prof - np.median(prof)) / (pstd + 1e-9)
        mi = int(np.argmax(snr))
        return {
            "n_rows": int(len(u_valid)),
            "max_straight_radon_snr": round(float(snr[mi]), 2),
            "peak_offset_px": round(float(v_arr[mi]), 1),
        }

    return {
        "fits_sha256": actual_sha,
        "shape": [int(ny), int(nx)],
        "norad_528_track": run_strip(0.0),
        "null_control_east_2500px": run_strip(2500.0),
    }


def check_json(path: pathlib.Path) -> int:
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["status"] == "NULL_DETECTION_NON_EXCLUSIONARY"
    assert doc["archive_scan"]["total_solved_exposures_1963"] == 3826
    assert doc["archive_scan"]["sunlit_crossings_by_norad"]["528"] == 3
    assert doc["archive_scan"]["sunlit_crossings_by_norad"]["527"] == 0
    assert doc["archive_scan"]["sunlit_crossings_by_norad"]["529"] == 0
    assert doc["archive_scan"]["sunlit_crossings_by_norad"]["637"] == 0
    assert doc["plate_27600_analysis"]["fits_sha256"] == PLATE_27600_SHA256
    assert doc["tle_source"]["parquet_sha256"] == PARQUET_SHA256
    assert doc["plate_27600_analysis"]["can_exclude_trajectory"] is False
    print(f"OK: verified {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scan-tap", type=pathlib.Path, help="Path to pinned 1963 TLE parquet")
    ap.add_argument("--analyze-fits", type=pathlib.Path, help="Path to 000011_1963_h.fits")
    ap.add_argument("--check-json", type=pathlib.Path, default=None, help="Verify JSON invariants")
    args = ap.parse_args(argv)

    if args.check_json is not None:
        return check_json(args.check_json)
    if args.scan_tap is not None:
        print(json.dumps(scan_tap(args.scan_tap), indent=2))
        return 0
    if args.analyze_fits is not None:
        print(json.dumps(analyze_plate_27600(args.analyze_fits), indent=2))
        return 0
    return check_json(DEFAULT_JSON)


if __name__ == "__main__":
    sys.exit(main())
