#!/usr/bin/env python3
"""Link the Polish 1964 aggregate station report to inactive scientific prerequisites."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "research/tle_custody/polish_observation_service_C241_LONTRA_R65.json"
SOURCE_SHA = "d1940d39f411e449572cc8c9848251e1d9223117733fb5aebe4afa3b92118473"
PDF_SHA = "0664d3134c15e999a67158c1dfd013a49e435fc00dbe86c78fc2b2452b526c94"
OUTPUT = "public/data/conde-polish-service-station-dependency.json"


def require(condition, reason):
    if not condition:
        raise ValueError("Polish-service scientific bridge: " + reason)


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate source JSON key: " + key)
        result[key] = value
    return result


def load(root=ROOT):
    content = (root / SOURCE).read_bytes()
    require(hashlib.sha256(content).hexdigest() == SOURCE_SHA, "SHA-256 drift in source")
    return json.loads(content, object_pairs_hook=no_duplicate_keys)


def edge(source, target, relation):
    return {"source": source, "target": target, "relation": relation,
            "documentary_only": True, "activation": False}


def build(source):
    require(source["schema"] == "conde.archival_observation_service_report/v1" and
            source["id"] == "C241-LONTRA-R65" and source["checked_utc"] == "2026-11-14",
            "source identity")
    doc = source["source"]
    require(doc["author"] == ["Ludosław Cichowicz", "Włodzimierz Zonn"] and
            doc["publication_year"] == 1964 and doc["volume"] == "XII" and
            doc["issue"] == 3 and doc["full_pdf_sha256"] == PDF_SHA and
            doc["full_pdf_bytes"] == 4882674 and
            doc["pdf_pages_one_based"] == [30, 31] and
            doc["printed_pages"] == [190, 191] and
            doc["verification"] ==
            "FULL_BINARY_DOWNLOADED_IFRO_AND_VISUAL_SCREENSHOT_PDF_PAGES_30_31",
            "facsimile custody or printed page")
    rep = source["reported_service"]
    require(rep["started_year"] == 1957 and rep["observations_through_year"] == 1963 and
            rep["aggregate_count_lower_bound_exclusive"] == 25000 and
            rep["count_scope"] == "MULTI_YEAR_MULTI_TARGET_ALL_STATIONS" and
            set(rep["satellite_origins"]) == {"USSR", "USA"} and
            set(rep["measurement_methods"]) == {"visual", "photographic", "radio"} and
            rep["stations_approx_before_1964"] == 10 and
            rep["stations_in_1964"] == 12 and
            rep["cospar_station_id_first"] == 1151 and
            rep["cospar_station_id_last"] == 1162 and
            rep["international_coordination_center"] == "Moscow",
            "aggregate report scope changed")
    bounds = source["boundaries"]
    require(bounds["observations_for_norad_527_528_529"] == [] and
            bounds["independent_measurement_rows_recovered"] == 0 and
            bounds["object_specific_time_observed"] is None and
            bounds["original_station_logs_recovered"] is False and
            bounds["individual_station_instrument_calibration_recovered"] is False and
            bounds["new_orbital_constraints"] == 0 and
            bounds["interpretation"] ==
            "CONTEMPORANEOUS_AGGREGATE_SERVICE_REPORT_NOT_OBJECT_MEASUREMENTS",
            "aggregate mistaken for observation")
    relations = [
        ("PDF:POSTEPY-1964-XII-3", "DOC:C241-LONTRA-R65", "ORIGINAL_1964_FACSIMILE"),
        ("DOC:C241-LONTRA-R65", "AGG:POLISH-1957-1963", "MULTIYEAR_SUMMARY"),
        ("AGG:POLISH-1957-1963", "H:NOT_YEAR_1963_COUNT", "AGGREGATE_NOT_ANNUAL"),
        ("AGG:POLISH-1957-1963", "H:NOT_NORAD_528", "NO_TARGET_ROWS"),
        ("DOC:C241-LONTRA-R65", "IDS:COSPAR-1151-1162", "STATION_ID_RANGE"),
        ("IDS:COSPAR-1151-1162", "H:NO_STATION_LOGS", "IDENTIFIERS_NOT_MEASUREMENTS"),
        ("DOC:C241-LONTRA-R65", "METHOD:VISUAL-PHOTO-RADIO", "REPORTED_METHOD_FAMILIES"),
        ("METHOD:VISUAL-PHOTO-RADIO", "H:NO_INSTRUMENT_CALIBRATION", "METHOD_NOT_SENSOR"),
        ("DOC:C241-LONTRA-R65", "COORD:MOSCOW", "REPORTED_COORDINATION"),
        ("COORD:MOSCOW", "H:NO_INDEPENDENCE_PROOF", "COORDINATION_NOT_INDEPENDENCE"),
        ("H:NOT_NORAD_528", "LATENT:POLAND:target_identity", "TARGET_ID_MISSING"),
        ("H:NO_STATION_LOGS", "LATENT:POLAND:station_log", "RAW_RECORD_MISSING"),
        ("H:NO_INSTRUMENT_CALIBRATION", "LATENT:POLAND:clock", "CLOCK_CALIBRATION_MISSING"),
        ("H:NO_INSTRUMENT_CALIBRATION", "LATENT:POLAND:frame", "REFERENCE_FRAME_MISSING"),
        ("H:NO_INSTRUMENT_CALIBRATION", "LATENT:POLAND:covariance", "UNCERTAINTY_MISSING"),
        ("H:NOT_YEAR_1963_COUNT", "LATENT:POLAND:epoch", "INDIVIDUAL_UTC_MISSING"),
        ("H:NO_INDEPENDENCE_PROOF", "LATENT:POLAND:dependencies", "RAW_LINEAGE_MISSING"),
        ("LATENT:POLAND:target_identity", "LEAN:candidatePolishStationObservation", "TARGET_MISSING"),
        ("LATENT:POLAND:station_log", "LEAN:candidatePolishStationObservation", "LOG_MISSING"),
        ("LATENT:POLAND:clock", "LEAN:candidatePolishStationObservation", "UTC_CONVERSION_MISSING"),
        ("LATENT:POLAND:frame", "LEAN:candidatePolishStationObservation", "FRAME_MISSING"),
        ("LATENT:POLAND:covariance", "LEAN:candidatePolishStationObservation", "ERROR_MODEL_MISSING"),
        ("LATENT:POLAND:epoch", "LEAN:candidatePolishStationObservation", "EPOCH_MISSING"),
        ("LATENT:POLAND:dependencies", "LEAN:candidatePolishStationObservation", "INDEPENDENCE_UNVERIFIED"),
        ("LEAN:candidatePolishStationObservation", "PARAM:polish_optical_clock_sigma_528", "NOT_PROMOTED"),
        ("LEAN:candidatePolishStationObservation", "PARAM:polish_direction_sigma_528", "NOT_PROMOTED"),
    ]
    graph = [edge(*r) for r in relations]
    latent_ids = ["target_identity", "station_log", "clock", "frame", "covariance",
                  "epoch", "dependencies"]
    result = {
        "schema": "conde.documentary-scientific-bridge/v1",
        "id": "C241-ABELHA-R59-POLISH-SERVICE",
        "occurrence_ids": ["C241-LONTRA-R65"],
        "matrix_C001_C238_unchanged": True,
        "sources": [{
            "id": source["id"], "path": SOURCE, "manifest_sha256": SOURCE_SHA,
            "original_pdf_sha256": PDF_SHA, "original_pdf_bytes": 4882674,
            "pdf_pages_one_based": [30, 31], "printed_pages": [190, 191],
            "report_year": 1964, "reported_span": [1957, 1963],
            "classification": "CONTEMPORANEOUS_AGGREGATE_NOT_INSTRUMENTAL_LOG",
        }],
        "reported_service": {
            "aggregate_count_lower_bound_exclusive": 25000,
            "aggregate_scope": "MULTI_YEAR_MULTI_TARGET_ALL_STATIONS",
            "norad_528_observations_in_report": None,
            "cospar_station_identifier_range": [1151, 1162],
            "stations_approx_before_1964": 10, "stations_in_1964": 12,
            "station_ids_are_observation_rows": False,
        },
        "source_family": "POLISH_SPACE_OBSERVATION_SERVICE",
        "independent_target_measurements_newly_recovered": 0,
        "number_of_historical_independent_528_measurements": None,
        "graph": graph, "delta_links": len(graph),
        "latents": [{"id": "LATENT:POLAND:" + x, "value": None, "activation": False}
                    for x in latent_ids],
        "lean_candidate": {
            "id": "candidatePolishStationObservation",
            "status": "NOT_PROMOTED", "compiled_theorem_claimed": False,
            "missing_premises": latent_ids,
        },
        "simulator_parameters": [
            {"id": "polish_optical_clock_sigma_528", "value": None, "activation": False},
            {"id": "polish_direction_sigma_528", "value": None, "activation": False},
        ],
        "historical_mcmc": "NOT_RUN", "delta_orbital_constraints": 0,
        "physical_domain_effect": "THETA_UNCHANGED", "activation": False,
        "next_test": ("Recover 1963 Polish station logs for COSPAR IDs 1151-1162; "
                      "match a target identifier, exposure epoch, instrument, "
                      "clock, frame, uncertainty, and raw-record dependencies."),
    }
    validate(result)
    return result


def validate(payload):
    require(payload["delta_links"] == 26 and
            payload["delta_orbital_constraints"] == 0 and
            payload["physical_domain_effect"] == "THETA_UNCHANGED" and
            payload["historical_mcmc"] == "NOT_RUN" and
            payload["activation"] is False, "physical promotion")
    require(payload["independent_target_measurements_newly_recovered"] == 0 and
            payload["number_of_historical_independent_528_measurements"] is None and
            payload["reported_service"]["norad_528_observations_in_report"] is None,
            "fabricated historical observations")
    require(payload["reported_service"]["station_ids_are_observation_rows"] is False and
            payload["reported_service"]["aggregate_scope"] ==
            "MULTI_YEAR_MULTI_TARGET_ALL_STATIONS", "aggregate or station identifiers promoted")
    require(payload["lean_candidate"]["status"] == "NOT_PROMOTED" and
            payload["lean_candidate"]["compiled_theorem_claimed"] is False and
            len(payload["lean_candidate"]["missing_premises"]) == 7,
            "Lean falsely promoted")
    require(len(payload["latents"]) == 7 and
            all(item["value"] is None and item["activation"] is False
                for item in payload["latents"] + payload["simulator_parameters"]),
            "synthetic uncertainty or parameter value")
    edges = payload["graph"]
    require(len(edges) == 26 and
            len(set((x["source"], x["target"], x["relation"]) for x in edges)) == 26 and
            all(x["activation"] is False and x["documentary_only"] is True
                for x in edges), "invalid evidence graph")


def render(root=ROOT):
    return (json.dumps(build(load(root)), ensure_ascii=False,
                       sort_keys=True, indent=2) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    content = render()
    path = ROOT / OUTPUT
    if args.check_site:
        require(path.read_bytes() == content, "published bytes diverge from signed source")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("Polish service R65: 26 documentary links, 7 null latents, 0 orbital constraints")


if __name__ == "__main__":
    main()
