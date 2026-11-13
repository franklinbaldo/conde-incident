#!/usr/bin/env python3
"""Connect C241-L38 station-journal lead to typed, inactive observables.

An undated institutional retrospective with a TLS-unverified transport copy
does not authenticate 1963 station logs, original measurements or tracking.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from export_soviet_raw_route_bridge import render as render_raw_route
from verify_yeniseisk_station1078 import validate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("research/tle_custody/yeniseisk_station1078_journals_C241-L38.json")
PARENT = Path("public/data/conde-soviet-raw-route-bridge.json")
OUT = ROOT / "public/data/conde-yeniseisk-station1078-bridge.json"
OBJECTS = (527, 528, 529)
CANDIDATE_DATES = ("1963-11-07", "1963-11-08", "1963-11-09")


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("station1078 bridge: " + reason)


def build(station: dict, parent: dict, digests: dict[str, str]) -> dict:
    try:
        validate(station)
    except (AssertionError, KeyError, TypeError) as exc:
        raise ValueError("station1078 bridge: station manifest not validated") from exc
    require(station["dependencies"] == ["C241-L29", "C241-L31", "C241-L34", "C241-L35", "C241-L37"],
            "station source dependencies altered")
    require(station["route"]["candidate_observation_dates"] == list(CANDIDATE_DATES) and
            station["route"]["target_norad_ids"] == list(OBJECTS),
            "unverified target or epoch substituted")
    require(station["independent_target_measurements"] == 0 and
            station["new_numeric_observables"] == 0 and
            station["orbital_constraints_activated"] == 0,
            "target observations invented")
    require(parent["id"] == "ABELHA-SOVIET-C241-L37-01" and
            parent["source_occurrence"] == "C241-L37" and
            parent["schema"] == "conde.soviet-raw-route-scientific-bridge/v1" and
            parent["new_independent_instrument_observations"] == 0 and
            parent["new_numeric_orbital_constraints"] == 0 and
            parent["physical_domain_effect"] == "THETA_UNCHANGED" and
            parent["activation"] is False and
            [p["norad"] for p in parent["simulator_latent_parameters"]] == list(OBJECTS) and
            all(p["activation"] is False and p["value"] is None
                for p in parent["simulator_latent_parameters"]),
            "parent source family or physical state altered")
    h = station["institutional_history"]
    s = station["retrieved_transport_copy"]
    route = station["route"]
    require(s["tls_certificate_validated"] is False and
            h["journal_november_1963_confirmed"] is False and
            h["present_day_holding_confirmed"] is False and
            h["source_original_observation_facsimile"] is False and
            all(route[k] is False for k in
                ("target_objects_explicitly_identified", "station_logs_retrieved",
                 "station_coordinates_confirmed_for_1963")),
            "unverified journal promoted to a primary record")
    graph = [
        {"from": "C241-L38", "to": "SOVIET_STATION_1078",
         "relation": "INSTITUTIONAL_HISTORY_NAMES_STATION", "documentary": True},
        {"from": "C241-L38", "to": "STATION_1078_JOURNALS",
         "relation": "RETROSPECTIVE_REPORTS_JOURNALS_AT_UNDATED_WRITING",
         "documentary": True, "present_day_holding_confirmed": False},
        {"from": "STATION_1078_JOURNALS", "to": "SOVIET_RAW_RESULTS_SERIAL",
         "relation": "POSSIBLE_ARCHIVAL_JOIN_NOT_PROVEN",
         "documentary": False, "active": False}
    ]
    graph.extend({"from": "C241-L38", "to": occurrence,
                  "relation": "RESEARCH_CONTEXT_NOT_OBSERVATION_DEPENDENCE",
                  "documentary": False, "active": False}
                 for occurrence in station["dependencies"])
    graph.extend({"from": "STATION_1078_JOURNALS", "to": f"NORAD_{n}_latent_track",
                  "relation": "TARGET_SPECIFIC_JOURNAL_SEARCH_NOT_AUTHENTICATED",
                  "active": False, "original_page": None, "observation_epoch_utc": None}
                 for n in OBJECTS)
    return {
        "schema": "conde.station1078-scientific-bridge/v1",
        "id": "ABELHA-STATION1078-C241-L38-01",
        "source_occurrence": "C241-L38",
        "parent_sha256": digests,
        "source": {
            "kind": h["kind"], "url": h["url"],
            "publication_date": h["date_of_web_publication"],
            "transport_copy_sha256": s["sha256"],
            "transport_copy_bytes": s["bytes"],
            "transport_tls_authenticated": False,
            "source_original_observation_facsimile": False,
            "historical_station_identifier": h["station_identifier"],
            "historical_station_name": h["observed_station_name"],
            "historic_journals_reported": True,
            "november_1963_journal_confirmed": False,
            "present_day_holding_confirmed": False,
            "historical_coordinates_confirmed": False,
            "station_1963_target_observation": None,
            "epistemic_status": station["epistemic_status"]
        },
        "dependency_graph": graph,
        "source_independence": {
            "relation_to_parent_soviet_publication": "UNDETERMINED",
            "instrument_independence": "NOT_ESTABLISHED",
            "observed_targets_count": 0,
            "new_verified_instrument_observations": 0
        },
        "lean_candidate": "Conde1963.sovietStation1078JournalRoutes",
        "lean_status": "TYPED_ARCHIVAL_SEARCH_NOT_COMPILED_PHYSICAL_RESTRICTION",
        "simulator_latent_parameters": [
            {"name": f"station1078_original_optical_direction_{n}",
             "norad": n, "candidate_dates_utc": list(CANDIDATE_DATES),
             "forward_observable": "topocentric_direction(orbit_n, station_position_1963, epoch_utc, frame)",
             "station_code": "1078", "station_position_1963": None,
             "original_journal_page": None, "target_designation_original": None,
             "observation_epoch_utc": None, "clock_correction": None,
             "observed_direction": None, "units": None, "frame": None,
             "instrument_sigma": None, "measurement_lineage": None,
             "value": None, "activation": False}
            for n in OBJECTS
        ],
        "promote_when": [
            "identify_current_custodian_and_accession", "authenticate_original_november_1963_log_page",
            "verify_original_target_designation_without_catalogue_assumption",
            "extract_instrument_epoch_and_clock", "establish_station_1963_coordinates_and_frame",
            "retrieve_actual_direction_units_and_uncertainty", "audit_instrument_lineage"
        ],
        "new_numeric_orbital_constraints": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": "Find accession and an original 7-9 Nov 1963 station 1078 log; a matching target is not assumed"
    }


def render() -> bytes:
    source = (ROOT / SOURCE).read_bytes()
    parent = (ROOT / PARENT).read_bytes()
    require(parent == render_raw_route(), "upstream scientific route stale or mutated")
    data = build(json.loads(source), json.loads(parent),
                 {str(SOURCE): hashlib.sha256(source).hexdigest(),
                  str(PARENT): hashlib.sha256(parent).hexdigest()})
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--write", action="store_true")
    operation.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = render()
    require(len(data) < 20_000, "contract exceeds 20 KB")
    if args.write:
        OUT.write_bytes(data)
    else:
        require(OUT.read_bytes() == data, "export differs from validated inputs")
    print("STATION1078_BRIDGE_OK", len(data))


if __name__ == "__main__":
    main()
