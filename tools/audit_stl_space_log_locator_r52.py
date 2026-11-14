"""Audit bibliographic locators without promoting them to orbital observations."""
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "research/tle_custody/stl_space_log_locator_r52.json"
TARGETS = (
    ("R52-S1", "secondary_commercial_inventory", "www.bolerium.com", 429),
    ("R52-S2", "digitized_bibliographic_record_snippet_only", "books.google.com", 200),
    ("R52-S3", "previously_verified_nasa_reproduction", "ntrs.nasa.gov", None),
)

def audit(record: dict) -> str:
    if record.get("id") != "C241-LONTRA-R52" or record.get("predecessor_id") != "C241-LONTRA-R51":
        raise ValueError("wrong evidence lineage")
    if record.get("evidence_class") != "CATALOG_AND_COMMERCIAL_INVENTORY_ONLY":
        raise ValueError("catalog cannot become a facsimile")
    target = record.get("target", {})
    if (target.get("volume"), target.get("issue"), target.get("year")) != (3, 4, 1963):
        raise ValueError("target issue changed")
    for key in ("physical_original_retrieved", "original_pages_inspected"):
        if target.get(key) is not False:
            raise ValueError("unread original promoted")
    for key in ("original_page_count", "original_pdf_sha256", "perigee_apogee_units_from_original"):
        if target.get(key) is not None:
            raise ValueError("invented original metadata")
    sources = record.get("sources", [])
    if not isinstance(sources, list) or len(sources) != len(TARGETS):
        raise ValueError("wrong locator count")
    for source, (identifier, role, domain, http) in zip(sources, TARGETS):
        if source.get("id") != identifier or source.get("role") != role or domain not in source.get("url", ""):
            raise ValueError("source identity changed")
        if source.get("independent_instrumental_observation") is not False:
            raise ValueError("editorial locator falsely counted as sensor")
        if identifier != "R52-S3":
            if source.get("source_payload_sha256") is not None or source.get("facsimile_retrieved") is not False:
                raise ValueError("source bytes were never custodied")
            if source.get("web_index_read") is not True or source.get("jatoba_http_code") != http:
                raise ValueError("source access audit changed")
        else:
            if source.get("linked_evidence_id") != "C241-LONTRA-R51" or source.get("new_bytes_retrieved_in_this_round") is not False:
                raise ValueError("NASA reproduction counted as new source")
    if sources[1].get("contains_issue_4") is not None:
        raise ValueError("Google Books issue coverage not verified")
    limits = record.get("limitations", {})
    for key in ("original_units_verified", "google_books_issue_4_contents_verified",
                "commercial_inventory_proves_current_archival_access",
                "direct_stl_to_soviet_1964_copying_demonstrated",
                "external_institution_contact_sent"):
        if limits.get(key) is not False:
            raise ValueError("unsupported conclusion " + key)
    if limits.get("original_fascicle_access") != "NOT_RETRIEVED" or limits.get("commercial_index_http429_is_not_absence") is not True:
        raise ValueError("incorrect archival state")
    for key in ("observations_527_528_529_1963_11_07_to_09",
                "independent_instrumental_sensors_added", "new_orbital_constraints_activated"):
        if type(limits.get(key)) is not int or limits[key] != 0:
            raise ValueError("unsupported orbital activation " + key)
    return "LOCATORS_ONLY_NO_ORIGINAL_NO_NEW_SENSOR"

if __name__ == "__main__":
    print(audit(json.loads(SOURCE.read_text(encoding="utf-8"))))
