#!/usr/bin/env python3
"""Custodial CGEO-34 JP2 -> geographic hypotheses/latent inputs, never a fall observation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from cgeo34_uwm_jp2 import verify_manifest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "research/geo/cgeo34_uwm_original_jp2_custody.json"
PARENT = "research/geo/uwm_aracaju_se_1954_1961_cartographic_custody.json"
GRAPH = "public/data/conde-historical-dependency-links.json"
OUT = ROOT / "public/data/conde-cgeo34-original-map-bridge.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("CGEO-34 bridge: " + message)


def build(source: dict, parent: dict, graph: dict, sha: dict[str, str], header: bytes) -> dict:
    # This verifies the archived manifest and first 103 JP2 bytes only; the
    # 110 MB complete object was independently acquired by the custodian.
    verify_manifest(source, parent, header)
    a = source["asset"]
    historical = source["map_historical_readings"]
    limits = source["scientific_limits"]
    require(graph["id"] == "POLVO-C241-P14-GEO-BB-DEPENDENCIES",
            "unexpected documentary parent")
    parent_limits = parent["epistemic_and_model_links"]
    require(all(parent_limits[k] is None for k in
                ("administrative_boundary_1963", "historical_polygon_1963",
                 "coordinates_of_alleged_fall", "map_1963_available_at_event")) and
            parent_limits["historical_reentry_inside_conde_evaluable"] is False and
            parent_limits["constraint_status"] == "CONNECTED_PENDING_CALIBRATION",
            "parent retrospectively gained a physical or legal boundary")
    links = [x for x in graph["candidate_links"] if x["variable"] == "conde_municipal_boundary_1963"]
    require(len(links) == 1 and links[0]["value"] is None and
            links[0]["simulator_filter"] is None and
            links[0]["status"] == "CONNECTED_PENDING_CALIBRATION" and
            "UWM-AGDM-10814" in links[0]["source_candidates"],
            "map parent already activated or UWM identity lost")
    require(any(x["from"] == "UWM-AGDM-10814" and x["to"] == "C24#1"
                and x["kind"] == "HISTORICAL_TOPONYM_CONTEXT_NOT_BOUNDARY"
                for x in graph["edges"]), "C24 documentary reference missing")
    require(source["graph_edges"] == [
        {"to": "CGEO-08", "relation": "SAME_PRINTED_SHEET_ORIGINAL_BITSTREAM_NO_NEW_INDEPENDENCE"},
        {"to": "CGEO-33", "relation": "HISTORICAL_BASEMAP_CANDIDATE_WITH_UNCERTAIN_COVERAGE_AND_SCALE"},
        {"to": "CGEO-18", "relation": "CITY_LABEL_CONTEXT_NOT_EVENT_COORDINATE"}
    ], "source graph changed")
    require(a["sha256"] == "6637246d2a68a2e7024e07829caa35a8af0a707905e6c606109f1da52ae808b3" and
            a["acquired_original_bitstream"] is True and
            a["full_image_visual_inspection_performed"] is False and
            source["same_physical_map_as_parent"] is True and
            historical["geodetic_datum"] is None and historical["position_accuracy_m"] is None and
            historical["catalog_year"] == 1954 and
            historical["communications_update_year"] == 1961 and
            historical["map_scale"] == 500000 and
            all(limits[k] is None for k in
                ("municipal_boundary_1963", "urban_center_geometry_1963",
                 "observed_reentry_location", "georeferenced_control_points",
                 "horizontal_error_m")) and
            limits["can_constrain_orbital_reentry"] is False,
            "anachronism or physical claim unexpectedly promoted")

    edges = [
        {"from": "CGEO-34", "to": source["parent_occurrence"],
         "relation": "ORIGINAL_JP2_SURROGATE_OF_SAME_CARTOGRAPHIC_SHEET",
         "independent_physical_witness": False},
        {"from": "CGEO-34", "to": "UWM-AGDM-10814",
         "relation": "CONTENTDM_ORIGINAL_DOWNLOAD_CUSTODY_WITH_WHOLE_FILE_SHA256"},
        {"from": "UWM-AGDM-10814", "to": "C24#1",
         "relation": "HISTORICAL_TOPONYM_CONTEXT_NOT_BOUNDARY_OR_EVENT"},
    ]
    edges.extend({"from": "CGEO-34", "to": entry["to"],
                  "relation": entry["relation"], "active_constraint": False}
                 for entry in source["graph_edges"])
    edges += [
        {"from": "CGEO-34", "to": "historical_map_georeference_1963",
         "relation": "MISSING_GEODETIC_DATUM_CONTROL_POINTS_AND_ERROR",
         "active_constraint": False},
        {"from": "historical_map_georeference_1963", "to": "conde_municipal_boundary_1963",
         "relation": "NOT_A_LEGALLY_CERTIFIED_1963_ADMINISTRATIVE_BOUNDARY",
         "active_constraint": False},
        {"from": "CGEO-18", "to": "reported_city_center_1963_geometry",
         "relation": "ORIGINAL_TUPI_WORDING_AND_1963_GEOMETRY_UNRECOVERED",
         "active_constraint": False},
    ]
    values = [
        ("historical_map_pixel_to_geodetic_transform", ["historical_geodetic_datum",
            "georeferenced_control_points", "horizontal_uncertainty_m"]),
        ("conde_municipal_boundary_1963", ["legal_boundary_effective_1963",
            "survey_epoch_and_datum", "boundary_uncertainty_m"]),
        ("reported_city_center_1963_geometry", ["original_tupi_portuguese_audio_or_transcript",
            "dated_1963_urban_feature_identification", "georeferencing_error_m"]),
        ("reported_event_position_1963", ["independent_event_localization",
            "timestamp_and_error", "location_reference_frame"]),
    ]
    params = [
        {"name": name, "value": None, "activation": False,
         "required_observables": fields, "uncertainty": None,
         "effect_on_theta": "NONE_UNTIL_CALIBRATED"}
        for name, fields in values
    ]
    return {
        "schema": "conde.cgeo34-original-map-scientific-bridge/v1",
        "id": "ABELHA-CGEO34-ORIGINAL-JP2-01",
        "source_occurrence": "CGEO-34",
        "parent_occurrence": source["parent_occurrence"],
        "source_sha256": sha,
        "source": {
            "institution": a["custodian"], "original_download_url": a["url"],
            "catalogue_url": a["catalog"], "digital_item_id": a["contentdm_item_id"],
            "downloaded_on": a["downloaded_on"],
            "jp2_bytes": a["bytes"], "jp2_sha256": a["sha256"],
            "sha256_scope": "COMPLETE_DOWNLOADED_JP2_BITSTREAM_CUSTODIAN_REPLAY_NOT_THIS_EXPORT",
            "header_sha256": a["header_sha256"],
            "width_px": a["width_px"], "height_px": a["height_px"],
            "copyright_checked_for_redistribution": False,
            "full_image_visual_inspection": False,
            "historical_map_nominal_year": 1954,
            "communications_update_year": 1961,
            "map_scale_denominator": historical["map_scale"],
            "geodetic_datum": None, "horizontal_error_m": None,
            "original_physical_survey_acquired": False,
        },
        "dependency_graph": edges,
        "documentary_context": {
            "snapshot_occurrence": "C24#1",
            "same_map_family_as_parent": True,
            "independent_physical_witnesses_added": 0,
            "lean_candidate": "Conde1963.historicalCartographyGeoreferenceCandidate",
            "lean_status": "TYPED_CANDIDATE_NOT_COMPILED_OBSERVATIONAL_PROOF",
            "hypotheses": ["H_CITY_CENTER_1963_UNLOCATED",
                           "H_CONDE_BOUNDARY_1963_UNCALIBRATED",
                           "H_528_REENTRY_LOCATION_UNOBSERVED"]
        },
        "simulator_latent_parameters": params,
        "activation": False,
        "new_instrumental_observations": 0,
        "new_numeric_orbital_constraints": 0,
        "physical_domain_effect": "THETA_UNCHANGED",
        "limitations": [
            "A downloaded JP2 surrogate is not the physical survey original.",
            "2017 file processing metadata is not a 1963 survey or capture date.",
            "Cartographic toponym is not a verified 1963 city-center polygon.",
            "A 1:500000 map without datum/control/error is not a fall coordinate.",
            "An independent instrument observation of 528 is still missing."
        ]
    }


def render() -> bytes:
    raw = {}
    for path in (SOURCE, PARENT, GRAPH):
        b = (ROOT / path).read_bytes()
        raw[path] = hashlib.sha256(b).hexdigest()
    source = json.loads((ROOT / SOURCE).read_text(encoding="utf-8"))
    parent = json.loads((ROOT / PARENT).read_text(encoding="utf-8"))
    graph = json.loads((ROOT / GRAPH).read_text(encoding="utf-8"))
    header = bytes.fromhex((ROOT / source["asset"]["header_fixture"]).read_text(encoding="ascii"))
    data = build(source, parent, graph, raw, header)
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--write-site", action="store_true")
    p.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    payload = render()
    if args.write_site:
        OUT.write_bytes(payload)
    elif args.check_site:
        require(OUT.read_bytes() == payload, "published bridge drift")
    else:
        print(payload.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
