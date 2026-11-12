#!/usr/bin/env python3
"""Independent conditional geometry/J2 audit for C241-T10 (no physical localization).

All historical values are read from pinned GitHub blobs. The legacy TLE-shaped
pair is unverified; the secondary mirror is NOT an independent NORAD observation.
No Texugo/Tartaruga module is imported.
"""
import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from urllib.request import urlopen

LEGACY_REF = "c84cce85e51252f9e589a851950385aea008e951"
MIRROR_REF = "1934198e260b9dae8c056587cc7a16c777d58d25"
LEGACY_BLOB = "0284f1217557b0ea891b5e51b6ac56bd13529d3f"
MIRROR_SHA256 = "18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd"
LEGACY_URL = f"https://raw.githubusercontent.com/franklinbaldo/conde-incident/{LEGACY_REF}/src/lib/constants.ts"
MIRROR_URL = f"https://raw.githubusercontent.com/franklinbaldo/conde-incident/{MIRROR_REF}/research/tle_custody/mirror_528_1963-10-27.tle"
DAY_S = 86400
J2, MU, R_E = 1.08262668e-3, 398600.4418, 6378.137
RAAN_TEXT_ROUNDING_DEG = 0.0001  # sum of two four-decimal half-quanta


def git_blob_sha1(blob: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(blob)).encode("ascii") + b"\0" + blob).hexdigest()


def check_checksum(line: str) -> None:
    if len(line) != 69 or line[68] not in "0123456789":
        raise ValueError("invalid TLE fixed width")
    calculated = sum(int(c) if c.isdigit() else (1 if c == "-" else 0)
                     for c in line[:68]) % 10
    if calculated != int(line[68]):
        raise ValueError("TLE checksum mismatch; checksum never attests source")


def parse_epoch(line1: str) -> datetime:
    check_checksum(line1)
    year = int(line1[18:20])
    year += 2000 if year < 57 else 1900
    day = Decimal(line1[20:32])
    if not (Decimal(1) <= day < Decimal(367)):
        raise ValueError("invalid TLE day")
    whole = int(day)
    us = int(((day - whole) * DAY_S * 1_000_000)
             .quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=whole - 1, microseconds=us)


def parse_elements(line2: str) -> dict:
    check_checksum(line2)
    if not line2.startswith("2 00528 "):
        raise ValueError("wrong NORAD identity")
    values = {
        "inclination": float(line2[8:16]),
        "raan": float(line2[17:25]),
        "eccentricity": float("0." + line2[26:33]),
        "mean_motion": float(line2[52:63]),
    }
    if (not all(math.isfinite(v) for v in values.values()) or
            not 0 <= values["inclination"] <= 180 or
            not 0 <= values["raan"] < 360 or
            not 0 <= values["eccentricity"] < 1 or
            values["mean_motion"] <= 0):
        raise ValueError("invalid orbital text fields")
    return values


