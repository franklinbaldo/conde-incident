#!/usr/bin/env python3
"""Source-locked CGEO-35 raster anchor -> geographic variables, not event coordinates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import export_cgeo34_original_map_bridge as prior_export
from cgeo35_uwm_raster import verify_contract

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "research/geo/cgeo35_uwm_jp2_raster_anchors.json"
PARENT = "research/geo/cgeo34_uwm_original_jp2_custody.json"
PRIOR = "public/data/conde-cgeo34-original-map-bridge.json"
OUT = ROOT / "public/data/conde-cgeo35-raster-anchor-bridge.json"


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ValueError("CGEO-35 bridge: " + detail)


def build(source: dict, parent: dict, earlier: dict, hashes: dict[str, str]) -> dict:
    verify_contract(source, parent)
    require(earlier["source_occurrence"] == "CGEO-34" and
            earlier["source"]["jp2_sha256"] == source["source_jp2_sha256"] and
            earlier["documentary_context"]["snapshot_occurrence"] == "C24#1" and
            earlier["documentary_context"]["same_map_family_as_parent"] is True and
            earlier["activation"] is False and
            earlier["new_instrumental_observations"] == 0 and
            earlier["physical_domain_effect"] == "THETA_UNCHANGED",
            "original cartography link changed or was falsely promoted")
    require(earlier["source_sha256"][PARENT] == hashes[PARENT],
            "CGEO-34 parent custody hash no longer matches")
    require(len(hashes) == 3 and all(len(h) == 64 for h in hashes.values()),
            "incomplete source digest set")
    image = source["image_space_only"]
    context = source["historical_context"]
    edges = [
        {"from": "CGEO-35", "to": "CGEO-34",
         "relation": "DERIVED_RASTER_FROM_SAME_SHA256_VERIFIED_JP2",
         "independent_observation": False},
        {"from": "CGEO-35", "to": "CGEO-20",
         "relation": "CONDE_AND_VILA_VELHA_ARE_DISTINCT_MAP_LABELS",
         "active_geographic_constraint": False},
        {"from": "CGEO-35", "to": "CGEO-18",
         "relation": "MAP_LABEL_NOT_TRANSLATED_1963_CITY_CENTER",
         "active_geographic_constraint": False},
        {"from": "CGEO-35", "to": "C24#1",
         "relation": "CARTOGRAPHIC_CONTEXT_VIA_CGEO34_NO_NEW_WITNESS",
         "active_geographic_constraint": False},
        {"from": "CGEO-35", "to": "historical_map_pixel_to_geodetic_transform",
         "relation": "IMAGE_PIXEL_ANCHOR_REQUIRES_DATUM_CONTROL_POINTS_AND_ERROR",
         "active_geographic_constraint": False},
        {"from": "historical_map_pixel_to_geodetic_transform",
         "to": "reported_city_center_1963_geometry",
         "relation": "MAP_LABEL_IS_NOT_HISTORICAL_URBAN_CENTER_IDENTIFICATION",
         "active_geographic_constraint": False},
    ]
    params = [
        {"name": "historical_map_pixel_to_geodetic_transform", "value": None,
         "unit": None, "uncertainty": None, "activation": False,
         "required_observables": ["map_datum", "control_points_with_error",
                                   "projection_definition"]},
        {"name": "reported_city_center_1963_geometry", "value": None,
         "unit": None, "uncertainty": None, "activation": False,
         "required_observables": ["original_1963_report_wording",
                                   "dated_urban_landmark_identification",
                                   "validated_geodetic_transform"]},
        {"name": "reported_event_position_1963", "value": None,
         "unit": None, "uncertainty": None, "activation": False,
         "required_observables": ["independent_ground_localization",
                                   "event_epoch", "position_error"]},
    ]
    return {
        "schema": "conde.cgeo35-raster-anchor-scientific-bridge/v1",
        "id": "ABELHA-CGEO35-PIXEL-ANCHOR-01",
        "source_occurrence": "CGEO-35",
        "parent_occurrence": "CGEO-34",
        "matrix_context": "C24#1",
        "source_sha256": hashes,
        "source": {
            "custodian": parent["asset"]["custodian"],
            "catalogue_url": source["source_url"],
            "original_jp2_sha256": source["source_jp2_sha256"],
            "pixel_crop_rgb_sha256": source["inspection"]["rgb_pixel_sha256"],
            "pixel_crop_sha_scope": "RGB_DECODED_ROI_NOT_WHOLE_JP2",
            "raster_inspection_mode": source["inspection"]["kind"],
            "reduction_levels": source["inspection"]["reduction_levels"],
            "original_pixel_roi_xyxy": source["inspection"]["original_pixel_roi_xyxy"],
            "original_map_year": context["printed_base_edition_year"],
            "communications_update_year": context["roads_update_year"],
            "map_scale_denominator": context["scale_denominator"],
            "independent_original_map_acquired": False,
        },
        "image_coordinate_datum": {
            "coordinate_system": "ORIGINAL_JP2_PIXEL_XY_TOP_LEFT",
            "label": "CONDE",
            "settlement_symbol_xy_pixels": image["conde_symbol_original_px_visual_estimate"],
            "manual_visual_tolerance_pixels": image["visual_estimate_tolerance_px"],
            "label_and_symbol_roi_xyxy": image["conde_label_and_settlement_symbol_original_px_roi"],
            "distinct_label": "Vila Velha",
            "distinct_label_roi_xyxy": image["vila_velha_label_original_px_roi"],
            "geographic_coordinates": None,
            "ground_tolerance_m": None,
            "interpretation": "A manually inspected map glyph, not a measured 1963 town centre.",
        },
        "dependency_graph": edges,
        "lean_candidate": "Conde1963.historicalMapPixelAnchorCandidate",
        "lean_status": "TYPED_CANDIDATE_NOT_COMPILED_OBSERVATIONAL_PROOF",
        "hypotheses": ["H_CONDE_MAP_LABEL_DISTINCT_FROM_CITY_CENTER",
                       "H_REENTRY_POSITION_NOT_OBSERVED"],
        "simulator_latent_parameters": params,
        "activation": False,
        "independent_physical_witnesses_added": 0,
        "new_numeric_orbital_constraints": 0,
        "physical_domain_effect": "THETA_UNCHANGED",
        "limitations": [
            "The raster crop is a derivative of CGEO-34, not an independent witness.",
            "Pixel tolerance is not a geodetic or horizontal uncertainty.",
            "The map is dated 1954 with a 1961 update, not a new 1963 survey.",
            "Conde and Vila Velha labels do not identify the reported city centre.",
            "The 1963 report, geodetic transform and an observed reentry location remain absent.",
        ],
    }


def render(root: Path = ROOT) -> bytes:
    files = (SOURCE, PARENT, PRIOR)
    raw = {path: (root / path).read_bytes() for path in files}
    require(raw[PRIOR] == prior_export.render(), "CGEO-34 bridge is stale or altered")
    values = [json.loads(raw[p]) for p in files]
    hashes = {path: hashlib.sha256(raw[path]).hexdigest() for path in files}
    d = build(*values, hashes)
    return (json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-site", action="store_true")
    parser.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.write_site:
        OUT.write_bytes(content)
    elif args.check_site:
        require(OUT.read_bytes() == content, "published bridge drift")
    else:
        print(content.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
