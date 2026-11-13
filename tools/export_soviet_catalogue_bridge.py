#!/usr/bin/env python3
"""C241-L29/L30 catalogue holdings -> candidate graph -> Lean/latent inputs.

Bibliographic listings cannot become tracking observations or active orbital
constraints. Upstream custodians own the original ledgers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOLDINGS = "research/tle_custody/soviet_1963_bibliographic_holdings_C241-L29.json"
CROSS = "research/tle_custody/soviet_1963_cross_id_C241-L30.json"
NASA = "research/tle_custody/nasa_527_1964_1967_crosswalk_C241-L28.json"
NASA1977 = "research/tle_custody/nasa_ssr_dec1977_528_identity_C241-L32.json"
MASEVICH = "research/tle_custody/masevich_periodicals_1963_C241-L34.json"
OUT = ROOT / "public/data/conde-soviet-catalogue-bridge.json"
IDS = ("C241-L29#1", "C241-L29#2")
OBJECTS = (527, 528, 529)
MISSING = ("original_soviet_designation", "original_soviet_page",
           "original_soviet_issue_scan_sha256", "original_epoch_utc",
           "original_station", "original_measurement",
           "original_orbit_elements", "frame", "time_standard",
           "measurement_units", "instrument_sigma", "origin_of_orbit_fit",
           "same_tracking_as_western")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("Soviet catalogue bridge: " + message)


def build(hold: dict, cross: dict, nasa: dict, nasa1977: dict, masevich: dict, parent_hashes: dict) -> dict:
    require(hold["schema"] == "conde.soviet_1963_holdings/v1"
            and hold["id"] == "C241-L29"
            and hold["verified_observations"] == 0
            and hold["orbital_constraint_activated"] is False,
            "holdings are not observational records")
    rows = hold["records"]
    require(len(rows) == 2 and [x["id"] for x in rows] == list(IDS)
            and len({x["url"] for x in rows}) == 2,
            "two distinct institutional catalogue listings required")
    for row in rows:
        require(row["year"] == 1963 and row["http_status"] == 200
                and row["facsimile_read"] is False
                and row["issue_pdf_sha256"] is None
                and row["primary_observation_527_528_529"] is None
                and len(row["sha256"]) == 64
                and row["bytes"] > 0, "invalid holdings evidence level")
    require(cross["schema"] == "conde.soviet-1963-cross-id-readiness/v1"
            and cross["id"] == "C241-L30"
            and cross["upstream"]["holdings"] == HOLDINGS
            and cross["upstream"]["nasa_527"] == NASA,
            "cross-identification lineage mismatch")
    checks = cross["bibliographic_cross_checks"]
    require(len(checks) == 2
            and {c["id"] for c in checks} ==
            {"CNII-AA00566856", "CNII-AA00826990"},
            "unexpected CiNii candidates")
    for check in checks:
        require(check["status"] in (
                    "LIBRARY_METADATA_ONLY",
                    "NO_1963_HOLDING_SHOWN_IN_THIS_CATALOG_VIEW")
                and check["pdf_sha256"] is None
                and check["issue_1963_content_seen"] is False
                and check["independent_observation"] is False
                and check["same_publication_proven"] is False
                and len(check["capture_sha256"]) == 64
                and check["capture_bytes"] > 0,
                "CiNii metadata falsely promoted")
    require(cross["western_object_aliases"][0]["western_crosswalk"]
            == "CONFIRMED_PRIMARY_NASA_CATALOG_ONLY"
            and cross["western_object_aliases"][0]["western_crosswalk_source"]
            == "C241-L28"
            and [r["norad"] for r in cross["western_object_aliases"]]
            == list(OBJECTS)
            and all(r["soviet_record_id"] is None
                    for r in cross["western_object_aliases"])
            and all(r["western_crosswalk"] == "PENDING_PRIMARY_NUMBER_MATCH"
                    for r in cross["western_object_aliases"][1:]),
            "NASA 527 is not a Soviet 528/529 cross-identification")
    require(nasa["schema"] == "conde.nasa-527-1964-1967-crosswalk/v1"
            and nasa["id"] == "C241-L28"
            and nasa["status"] == "PRIMARY_DOCUMENTARY_CROSSWALK_ONLY"
            and len(nasa["source_documents"]) >= 1
            and all(doc["row"]["catalog_number_printed"] == 527
                    and doc["row"]["international_designator_printed"] == "1963 03A"
                    for doc in nasa["source_documents"]),
            "primary NASA documentary number crosswalk absent")
    # This is a primary *retrospective catalogue* identity, not 1963
    # instrument data. Keep the 2026-11-13 C241-L30 source ledger untouched:
    # its old western alias state describes what was known when audited.
    require(nasa1977["schema"] == "conde.nasa-retrospective-satellite-catalog-crosswalk/v1"
            and nasa1977["record_id"] == "C241-L32", "1977 identity source mismatch")
    source = nasa1977["source"]
    require(source["ntrs_id"] == "19780009188"
            and source["ntrs_url"] == "https://ntrs.nasa.gov/citations/19780009188"
            and source["pdf_url"].endswith("/19780009188.pdf")
            and source["pdf_sha256"] ==
            "c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8"
            and source["pdf_bytes"] == 11563410
            and source["date_published"] == "1977-12-31"
            and source["printed_page"] == 43
            and source["page_index_zero_based"] == 46
            and source["full_page_visual_review"] == "VISUALLY_VERIFIED_1977_SOURCE"
            and source["document_kind"] ==
            "ORIGINAL_NASA_1977_PUBLICATION_RETROSPECTIVE_CATALOG_NOT_1963_SENSOR",
            "1977 publication identity or facsimile custody changed")
    row = nasa1977["row"]
    require(row["international_designator_printed"] == "1963 003B"
            and row["catalog_number_printed"] == 528
            and row["identity_match"] == "DIRECT_VISUAL_VERIFIED"
            and row["reported_decay_day_from_1977_table"] == "1963-11-08"
            and row["decay_date_cell_crosscheck"] == "1963-11-08"
            and all(row[k] is None for k in (
                "source_528_sensor_id", "original_1963_tle_pair",
                "original_1963_observation_epoch_utc", "reentry_physical_time_utc",
                "reentry_location", "decay_day_timezone", "decay_day_error_seconds")),
            "1977 row cannot provide unseen time, place, sensor, or TLE")
    controls = nasa1977["control_rows"]
    require(len(controls) == 2 and
            [(c["international_designator_printed"], c["catalog_number_printed"],
              c["decay_day_printed"]) for c in controls] ==
            [("1963 003A", 527, "1969-01-09"),
             ("1963 003C", 529, "1963-12-31")],
            "1977 control rows or object ordering changed")
    provenance = nasa1977["independence"]
    require(provenance["chronology_not_contemporary_to_1963"] is True
            and provenance["does_not_constitute_additional_radar_tracking"] is True
            and provenance["second_document_does_not_independently_validate_reentry"] is True
            and provenance["independent_528_instrumental_observations_added"] == 0
            and nasa1977["graph"]["physical_constraints_activated"] == 0
            and nasa1977["graph"]["lean_predicates_activated"] == 0
            and nasa1977["graph"]["change_to_simulation_parameters"] is False,
            "retrospective catalogue falsely promoted to sensor")
    require(any(c["occurrence"] == "C197#1" for c in nasa1977["context"]),
            "missing 1963 contemporary catalogue link")
    joins = cross["candidate_joins"]
    require(len(joins) == 6
            and {(j["source_holding_id"], j["target_norad"])
                 for j in joins} == {(s, n) for s in IDS for n in OBJECTS},
            "incomplete or duplicated six-way retrieval candidates")
    for join in joins:
        require(join["join_status"] == "PENDING_NO_ISSUE_FACSIMILE"
                and all(join[k] is None for k in MISSING)
                and join["independent_sensor_confirmed"] is False
                and join["physical_constraint_active"] is False,
                "a candidate was upgraded without primary measurements")
    counts = cross["result"]
    require(counts["candidate_joins_pending"] == 6
            and counts["candidate_joins_confirmed"] == 0
            and counts["contemporary_1963_soviet_527_528_529_instrument_observations_verified"] == 0
            and counts["independent_measurements_added"] == 0
            and counts["orbital_constraints_activated"] == 0
            and counts["lean_activated"] is False,
            "published counts conflict with missing instrumental evidence")
    # C241-L34 is a contemporary *bibliographic mention* in third-party
    # digitized pages, not a station's 1963 observations. Two named periodicals
    # may resemble L29 holdings, but their edition identity is not established.
    require(masevich["schema"] == "conde.contemporary_bibliographic_locator/v1"
            and masevich["id"] == "C241-L34"
            and masevich["target_objects"] == list(OBJECTS)
            and masevich["dependencies"] == ["C241-L29", "C241-L31"]
            and masevich["epistemic_level"] ==
            "1963_CONTEMPORARY_BIBLIOGRAPHIC_REFERENCE_ONLY",
            "contemporary bibliography identifier or dependencies changed")
    src = masevich["source"]
    require(src["russian_preface_date"] == "1963-02"
            and src["russian_edition_year"] == 1963
            and src["source_authentication"] ==
            "THIRD_PARTY_PAGE_IMAGES_VISUALLY_INSPECTED_NOT_MASTER_AUTHENTICATED"
            and src["landing_url"] == "https://djvu.online/file/raBEGf36i2gfZ"
            and src["landing_html_sha256"] ==
            "9e142d1ac2d17be5ffd44e4425baa21389f8075951c4704e2035f0fb8beb0a92"
            and src["landing_html_bytes"] == 806435
            and len(src["images"]) == 2
            and [(a["viewer_page"], a["printed_page"], a["sha256"], a["bytes"])
                 for a in src["images"]] == [
                (6, None, "0d68650aa352f7404f4251abf53c3d117efd3dde377b6c5667df85516089f901", 121794),
                (7, 6, "fea39a91dae6ce25b977e4562c758818dc44667dc7559b7d99f9ecc6231f4bb2", 44202)],
            "1963 preface custody or page provenance changed")
    bibliography = masevich["bibliography"]
    require([b["title"] for b in bibliography] == [
                "Искусственные спутники Земли",
                "Бюллетень станций оптических наблюдений искусственных спутников"]
            and [b["mention_location"] for b in bibliography] == [
                "preface spans images 006 and 007", "printed page 6 / image 007"]
            and all(b["catalog_or_original_volume_retrieved"] is False
                    for b in bibliography), "unverified bibliography promoted")
    limits = masevich["interpretive_limits"]
    require(limits["target_specific_primary_measurements"] == 0
            and limits["observed_objects_identified_in_pages"] == []
            and limits["station_ephemeris_or_tle_record_found"] is False
            and limits["independent_physical_observation"] is False
            and limits["orbital_constraint_activated"] is False
            and limits["publication_independence_not_established"] is True
            and limits["no_facsimile_of_bulletin_issue_retrieved"] is True
            and limits["february_1963_preface_does_not_cover_november_1963"] is True,
            "bibliography cannot become a contemporaneous orbital sensor")
    graph = []
    for record in rows:
        graph.append({
            "from": record["id"], "to": "C241-L30",
            "type": "BIBLIOGRAPHIC_HOLDING_NOT_MEASUREMENT",
            "source_url": record["url"],
            "html_sha256": record["sha256"],
            "issue_numbers": record["issues"],
            "issue_page": None,
        })
    for check in checks:
        graph.append({
            "from": check["id"], "to": check["possible_relation_to"],
            "type": ("UNCONFIRMED_TITLE_SIMILARITY"
                     if check["possible_relation_to"]
                     else "NO_DOCUMENTED_MATCH"),
            "source_url": check["url"],
            "html_sha256": check["capture_sha256"],
            "issue_page": None,
        })
    for join in joins:
        graph.append({
            "from": join["source_holding_id"],
            "to": f"NORAD_{join['target_norad']}_latent_track",
            "type": "RETRIEVAL_CANDIDATE_NOT_IDENTIFIED_TRACK",
            "original_page": None,
            "observing_epoch_utc": None,
            "instrument_sigma": None,
            "activation": False,
        })
    for i, periodical in enumerate(bibliography, 1):
        graph.append({
            "from": "C241-L34",
            "to": f"SOVIET_PERIODICAL_SEARCH_TITLE_{i}",
            "type": "CONTEMPORARY_BIBLIOGRAPHIC_MENTION_NOT_MEASUREMENT",
            "title": periodical["title"],
            "source_url": src["images"][0 if i == 1 else 1]["url"],
            "source_webp_sha256": src["images"][0 if i == 1 else 1]["sha256"],
            "printed_page": None if i == 1 else 6,
            "observing_epoch_utc": None,
            "sensor": None,
            "activation": False,
        })
    for related in masevich["dependencies"]:
        graph.append({
            "from": "C241-L34", "to": related,
            "type": "RESEARCH_CONTEXT_NOT_VERIFIED_SAME_ISSUE_OR_TRACK",
            "publication_identity_confirmed": False,
            "target_norad_identified": False,
            "activation": False,
        })
    identities = [
        {"source_id": "C241-L28", "norad": 527, "designator": "1963 03A",
         "evidence_level": "ORIGINAL_NASA_RETROSPECTIVE_CATALOG_ONLY"},
        {"source_id": "C241-L32", "norad": 528, "designator": "1963 003B",
         "evidence_level": "VISUALLY_VERIFIED_NASA_1977_CATALOG_ONLY"},
        {"source_id": "C241-L32", "norad": 529, "designator": "1963 003C",
         "evidence_level": "VISUALLY_VERIFIED_NASA_1977_CONTROL_ROW_ONLY"},
    ]
    for identity in identities[1:]:
        graph.append({
            "from": identity["source_id"],
            "to": f"NORAD_{identity['norad']}_latent_track",
            "type": "RETROSPECTIVE_NASA_IDENTITY_NOT_SOVIET_OBSERVATION",
            "international_designator": identity["designator"],
            "ntrs_id": source["ntrs_id"],
            "pdf_sha256": source["pdf_sha256"],
            "printed_page": source["printed_page"],
            "observation_epoch_utc": None,
            "instrument_covariance": None,
            "activation": False,
        })
    return {
        "schema": "conde.soviet-catalogue-scientific-bridge/v1",
        "id": "ABELHA-SOVIET-C241-L29-L30-01",
        "parent_sha256": parent_hashes,
        "source_occurrences": list(IDS),
        "bibliographic_catalogue_ids": [c["id"] for c in checks],
        "nasa_documentary_crosswalk": "C241-L28:527=1963 03A",
        "primary_nasa_catalogue_identifications": identities,
        "primary_nasa_1977_source": {
            "source_id": "C241-L32", "pdf_url": source["pdf_url"],
            "pdf_sha256": source["pdf_sha256"],
            "printed_page": source["printed_page"],
            "editorial_date": source["date_published"],
            "instrument_observation_epoch": None,
            "decay_day_528": row["reported_decay_day_from_1977_table"],
            "physical_reentry_time": None, "physical_reentry_place": None,
        },
        "contemporary_1963_bibliographic_lead": {
            "source_id": "C241-L34",
            "preface_date": src["russian_preface_date"],
            "source_kind": src["source_authentication"],
            "landing_url": src["landing_url"],
            "source_page_webp_sha256": [a["sha256"] for a in src["images"]],
            "periodical_titles": [b["title"] for b in bibliography],
            "relationship_to_holdings": "SEARCH_CONTEXT_NOT_PROVEN_SAME_ISSUE",
            "original_issue_facsimile": None,
            "target_specific_observation_epoch": None,
            "instrument_covariance": None,
            "lean_candidate": "Conde1963.sovietContemporaryBibliographicLeads",
            "sensor_count_added": 0,
            "activation": False,
        },
        "source_relation": "TWO_TITLES_HOLDINGS_NOT_INDEPENDENT_TRACKING",
        "evidence_level": "BIBLIOGRAPHIC_METADATA_NOT_INSTRUMENTAL",
        "candidate_join_count": 6,
        "source_dependency_graph": graph,
        "lean_module": "Conde1963.SovietCatalogueCandidate",
        "lean_catalogue_identity_declaration": "Conde1963.nasaRetrospective1977Labels",
        "lean_status": "TYPED_RETRIEVAL_CANDIDATE_NOT_PHYSICAL_THEOREM",
        "simulator_latent_parameters": [
            {"name": f"soviet_1963_independent_track_{n}_unknown",
             "norad": n, "value": None, "active": False}
            for n in OBJECTS
        ],
        "temporal_alignment": None,
        "instrument_covariance": None,
        "original_facsimile_sha256": None,
        "independent_observations": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": cross["next_test"],
    }


def render() -> bytes:
    paths = (HOLDINGS, CROSS, NASA, NASA1977, MASEVICH)
    raw = [(ROOT / p).read_bytes() for p in paths]
    payload = build(*(json.loads(b) for b in raw),
                    {p: hashlib.sha256(b).hexdigest()
                     for p, b in zip(paths, raw)})
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = render()
    require(len(payload) <= 20_000, "oversized published JSON")
    if args.write:
        OUT.write_bytes(payload)
    else:
        require(OUT.read_bytes() == payload, "published JSON is stale")
    print("SOVIET_CATALOGUE_BRIDGE_OK", len(payload))


if __name__ == "__main__":
    main()