def angular_distance(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def plane_separation(i1: float, o1: float, i2: float, o2: float) -> float:
    """Angle between orbit normals, assuming common reference frame/convention.

    NOT the same as RAAN difference, and NOT empirically established here.
    """
    alpha, beta = math.radians(i1), math.radians(i2)
    delta = math.radians(o1 - o2)
    dot = math.cos(alpha) * math.cos(beta) + math.sin(alpha) * math.sin(beta) * math.cos(delta)
    return math.degrees(math.acos(max(-1, min(1, dot))))


def proxy_node_rate(e: dict) -> float:
    # Independently use T = 86400 / rev-per-day, Kepler's third law, then J2.
    period = DAY_S / e["mean_motion"]
    a = (MU * (period / (2 * math.pi)) ** 2) ** (1 / 3)
    p = a * (1 - e["eccentricity"] ** 2)
    if p <= R_E:
        raise ValueError("pericenter inside reference ellipsoid")
    secular_rad_s = -1.5 * J2 * (2 * math.pi / period) * (R_E / p) ** 2 * math.cos(math.radians(e["inclination"]))
    return math.degrees(secular_rad_s) * DAY_S


def audit(legacy_lines: tuple[str, str], mirror_lines: tuple[str, str]) -> dict:
    for lines in (legacy_lines, mirror_lines):
        if len(lines) != 2 or not lines[0].startswith("1 00528U"):
            raise ValueError("two-line NORAD 528 required")
    t0, t1 = parse_epoch(legacy_lines[0]), parse_epoch(mirror_lines[0])
    a, b = parse_elements(legacy_lines[1]), parse_elements(mirror_lines[1])
    seconds = abs((t1 - t0).total_seconds())
    if seconds <= 0:
        raise ValueError("zero epoch separation")
    raandiff = angular_distance(a["raan"], b["raan"])
    plane = plane_separation(a["inclination"], a["raan"], b["inclination"], b["raan"])
    rates = (proxy_node_rate(a), proxy_node_rate(b))
    drift = max(abs(rate) for rate in rates) * seconds / DAY_S
    minimum_rate = max(0., raandiff - RAAN_TEXT_ROUNDING_DEG) * DAY_S / seconds
    return {
        "record_id": "C241-T10-GAVIAO",
        "legacy_epoch_utc": t0.isoformat(),
        "secondary_epoch_utc": t1.isoformat(),
        "epoch_difference_seconds": seconds,
        "raan_difference_deg": raandiff,
        "conditional_normal_plane_separation_deg": plane,
        "raan_is_not_plane_angle": abs(raandiff - plane) > 0.1,
        "j2_rates_deg_per_day": list(rates),
        "j2_max_proxy_drift_deg": drift,
        "minimum_required_rate_deg_per_day": minimum_rate,
        "offset_only_j2": "EXCLUDED_CONDITIONALLY" if min(raandiff, raandiff - RAAN_TEXT_ROUNDING_DEG) > drift else "NOT_EXCLUDED_BY_THIS_PROXY",
        "legacy_instrumental_provenance": "NOT_VERIFIED",
        "secondary_independent_tracking": "NOT_ESTABLISHED",
        "common_reference_frame": "ASSUMED_ONLY_FOR_GEOMETRIC_CONDITIONAL",
        "lean_physical_constraint": "NOT_ESTABLISHED",
        "terminal_simulation_with_holdout": "NOT_RUN",
        "site_of_impact": "INDETERMINATE",
    }


def load_pinned() -> tuple[tuple[str, str], tuple[str, str]]:
    with urlopen(LEGACY_URL, timeout=30) as response:
        raw_legacy = response.read()
    with urlopen(MIRROR_URL, timeout=30) as response:
        raw_mirror = response.read()
    if git_blob_sha1(raw_legacy) != LEGACY_BLOB:
        raise ValueError("legacy Git blob fingerprint mismatch")
    if hashlib.sha256(raw_mirror).hexdigest() != MIRROR_SHA256:
        raise ValueError("secondary TLE SHA256 mismatch")
    content = raw_legacy.decode("utf-8")
    block = re.search(r"\b528:\s*\{(.*?)\n\s*\},", content, re.DOTALL)
    if block is None:
        raise ValueError("missing legacy 528 stanza")
    lines = []
    for field in ("line1", "line2"):
        match = re.search(r"\b" + field + r":\s*'([^']+)'", block.group(1))
        if match is None:
            raise ValueError("missing legacy " + field)
        lines.append(match.group(1))
    return (lines[0], lines[1]), tuple(raw_mirror.decode("ascii").splitlines())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pinned", action="store_true", required=True,
                        help="Fetch both public revision-pinned sources and verify content hashes")
    args = parser.parse_args()
    if args.pinned:
        report = audit(*load_pinned())
        report["sources"] = {"legacy_git_blob_sha1": LEGACY_BLOB,
                             "secondary_tle_sha256": MIRROR_SHA256,
                             "legacy_url": LEGACY_URL, "secondary_url": MIRROR_URL}
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
