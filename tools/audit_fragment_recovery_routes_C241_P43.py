#!/usr/bin/env python3
"""Audit 1963 debris archival leads; secondary references never become 528 measurements."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research/tle_custody/fragment_recovery_archival_routes_C241-P43.json"
EXPECTED = (
    ("P43-R1", "NASA History Office", None, "23 February 1968"),
    ("P43-R2", "Record Group 220", 17, "Guidelines for Interagency"),
    ("P43-R3", "Record Group 220", 18, "22 May 1963"),
    ("P43-R4", "Record Group 59", 2989, "14 June 1962"),
)

def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("P43 archival custody: " + reason)

def audit(data: dict) -> dict:
    require(data.get("id") == "C241-P43" and data.get("schema") == "conde.fragment-archive-route/v1", "ledger identity")
    sources = data.get("sources")
    require(isinstance(sources, list) and len(sources) == 2, "source count")
    article, museum = sources
    require(article["id"] == "JAMES-DAVID-2005" and article["doi"] == "10.1080/14777620590933584", "paper identity")
    require(article["journal_year"] == 2005 and article["online_date"] == "2006-08-07" and article["journal_pages"] == "43-65", "publication vs online date")
    require(article["access_level"] == "PUBLISHER_INDEX_REFERENCES_ONLY", "full article access falsely asserted")
    require(museum["id"] == "NASM-A19650278001" and museum["catalogue_accession"] == "A19650278001", "NASM accession")
    require(museum["url"].startswith("https://airandspace.si.edu/collection-objects/"), "NASM URL")
    require(museum["launch_year"] == 1962 and museum["recovery_year"] == 1963, "launch year vs recovery year")
    require(museum["recovery_months"] == ["April", "June"] and "Australia" in museum["recovery_place"], "museum case identity")
    for item in sources:
        require(item["source_payload_sha256"] is None and item["specific_528_or_conde_case_confirmed"] is False, "unsupported source proof")
    require(article["raw_article_pdf_retrieved"] is False and museum["raw_artifact_examined"] is False, "unretrieved raw sources")
    require(museum["identified_with_norad_528"] is False, "1962 fragments misattributed to 528")
    routes = data.get("archival_routes")
    require(isinstance(routes, list) and len(routes) == 4, "route count")
    require(len({r["id"] for r in routes}) == len(routes), "duplicate route")
    for route, (ident, repo, box, item) in zip(routes, EXPECTED):
        require(route["id"] == ident and repo in route["repository"] and item in route["cited_item"], "archive locator drift " + ident)
        require(route.get("box") == box and route["source_id"] == article["id"], "wrong box/source " + ident)
        require(route["kind"] == "secondary_citation_to_primary_record", "false primary status " + ident)
        require(route["item_retrieved"] is False and route["case_1963_003_b_confirmed"] is False, "unproven primary case " + ident)
        require(len(route["recommended_lookup"]) > 30, "missing actionable retrieval " + ident)
    c = data.get("classification", {})
    require(c.get("stage") == "ARCHIVAL_FINDING_AID_CANDIDATES_NOT_CASE_EVIDENCE", "source promoted without raw case")
    require(c.get("publisher_index_not_primary_paper") is True and c.get("museum_1962_launch_is_not_1963_003") is True, "missing source limitations")
    require(type(c.get("institutional_leads_count")) is int and c["institutional_leads_count"] == len(routes), "count drift")
    require(type(c.get("source_works_count")) is int and c["source_works_count"] == 2, "duplicated paper notes as sources")
    for key in ("primary_case_files_retrieved", "observations_of_527_528_529_added", "sensor_epochs_utc_added", "physical_constraints_activated"):
        require(type(c.get(key)) is int and c[key] == 0, "unproven activation " + key)
    require(c.get("theta_effect") == "UNCHANGED", "domain narrowed without sensor")
    return {"status": "ARCHIVAL_LEADS_ONLY", "new_archival_locators": len(routes), "source_works": len(sources), "instrumental_observations": 0, "theta_effect": "UNCHANGED"}

if __name__ == "__main__":
    print(json.dumps(audit(json.loads(LEDGER.read_text(encoding="utf-8"))), sort_keys=True))
