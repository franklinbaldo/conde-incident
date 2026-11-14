#!/usr/bin/env python3
"""CGEO-54: verify nine real NARA degree-square queries and index inventory."""
import argparse
import json
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/geo/cgeo54_nara_adjacent_overlay_index.json"
API = "https://catalog.archives.gov/proxy/v3/records/search"
EXPECTED = {
    "10S036W": ("46716333", 7, 18),
    "10S037W": ("46716347", 19, 29),
    "10S038W": ("46716360", 30, 35),
    "11S036W": (None, None, None),
    "11S037W": ("46716637", 245, 250),
    "11S038W": ("46716645", 251, 258),
    "12S036W": (None, None, None),
    "12S037W": ("46716877", 429, 432),
    "12S038W": ("46716883", 433, 448),
}

def need(ok, why):
    if not ok:
        raise ValueError(why)

def parse_response(status, mime, body):
    need(status == 200, "non-200 response")
    need(mime.split(";")[0].strip().lower() == "application/json", "non-JSON MIME / HTML SPA")
    try:
        d = json.loads(body)
    except (ValueError, UnicodeDecodeError) as e:
        raise ValueError("invalid JSON response") from e
    need(isinstance(d, dict) and isinstance(d.get("body"), dict), "API body missing")
    h = d["body"].get("hits")
    need(isinstance(h, dict) and isinstance(h.get("hits"), list), "hits missing")
    need(isinstance(h.get("total"), dict) and type(h["total"].get("value")) is int, "total missing")
    need(h["total"]["value"] >= len(h["hits"]) >= 0, "hit count contradiction")
    return d

def validate(d):
    need((d.get("schema"),d.get("id"),d.get("parent")) ==
         ("conde.cgeo.nara-adjacent-overlay-index/v1","CGEO-54","CGEO-53"),"schema/lineage")
    need((d.get("endpoint"),d.get("query_limit")) == (API,10), "query contract")
    need((d.get("record_group"),d.get("series"),d.get("microfilm"),d.get("roll")) ==
         ("373","306062","M1765","317"),"archival ancestry")
    records = d.get("records")
    need(isinstance(records, list) and [x.get("square") for x in records] == list(EXPECTED),"nine squares")
    seen = set()
    total = 0
    for r in records:
        square = r["square"]
        naid,first,last = EXPECTED[square]
        scans = r.get("scans")
        need(isinstance(scans,list), "scan inventory missing")
        want = [] if naid is None else [f"m1765-317-{i:05d}.jpg" for i in range(first,last+1)]
        need(scans == want, "wrong index scans or missing/extra scans")
        need(not (seen.intersection(scans)), "duplicate JPG across separate fileUnits")
        seen.update(scans)
        need((r.get("naid"),r.get("query_total"),r.get("title"),r.get("query_result")) ==
             (naid, 1 if naid else 0, f"Overlay indexes for degree square {square}" if naid else None,
              "fileUnit" if naid else "zero_hits_not_absence"),"record identity")
        snap=r.get("snapshot")
        need(isinstance(snap,dict) and snap.get("http_status")==200 and
             snap.get("content_type")=="application/json" and
             type(snap.get("body_bytes")) is int and snap["body_bytes"] > 0 and
             isinstance(snap.get("sha256"),str) and len(snap["sha256"])==64 and
             all(c in "0123456789abcdef" for c in snap["sha256"]), "snapshot custody")
        total += len(scans)
    need(total==63 and len(seen)==63, "catalogued index count")
    c = d.get("interpretation",{})
    need((c.get("file_units_confirmed"),c.get("catalogued_index_scans"))==(7,63), "counts")
    need(c.get("original_aerial_photographs_acquired") == 0 and
         c.get("independent_photographic_observations")==0 and
         c.get("zero_hit_squares_are_proven_absent") is False and
         c.get("all_index_sheets_are_original_frames") is False, "false photographic inference")
    l=d.get("limitations",{})
    for k in ("photographic_coverage_of_conde","historical_city_center_geometry_1963",
              "alleged_event_location","spot_number_for_125374","negative_can"):
        need(k in l and l[k] is None, "invented bridge: "+k)
    need(l.get("orbital_constraint_activated") is False, "invented orbit constraint")
    return total

def check_live_record(d, square, naid, first, last):
    hits = d["body"]["hits"]["hits"]
    matches = [h for h in hits if str(h.get("_id")) == naid]
    need(len(matches)==1,"fileUnit disappeared/ambiguous")
    rec = matches[0].get("_source",{}).get("record",{})
    need(rec.get("levelOfDescription")=="fileUnit", "not fileUnit")
    need(rec.get("title")==f"Overlay indexes for degree square {square}", "title mismatch")
    need(f"Latitude: {square[:3]}" in rec.get("scopeAndContentNote","") and
         f"Longitude: {square[3:]}" in rec.get("scopeAndContentNote",""),"scope mismatch")
    names={o.get("objectFilename") for o in rec.get("digitalObjects",[]) if isinstance(o,dict)}
    need(f"m1765-317-{first:05d}.jpg" in names and f"m1765-317-{last:05d}.jpg" in names,
         "scan anchors absent")
    return len(names)

def live():
    for square,(naid,first,last) in EXPECTED.items():
        if naid is None:
            continue  # Search omission is not a negative gate on future digitization.
        req=Request(API+"?"+urlencode({"q":square,"limit":10}),
                    headers={"Accept":"application/json","User-Agent":"Conde-CGEO54/1.0"})
        with urlopen(req,timeout=35) as response:
            status=response.status
            mime=response.headers.get("Content-Type","")
            body=response.read(1_000_000)
        d=parse_response(status,mime,body)
        count=check_live_record(d,square,naid,first,last)
        print("NARA_LIVE_PASS",square,naid,"objects",count,
              "bytes",len(body),"sha256",hashlib.sha256(body).hexdigest())

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--live",action="store_true")
    args=p.parse_args()
    print("CGEO54_OFFLINE_PASS",validate(json.loads(FILE.read_text(encoding="utf8"))))
    if args.live:
        live()
