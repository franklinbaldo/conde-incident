#!/usr/bin/env python3
"""CGEO-53: validate NARA Catalog JSON without confusing index hits for film."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/geo/cgeo53_nara_v3_catalog.json"
API = "https://catalog.archives.gov/proxy/v3/records/search"
EXPECTED = {
    "11S037W": (1, "46716637", "Overlay indexes for degree square 11S037W"),
    "11S038W": (1, "46716645", "Overlay indexes for degree square 11S038W"),
    "125374": (183, None, None),
    "133002": (3451, None, None),
}
SNAPSHOTS = {
    "11S037W": (1878, "b1d3dd3ee52f898a61afcb28bc1abfa789da5dd4778df3726a39bbf66017579c"),
    "11S038W": (7519, "62d40bb409c395f926f47955dc77a988741604daab8beee4e1e6c2d9bdf1039d"),
    "125374": (7473, "2009fb27dca4fa05f1a52baace69ed5f4baf741b78715982de7458570c135d9b"),
    "133002": (8439, "22013197a13f7fbbe27e89ecfc9fa23dbf3cee0d525fc7756e83d1cb6d0f14a1"),
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def parse_response(status, content_type, body):
    require(status == 200, "HTTP status does not establish valid search")
    require(content_type.split(";")[0].strip().lower() == "application/json", "HTML shell or mislabeled response")
    try:
        d = json.loads(body)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("Non-JSON search response") from exc
    require(isinstance(d, dict) and isinstance(d.get("body"), dict), "Missing API body")
    hits = d["body"].get("hits")
    require(isinstance(hits, dict), "Missing hits object")
    require(isinstance(hits.get("hits"), list), "Missing hits array")
    total = hits.get("total")
    require(isinstance(total, dict) and type(total.get("value")) is int and total["value"] >= 0, "Missing total")
    require(total["value"] >= len(hits["hits"]), "Impossible hit count")
    for hit in hits["hits"]:
        require(isinstance(hit, dict) and isinstance(hit.get("_source"), dict), "Malformed hit source")
        require(isinstance(hit["_source"].get("record"), dict), "Malformed archival record")
    return d

def verify_cell_hits(document, q, expected_naid):
    hits = document["body"]["hits"]["hits"]
    matches = [h for h in hits if str(h.get("_id")) == expected_naid]
    require(len(matches) == 1, "Requested file unit not found uniquely")
    rec = matches[0]["_source"]["record"]
    require(rec.get("levelOfDescription") == "fileUnit", "Matched record is not file unit")
    require(rec.get("title") == EXPECTED[q][2], "Degree-square title mismatch")
    return matches[0]

def validate(d):
    require((d.get("schema"),d.get("id")) == ("conde.cgeo.nara-catalog-v3/v1","CGEO-53"), "schema/id")
    require(d.get("parents") == ["CGEO-47","CGEO-48","CGEO-49","CGEO-50","CGEO-51","CGEO-52"], "lineage")
    require(d.get("endpoint") == API, "unproven search API")
    queries = d.get("queries")
    require(isinstance(queries, list) and [x.get("q") for x in queries] == list(EXPECTED), "query identities")
    for x in queries:
        q=x["q"]
        count, naid, title = EXPECTED[q]
        require((x.get("limit"),x.get("http_status"),x.get("body_format")) == (10,200,"JSON"), "response label")
        require((x.get("total_hits"),x.get("matched_naid"),x.get("title")) == (count,naid,title), "fabricated search result")
        require((x.get("body_bytes"),x.get("sha256")) == SNAPSHOTS[q], "snapshot mismatch")
        require(x.get("level") == ("fileUnit" if naid else None), "wrong archival level")
    a = d.get("archival_lineage",{})
    require((a.get("record_group"),a.get("series"),a.get("degree_square"),a.get("file_unit")) ==
            ("373","306062","11S037W","46716637"), "archival parent")
    require((a.get("overlay"),a.get("op_file_number"),a.get("candidate_exposures")) ==
            ("m1765-317-00248.jpg","125374",[26,16]), "overlay lineage")
    require(a.get("spot_number") is None and a.get("negative_can") is None, "invented can")
    i = d.get("interpretation",{})
    require(i.get("catalog_search_operational") is True and i.get("matched_file_units") == 2, "wrong conclusion")
    for key in ("individual_frame_found","op_file_number_is_spot_confirmed",
                "numeric_query_hits_are_relevant_negatives","search_result_counts_are_complete_photo_inventory"):
        require(i.get(key) is False, key)
    require(i.get("nara_source_family_independent_photographs") == 0, "invented independent images")
    limits = d.get("limitations",{})
    for k in ("center_geometry_1963","alleged_event_location","individual_exposure_date"):
        require(k in limits and limits[k] is None, k)
    require(limits.get("orbit_constraints_activated") is False, "invented orbital constraint")
    return len(queries)

def live_one(q, limit=10):
    url = API + "?" + urlencode({"q":q,"limit":limit})
    req = Request(url, headers={"Accept":"application/json","User-Agent":"Conde-CGEO53/1.0"})
    with urlopen(req, timeout=35) as response:
        status,ctype,body = response.status,response.headers.get("Content-Type",""),response.read(3_000_000)
    result = parse_response(status,ctype,body)
    return result, len(body), hashlib.sha256(body).hexdigest()

def live():
    # Require positive record identity, not a fixed hit count or mutable HTML digest.
    for q in ("11S037W","11S038W"):
        data,nbytes,sha = live_one(q)
        verify_cell_hits(data,q,EXPECTED[q][1])
        print("NARA_JSON_LIVE_PASS",q,"record",EXPECTED[q][1],"bytes",nbytes,"sha256",sha)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--live",action="store_true")
    args=parser.parse_args()
    print("CGEO53_OFFLINE_PASS",validate(json.loads(DATA.read_text(encoding="utf8"))))
    if args.live:
        live()
