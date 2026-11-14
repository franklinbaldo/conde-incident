#!/usr/bin/env python3
"""CGEO-52: fail closed when a catalog is blocked or returns HTML instead of hits."""
import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/geo/cgeo52_ncap_crossarchive_route.json"
PARENT = ROOT / "research/geo/cgeo51_nara_copy_access.json"
NARA = "https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography"
NCAP = "https://www.ncap.org/image-collection/nara"
CATALOG = "https://catalog.archives.gov/proxy/records/search?limit=25&page=1&q=11S037W"

def require(value, label):
    if not value:
        raise ValueError(label)

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate(d, previous):
    require((d.get("schema"), d.get("id")) == ("conde.cgeo.ncap-crossarchive-route/v1","CGEO-52"), "schema/id")
    require(d["parents"] == ["CGEO-47","CGEO-48","CGEO-49","CGEO-50","CGEO-51"], "parents")
    require(previous["id"] == "CGEO-51", "parent identity")
    p, n = previous["nara"], d["nara"]
    require((n["file_unit"],n["series"],n["overlay"],n["op_file_number"]) ==
            (p["unit"],p["series"],p["overlay"],p["op_file_number"]), "archival lineage")
    require((n["record_group"],n["degree_square"],n["candidate_exposures"]) ==
            ("373","11S037W",[26,16]), "archive identification")
    require(n["spot_number"] is None and n["negative_can"] is None, "invented film identifiers")
    s = d["sources"]
    require(len(s) == 3 and [x["kind"] for x in s] ==
            ["nara_primary_guide","ncap_partner_catalog","catalog_search_attempt"], "source identities")
    require([x["url"] for x in s] == [NARA,NCAP,CATALOG], "source URL substitution")
    require(s[0]["content_acquired"] is True and s[0]["http_status"] == 200 and s[0]["body_bytes"] == 51079, "NARA acquisition")
    require(s[0]["sha256"] == "326b33c82aaef86bfba3b4be2a201c311ad167a6a2a0785dcb366ed1ff836648", "NARA bytes mismatch")
    require(s[1]["http_status"] == 403 and s[1]["content_acquired"] is False, "NCAP access unsupported")
    require(s[1]["error_response_bytes"] == 5432 and s[1]["published_geographical_coverage_mentions_brazil"] is False, "published coverage")
    require(s[1]["absence_of_brazil_photographs_proven"] is False, "absence not established")
    require(s[2]["http_status"] == 200 and s[2]["body_bytes"] == 5454 and
            s[2]["body_format"] == "HTML_APP_SHELL_NOT_SEARCH_JSON", "catalog response type")
    require(s[2]["catalog_results_parsed"] is False and s[2]["zero_photograph_hits_proven"] is False, "false result count")
    route = d["route"]
    require(route["nara_reports_ncap_scans_added_to_catalog"] is True and
            route["ncap_reports_rg373_digitization_partnership"] is True and
            route["ncap_page_lists_argentina_but_not_brazil"] is True, "unsupported partnership")
    require(route["individual_conde_film_digitized"] is None and route["public_negative_url"] is None, "invented scan")
    require(all(route[x] is False for x in ("can_locator_accessed","contact_sent","physical_negative_requested")), "false action")
    limits = d["limitations"]
    require(limits["source_families_independent_photographs"] == 0 and
            limits["conclusive_absence_of_coverage"] is False and
            limits["conde_urban_photo_acquired"] is False, "false photographic result")
    require(all(limits[k] is None for k in ("exposure_date_verified","center_geometry_1963","event_location")), "false geometry")
    require(limits["orbital_constraints_activated"] is False and
            limits["status"] == "DIGITIZATION_ROUTE_IDENTIFIED_BRAZIL_COVERAGE_UNVERIFIED", "false orbital result")
    require(d["next_check"].startswith("Use a functioning NCAP"), "next action")
    return 3

def live():
    request = Request(NARA, headers={"User-Agent":"Conde-CGEO52/1.0"})
    with urlopen(request,timeout=35) as response:
        require(response.status == 200, "NARA not HTTP 200")
        body = response.read().lower()
    require(b"national collection of aerial photography" in body and
            b"scanned" in body and b"spot number" in body, "partnership text changed")
    return len(body)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    args = ap.parse_args()
    print("CGEO52_OFFLINE_PASS",validate(load(DATA),load(PARENT)))
    if args.live:
        print("CGEO52_NARA_LIVE_PASS",live())
