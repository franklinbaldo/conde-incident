"""Fail-closed audit of the scoped 00472 visual-page survey."""
from __future__ import annotations
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/archive/ultima_hora_ne_00472_page_review_R68.json"
EXPECTED_HASH = "8564c0c8c26857e0feda54fc5da0f9d3ca0c34c8de02c44e3074aa79a101cece"

def validate(d: dict) -> bool:
    if d.get("schema") != "conde.newspaper_page_review/v1" or d.get("id") != "C241-LONTRA-R68" or d.get("refs_issue") != 871:
        raise ValueError("wrong review identity")
    source = d["source"]
    if (source["collection_id"], source["edition"], source["date_printed"]) != ("765147", "00472", "1963-11-09"):
        raise ValueError("wrong source edition")
    if source["pdf_sha256"] != EXPECTED_HASH or source["pdf_bytes"] != 5275519 or source["pdf_pages"] != 10 or source["redownload"] is not False:
        raise ValueError("source provenance mismatch")
    if source["pdf_url"] != "https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00472.pdf":
        raise ValueError("incorrect source URL")
    if d["method"]["full_body_reading"] is not False or d["method"]["negative_is_page_scoped"] is not False:
        raise ValueError("scope promoted without reading")
    pages = d["pages"]
    if len(pages) != 10 or [x["pdf_page"] for x in pages] != list(range(1, 11)):
        raise ValueError("incorrect page coverage")
    for i, page in enumerate(pages):
        expected = "CAPA_VERIFICADA_R67" if i == 0 else "PANORAMA_MANCHETES_LAYOUT"
        if (page["status"], page["review_scope"], page["event_time_literal"], page["conde_ba_article_verified"], page["independent_witness_verified"], page["full_page_body_read"]) != ("EXAMINADA", expected, None, False, False, False):
            raise ValueError("unsupported conclusion on page " + str(i + 1))
    hits = d["false_positives"]
    if [(x["pdf_page"], x["term"], x["reading"]) for x in hits] != [
        (7, "Conde", "Av. Conde da Boa Vista"), (9, "Conde", "Av. Conde da Boa Vista")
    ]:
        raise ValueError("false positive provenance")
    result = d["result"]
    expected_result = {
        "pages_visually_reviewed": 10, "new_internal_pages_reviewed": 9,
        "pages_remaining_for_panorama_of_all_four_editions": 35,
        "confirmed_independent_event_time": None, "source_chain": "UNDETERMINED",
        "whole_edition_no_article_claim": False, "whole_edition_no_time_claim": False,
        "physical_orbital_constraint_added": False
    }
    for k, v in expected_result.items():
        if result.get(k, object()) != v:
            raise ValueError("false scientific promotion " + k)
    return True

if __name__ == "__main__":
    assert validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("PASS C241-LONTRA-R68: 9 internal pages surveyed, full texts NOT_READ, event clock unconfirmed")
