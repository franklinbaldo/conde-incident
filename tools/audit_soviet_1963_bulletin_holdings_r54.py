"""Guard against promoting Soviet optical-bulletin catalogue holdings to measurements."""
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "research/tle_custody/soviet_optical_bulletin_holdings_C241_LONTRA_R54.json"
ISSUES = [32, 33, 34, 35, 36, 37]
LOCATORS = [
    ("R54-UA1", "institutional_holdings_list", "maoling.mao.kiev.ua"),
    ("R54-UA2", "same_institution_duplicate_holdings_list", "maoling.mao.kiev.ua"),
    ("R54-JP1", "independent_bibliographic_locator_not_sensor", "ci.nii.ac.jp")
]


def audit(data):
    if (data.get("id"), data.get("predecessor_id"), data.get("evidence_class")) != (
        "C241-LONTRA-R54", "C241-LONTRA-R53", "INSTITUTIONAL_SERIAL_HOLDINGS_METADATA_ONLY"
    ):
        raise ValueError("source lineage or epistemic class changed")
    subject = data["subject"]
    if subject.get("catalog_year") != 1963 or subject.get("issue_numbers_in_ukrainian_catalog") != ISSUES:
        raise ValueError("wrong year/issue list")
    for key in ("issue_publication_months_verified", "issue_contents_read",
                "november_1963_coverage_verified", "target_designations_in_contents_verified",
                "physical_facsimile_retrieved"):
        if subject.get(key) is not False:
            raise ValueError("uninspected content asserted: " + key)
    for key in ("facsimile_pdf_sha256", "pages_or_observation_utc_verified"):
        if subject.get(key) is not None:
            raise ValueError("invented source metadata: " + key)
    sources = data.get("locators")
    if not isinstance(sources, list) or len(sources) != 3:
        raise ValueError("unexpected catalogues")
    for src, (sid, role, domain) in zip(sources, LOCATORS):
        if (src.get("id"), src.get("role")) != (sid, role) or domain not in src.get("url", ""):
            raise ValueError("locator identity changed")
        if src.get("retrieved_facsimile") is not False or src.get("content_sha256") is not None:
            raise ValueError("invented facsimile")
        if src.get("independent_instrumental_observation") is not False:
            raise ValueError("false sensor independence")
    for src in sources[:2]:
        if src.get("holdings_year") != 1963 or src.get("issues") != ISSUES:
            raise ValueError("Ukrainian catalogue transcription changed")
    if sources[0].get("direct_jatoba_http_status") is not None or sources[0].get("direct_jatoba_error_class") != "TLS_HOSTNAME_MISMATCH":
        raise ValueError("invalid direct access")
    if sources[1].get("same_catalog_as") != "R54-UA1":
        raise ValueError("duplicate Ukrainian pages counted as two sources")
    if sources[2].get("catalog_id") != "AA00566856" or sources[2].get("kyoto_holdings") != "32-59, 1963-1971":
        raise ValueError("Japanese locator changed")
    limits = data["epistemic_limits"]
    for key in ("copies_or_scans_inspected", "independent_instrumental_sensors",
                "new_527_528_529_observations_1963_11_07_to_09", "new_orbital_constraints_activated"):
        if type(limits.get(key)) is not int or limits[key] != 0:
            raise ValueError("unsupported observations: " + key)
    if limits.get("bibliographic_institutions") != 2:
        raise ValueError("catalogue institutions miscounted")
    for key in ("current_physical_holdings_verified", "same_scanned_copy_proven",
                "bibliographic_issue_number_establishes_observation_date", "external_institution_contact_sent"):
        if limits.get(key) is not False:
            raise ValueError("unsupported inference: " + key)
    return "SIX_1963_ISSUES_INDEXED_ONLY"


if __name__ == "__main__":
    print(audit(json.loads(SOURCE.read_text(encoding="utf-8"))))
