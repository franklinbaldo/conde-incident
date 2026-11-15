"""CGEO-70: guard exact source, historical slots and scoped visual-page evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/editorial/cgeo70_uh_four_internal_pages_20261115.json"
INVENTORY = ROOT / "research/editorial/cgeo65_uh_bn_inventory_20261115.json"
COVERS = ROOT / "research/editorial/cgeo66_uh_cover_dates_20261115.json"
PREREG = ROOT / "research/editorial/cgeo64_null_narrative_prereg_20261114.json"
PRIOR = ROOT / "research/editorial/cgeo69_uh_four_frontpages_20261115.json"
FROZEN = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
EXPECTED = {
  "00442": [
    "1963-10-09",
    "CONTROL_OCT07",
    6,
    "7b7c6189f86a9da5457332927f847262a72a4d0989a18f9b0042283c83e90a6a",
    "F04_WINDOWS",
    "Janelas in property-classified OCR; visual page is real-estate advertising, not a spacecraft aperture.",
    "CLASSIFIED_PROPERTY"
  ],
  "00447": [
    "1963-10-14",
    "CONTROL_OCT14",
    5,
    "e249c946712b7685e0a34d3de9a7250929957deb7a4c5894fbdb94aa0d02242b",
    "F01_METAL_SPHERE",
    "Metaphorical 'esfera orgânica' in Buddhist-monks report, not a metal sphere.",
    "BUDDHIST_REPORT"
  ],
  "00455": [
    "1963-10-22",
    "CONTROL_OCT21",
    5,
    "d4e08e37c815b538d29eb56c2354ddb3d60b8e2f3dbf27573d643693a7110830",
    "X01_SATELLITE",
    "Reporting about rockets, spacecraft/satellites and prospects of reaching the Moon; genuine space vocabulary but not any frozen FBIS composite motif.",
    "SPACE_PROGRAM_REPORT"
  ],
  "00467": [
    "1963-11-04",
    "TARGET_NOV04",
    2,
    "82c0345dccc9c7d48db3512b134b84b0d1d39579410b5f91530109674bd995f9",
    "X01_SATELLITE",
    "Urban-development 'cidades satélites' is a place-planning usage, not an orbiting spacecraft.",
    "URBAN_PLANNING"
  ]
}

def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)

def validate(doc: dict, inv: dict, covers: dict, prereg: dict, prior: dict) -> int:
    require((doc.get("type"), doc.get("id")) ==
            ("HistoricalPressFrozenWeekInternalPageAudit","CGEO-70"),"identity")
    require(doc.get("issue") == "https://github.com/franklinbaldo/conde-incident/issues/887","issue")
    require(doc.get("prereg_path") == "research/editorial/cgeo64_null_narrative_prereg_20261114.json"
            and doc.get("prereg_blob_sha") == FROZEN,"frozen design")
    require(doc.get("source_inventory_path") == "research/editorial/cgeo65_uh_bn_inventory_20261115.json"
            and doc.get("source_cover_crosswalk") == "research/editorial/cgeo66_uh_cover_dates_20261115.json"
            and doc.get("prior_audit_path") == "research/editorial/cgeo69_uh_four_frontpages_20261115.json","lineage")
    require(prereg.get("id") == "CGEO-64" and len(prereg["frozen_fbis_fragments"]) == 8,"prereg")
    require(inv.get("id") == "CGEO-65" and covers.get("id") == "CGEO-66"
            and prior.get("id") == "CGEO-69" and len(prior["pages"]) == 4,"sources")
    require("all four quadrants" in doc.get("method","")
            and "same-article" in doc.get("method",""),"visual/article method")
    require("NOT a random or representative sample" in doc.get("selection_bias","")
            and "MUST NOT be extrapolated" in doc["selection_bias"],"selection caveat")
    pins = {x["id"]: x for x in inv["issues"] if x["status"] == "PDF_BYTES_ACQUIRED"}
    dates = {x["issue_id"]: x["date"] for x in covers["cover_dates"]}
    slots = {(x["publication"],x["issue_id"]):(x["date"],x["week"])
             for x in covers["slots"] if x.get("issue_id")}
    fragments = {x["id"] for x in prereg["frozen_fbis_fragments"]}
    pages = doc.get("pages",[])
    require(len(pages) == 4 and {x.get("issue_id") for x in pages} == set(EXPECTED),"four pages")
    for x in pages:
        key=x["issue_id"]
        date,week,page,sha,frag,context,genre = EXPECTED[key]
        require((x.get("publication"),x.get("date"),x.get("week"),x.get("pdf_page")) ==
                ("UH_RE",date,week,page),"page chronology")
        require(x.get("source_sha256") == sha == pins[key]["sha256"] and
                x.get("source_url") == pins[key]["url"] and page <= pins[key]["pages"],
                "SHA URL page pin")
        require(dates[key] == date and slots[("UH_RE",key)] == (date,week),"date slot")
        require(x.get("review")=="FULL_PAGE_VISUAL_FOUR_QUADRANTS_TEXT_LAYER_AUXILIARY"
                and x.get("selection")=="PURPOSIVE_TEXT_LAYER_LEAD_OR_FIXED_NEXT_PAGE"
                and x.get("genre")==genre,"review and selection")
        require(x.get("whole_issue_read") is False and
                x.get("independent_conde_witness") is False,"no independent witness")
        counts = x.get("confirmed_article_counts")
        require(isinstance(counts,dict) and set(counts)==fragments and
                all(type(counts[f]) is int and counts[f] == 0 for f in fragments),
                "eight negative counts strictly scoped")
        require(x.get("lexical_adjudication") ==
                {"fragment_or_context":frag,"context":context,"fbis_composite_match":False},
                "lexical context and article boundary")
    c=doc.get("coverage",{})
    require(c == {
        "new_internal_pages_fully_read":4,
        "prior_front_pages_fully_read":4,
        "total_pages_scoped_across_cgeo69_cgeo70":8,
        "pages_by_week_scoped":{k:2 for k in ("CONTROL_OCT07","CONTROL_OCT14","CONTROL_OCT21","TARGET_NOV04")},
        "whole_issues_read":0,"jb_pages_read":0,"predeclared_slots_changed":0,
        "full_corpus_baseline_rate":None,"first_pre_event_occurrence":None,
        "general_verdict":"UNDETERMINED",
    },"coverage and provisional verdict")
    require(doc.get("lineage_and_limits")=={
        "distinct_publication_lineages_for_four_pages":1,
        "same_article_republications_authenticated":0,
        "independent_conde_witness_found":False,
        "source_hour_of_event_found":False,
        "space_vocabulary_is_not_fbis_sphere_fragment":True,
        "not_all_pages_of_any_issue_inspected":True,
        "historical_center_1963":None,
        "orbital_constraint_activated":False,
        "deliberate_fraud_proven":False,
    },"causal limits")
    require("zero confirmed frozen composite motifs" in doc.get("interpretation","")
            and "not proof of borrowing" in doc["interpretation"],"interpretation")
    return len(pages)

if __name__ == "__main__":
    args=[json.loads(p.read_text(encoding="utf-8"))
          for p in (DATA,INVENTORY,COVERS,PREREG,PRIOR)]
    print(f"CGEO-70: {validate(*args)} internal pages; denominator scoped; verdict UNDETERMINED")
