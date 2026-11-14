"""Audit the USNO 1963 Soviet-Astronomy translation access route without promoting catalogues to measurements."""
import json
import re
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/tle_custody/usno_soviet_astronomy_translation_C241_LONTRA_R58.json"


def validate(record):
    if record.get("id") != "C241-LONTRA-R58" or record.get("evidence_class") != "SERIAL_TRANSLATION_CATALOGUE_AND_DUAL_LANGUAGE_ACCESS_ROUTE":
        raise ValueError("Wrong documentary evidence identity/class")
    origin = record.get("upstream", {})
    if (origin.get("source_id"), origin.get("digest_id"), origin.get("report_number"), origin.get("report_date")) != (
        "C241-LONTRA-R57", "C241-LONTRA-R56", "1521678463", "1963-06-19"
    ):
        raise ValueError("Upstream attribution changed")
    if origin.get("conflict") != "ISSUE_NUMBER_MONTH_UNRESOLVED" or "no. 5, May 1963" not in origin.get("claimed_russian_issue", ""):
        raise ValueError("Unresolved original citation silently changed")
    cat = record.get("catalog", {})
    if cat.get("institution") != "United States Naval Observatory Library" or cat.get("record_bib_id") != "09761":
        raise ValueError("Unrecognized library record")
    if cat.get("url") != "https://1535.sydneyplus.com/genieplus/final/ViewRecord.aspx?record=aa7060ad-8a7f-459c-a99a-6c4ff9955c7d&template=Books":
        raise ValueError("Catalogue permalink changed")
    if cat.get("translation_of") != "Astronomicheskii zhurnal" or cat.get("title") != "Soviet astronomy. AJ":
        raise ValueError("Not the documented translation series")
    if (cat.get("catalogue_number_translation"), cat.get("catalogue_number_russian_original")) != ("QB 1 .A456", "QB 1 .A455"):
        raise ValueError("Russian versus translation catalogue numbers conflated")
    if cat.get("holdings_english") != "Vol. 1 (1957)–Vol. 16 (1972/73)":
        raise ValueError("Holdings range changed")
    replay = cat.get("catalogue_replay", {})
    if replay.get("status") != 200 or replay.get("bytes") != 249067:
        raise ValueError("Catalogue HTML replay not documented")
    if not re.fullmatch(r"[a-f0-9]{64}", str(replay.get("sha256", ""))) or replay["sha256"] != "d1b1efbc8db7e7d39692ed61da31a3cb4b3c02f6c3c2480490f467fe0c59bc85":
        raise ValueError("Catalogue digest altered")
    if "not article" not in replay.get("scope", ""):
        raise ValueError("HTML digest cannot certify original article")
    limits = record.get("inference_limits", {})
    if limits.get("english_volume_1963_candidate") != 7 or limits.get("candidate_volume_is_inference") is not True:
        raise ValueError("Candidate English volume must remain explicitly inferential")
    forbidden_true = (
        "issue_by_issue_mapping_verified", "original_russian_volume_40_issue_3_seen",
        "original_russian_volume_40_issue_5_seen", "translation_article_seen",
        "intermediary_intelligence_report_seen", "independent_sensor_identified",
        "contacting_institution"
    )
    if any(limits.get(key) is not False for key in forbidden_true):
        raise ValueError("Catalogue cannot be promoted to direct article/sensor/access claim")
    unknown = ("original_article_author", "original_article_title", "original_article_pages", "original_article_pdf_sha256")
    if any(limits.get(key) is not None for key in unknown):
        raise ValueError("Cannot infer article metadata/hash without original")
    if limits.get("observation_rows_527_528_529") != [] or limits.get("activated_orbital_constraints") != 0:
        raise ValueError("No orbital measurement or constraint from library catalogue")
    return True


if __name__ == "__main__":
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("C241-LONTRA-R58 USNO catalogue custody: PASS (holdings/translation only)")
