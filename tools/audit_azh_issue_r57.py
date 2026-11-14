"""Fail-closed audit of 1963 Soviet journal holdings and bibliographic chronology."""
import json
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "research/tle_custody/azh_1963_holdings_C241_LONTRA_R57.json"


def validate(record):
    if record.get("id") != "C241-LONTRA-R57":
        raise ValueError("Wrong evidence ID")
    source = record.get("upstream", {})
    if source.get("intermediary_us_report_number") != "1521678463" or source.get("intermediary_us_report_date") != "1963-06-19":
        raise ValueError("Intelligence report genealogy changed")
    original = record.get("original_publication", {})
    if (original.get("year"), original.get("volume"), original.get("claimed_issue"), original.get("claimed_month")) != (1963, 40, 5, "1963-05"):
        raise ValueError("The quoted bibliographic claim must remain exact")
    if original.get("actual_issue_month") is not None or original.get("facsimile_retrieved") is not False or original.get("original_pdf_sha256") is not None:
        raise ValueError("Cannot invent date, issue facsimile or original hash")
    if original.get("status") != "ORIGINAL_NOT_RETRIEVED":
        raise ValueError("Issue must remain unread")
    holdings = record.get("holdings", [])
    if len(holdings) != 2 or len({x.get("institution") for x in holdings}) != 2:
        raise ValueError("Two separate institutional catalogues required")
    if any((x.get("year"), x.get("volume"), x.get("issues_listed")) != (1963, 40, list(range(1, 7))) for x in holdings):
        raise ValueError("1963 volume and catalogue issue range must be preserved")
    if any(x.get("issue_original_seen") is not False or not str(x.get("catalogue_url", "")).startswith("https://") for x in holdings):
        raise ValueError("A holdings list is not a facsimile")
    main, secondary = holdings
    if main.get("http_status_observed") != 200 or main.get("html_bytes_observed") != 434958 or main.get("html_sha256_observed") != "f6a392494d5100a44a5343190561c81bb57d6366193c2dc113202b904848913f":
        raise ValueError("Live source HTML custody altered")
    if secondary.get("http_status_observed") != 403 or secondary.get("status") != "SEARCH_INDEX_EXCERPT_ONLY_REPLAY_403":
        raise ValueError("Do not claim direct download from second catalogue")
    chronology = record.get("chronology_review", {})
    if chronology.get("status") != "CITATION_CHRONOLOGY_UNRESOLVED" or "cannot prove" not in chronology.get("conclusion_not_allowed", ""):
        raise ValueError("No unverified correction of original issue date")
    limits = record.get("scientific_limits", {})
    if limits.get("norad_527_528_529_instrumental_observations") != [] or limits.get("activated_orbital_constraints") != 0 or limits.get("new_sensor_identified") is not False or limits.get("contact_with_institutions") is not False:
        raise ValueError("Bibliographic holdings cannot activate orbital constraints")
    return True


if __name__ == "__main__":
    validate(json.loads(PATH.read_text(encoding="utf-8")))
    print("C241-LONTRA-R57 bibliography: PASS (catalogue-level only)")
