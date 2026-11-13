#!/usr/bin/env python3
"""C241-L37 institutional/retrospective source routing into the pending 527-529 graph.

No scientific observation is inferred from a bibliography or a 2007 testimony.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from export_soviet_catalogue_bridge import render as render_catalogue
from verify_soviet_raw_observations_route import validate as validate_route

ROOT = Path(__file__).resolve().parents[1]
ROUTE = Path("research/tle_custody/soviet_raw_observations_route_C241-L37.json")
PARENT = Path("public/data/conde-soviet-catalogue-bridge.json")
OUT = ROOT / "public/data/conde-soviet-raw-route-bridge.json"
OBJECTS = (527, 528, 529)


def require(condition: bool, problem: str) -> None:
    if not condition:
        raise ValueError("Soviet raw-route bridge: " + problem)


def build(route: dict, catalogue: dict, hashes: dict) -> dict:
    # Custodian's validator checks the original manifest. It does not replay
    # a 7 MB PDF here; the PDF SHA is the upstream custodian's statement.
    try:
        validate_route(route)
    except (AssertionError, KeyError, TypeError) as exc:
        raise ValueError("Soviet raw-route bridge: custody not validated") from exc
    require(catalogue["id"] == "ABELHA-SOVIET-C241-L29-L30-01" and
            catalogue["schema"] == "conde.soviet-catalogue-scientific-bridge/v1" and
            catalogue["source_occurrences"] == ["C241-L29#1", "C241-L29#2"] and
            catalogue["candidate_join_count"] == 6 and
            catalogue["independent_observations"] == 0 and
            catalogue["activation"] is False and
            catalogue["physical_domain_effect"] == "THETA_UNCHANGED" and
            all(item["active"] is False and item["value"] is None
                for item in catalogue["simulator_latent_parameters"]),
            "old six candidates were altered or promoted")
    original = route["retrospective_author_source"]
    distinction = route["source_distinction"]
    followups = route["bibliographic_followups"]
    require(original["url"] == "https://iki.cosmos.ru/sites/default/files/publications/2007pervaya_r.pdf" and
            original["sha256"] == "8dc0d5b54985ab53d394babbad36da03ae02cef17f5ad897ad94e05acf9005f5" and
            original["hash_scope"].startswith("entire 2007 host PDF") and
            distinction["same_serial_title_proven"] is False and
            distinction["raw_series_target_measurements_read"] is False and
            route["dependencies"] == ["C241-L29", "C241-L31", "C241-L34", "C241-L35"] and
            len(followups) == 2 and
            followups[0]["catalog_record_id"] == "000200_000018_RU_NLR_INFOCOMM10_1000287767" and
            followups[0]["period_described_in_catalogue"] == "June 1963" and
            followups[0]["source_bytes_sha256"] is None and
            followups[0]["target_527_528_529_explicitly_named"] is False and
            followups[1]["source_bytes_sha256"] is None and
            route["new_numeric_observables"] == 0,
            "2007 retrospective claim/1964 catalogue cannot turn into 1963 targets")
    graph = [
        {"from": "C241-L37", "to": "SOVIET_METHODS_SERIAL", "relation": "RETROSPECTIVE_AUTHOR_DESCRIBES_METHODS_SERIES", "active": False},
        {"from": "C241-L37", "to": "SOVIET_RAW_RESULTS_SERIAL", "relation": "RETROSPECTIVE_AUTHOR_DESCRIBES_RAW_DATA_SERIES", "active": False},
        {"from": "SOVIET_RAW_RESULTS_SERIAL", "to": "RNB-1000287767", "relation": "CATALOGUE_SAME_TITLE_NOT_TARGET_OBSERVATION", "active": False},
        {"from": "SOVIET_RAW_RESULTS_SERIAL", "to": "GOOGLE-BOOKS-V224", "relation": "CATALOGUE_METADATA_NO_FACSIMILE", "active": False},
    ]
    graph += [{"from": "C241-L37", "to": source, "relation": "RESEARCH_CONTEXT_SERIES_IDENTITY_UNPROVEN", "active": False}
              for source in route["dependencies"]]
    graph += [{"from": "SOVIET_RAW_RESULTS_SERIAL", "to": f"NORAD_{n}_latent_track",
               "relation": "TARGET_SPECIFIC_RECORD_SEARCH_NOT_IDENTIFIED", "active": False,
               "observing_epoch_utc": None, "original_page": None,
               "frame": None, "instrument_sigma": None}
              for n in OBJECTS]
    return {
        "schema": "conde.soviet-raw-route-scientific-bridge/v1",
        "id": "ABELHA-SOVIET-C241-L37-01",
        "source_occurrence": "C241-L37",
        "parent_sha256": hashes,
        "source": {"kind": original["source_role"], "editorial_year": original["publication_year"],
                   "url": original["url"], "pdf_sha256": original["sha256"],
                   "printed_pages": original["printed_pages_on_spread"],
                   "pdf_index_zero_based": original["pdf_page_index_zero_based"],
                   "hash_scope": original["hash_scope"], "documentary_status": "ORIGINAL_2007_PDF_CUSTODIAN_VISUAL_AUDIT"},
        "two_serials": {"methods_title": distinction["methods_series"],
                        "raw_title": distinction["raw_data_series"],
                        "identity_equivalent": False,
                        "raw_target_measurements_read": False},
        "catalogue_leads": [
            {"id": "RNB-1000287767", "url": followups[0]["catalog_url"],
             "publication_year": followups[0]["catalogue_year_of_publication"],
             "described_observation_month": followups[0]["period_described_in_catalogue"],
             "facsimile_sha256": None, "target_identified": False,
             "epistemic_status": followups[0]["source_status"]},
            {"id": "GOOGLE-BOOKS-V224", "url": followups[1]["catalog_url"],
             "facsimile_sha256": None, "target_identified": False,
             "epistemic_status": followups[1]["source_status"]}],
        "source_dependency_graph": graph,
        "existing_soviet_candidate_joins": catalogue["candidate_join_count"],
        "new_retrieval_paths": len(OBJECTS),
        "lean_candidate": "Conde1963.sovietRawSeriesRoutes",
        "lean_status": "TYPED_SOURCE_SEARCH_NOT_COMPILED_PHYSICAL_RESTRICTION",
        "simulator_latent_parameters": [
            {"name": f"soviet_1963_raw_angular_obs_{n}", "norad": n,
             "forward_observable": "topocentric_direction_from_orbit_and_station_at_epoch",
             "original_observation": None, "unit": None, "time_utc": None,
             "station": None, "frame": None, "sigma": None,
             "source_identity_confirmed": False, "value": None, "activation": False}
            for n in OBJECTS],
        "promote_when": ["original_issue_scan_and_page", "target_designation_verified",
                         "actual_instrument_epoch_and_clock", "station_and_frame",
                         "angular_measurement_units_and_sigma", "independent_lineage_review"],
        "new_independent_instrument_observations": 0,
        "new_numeric_orbital_constraints": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": "Find a November 7-9 1963 raw-data issue and verify an original line for 1963-003A/B/C before fitting"
    }


def render() -> bytes:
    raw_route = (ROOT / ROUTE).read_bytes()
    raw_parent = (ROOT / PARENT).read_bytes()
    require(raw_parent == render_catalogue(), "parent catalogue export stale or altered")
    result = build(json.loads(raw_route), json.loads(raw_parent),
                   {str(ROUTE): hashlib.sha256(raw_route).hexdigest(),
                    str(PARENT): hashlib.sha256(raw_parent).hexdigest()})
    return (json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = p.parse_args()
    data = render()
    require(len(data) < 20_000, "JSON over file ceiling")
    if args.write:
        OUT.write_bytes(data)
    else:
        require(OUT.read_bytes() == data, "stale published route")
    print("SOVIET_RAW_ROUTE_BRIDGE_OK", len(data))


if __name__ == "__main__":
    main()
