"""Audit scanned Hungarian Academy bibliography without inventing satellite observations."""
from __future__ import annotations
import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "research/tle_custody/hungarian_interobs_bibliography_C241_LONTRA_R64.json"
PDF_HASH = "cc91eb383c90ecd5f15f5d2db89e08860642c6a8a683401350e97af8bb4098ac"
SOURCE = "https://real-ms.mtak.hu/30094/1/1.pdf"
TITLES = {
    27: ("Международное сотрудничество", 1, "Москва", 1962),
    28: ("О точности базисных визуальных наблюдений", 2, "Варшава", 1963),
    29: ("О вычислении мгновенных элементов орбиты", 3, "Берлин", 1964),
}

def validate(data: dict) -> bool:
    if data.get("id") != "C241-LONTRA-R64" or data.get("schema") != "conde.archival_bibliography_locator/v1":
        raise ValueError("source ID/schema altered")
    s = data.get("source", {})
    invariants = {
        "url": SOURCE, "pdf_sha256": PDF_HASH, "pdf_size_bytes": 46217178,
        "pdf_pages": 167, "source_page_appendix_heading_one_based": 93,
        "source_page_bibliography_one_based": 95, "appendix_printed_page": 3,
        "source_publication_year_known": False,
        "whole_pdf_download": "IFRO_EXECUTOR_HTTP_SUCCESS",
        "visual_verification": "RENDERED_PAGES_93_AND_95_INSPECTED",
        "type": "LATER_AUTHOR_BIBLIOGRAPHY_SCANNED_IN_HUNGARIAN_ACADEMY_ARCHIVE",
    }
    for k,v in invariants.items():
        if s.get(k) != v:
            raise ValueError("source custody altered: " + k)
    if "Almár Iván" not in s.get("appendix_heading_original", ""):
        raise ValueError("bibliography author/appendix changed")
    refs = data.get("references")
    if not isinstance(refs, list) or len(refs) != 3:
        raise ValueError("source references incomplete")
    for item in refs:
        num=item.get("item")
        if num not in TITLES:
            raise ValueError("unverified bibliography number")
        prefix,issue,place,year = TITLES[num]
        if (not item.get("title_original", "").startswith(prefix)
            or item.get("series") != "Наблюдения ИСЗ" or item.get("issue") != issue
            or item.get("place") != place or item.get("year") != year):
            raise ValueError("bibliographic source values changed")
    if [i["item"] for i in refs] != [27,28,29]:
        raise ValueError("bibliography order/IDs altered")
    if refs[1].get("subject_observation_year") != 1962:
        raise ValueError("1962 observation programme falsely redated")
    c=data.get("context", {})
    if (c.get("kyiv_holding_title"),c.get("kyiv_holding_issue"),c.get("kyiv_holding_year")) != ("Наблюдения ИСЗ",2,1963):
        raise ValueError("Kyiv catalog crosswalk altered")
    if c.get("different_series_first_1963_issue") != 32 or c.get("different_series") != "Бюллетень станций оптического наблюдения ИСЗ":
        raise ValueError("two series conflated")
    if c.get("series_identity_status") != "ISSUE_2_BIBLIOGRAPHIC_LINK_NOT_FACSIMILE_OF_THE_ORIGINAL":
        raise ValueError("bibliography promoted to original")
    b=data.get("boundaries", {})
    for k in ("original_1963_article_recovered", "original_soviet_bulletin_32_recovered",
              "observation_date_1963_in_article_demonstrated", "independent_sensor_measurements_confirmed", "archive_contacted"):
        if b.get(k) is not False:
            raise ValueError("unsupported evidence promotion: " + k)
    if b.get("observations_identified_norad_527_528_529") != [] or b.get("new_orbital_constraints") != 0:
        raise ValueError("invented NORAD observation or orbit constraint")
    if b.get("epistemic_class") != "RETROSPECTIVE_BIBLIOGRAPHY_NOT_OBSERVATION":
        raise ValueError("wrong evidentiary class")
    return True

if __name__ == "__main__":
    validate(json.loads(MANIFEST.read_text(encoding="utf8")))
    print("C241-LONTRA-R64 PASS: 1963 Warsaw bibliography is not a target observation")
