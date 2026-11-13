"""Audit CGEO-18's geographically non-identifying FBIS city-center claim."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research/geo/cgeo18_fbis_city_center_phrase.json"
EXPECTED_SHA256 = "63654bcd90c0515f30e31ed511a12a05f170ff4470e3d8a6f40fca12012a1adb"
EXPECTED_SIZE = 126624


def validate(data: dict) -> None:
    if data["schema"] != "conde.gis.fbis-city-center-claim/v1" or data["id"] != "CGEO-18":
        raise ValueError("wrong version or identity")
    if data["municipality"]["ibge_code"] != "2908606" or data["municipality"]["state"] != "Bahia":
        raise ValueError("wrong Conde homonym")
    doc = data["document"]
    if (doc["sha256"] != EXPECTED_SHA256 or doc["byte_size"] != EXPECTED_SIZE
            or doc["pdf_page_one_based"] != 1 or doc["printed_marker"] != "FBIS 03"
            or doc["declassification_authority_visible"] != "NND 968063"
            or not doc["url"].startswith("https://")):
        raise ValueError("source custody drift")
    if doc["source_role"] != "contemporary_secondary_report_of_claim":
        raise ValueError("FBIS is not an event sensor")
    if doc["original_portuguese_audio_acquired"] is not False or doc["original_portuguese_words_verified"] is not False:
        raise ValueError("underlying Portuguese audio/text not recovered")
    t = data["transcript"]
    if (t["broadcast_header_printed"] != "RIO DE JANEIRO RADIO TUPI IN PORTUGUESE 2330 8 NOV 63 W"
            or t["reported_municipality_english"] != "REPORTS FROM THE MUNICIPALITY OF CONDE"
            or t["location_phrase_english"] != "FELL IN THE CENTER OF THE CITY"
            or t["processing_line_printed"] != "9 NOV 111A RWS/GY"):
        raise ValueError("verbatim wording mismatch")
    if t["language_of_visible_transcript"] != "en" or t["underlying_broadcast_language_claimed"] != "pt":
        raise ValueError("translation mistaken for original Portuguese")
    if t["reported_utterance_not_primary_physical_observation"] is not True:
        raise ValueError("report promoted to physical observation")
    for k in ("reported_event_date", "reported_event_time", "verified_event_date",
              "verified_event_time", "broadcast_clock_timezone", "processing_line_semantics"):
        if t[k] is not None:
            raise ValueError("unverified chronology filled: " + k)
    geo = data["spatial_interpretation"]
    if geo["expression_kind"] != "INFORMAL_REPORTED_URBAN_CENTRALITY":
        raise ValueError("informal city center turned into physical fix")
    if geo["urban_seat_candidate_is_verified"] is not False:
        raise ValueError("urban seat assumed as exact center")
    for k in ("municipal_polygon_centroid_is_city_center",
              "praça_severiano_lima_1958_identity_confirmed", "other_square_identity_confirmed",
              "can_constrain_orbital_reentry"):
        if geo[k] is not False:
            raise ValueError("unsupported geographic inference: " + k)
    for k in ("matched_street", "matched_square", "matched_landmark", "source_coordinates",
              "geo_reference_control_points", "historical_center_point", "historical_center_polygon",
              "reported_impact_location", "legal_boundary_1963", "horizontal_accuracy_m", "crs"):
        if geo[k] is not None:
            raise ValueError("unsupported geocoding: " + k)
    if geo["epistemic_status"] != "DOCUMENTED_TEXTUAL_CLAIM_NOT_VERIFIED_GROUND_EVENT":
        raise ValueError("epistemic status promoted")
    links = {(edge["from"], edge["to"], edge["relation"]) for edge in data["dependency_graph"]}
    required = {
        ("CGEO-18", "C01", "SAME_TUPI_FBIS_REPORT_LINEAGE_NOT_NEW_WITNESS"),
        ("CGEO-18", "CGEO-17", "GEOGRAPHIC_INTERPRETATION_DEPENDS_ON_HISTORICAL_TOPONYM_CROSSWALK"),
    }
    if not required.issubset(links):
        raise ValueError("report dependency/independence broken")


def verify_source(path: Path) -> None:
    """Only claim a binary SHA match when the real PDF has been supplied."""
    raw = path.read_bytes()
    if len(raw) != EXPECTED_SIZE or hashlib.sha256(raw).hexdigest() != EXPECTED_SHA256:
        raise ValueError("different or incomplete FBIS PDF")


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--verify-pdf", type=Path, help="optional original downloaded PDF, never a fixture")
    args = p.parse_args()
    validate(json.loads(CONTRACT.read_text(encoding="utf-8")))
    if args.verify_pdf:
        verify_source(args.verify_pdf)
    print("CGEO-18: verified contract" + (" and source bytes" if args.verify_pdf else " (offline only)"))


if __name__ == "__main__":
    main()
