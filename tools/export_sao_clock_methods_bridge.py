#!/usr/bin/env python3
"""Source-locked P-14/SR266 calibration genealogy; no NORAD 528 promotion."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from tle_sao_p14_a1_c241_l59 import validate as validate_p14, a1_minus_wwv_seconds
from tle_sao_sr266_c241_l60 import validate as validate_sr266

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "C241-L59": ("research/tle_custody/sao_p14_a1_clock_1963_C241-L59.json",
                 "b5424d7c2258dd695be8c2643c5599abcd3a931af8b66b5be8e0be71f4546975"),
    "C241-L60": ("research/tle_custody/sao_sr266_synthetic_1963_C241-L60.json",
                 "64f4fcd78ee7c9063e71d2f1e712eadc5512295b609ad652c67c03f4893a0c55"),
}
OUT = ROOT / "public/data/conde-sao-clock-methods-bridge.json"


def require(test, msg):
    if not test:
        raise ValueError("SAO-clock-bridge: " + msg)


def no_duplicate_keys(pairs):
    obj = {}
    for k, v in pairs:
        require(k not in obj, "duplicate JSON key: " + k)
        obj[k] = v
    return obj


def load(root=ROOT):
    result = {}
    for sid, (path, digest) in SOURCES.items():
        b = (root / path).read_bytes()
        require(hashlib.sha256(b).hexdigest() == digest, "SHA drift: " + sid)
        result[sid] = json.loads(b, object_pairs_hook=no_duplicate_keys)
    return result


def edge(a, b, relation):
    return {"source": a, "target": b, "relation": relation,
            "epistemic_status": "DOCUMENTARY_DEPENDENCY_ONLY", "activation": False}


def build(sources):
    require(set(sources) == set(SOURCES), "source set changed")
    p14, sr266 = sources["C241-L59"], sources["C241-L60"]
    validate_p14(p14)
    validate_sr266(sr266)
    p, s = p14["measurement_method_context_only"], sr266["published_dataset"]
    pt, st = p14["target_527_528_529"], sr266["target_527_528_529"]
    require(pt["physical_constraints_activated"] == st["physical_constraints_activated"] == 0,
            "physical constraints introduced")
    require(p14["observations_scope"]["norad_527_528_529_in_list"] is False and
            s["includes_1963_003"] is False, "unverified target identity")
    require(p["time_scale"] == "SMOOTHED_PRELIMINARY_A1_NOT_UTC" and
            s["time_scale"] == "A.S._ATOMIC_TIME_NOT_UTC", "clock scales conflated")
    require(p["angular_reference"] ==
            "TOPOCENTRIC_RA_DEC_MEAN_EQUATOR_EQUINOX_1950_NOT_UNIFORM_STAR_CATALOG" and
            s["direction_frame"] == "HISTORIC_FIXED_EARTH_REFERENCE_NOT_TEME", "frames conflated")
    require(s["independence_policy"].startswith("DERIVED_ROWS_SHARE_INPUT_SENSOR_OBSERVATIONS"),
            "synthetic independent sensor")
    require(p["station_geodetic_reference"] == "KAULA_ELLIPSOID_1964", "geodetic frame wrong")
    clock = p["a1_minus_wwv_seconds"]
    require(clock["mjd_upper_exclusive"] == 38334.0, "clock extrapolated into November")
    edges = [
        edge("C241-L59", "DOC:SAO:P14:SR185", "PUBLISHED_SOURCE_PDF"),
        edge("C241-L60", "DOC:SAO:SR266", "PUBLISHED_SOURCE_PDF"),
        edge("DOC:SAO:P14:SR185", "SERIES:P14:NINE_SELECTED_TARGETS", "CATALOG_SCOPE_ONLY"),
        edge("SERIES:P14:NINE_SELECTED_TARGETS", "H:P14_528_UNLISTED", "NEGATIVE_SCOPE_ONLY"),
        edge("DOC:SAO:P14:SR185", "CAL:A1_MINUS_WWV_EMITTED", "HISTORICAL_CLOCK_FORMULA"),
        edge("CAL:A1_MINUS_WWV_EMITTED", "LATENT:WWV_EMITTED_TO_UTC", "MISSING_CONVERSION"),
        edge("LATENT:WWV_EMITTED_TO_UTC", "LEAN:candidateSaoClockCompatibility", "PREMISE_NOT_VERIFIED"),
        edge("DOC:SAO:P14:SR185", "FRAME:TOPO_RA_DEC_MEAN_1950", "NOT_TEME"),
        edge("FRAME:TOPO_RA_DEC_MEAN_1950", "LATENT:FRAME_TRANSFORM", "REQUIRES_EPOCH_AND_STATION"),
        edge("DOC:SAO:P14:SR185", "DATUM:KAULA_1964", "NOT_WGS84"),
        edge("DATUM:KAULA_1964", "LATENT:STATION_GEODETIC_TRANSFORM", "REQUIRES_CALIBRATION"),
        edge("DOC:SAO:SR266", "METHOD:SYNTHETIC_SIMULTANEOUS_PAIRS", "DERIVED_FROM_OVERLAPPING_FRAMES"),
        edge("METHOD:SYNTHETIC_SIMULTANEOUS_PAIRS", "H:SYNTHETIC_NOT_NEW_SENSOR", "SHARED_INPUT_FRAMES"),
        edge("DOC:SAO:SR266", "FRAME:HISTORIC_FIXED_EARTH", "NOT_TEME"),
        edge("DOC:SAO:SR266", "CLOCK:A_S_ATOMIC", "NOT_UTC_NOT_A1"),
        edge("CLOCK:A_S_ATOMIC", "LATENT:AS_TO_UTC", "MISSING_CONVERSION"),
        edge("LATENT:AS_TO_UTC", "LEAN:candidateSaoClockCompatibility", "PREMISE_NOT_VERIFIED"),
        edge("H:P14_528_UNLISTED", "H:528_INSTRUMENTAL_OBSERVATION_UNKNOWN", "NOT_GLOBAL_NEGATIVE"),
        edge("H:SYNTHETIC_NOT_NEW_SENSOR", "H:528_INSTRUMENTAL_OBSERVATION_UNKNOWN", "NOT_GLOBAL_NEGATIVE"),
        edge("H:528_INSTRUMENTAL_OBSERVATION_UNKNOWN", "LATENT:RAW_528_IDENTIFICATION", "MISSING_ORIGINAL_RECORD"),
        edge("LATENT:RAW_528_IDENTIFICATION", "LEAN:candidateSaoClockCompatibility", "CONDITIONAL_IDENTITY"),
        edge("LEAN:candidateSaoClockCompatibility", "MODEL:OBSERVABLE_528_TIMESTAMP", "NOT_COMPILED_NO_528_DATA"),
        edge("LATENT:FRAME_TRANSFORM", "MODEL:OBSERVABLE_528_DIRECTION", "NOT_CALIBRATED"),
        edge("LATENT:STATION_GEODETIC_TRANSFORM", "MODEL:OBSERVABLE_528_DIRECTION", "NOT_CALIBRATED"),
        edge("MODEL:OBSERVABLE_528_TIMESTAMP", "PARAM:orbit_measurement_epoch_528", "NOT_ACTIVATED"),
        edge("MODEL:OBSERVABLE_528_DIRECTION", "PARAM:orbit_line_of_sight_528", "NOT_ACTIVATED"),
        edge("H:SYNTHETIC_NOT_NEW_SENSOR", "PARAM:measurement_independence_weight_528", "NOT_CALIBRATED"),
    ]
    latent_ids = (
        "WWV_EMITTED_TO_UTC", "AS_TO_UTC", "FRAME_TRANSFORM", "STATION_GEODETIC_TRANSFORM",
        "RAW_528_IDENTIFICATION", "RAW_528_FRAME", "RAW_528_STATION", "RAW_528_UTC",
        "RAW_528_COVARIANCE", "SYNTHETIC_INPUT_OVERLAP", "HISTORICAL_CLOCK_CALIBRATION",
    )
    return {
        "schema": "conde.sao-clock-method-dependencies/v1",
        "id": "ABELHA-C241-L59-L60-01",
        "sources": [
            {"occurrence_id": sid, "path": path, "sha256": sha,
             "original_pdf_url": (p14["source"]["pdf_url"] if sid == "C241-L59" else sr266["source"]["url"]),
             "original_pdf_sha256": (p14["source"]["pdf_sha256"] if sid == "C241-L59" else sr266["source"]["sha256"]),
             "original_pdf_pages_inspected_zero_based": ([0, 2, 3, 4, 5] if sid == "C241-L59" else [8, 9, 13, 15]),
             "status": "PUBLISHED_PRIMARY_METHOD_NOT_TARGET_528_OBSERVATION"}
            for sid, (path, sha) in SOURCES.items()],
        "matrix_snapshot_ref": None, "matrix_line": None, "row_sha256": None,
        "source_lineage_type": "TWO_DISTINCT_SAO_METHOD_PUBLICATIONS_NOT_TWO_528_SENSORS",
        "published_target_scope": {"P14_number_of_selected_targets": len(p14["observations_scope"]["listed_targets"]),
                                   "P14_selected_rows": sum(p14["observations_scope"]["selected_counts"]),
                                   "SR266_table1_targets": s["table1_target_count"],
                                   "527_528_529_listed_in_either": False,
                                   "not_in_catalogue_is_not_global_absence": True},
        "time_model": {
            "P14": {"reported_scale": p["time_scale"], "reference": p["time_emission_reference"],
                    "valid_mjd_lower_inclusive": clock["mjd_lower_inclusive"],
                    "valid_mjd_upper_exclusive": clock["mjd_upper_exclusive"],
                    "A1_minus_WWV_emitted_seconds_at_mjd_38030": a1_minus_wwv_seconds(p14, 38030),
                    "intercept_seconds": clock["intercept_seconds"],
                    "slope_seconds_per_day": clock["slope_seconds_per_day"],
                    "not_a_UTC_conversion": True},
            "SR266": {"reported_scale": s["time_scale"], "not_A1_or_UTC": True},
            "transfer_between_series_authorized": False},
        "source_only_error_context": {
            "P14_assigned_angular_standard_error_arcsec": p["assigned_angular_standard_error_arcsec"],
            "P14_timing_milliseconds_range": p["time_uncertainty_milliseconds_range"],
            "SR266_synthetic_rejection_threshold_arcsec": s["synthetic_rejection_threshold_arcsec"],
            "SR266_timing_milliseconds_context": s["timing_uncertainty_msec_context"],
            "none_are_covariance_for_528": True},
        "graph": edges,
        "hypotheses": ["H:P14_528_UNLISTED", "H:SYNTHETIC_NOT_NEW_SENSOR", "H:528_INSTRUMENTAL_OBSERVATION_UNKNOWN"],
        "lean_candidate": "candidateSaoClockCompatibility", "lean_status": "CANDIDATE_ONLY_NOT_COMPILED",
        "lean_required_premises": ["same_target_identity", "original_raw_frame_and_UTC_epoch",
                                   "clock_to_UTC_calibration", "station_geodetic_datum_transform",
                                   "direction_frame_transform", "covariance_and_input_measurement_dependency"],
        "latents": [{"id": "LATENT:" + x, "value": None, "activation": False} for x in latent_ids],
        "simulator_parameters": [
            {"id": "PARAM:orbit_measurement_epoch_528", "value": None, "activation": False},
            {"id": "PARAM:orbit_line_of_sight_528", "value": None, "activation": False},
            {"id": "PARAM:measurement_independence_weight_528", "value": None, "activation": False}],
        "independent_instrumental_measurements_added_for_528": 0,
        "new_activated_physical_constraints": 0,
        "global_unknown_528_observation_count": None,
        "activation": False, "physical_domain_effect": "THETA_UNCHANGED",
        "next_falsifiable_test": "Locate original identified 528 raw frame or ledger row with station, UTC/time scale, calibration, directional frame, uncertainty and shared input provenance; never transfer P14 or SR266 errors or clock models by analogy."
    }


def render(root=ROOT):
    return (json.dumps(build(load(root)), ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def main():
    p = argparse.ArgumentParser()
    modes = p.add_mutually_exclusive_group()
    modes.add_argument("--write-site", action="store_true")
    modes.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    data = render()
    if args.write_site:
        OUT.write_bytes(data)
    elif args.check_site:
        require(OUT.read_bytes() == data, "published JSON differs from source")
    else:
        print(data.decode(), end="")

if __name__ == "__main__":
    main()
