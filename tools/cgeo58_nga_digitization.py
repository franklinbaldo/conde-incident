#!/usr/bin/env python3
"""CGEO-58: audit an institutional digitization lead, never an assumed aerial frame."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo58_nga_historical_imagery_route.json"
SOURCES = {
    "NGA-HIST": ("https://www.nga.mil/resources/Historical_Maps_and_Charts.html", 27834, "7f21f746057d7cebb2064946d051a4adde7f8263af8629cd8bacdb554a4a070d", "NGA institutional capacity statement"),
    "NGA-FOIA": ("https://www.nga.mil/resources/FOIA_Information.html", 35581, "71ee943bfaf0810792b1950308d6b7a76991b8001859e77e2bdd69ef476d72a7", "NGA existing-records FOIA request channel"),
    "NARA-GUIDE": ("https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography", 51079, "326b33c82aaef86bfba3b4be2a201c311ad167a6a2a0785dcb366ed1ff836648", "RG 373 original film can locator workflow; availability not established"),
}
EXPECTED_LIMITS = {
    "nga_has_specific_conde_negative": None,
    "nga_record_identified": None,
    "nga_public_digitization_available": None,
    "nga_fees_or_conditions": None,
    "original_film_frames_acquired": 0,
    "verified_conde_1963_geometry": None,
    "verified_fall_location": None,
    "orbital_constraint_activated": False,
}
EXPECTED_INDEX = {
    "archive": "NARA RG 373 / M1765 reel 317",
    "op_file_numbers": ["125370", "125374"],
    "sheets": ["00247", "00248", "00431", "00432"],
    "spot_numbers_verified": [],
    "individual_exposure_ids_verified": [],
    "film_can_identifiers_verified": [],
}
CLAIM_FRAGMENTS = (
    ("NGA-HIST", "1935 to 2004", "not confirmed public access"),
    ("NGA-FOIA", "existing agency records", "not proof"),
    ("NARA-GUIDE", "verified spot numbers", "requires validated spot"),
)

def validate(d):
    if not isinstance(d, dict) or (d.get("schema"), d.get("id"), d.get("parent"), d.get("date")) != (
        "conde.cgeo.nga-historical-imagery-route/v1", "CGEO-58", "CGEO-57", "2026-11-14"
    ):
        raise ValueError("unexpected evidence identity")
    if d.get("classification") != "new institutional retrieval lead, not new aerial photography":
        raise ValueError("lead presented as acquired aerial photography")
    rows = d.get("sources")
    if not isinstance(rows, list) or len(rows) != len(SOURCES):
        raise ValueError("three primary sources required")
    seen = set()
    for row in rows:
        sid = row.get("id")
        if sid not in SOURCES or sid in seen:
            raise ValueError("duplicate or unrecognized source")
        seen.add(sid)
        url, n, sha, role = SOURCES[sid]
        if (row.get("url"), row.get("bytes"), row.get("sha256"), row.get("role"), row.get("http_status")) != (
            url, n, sha, role, 200
        ):
            raise ValueError("source evidence identity changed")
    if seen != set(SOURCES):
        raise ValueError("missing source")
    claims = d.get("claims")
    if not isinstance(claims, list) or len(claims) != 3:
        raise ValueError("claim provenance incomplete")
    for row, (sid, fragment, limiting) in zip(claims, CLAIM_FRAGMENTS):
        if row.get("source_id") != sid or fragment not in row.get("claim", "") or limiting not in row.get("implication", ""):
            raise ValueError("unsupported or overstated institutional claim")
    if d.get("known_index") != EXPECTED_INDEX:
        raise ValueError("unverified negative or exposure identifier")
    if d.get("contact") != {"nga_request_sent": False, "foia_request_sent": False, "nara_contact_sent": False}:
        raise ValueError("unverified contact")
    if d.get("limitations") != EXPECTED_LIMITS:
        raise ValueError("unsupported photographic, geometric or orbital assertion")
    return len(seen)

def replay(d):
    for row in d["sources"]:
        req = Request(row["url"], headers={"User-Agent": "CondeIncident-CGEO58/1.0"})
        with urlopen(req, timeout=40) as response:
            status = response.status
            mime = response.headers.get("Content-Type", "")
            blob = response.read(250000)
        if status != 200 or "text/html" not in mime or b"<html" not in blob[:1000].lower():
            raise ValueError("expected real HTTP HTML source")
        if len(blob) != row["bytes"] or hashlib.sha256(blob).hexdigest() != row["sha256"]:
            raise ValueError("source changed since recorded: " + row["id"])
        print("REPLAY_OK id=%s bytes=%d sha256=%s" % (row["id"], len(blob), row["sha256"]))
    return len(d["sources"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    print("CGEO58_CONTRACT_PASS sources=%d frames=0" % validate(data))
    if args.live:
        print("CGEO58_LIVE_PASS sources=%d" % replay(data))

