"""CGEO-67: adjudicate specific PDF passages, never claim a newspaper rate."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "research/editorial/cgeo67_uh_lexical_adjudication_20261115.json"
INVENTORY = ROOT / "research/editorial/cgeo65_uh_bn_inventory_20261115.json"
COVERS = ROOT / "research/editorial/cgeo66_uh_cover_dates_20261115.json"
PREREG = ROOT / "research/editorial/cgeo64_null_narrative_prereg_20261114.json"
FROZEN = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"

# Audited at the level of these passages, not entire PDF pages.
EXPECTED = {
    "C67-A": ("00440", "1963-10-07", 5, "CONTROL_OCT07",
              "F01_METAL_SPHERE", False, "MISSING_METAL_IN_SAME_ARTICLE"),
    "C67-B": ("00457", "1963-10-24", 4, "CONTROL_OCT21",
              "F03_FOUR_METER_HOLE", False, "FABRIC_LENGTH_NOT_HOLE"),
    "C67-C": ("00471", "1963-11-08", 8, "TARGET_NOV04",
              "F03_FOUR_METER_HOLE", True, "SAME_DAY_DIFFERENT_STORY_NO_CHRONOLOGY"),
}
CONTEXT = {
    "C67-A": "Soccer match analysis under the heading A LIDERANÇA: esfera refers to the ball; no metallic sphere in this passage.",
    "C67-B": "Uma original sacola para ir à praia: craft instructions list 4 metros de algodão xadrez, not a pit or crater.",
    "C67-C": "Polícia arranca confissão do pescador: Roubei estátuas e enterrei em Rio Doce. Four-metre-deep hole refers to burial of stolen statues, not Conde.",
}


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def validate(doc: dict, inventory: dict, covers: dict, prereg: dict) -> int:
    require((doc.get("type"), doc.get("id")) ==
            ("HistoricalPressLexicalAdjudication", "CGEO-67"), "identity")
    require(doc.get("issue") == "https://github.com/franklinbaldo/conde-incident/issues/887", "issue")
    require((doc.get("prereg_path"), doc.get("prereg_blob_sha")) ==
            ("research/editorial/cgeo64_null_narrative_prereg_20261114.json", FROZEN), "prereg frozen")
    require(doc.get("source_inventory_path") == "research/editorial/cgeo65_uh_bn_inventory_20261115.json"
            and doc.get("cover_crosswalk_path") == "research/editorial/cgeo66_uh_cover_dates_20261115.json", "sources")
    require(prereg.get("id") == "CGEO-64" and len(prereg["frozen_fbis_fragments"]) == 8, "prereg read")
    require(inventory.get("id") == "CGEO-65" and covers.get("id") == "CGEO-66", "upstream identity")
    require(inventory["coverage"]["pages_fully_inspected_for_rates"] == 0, "upstream has no full-page denominator")
    require(covers["coverage"]["pages_fully_read_for_fragment_rates"] == 0, "upstream has no full-page denominator")
    by_issue = {x["id"]: x for x in inventory["issues"] if x["status"] == "PDF_BYTES_ACQUIRED"}
    by_date = {x["issue_id"]: x["date"] for x in covers["cover_dates"]}
    by_slot = {(x["date"], x["publication"]): x["week"] for x in covers["slots"]}
    required_fragments = {f["id"] for f in prereg["frozen_fbis_fragments"]}
    rows = doc.get("adjudicated_passages", [])
    require(len(rows) == 3 and {r.get("id") for r in rows} == set(EXPECTED), "adjudicated set")
    for row in rows:
        rid = row["id"]
        eid, date, page, week, fragment, lexical, reason = EXPECTED[rid]
        require((row.get("issue_id"), row.get("date"), row.get("pdf_page"), row.get("week"),
                 row.get("fragment_id"), row.get("lexical_fragment_match"), row.get("reason")) ==
                (eid, date, page, week, fragment, lexical, reason), "fixed passage")
        require(row.get("publication") == "UH_RE", "publication")
        require(row["fragment_id"] in required_fragments, "not frozen fragment")
        require(row["source_sha256"] == by_issue[eid]["sha256"], "source hash")
        require(1 <= page <= by_issue[eid]["pages"], "page")
        require(by_date[eid] == date and by_slot[(date, "UH_RE")] == week, "cover/date/slot")
        require(row.get("context") == CONTEXT[rid], "edited context requires new review")
        require((row.get("inspection"), row.get("whole_page_read"),
                 row.get("independent_conde_witness")) ==
                ("VISUAL_PASSAGE_AND_PDF_TEXT", False, False), "overclaimed inspection")
    leads = doc.get("unresolved_ocr_leads", [])
    require(leads == [{"publication":"UH_RE","issue_id":"00441","date":"1963-10-08",
                      "pdf_page":7,"token":"4 metros","fragment_id":"F03_FOUR_METER_HOLE",
                      "status":"OCR_TOKEN_ONLY_NOT_ARTICLE_ADJUDICATED"}], "unresolved OCR must remain unresolved")
    c = doc.get("coverage", {})
    require(c == {
        "adjudicated_passages": 3,
        "frozen_edition_date_slots_changed": 0,
        "pages_fully_read_for_rates": 0,
        "fully_read_articles_for_rates": 0,
        "baseline_rates": None,
        "fragment_verdicts": None,
        "first_pre_event_borrowing": None,
        "jb_rj_articles_read": 0,
    }, "unsupported denominator/rate")
    require(doc.get("interpretation") == {
        "verdict": "UNDETERMINED",
        "same_day_publication_is_pre_event": False,
        "fbis_portuguese_verbatim_authenticated": False,
        "narrative_fabrication_proven": False,
        "orbital_constraint_activated": False,
        "historical_center_1963": None,
    }, "unsupported conclusion")
    require(len(doc.get("limitations", [])) >= 4 and "OCR is lead only" in doc.get("method", ""), "limits")
    return len(rows)


if __name__ == "__main__":
    document = json.loads(FILE.read_text(encoding="utf-8"))
    print("CGEO-67 passage checks:", validate(
        document, json.loads(INVENTORY.read_text()), json.loads(COVERS.read_text()),
        json.loads(PREREG.read_text())), "; full pages=0; rate=null; verdict=UNDETERMINED")
