#!/usr/bin/env python3
"""CGEO-55: cross-square NARA flight-overlay custodian, not a georeferencer."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/geo/cgeo55_nara_12s037w_overlays.json"
MEDIA = "https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/"
KNOWN = {
    "00429": ("12S037W", "cover_sheet", 2238940, "58e1f0f08a2f91df260f429bc4c6d326ff31a2e7aa9ba59e817fbb6e586686aa", 3188, None),
    "00430": ("12S037W", "reference_chart", 2488224, "8f7b9cf864083ef628429165fc72a07cad55730401316ee22220586d5da5f75d", 3620, None),
    "00431": ("12S037W", "flight_overlay", 2487325, "b4422aad1d0ca1a53dbb762c20e653cb34c42785abcd4e162e3f943300c6227d", 3620, "125374"),
    "00432": ("12S037W", "flight_overlay", 2420414, "fcd14c0cd438c40e4ce6733c896869d12e8899e31d2cf9c5cb62ce03ba4af6b9", 3620, "125370"),
    "00247": ("11S037W", "flight_overlay_cross_reference", 2497049, "b671f0378e2b57502f616be5aaa57ae45041048aa576bbf04c6eed9a6843a404", 3620, "125370"),
    "00248": ("11S037W", "flight_overlay_cross_reference", 2519162, "21016e6c141d5ac495893e13bc9a4b01bbf992e596416054fd0c03c164f3d2a0", 3620, "125374"),
}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def validate(data):
    need((data.get("schema"), data.get("id"), data.get("parent")) ==
         ("conde.cgeo.nara-12s037w-overlays/v1", "CGEO-55", "CGEO-54"), "lineage")
    c = data.get("catalog", {})
    need((c.get("naid"), c.get("square"), c.get("record_group"), c.get("series"),
          c.get("microfilm"), c.get("roll")) ==
         ("46716877", "12S037W", "373", "306062", "M1765", "317"),
         "catalog provenance")
    need(c.get("media_type") == "microfilm_scan_of_flight_overlay_or_reference",
         "scan mistaken for aerial photograph")
    scans = data.get("scans")
    need(isinstance(scans, list) and
         [r.get("sheet") for r in scans] == list(KNOWN), "scans missing/reordered")
    for r in scans:
        sheet = r["sheet"]
        square, role, size, sha, width, op = KNOWN[sheet]
        need((r.get("square"), r.get("role"), r.get("bytes"), r.get("sha256"),
              r.get("width"), r.get("height"), r.get("op_file_no")) ==
             (square, role, size, sha, width, 3988, op), "scan custody/identity " + sheet)
        need(isinstance(r.get("visible_annotation"), str) and
             len(r["visible_annotation"]) >= 4, "annotation missing " + sheet)
        if role == "reference_chart":
            need("Conde" in r["visible_annotation"], "Conde chart label missing")
    matches = data.get("cross_square_matches")
    need(isinstance(matches, list) and len(matches) == 2, "cross-square count")
    for match, op, sheets in zip(matches, ("125374", "125370"),
                                  (["00248", "00431"], ["00247", "00432"])):
        need(match.get("op_file_no") == op and match.get("sheets") == sheets,
             "mismatched OP cross-reference")
        need("not same exposure/spot" in match.get("meaning", ""),
             "OP number promoted to exposure/spot")
        need(all(next(s for s in scans if s["sheet"] == x)["op_file_no"] == op
                 for x in sheets), "OP number differs from original")
    expected = {
        "scans_acquired": 6,
        "scans_new_for_square_12S037W": 4,
        "flight_overlays_in_square_12S037W": 2,
        "op_file_cross_square_matches": 2,
        "original_individual_aerial_frames_acquired": 0,
        "independent_photographic_observations": 0,
        "cross_square_identifier_reuse": True,
        "spatial_overlap_of_exposures_proven": False,
    }
    need(data.get("interpretation") == expected, "invalid interpretation")
    limits = data.get("limits", {})
    for key in ("date_of_individual_exposure", "spot_number", "negative_can",
                "flight_footprint_georeferenced", "coverage_of_conde_center",
                "historical_city_center_geometry_1963", "alleged_fall_location"):
        need(key in limits and limits[key] is None, "unsupported bridge: " + key)
    need(limits.get("orbital_constraint_activated") is False, "invented orbit")
    return len(scans)

def live():
    # Exact source replay: no thumbnail, HTML fallback, range, or zero-byte success.
    for sheet, (_sq, _role, expected_size, expected_sha, _width, _op) in KNOWN.items():
        url = MEDIA + "m1765-317-" + sheet + ".jpg"
        req = Request(url, headers={"User-Agent":"Conde-CGEO55/1.0"})
        with urlopen(req, timeout=60) as response:
            need(response.status == 200, "HTTP failure " + sheet)
            need(response.headers.get("Content-Type","").lower().split(";")[0].strip()
                 in ("image/jpeg", "image/jpg", "application/octet-stream"),
                 "not JPEG HTTP content-type " + sheet)
            body = response.read(5_000_001)
        need(len(body) == expected_size, "byte count " + sheet)
        need(body[:3] == b"\xff\xd8\xff" and body[-2:] == b"\xff\xd9",
             "not full JPEG " + sheet)
        digest = hashlib.sha256(body).hexdigest()
        need(digest == expected_sha, "SHA256 mismatch " + sheet)
        print("CGEO55_NARA_ORIGINAL_PASS",sheet,"bytes",len(body),"sha256",digest)
    print("CGEO55_NARA_ALL_SIX_PASS")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    args = p.parse_args()
    print("CGEO55_CONTRACT_PASS", validate(json.loads(SOURCE.read_text(encoding="utf8"))))
    if args.live:
        live()
