#!/usr/bin/env python3
"""CGEO-51: validate archive access without inventing a film can or remote scan."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/geo/cgeo51_nara_copy_access.json"
PARENT = ROOT / "research/geo/cgeo50_nara_locator_search.json"
SOURCES = [
    ("nara_order", "https://www.archives.gov/research/cartographic/order"),
    ("nara_locator", "https://unwritten-record.blogs.archives.gov/2019/09/11/researching-foreign-aerial-photography/"),
    ("nara_staff_reply", "https://openhistoryhub.com/t/how-aerial-photos-from-2ww-can-be-researched/61447"),
]

def check(expr, message):
    if not expr:
        raise ValueError(message)

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(d, parent):
    check(d.get("schema") == "conde.cgeo.nara-copy-access/v1" and d.get("id") == "CGEO-51", "schema/id")
    check(d["lineage"] == ["CGEO-47","CGEO-48","CGEO-49","CGEO-50"], "lineage")
    n = d["nara"]
    check(n["unit"] == parent["nara_file_unit"] and n["overlay"] == parent["candidate_overlay"], "nara lineage")
    check(n["op_file_number"] == parent["candidate_handwritten_number"] == "125374", "op file")
    check(n["series"] == "306062" and n["film"] == "M1765" and n["roll"] == "317", "archive locator")
    check(n["candidate_exposures"] == [26,16] and n["spot_number"] is None and n["can_number"] is None, "unknown identifiers")
    check(len(d["sources"]) == len(SOURCES), "source count")
    for src, (kind, url) in zip(d["sources"], SOURCES):
        check((src["kind"],src["url"]) == (kind,url), "source substitution")
        check(src["http_status"] == 200 and src["bytes"] > 10000, "bad acquisition")
        h = src["sha256"]
        check(len(h) == 64 and all(c in "0123456789abcdef" for c in h), "bad sha")
    p = d["access_policy"]
    check(p["digital_locator_can_be_requested"] is True and p["locator_is_open_online"] is False, "locator access")
    check(p["remote_film_copy_offered"] is False and p["onsite_researcher_or_representative_needed"] is True, "remote copy assumption")
    check(p["onsite_camera_or_scanner_possible"] is True and p["advance_request_for_original_negative_may_be_needed"] is True, "access procedure")
    check(len(d["questions"]) == 3, "request questions")
    check(all(x is False for x in d["actions"].values()), "unperformed external action")
    lim = d["limitations"]
    check(all(lim[k] is None for k in ("authentic_photo_of_urban_conde", "photo_exposure_date", "historical_city_center_1963", "event_location")), "unsupported conclusion")
    check(lim["orbital_constraint_activated"] is False and lim["status"] == "ONSITE_ACQUISITION_PATH_ONLY", "unsupported orbital conclusion")
    return len(SOURCES)

def live(d):
    for src in d["sources"]:
        req = Request(src["url"], headers={"User-Agent":"Conde-CGEO51/1.0"})
        with urlopen(req, timeout=35) as r:
            body = r.read()
            check(r.status == 200 and len(body) > 1000, "live acquisition")
        html = body.decode("utf-8", errors="replace").lower()
        if src["kind"] == "nara_order":
            check("aerial photographs" in html and "research room" in html, "copy policy changed")
        elif src["kind"] == "nara_locator":
            check("spot number" in html and "can locator" in html, "locator policy changed")
        else:
            check("cartographic branch" in html and "offsite" in html, "staff answer changed")
    return len(d["sources"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    data = read(DATA)
    print("CGEO51_OFFLINE_PASS", validate(data, read(PARENT)))
    if args.live:
        print("CGEO51_LIVE_PASS", live(data))
