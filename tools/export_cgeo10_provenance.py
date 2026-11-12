#!/usr/bin/env python3
"""Trace CGEO-10's IBGE 1960 *retrospective* proxy to a pending 1963 boundary.

Only documentary and cartographic relationships are exported. This does not
activate orbital reentry constraints, infer historical survey epochs, or read
the frozen 241-row matrix as though it contained a new C-number.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETRO_PATH = "research/geo/ibge_conde_1960_retro_mesh_2026-11-12.json"
NATIVE_PATH = "research/geo/conde_ibge_1960_world_polyconic.json"
LEGAL_PATH = "research/geo/conde_1944_1953_temporal_bridge.json"
OUTPUT = ROOT / "public/data/conde-cgeo10-provenance.json"
ZIP_SHA = "261399b8557ee26c118e94b13cebf3b6b3e1c70e91b5e8438a348847b875120f"
SOURCE_ID = "IBGE_CGEO10_1960_RECONSTRUCTED_ZIP"
OCCURRENCE_ID = "CGEO-10:CONDE-BA:2908606:SHP-2449"
FAMILY = "IBGE_1991_DERIVED_HISTORICAL_DIVISION"


def read_json(root: Path, path: str) -> tuple[dict, str]:
    raw = (root / path).read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def checked(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError("CGEO-10 provenance mismatch: " + description)


def build(root: Path = ROOT) -> dict:
    retro, retro_sha = read_json(root, RETRO_PATH)
    native, native_sha = read_json(root, NATIVE_PATH)
    legal, legal_sha = read_json(root, LEGAL_PATH)
    origin = retro["source"]
    binary = origin["binary"]
    nsrc = native["source"]
    checked(retro["schema"] == "conde.geo.retrospective-mesh-custody/v1"
            and retro["record_id"] == native["id"] == "CGEO-10", "record/schema")
    checked(origin["url"] == nsrc["archive_url"]
            and origin["url"].startswith("https://geoftp.ibge.gov.br/")
            and origin["publisher"] == nsrc["publisher"] == "IBGE", "origin URL/publisher")
    checked(binary["source_zip_sha256"] == nsrc["zip_sha256"] == ZIP_SHA
            and binary["source_zip_bytes"] == 2222445, "ZIP custody")
    checked(binary["municipality_code"] == nsrc["dbf_identifier"]["codigo"] == "2908606"
            and binary["municipality_name"] == nsrc["dbf_identifier"]["nome"] == "Conde"
            and native["municipality"] == {"ibge_code": "2908606", "name": "Conde", "uf": "BA"},
            "municipality, disambiguation")
    checked(binary["dbf_record_index_0based"] == nsrc["shapefile_record_index_zero_based"] == 2448
            and binary["shapefile_record_1based"] == 2449
            and binary["dbf_total_records"] == 2766, "record index")
    checked(binary["source_components"]["05-malha municipal 1960.shp"]["sha256"] ==
            nsrc["members_sha256"][".shp"], "SHP member content hash")
    checked(binary["source_components"]["05-malha municipal 1960.prj"]["sha256"] ==
            nsrc["members_sha256"][".prj"], "PRJ member hash")
    # Two authors computed different scopes: 808-byte record vs its parsed
    # geometry. They MUST NOT be silently represented by a shared hash.
    checked(binary["record_bytes"] == 808
            and binary["record_sha256"] == "6258845cd887418a078fb507dda4b462dc12b44145f929775199cc80f5681b65"
            and nsrc["shapefile_record_sha256"] ==
            "2970e4ee04d39e1c4865dbdb56ee1a21db9999d8c964ef0f08828c001783c601",
            "distinct record-byte/parsed-record hashes")
    checked(binary["vertex_count_including_closure"] ==
            native["native_geometry"]["vertex_count_with_closure"] == 47,
            "geometry vertex count")
    checked(native["native_crs"]["projection"] == "Polyconic"
            and native["native_crs"]["linear_unit"] == "metre"
            and native["native_crs"]["epsg_projected"] is None,
            "native projected XY must not become lon/lat")
    checked(origin["archive_year_label"] == nsrc["nominal_map_year"] == 1960
            and origin["publication_year"] == 2011, "reference vs publication year")
    checked("1991" in retro["method_and_limits"]["reconstruction"]
            and "2013" in retro["method_and_limits"]["coordinate_epoch"],
            "retrospective polygon union lineage")
    checked(legal["id"] == "CGEO-09" and legal["event_date"] == "1963-11-08"
            and legal["dependency_graph"]["boundary_1963"] is None
            and legal["dependency_graph"]["can_constrain_orbital_reentry_1963"] is False,
            "legal 1963 boundary bridge")
    h = native["historical_1963"]
    m = retro["method_and_limits"]
    checked(h["requested_event_date"] == legal["event_date"]
            and all(h[k] is None for k in (
                "legal_boundary_for_date", "date_1963_membership",
                "coordinate_transformation_to_event_frame",
                "geodetic_epoch_and_horizontal_accuracy_m"))
            and h["can_constrain_reentry"] is False, "event-location claim")
    checked(m["horizontal_accuracy_m"] is None
            and m["source_legal_boundary_1963"] is None
            and m["verified_intervening_legal_changes_1960_1963"] is False
            and m["admissible_historical_boundary_1963"] is False
            and m["orbital_constraint_activated"] is False, "missing temporal/geodetic bridge")
    checked(native["dependency_graph"]["edges"] == [
        {"source": "CGEO-10", "target": "municipal_cartography_1960",
         "kind": "RETROSPECTIVE_CARTOGRAPHIC_RECONSTRUCTION"},
        {"source": "CGEO-09", "target": "legal_boundary_1963_LATENT",
         "kind": "NORMATIVE_CONTINUITY_PENDING"},
        {"source": "municipal_cartography_1960",
         "target": "legal_boundary_1963_LATENT",
         "kind": "NOT_A_VALIDATED_TEMPORAL_BRIDGE"},
    ], "dependency edge direction/kind")

    nodes = [
        {"id": SOURCE_ID, "kind": "primary_digital_cartographic_archive",
         "sha256": ZIP_SHA, "url": origin["url"],
         "reference_year": 1960, "publication_year": 2011,
         "source_family": FAMILY},
        {"id": "IBGE_RETROSPECTIVE_1991_POLYGON_UNION_METHOD",
         "kind": "declared_reconstruction_method_not_original_1991_bytes",
         "source_family": FAMILY},
        {"id": OCCURRENCE_ID, "kind": "derived_shapefile_record_occurrence",
         "source_family": FAMILY, "record_index_1based": 2449,
         "record_bytes_sha256": binary["record_sha256"],
         "parsed_geometry_sha256": nsrc["shapefile_record_sha256"]},
        {"id": "CGEO-10", "kind": "post_matrix_cartographic_claim",
         "not_in_frozen_matrix": True, "source_family": FAMILY},
        {"id": "municipal_cartography_1960",
         "kind": "retrospective_cartographic_proxy_not_1963_boundary"},
        {"id": "CGEO-09", "kind": "distinct_legal_chronology_custody"},
        {"id": "legal_boundary_1963_LATENT",
         "kind": "unknown_legal_boundary_1963",
         "value": None, "uncertainty_m": None},
        {"id": "lean_candidate_CGEO10_1963_membership",
         "kind": "conditional_predicate_not_proved_or_activated"},
        {"id": "sim_param_legal_boundary_Conde_BA_1963",
         "kind": "latent_simulation_parameter", "value": None},
    ]
    edges = [
        {"from": SOURCE_ID, "to": "IBGE_RETROSPECTIVE_1991_POLYGON_UNION_METHOD",
         "relation": "metadata_describes_method_not_original_1991_bytes"},
        {"from": SOURCE_ID, "to": OCCURRENCE_ID,
         "relation": "contains_hashed_dbf_shp_record"},
        {"from": "IBGE_RETROSPECTIVE_1991_POLYGON_UNION_METHOD", "to": OCCURRENCE_ID,
         "relation": "reconstructed_using_declared_method"},
        {"from": OCCURRENCE_ID, "to": "CGEO-10",
         "relation": "supports_cartographic_documentary_claim"},
        {"from": "CGEO-10", "to": "municipal_cartography_1960",
         "relation": "retrospective_proxy_only"},
        {"from": "municipal_cartography_1960", "to": "legal_boundary_1963_LATENT",
         "relation": "NOT_A_VALIDATED_TEMPORAL_BRIDGE"},
        {"from": "CGEO-09", "to": "legal_boundary_1963_LATENT",
         "relation": "NORMATIVE_CONTINUITY_PENDING"},
        {"from": "legal_boundary_1963_LATENT", "to": "lean_candidate_CGEO10_1963_membership",
         "relation": "requires_proven_boundary_and_event_coordinates"},
        {"from": "lean_candidate_CGEO10_1963_membership", "to":
         "sim_param_legal_boundary_Conde_BA_1963",
         "relation": "conditional_only_NOT_ACTIVATED"},
    ]
    return {
        "schema": "conde.cgeo10-documentary-bridge/v1",
        "source_id": SOURCE_ID,
        "custody_status": "REUSED_IBGE_DIGITAL_AUDITS_NOT_REDOWNLOADED_THIS_ROUND",
        "occurrence_id": OCCURRENCE_ID,
        "matrix_identity": {
            "supplemental_not_in_frozen_C001_C238": True,
            "frozen_matrix_git_blob_sha1": "a7978c3a75a153b16ab70118a92c434bba674cb7",
            "frozen_matrix_occurrence_count_delta": 0,
        },
        "documents": [
            {"path": RETRO_PATH, "sha256": retro_sha},
            {"path": NATIVE_PATH, "sha256": native_sha},
            {"path": LEGAL_PATH, "sha256": legal_sha},
        ],
        "nodes": nodes, "edges": edges,
        "source_independence": {
            "family": FAMILY, "independent_observation_count": None,
            "stanford_mirror_independent": False,
            "multiple_project_extractions_independent": False,
            "ibge_1991_method_independent_field_measurement": False,
        },
        "constraint_candidate": {
            "id": "CGEO10_CONDE_BA_BOUNDARY_ON_1963_11_08",
            "status": "CONNECTED_PENDING_CALIBRATION",
            "activation": False,
            "logical_form": "if authenticated_boundary_1963 and validated_frame_and_event_position then membership(event_point,boundary_1963) may be evaluated",
            "lean_status": "NOT_PROMOTED",
            "simulation_status": "CANDIDATE_NOT_ACTIVATED",
            "event_date": "1963-11-08",
            "boundary_value": None,
            "event_position": None,
            "horizontal_error_m": None,
            "geodetic_epoch": None,
            "required_bridges": [
                "authenticated_original_legal_annexes_and_1959_1963_changes",
                "georeferenced_1963_legal_boundary_with_uncertainty",
                "validated_datum_epoch_frame_transform",
                "independently_observed_event_position_and_error",
            ],
            "verified_reentry_point": None,
            "verified_reentry_time": None,
        },
        "connectivity_delta": {"new_documentary_bridge": 1,
                               "new_physical_observations": 0,
                               "active_orbital_constraints": 0},
    }


def serialize(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-site", action="store_true")
    mode.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    payload = serialize(build())
    if len(payload.encode()) > 20_000:
        raise SystemExit("CGEO-10 provenance feed > 20,000 bytes")
    if args.write_site:
        OUTPUT.write_text(payload, encoding="utf-8")
    elif not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != payload:
        raise SystemExit("stale CGEO-10 provenance feed")
    print(json.dumps({"source_id": SOURCE_ID, "occurrence_id": OCCURRENCE_ID,
                      "nodes": len(build()["nodes"]), "edges": len(build()["edges"]),
                      "bytes": len(payload.encode())}))


if __name__ == "__main__":
    main()
