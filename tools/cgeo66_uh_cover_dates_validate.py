"""CGEO-66: issue-date crosswalk only; never turn a cover scan into a read article."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
from cgeo64_prereg_validate import load_and_verify
from cgeo65_uh_bn_inventory_validate import validate as validate_inventory
ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/editorial/cgeo66_uh_cover_dates_20261115.json"
FROZEN = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
EXPECTED = {"00439":"1963-10-06","00440":"1963-10-07","00441":"1963-10-08","00442":"1963-10-09","00443":"1963-10-10","00444":"1963-10-11","00445":"1963-10-12","00446":"1963-10-13","00447":"1963-10-14","00448":"1963-10-15","00449":"1963-10-16","00450":"1963-10-17","00451":"1963-10-18","00452":"1963-10-19","00455":"1963-10-22","00456":"1963-10-23","00457":"1963-10-24","00458":"1963-10-25","00459":"1963-10-26","00466":"1963-11-03","00467":"1963-11-04","00468":"1963-11-05","00469":"1963-11-06","00470":"1963-11-07","00471":"1963-11-08","00472":"1963-11-09"}
def require(value, reason):
    if not value:
        raise ValueError(reason)
def validate(data: dict, inventory: dict, prereg: dict) -> tuple[int,int]:
    require((data.get("type"),data.get("id"),data.get("status")) == ("HistoricalPressCoverDateCrosswalk","CGEO-66","COVER_DATES_ONLY_NOT_ARTICLE_REVIEW"),"contract")
    require(data.get("prereg_git_blob_sha")==FROZEN,"frozen hash")
    require(data.get("source_manifest")=="research/editorial/cgeo65_uh_bn_inventory_20261115.json","source lineage")
    require(data.get("prereg_path")=="research/editorial/cgeo64_null_narrative_prereg_20261114.json","prereg lineage")
    validate_inventory(inventory)
    known={x["id"]:x for x in inventory["issues"] if x["status"]=="PDF_BYTES_ACQUIRED"}
    dates=data.get("cover_dates",[])
    require(len(dates)==26,"26 scanned covers only")
    require({r.get("issue_id"):r.get("date") for r in dates}==EXPECTED,"issue-date crosswalk")
    require(len({r.get("issue_id") for r in dates})==26,"duplicate cover")
    for r in dates:
        issue=r["issue_id"]
        require(issue in known and known[issue].get("sha256"),"date without original PDF and hash")
        require(r.get("source_page")==1 and r.get("verification")=="COVER_MASTHEAD_VISUAL_WITH_EMBEDDED_TEXT_CROSSCHECK","provenance")
        day=dt.date.fromisoformat(r["date"])
        require(day.year==1963,"year")
    required={(day,p["id"],w["id"]) for w in prereg["sampling"]["weeks"] for day in w["dates"] for p in prereg["sampling"]["publications"]}
    slots=data.get("slots",[])
    require(len(slots)==50 and {(s.get("date"),s.get("publication"),s.get("week")) for s in slots}==required,"frozen slot product changed")
    ncover=n404=0
    bydate={v:k for k,v in EXPECTED.items()}
    for s in slots:
        if s["publication"]=="UH_RE" and s["date"] in bydate:
            require((s.get("issue_id"),s.get("status"))==(bydate[s["date"]],"COVER_DATE_VERIFIED_ARTICLES_NOT_READ"),"cover slot")
            require("unverified_candidate_id" not in s,"false candidate")
            ncover+=1
        elif s["publication"]=="UH_RE" and s["date"]=="1963-10-21":
            require((s.get("issue_id"),s.get("unverified_candidate_id"),s.get("status"))==(None,"00454","UNACQUIRED_404_ISSUE_NUMBER_CANDIDATE_ONLY"),"404 is not dated")
            require(any(x["id"]=="00454" and x.get("http_result")=="404" for x in inventory["issues"]),"404 original")
            n404+=1
        else:
            require(s.get("issue_id") is None and s.get("status")=="NOT_ACQUIRED_NOT_READ" and "unverified_candidate_id" not in s,"unacquired is not zero")
    require((ncover,n404)==(19,1),"planned coverage")
    c=data.get("coverage",{})
    require((c.get("cover_dated_pdfs"),c.get("pre_event_target_and_baseline_uh_slots_cover_dated"),c.get("pre_event_target_and_baseline_uh_slots_expected"),c.get("pre_event_uh_missing_cover"),c.get("total_frozen_slots"))==(26,19,20,1,50),"coverage totals")
    require(c.get("post_event_sensitivity_uh_covered")==0 and c.get("jb_rj_cover_dated")==0,"unsupported coverage")
    require(c.get("pages_fully_read_for_fragment_rates")==0 and c.get("articles_verified_by_full_reading")==0 and c.get("fragment_rates") is None,"invented denominator")
    verdict=data.get("conclusion",{})
    require(verdict.get("verdict")=="UNDETERMINED" and verdict.get("first_pre_8_nov_occurrence") is None and verdict.get("physical_event_location") is None and verdict.get("orbital_constraint") is False and verdict.get("fraud") is False,"invalid inference")
    require(data.get("handoff",{}).get("issue_id")=="00472" and data["handoff"].get("cover_date")=="1963-11-09","lontra date handoff")
    return ncover,n404
if __name__=="__main__":
    p=load_and_verify()
    i=json.loads((ROOT/"research/editorial/cgeo65_uh_bn_inventory_20261115.json").read_text())
    d=json.loads(FILE.read_text())
    print("CGEO-66 verified covers/missing:",validate(d,i,p),"; 0 full article pages read; rates=null")
