"""CGEO-68: guard article boundaries and false-positive OCR cues."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "research/editorial/cgeo68_uh_article_boundary_20261115.json"
INVENTORY = ROOT / "research/editorial/cgeo65_uh_bn_inventory_20261115.json"
COVERS = ROOT / "research/editorial/cgeo66_uh_cover_dates_20261115.json"
PREREG = ROOT / "research/editorial/cgeo64_null_narrative_prereg_20261114.json"
PREVIOUS = ROOT / "research/editorial/cgeo67_uh_lexical_adjudication_20261115.json"
FROZEN = "0d13d9359080699e5f8402ca9b7014d7f1f6d59a"
EXPECTED = {
    "C68-A": ("00441", "1963-10-08", "CONTROL_OCT07", 7,
              "F03_FOUR_METER_HOLE",
              "afastamento de 4 metros em qualquer nova construção naquela artéria",
              "Municipal-building setback complaint about a building near number 192; no hole, crater or excavation in this passage."),
    "C68-B": ("00471", "1963-11-08", "TARGET_NOV04", 8,
              "F04_WINDOWS", "vinham à janela para espiar o tempo",
              "Window in the Stanislaw Ponte Preta column 'Cão – o Melhor Amigo, Como Sempre', not a window/opening in a metallic sphere. Separate article from the police report on buried statues on the same PDF page."),
}
BOUNDARY = {
    "issue_id": "00471",
    "pdf_page": 8,
    "fragment_A": "F03_FOUR_METER_HOLE",
    "fragment_B": "F04_WINDOWS",
    "article_A": "Polícia arranca confissão do pescador: roubei estátuas e enterrei em Rio Doce",
    "article_B": "Cão – o Melhor Amigo, Como Sempre (Stanislaw Ponte Preta)",
    "joint_article_with_both_fragments": False,
    "note": "Co-occurrence on a newspaper page is NOT co-occurrence in one article, still less in one Conde witness. The F03 wording is a same-day different-story lexical match, while singular janela is not the spacecraft F04 motif.",
}
COVERAGE = {
    "new_passages_adjudicated": 2,
    "fully_inspected_newspaper_pages_for_rates": 0,
    "fully_inspected_articles_for_rates": 0,
    "predeclared_slots_changed": 0,
    "baseline_rates": None,
    "fragment_verdicts": None,
    "first_pre_event_borrowing": None,
}
INTERPRETATION = {
    "verdict": "UNDETERMINED",
    "narrative_fabrication_proven": False,
    "chronology_same_day_known": False,
    "historical_center_1963": None,
    "orbital_constraint_activated": False,
}

def require(condition: bool, problem: str) -> None:
    if not condition:
        raise ValueError(problem)

def validate(doc: dict, inv: dict, covers: dict, prereg: dict, previous: dict) -> int:
    require((doc.get("type"), doc.get("id")) ==
            ("HistoricalPressArticleBoundaryAdjudication", "CGEO-68"), "identity")
    require(doc.get("issue") == "https://github.com/franklinbaldo/conde-incident/issues/887", "issue")
    require(doc.get("prereg_blob_sha") == FROZEN and
            doc.get("prereg_path") == "research/editorial/cgeo64_null_narrative_prereg_20261114.json", "frozen prereg")
    require(prereg.get("id") == "CGEO-64" and len(prereg["frozen_fbis_fragments"]) == 8, "prereg source")
    require((inv.get("id"), covers.get("id"), previous.get("id")) ==
            ("CGEO-65", "CGEO-66", "CGEO-67"), "upstream identities")
    require(doc.get("sources") == [
        "research/editorial/cgeo65_uh_bn_inventory_20261115.json",
        "research/editorial/cgeo66_uh_cover_dates_20261115.json",
        "research/editorial/cgeo67_uh_lexical_adjudication_20261115.json"
    ], "upstream documents")
    require("OCR is a lead only" in doc.get("method", ""), "OCR caveat")
    require(any(x.get("issue_id") == "00441" and x.get("status") ==
                "OCR_TOKEN_ONLY_NOT_ARTICLE_ADJUDICATED"
                for x in previous["unresolved_ocr_leads"]), "previous OCR trace")
    require(any(x.get("id") == "C67-C" and x.get("lexical_fragment_match") is True
                for x in previous["adjudicated_passages"]), "previous F03 passage")
    rows = doc.get("adjudications", [])
    require(len(rows) == 2 and {x.get("id") for x in rows} == set(EXPECTED), "exactly two passages")
    by_issue = {x["id"]: x for x in inv["issues"] if x["status"] == "PDF_BYTES_ACQUIRED"}
    by_date = {x["issue_id"]: x["date"] for x in covers["cover_dates"]}
    by_slot = {(x["date"], x["publication"]): x["week"] for x in covers["slots"]}
    by_fragment = {x["id"] for x in prereg["frozen_fbis_fragments"]}
    for row in rows:
        issue, day, week, page, fragment, wording, context = EXPECTED[row["id"]]
        require((row.get("issue_id"), row.get("date"), row.get("week"), row.get("pdf_page"),
                 row.get("fragment_id"), row.get("wording"), row.get("context")) ==
                (issue, day, week, page, fragment, wording, context), "immutable visual adjudication")
        require(row["publication"] == "UH_RE" and fragment in by_fragment, "publication/fragment")
        require(by_date[issue] == day and by_slot[(day, "UH_RE")] == week, "date/slot")
        require(1 <= page <= by_issue[issue]["pages"], "page range")
        require(row.get("source_sha256") == by_issue[issue]["sha256"] and
                row.get("source_url") == by_issue[issue]["url"], "source custody")
        require(row.get("fragment_match") is False and
                row.get("review") == "VISUAL_PASSAGE_AND_PDF_TEXT" and
                row.get("whole_page_read") is False and
                row.get("independent_conde_witness") is False, "false match or overclaim")
    require(doc.get("same_page_nonindependence") == BOUNDARY, "article boundary")
    require(doc.get("closes_upstream_ocr_lead") ==
            "CGEO-67/00441:p7/4 metros; CGEO-67 remains immutable historical record.", "OCR trace")
    require(doc.get("coverage") == COVERAGE, "no invented denominators")
    require(doc.get("interpretation") == INTERPRETATION, "no invented conclusion")
    require(len(doc.get("limits", [])) >= 5, "scientific limits")
    return len(rows)

if __name__ == "__main__":
    result = validate(*[json.loads(p.read_text(encoding="utf-8"))
                        for p in (DATA, INVENTORY, COVERS, PREREG, PREVIOUS)])
    print(f"CGEO-68: {result} passages checked, full-page denominator 0, baseline null, verdict UNDETERMINED")
