#!/usr/bin/env python3
"""Validate NARA RG 373 candidate search while forbidding premature geocoding."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "research/geo/cgeo46_nara_rg373_overlays.json"
PRIOR = ROOT / "research/geo/cgeo45_mi1850_roll58.json"


def degree_square(latitude: float, longitude: float) -> str:
    if not all(map(math.isfinite, (latitude, longitude))):
        raise ValueError("coordinate must be finite")
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("coordinate out of range")
    return f"{math.floor(abs(latitude)):02d}{'S' if latitude < 0 else 'N'}{math.floor(abs(longitude)):03d}{'W' if longitude < 0 else 'E'}"


def validate(d: dict, prior: dict | None = None) -> None:
    assert d["id"] == "CGEO-46"
    assert d["schema"] == "conde.cgeo.nara-rg373-overlays/v1"
    guide = d["nara_guide"]
    assert guide["institution"].startswith("US National Archives")
    assert guide["url"] == "https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography"
    assert guide["status"] == "GUIDE_ACQUIRED"
    assert guide["record_group"] == "373"
    assert guide["bytes"] > 10000
    assert len(guide["sha256"]) == 64
    c = d["candidate"]
    assert (c["municipality"], c["state"], c["country"], c["ibge_code"]) == ("Conde", "BA", "Brazil", "2908606")
    assert c["location_epoch"] == "modern_approximate_search_only"
    assert c["degree_square_candidate"] == degree_square(c["latitude"], c["longitude"])
    assert c["catalog_search_url"] == "https://catalog.archives.gov/search?q=" + c["degree_square_candidate"]
    assert c["catalog_result_status"] == "NOT_VERIFIED"
    assert c["aerial_coverage_status"] == "NOT_VERIFIED"
    n = d["nara_identifier_resolution"]
    assert all(v is None for v in n.values()), "do not invent NARA mission, frame, can or SGB equivalence"
    l = d["limitations"]
    assert l["guide_is_inventory_of_conde"] is False
    assert l["original_frames_acquired"] is False
    assert l["exposure_date_authenticated"] is False
    assert l["center_conde_nov_1963"] is None
    assert l["georeferenced_footprint"] is None
    assert l["reentry_point"] is None
    assert l["can_constrain_orbital_reentry"] is False
    s = d["sgb_provenance"]
    assert s["based_on"] == "CGEO-45"
    assert (s["roll"], s["line"], s["frame_labels"]) == ("58", "X-NNI", ["7150", "7157"])
    assert s["year_range_on_index"] == "1964-1970"
    if prior is not None:
        assert s["image_sha256"] == prior["source"]["sha256"]
        assert s["roll"] == prior["inspection"]["upper"]["roll"] == prior["inspection"]["lower"]["roll"]
        assert s["line"] == prior["inspection"]["upper"]["line"] == prior["inspection"]["lower"]["line"]
        assert s["frame_labels"] == [prior["inspection"]["lower"]["printed_frame"], prior["inspection"]["upper"]["printed_frame"]]


def live_check(d: dict) -> None:
    g = d["nara_guide"]
    with urlopen(Request(g["url"], headers={"User-Agent": "CondeResearch/1.0"}), timeout=35) as r:
        b = r.read(2_000_000)
    for word in (b"Record Group 373", b"degree square", b"spot number", b"1935"):
        assert word.lower() in b.lower(), "institutional page missing essential text"
    sha = hashlib.sha256(b).hexdigest()
    print(f"NARA live guide: bytes={len(b)} sha256={sha} pinned_sha_match={sha == g['sha256']}")
    if sha != g["sha256"]:
        print("NOTICE: live HTML byte drift; previously acquired SHA remains immutable; text anchors still checked")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    a = p.parse_args()
    d = json.loads(DATA.read_text())
    prior = json.loads(PRIOR.read_text())
    validate(d, prior)
    print("CGEO-46 offline: PASS (NARA coverage UNKNOWN, no geometry promoted)")
    if a.live:
        live_check(d)


if __name__ == "__main__":
    main()

