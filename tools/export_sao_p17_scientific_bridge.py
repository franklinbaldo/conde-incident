#!/usr/bin/env python3
"""C241-L44: published SAO P-17 selection -> scope-only graph, never a target track."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

if __package__:
    from .tle_sao_p17_coverage_c241_l44 import check as check_p17
else:
    from tle_sao_p17_coverage_c241_l44 import check as check_p17

ROOT = Path(__file__).resolve().parents[1]
LEDGER = "research/tle_custody/sao_p17_oct_dec_1963_scope_C241-L44.json"
LEDGER_SHA256 = "3e0e3530f31a506d9af7acc52180bca97c8406bf904a93d12e3370b8c073273c"
L43 = "public/data/conde-sao-1963-archive-bridge.json"
L43_SHA256 = "197a69824bf07ed183b4d5adf2ab2966d9217ebf4113be4b4280711fbfeb28d6"
OUT = ROOT / "public/data/conde-sao-p17-scope-bridge.json"
DESIGNATIONS = ((527, "1963-003A"), (528, "1963-003B"), (529, "1963-003C"))
FIELDS = (
    "date", "smoothed_preliminary_A1_time", "time_rms_milliseconds",
    "topocentric_ra_fk4_1950", "topocentric_dec_fk4_1950",
    "position_rms_arcseconds", "station_id", "film_frame", "observation_id",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("SAO P-17 scientific bridge: " + message)


def build(manifest: dict, ledger_sha: str, parent: dict, parent_sha: str) -> dict:
    require(ledger_sha == LEDGER_SHA256 and parent_sha == L43_SHA256,
            "source ledger or prior archive bridge digest drifted")
    check_p17(manifest)
    source = manifest["source"]
    require(source["sha256"] == "6b77e832e4273f7781cb61bfea7d38685c99d63e2f6b370a76d0b28a225ddf86"
            and source["bytes"] == 10988993 and source["pages"] == 176,
            "original PDF custody changed")
    require(manifest["observational_fields_documented_for_listed_objects"] == list(FIELDS),
            "listed-target method fields changed")
    require(manifest["star_reference"] == "FK4 equator and equinox 1950.0; not TEME or modern ITRF",
            "star frame changed")
    require(manifest["time_reference"] ==
            "Smoothed preliminary A.1, conversion from WWV emitted in source; NOT automatically UTC",
            "time standard changed")
    require(manifest["context_not_target_sigma"] == {
        "position_rms_for_printed_rows_arcsec": 4,
        "clock_uncertainty_range_milliseconds": [0.5, 20],
    }, "accuracy context changed or confused with target error")
    require(manifest["observed_targets_in_this_publication"] == []
            and manifest["raw_measurements_for_527_528_529"] is None
            and manifest["orbital_covariance_for_527_528_529"] is None,
            "target-specific physical observation fabricated")
    require(manifest["independent_target_measurements_recovered"] == 0
            and manifest["physical_constraints_activated"] == 0,
            "catalogue metadata promoted to physical evidence")
    require(parent["schema"] == "conde.sao-1963-archive-scientific-bridge/v1"
            and parent["source_occurrence"] == "C241-L43"
            and parent["activation"] is False
            and parent["independent_instrumental_observations_added"] == 0,
            "prior archive finding aid is not a source of orbital measurements")
    require(parent["source"]["archive_collection"] == "SIA.FARU0171",
            "archive collection unexpectedly changed")
    require({row["id"] for row in parent["archive_files"]} >=
            {"SIA.FARU0171:refIDd1e2142", "SIA.FARU0171:refIDd1e2360"},
            "required optical and clock finding aids missing")
    document = "NASA:NTRS:19680020675:SAO-P17"
    edges = [
        {"from": "C241-L44", "to": document,
         "relation": "ORIGINAL_PUBLISHED_SELECTED_CATALOGUE", "independent_sensor": False},
        {"from": "C241-L43", "to": document,
         "relation": "RELATED_SAO_FINDING_AID_NOT_PROVEN_SAME_DATA", "independent_sensor": False},
        {"from": "SIA.FARU0171:refIDd1e2142", "to": document,
         "relation": "ORIGINAL_REPORT_SEARCH_ROUTE_NOT_DOCUMENT_IDENTITY", "independent_sensor": False},
        {"from": "SIA.FARU0171:refIDd1e2360", "to": document,
         "relation": "CLOCK_CALIBRATION_SEARCH_ROUTE_NOT_TARGET_TIME", "independent_sensor": False},
    ]
    rows = []
    for designation, count in zip(manifest["included_designations"],
                                  manifest["included_counts"], strict=True):
        row = "SAO-P17:PRINTED:" + designation.replace(" ", "_")
        rows.append({"id": row, "designation": designation, "printed_count": count,
                     "is_researched_target": False})
        edges.append({"from": document, "to": row,
                      "relation": "EXPLICITLY_LISTED_IN_SELECTED_PUBLICATION",
                      "independent_sensor": False})
    latent = []
    for norad, intldes in DESIGNATIONS:
        absent = "SAO-P17:NOT_LISTED:" + intldes
        candidate = "sao_p17_scope_target_" + str(norad)
        edges.extend([
            {"from": document, "to": absent,
             "relation": "NOT_LISTED_IN_THIS_SELECTED_CATALOGUE_ONLY",
             "independent_sensor": False},
            {"from": absent, "to": candidate,
             "relation": "CATALOGUE_SELECTION_CONDITIONS_SEARCH_NOT_ORBIT",
             "independent_sensor": False},
        ])
        latent.append({
            "object_id": norad, "international_designator": intldes,
            "candidate_node": candidate,
            "published_catalogue_includes_target": False,
            "global_sao_nonobservation_proved": False,
            "observables": {"source_observation_id": None, "observation_epoch_utc": None,
                            "observatory_station": None, "angular_position_rad": None,
                            "reference_frame": None, "angular_covariance_rad2": None,
                            "time_standard_conversion": None, "clock_error_seconds": None},
            "conditional_forward_operator": "RADEC_from_state_at_station_and_epoch",
            "constraint": "IF_ORIGINAL_TRACK_TARGET_FRAME_EPOCH_CALIBRATION_THEN_RADEC_RESIDUAL",
            "activation": False,
            "requires": ["original_1963_target_identification",
                         "film_or_log_measurement_and_station",
                         "A1_to_UTC_calibration_and_time_sigma",
                         "FK4_1950_to_model_frame_transform",
                         "angular_error_and_independence_lineage"],
        })
    return {
        "schema": "conde.sao-p17-selected-catalogue-bridge/v1",
        "id": "ABELHA-C241-L44-SAO-P17-01",
        "source_occurrence": "C241-L44",
        "source_type": "ORIGINAL_PUBLISHED_1968_SELECTED_CATALOGUE_OF_1963_OBSERVATIONS",
        "source": {"ntrs_id": source["ntrs_id"], "url": source["url"],
                   "bibliography_url": source["bibliography_url"],
                   "published": source["published"], "observations_interval": source["observations_interval"],
                   "pdf_pages": source["pages"], "pdf_bytes": source["bytes"],
                   "pdf_sha256": source["sha256"],
                   "hash_scope": "COMPLETE_ORIGINAL_PDF_NOT_MEASUREMENT_FOR_528"},
        "inputs": [{"path": LEDGER, "sha256": ledger_sha},
                   {"path": L43, "sha256": parent_sha}],
        "printed_catalogue_rows": rows,
        "methodology_applies_only_to_listed_observations": {
            "fields": list(FIELDS), "time_standard": manifest["time_reference"],
            "star_frame": manifest["star_reference"],
            "position_rms_context_arcsec": 4,
            "clock_uncertainty_context_ms_range": [0.5, 20],
            "transfer_precision_to_527_528_529": False,
        },
        "negative_finding_scope": "527_528_529_NOT_IN_THIS_SELECTED_P17_PRINTED_CATALOGUE",
        "not_supported": ["NO_SAO_OBSERVATION_EVER_EXISTED",
                          "NO_NORAD_OBSERVATION_EXISTED", "REENTRY_TIME_OR_LOCATION"],
        "dependency_graph": edges,
        "hypotheses": ["H_P17_PUBLICATION_SELECTION_DOES_NOT_EXHAUST_SAO_FILMS",
                       "H_ORIGINAL_SAO_REPORT_MAY_IDENTIFY_527_528_529"],
        "lean_candidate": "Conde1963.saoP17SelectedCatalogueScope",
        "lean_status": "DOCUMENTARY_PREDICATE_CANDIDATE_NOT_COMPILED_PHYSICAL_THEOREM",
        "candidate_restriction_status": "CONNECTED_ONLY_TO_PUBLICATION_SELECTION",
        "simulator_latent_parameters": latent,
        "independent_instrumental_observations_added": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_falsifier": "Inspect original SAO optical log and timing-calibration file; establish designation, UTC conversion, station, FK4 frame, uncertainties and observation lineage",
    }


def render(root: Path = ROOT) -> bytes:
    raw = (root / LEDGER).read_bytes()
    prior = (root / L43).read_bytes()
    obj = build(json.loads(raw), hashlib.sha256(raw).hexdigest(),
                json.loads(prior), hashlib.sha256(prior).hexdigest())
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--write-site", action="store_true")
    p.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    blob = render()
    if args.write_site:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(blob)
    elif args.check_site:
        require(OUT.read_bytes() == blob, "exported bytes differ from current inputs")
    else:
        print(blob.decode(), end="")


if __name__ == "__main__":
    main()
