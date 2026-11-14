#!/usr/bin/env python3
"""Source-locked L61/P17 clock dependency: November convention is not a 528 UTC observation."""
from __future__ import annotations
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from export_sao_clock_methods_bridge import render as render_prior
from tle_sao_p17_wwv_step_c241_l61 import check as validate_p17, a1_minus_wwv

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "C241-L44": ("research/tle_custody/sao_p17_oct_dec_1963_scope_C241-L44.json",
                 "3e0e3530f31a506d9af7acc52180bca97c8406bf904a93d12e3370b8c073273c"),
    "C241-L61": ("research/tle_custody/sao_p17_nov_clock_C241-L61.json",
                 "03c706b04cb865b9b0f6437525789c95c1c4d5b6afc3ce5e878d96d2b3b5d8a9"),
}
PRIOR_SHA256 = "89979692b06017d81780ac870629b21bee4991d803b539f9ebe16ee406b0b873"
OUT = ROOT / "public/data/conde-sao-p17-nov-provenance-bridge.json"

def require(value, reason):
    if not value:
        raise ValueError("SAO-P17-bridge: " + reason)

def unique_pairs(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, "duplicate JSON key: " + k)
        result[k] = v
    return result

def load(root=ROOT):
    sources = {}
    for sid, (name, expected) in SOURCES.items():
        data = (root / name).read_bytes()
        require(hashlib.sha256(data).hexdigest() == expected, "manifest SHA drift " + sid)
        sources[sid] = json.loads(data, object_pairs_hook=unique_pairs)
    return sources

def edge(a, b, relation):
    return {"source": a, "target": b, "relation": relation,
            "epistemic_status": "DOCUMENTARY_CONDITIONAL", "activation": False}

def build(sources, prior):
    require(set(sources) == set(SOURCES), "source IDs changed")
    require(hashlib.sha256(prior).hexdigest() == PRIOR_SHA256, "parent bridge bytes drift")
    l44, l61 = sources["C241-L44"], sources["C241-L61"]
    validate_p17(l61)
    require(l44["id"] == "C241-L44" and
            l44["source"]["ntrs_id"] == l61["source"]["ntrs"] and
            l44["source"]["sha256"] == l61["source"]["sha256"] and
            l44["source"]["bytes"] == l61["source"]["pdf_bytes"] and
            l44["source"]["pages"] == l61["source"]["pdf_pages"] and
            l44["source"]["url"] == l61["source"]["url"],
            "L61 not identical original PDF to L44")
    require(l44["observed_targets_in_this_publication"] == [] and
            not l44["physical_constraints_activated"] and
            not l44["independent_target_measurements_recovered"],
            "L44 scope incorrectly promoted")
    require(l61["source"]["prior_manifest"] == SOURCES["C241-L44"][0],
            "prior manifest mismatch")
    require(l61["dependencies"] == ["C241-L44","C241-L59","RU301:SC8:14881-14902"],
            "lineage changed")
    require(l61["model"]["observed_target_528"] is False and
            l61["model"]["utc_conversion_proven"] is False and
            l61["independent_528_observations_added"] == 0 and
            l61["hard_constraints_activated"] == 0,
            "unwarranted 528 activation")
    tick = str(a1_minus_wwv("38341"))
    require(tick == "2.740565438" and
            Decimal(l61["model"]["intercept_difference_seconds"]) == Decimal("0.1"),
            "November clock branch mismatch")
    links = [
        edge("C241-L61","C241-L44","SAME_P17_PDF_NEW_PAGE_LEVEL_METHOD"),
        edge("C241-L44","DOC:SAO:P17:SR275","CUSTODIED_HISTORIC_CATALOG"),
        edge("DOC:SAO:P17:SR275","CLOCK:P17:A1_MINUS_WWV","PUBLISHED_METHOD_ONLY"),
        edge("CLOCK:P17:A1_MINUS_WWV","CLOCK:P17:NOV_BRANCH","1963_11_01_DISCONTINUITY"),
        edge("CLOCK:P17:NOV_BRANCH","LATENT:WWV_EMITTED_TO_UTC","MISSING_CONVERSION"),
        edge("C241-L59","DOC:SAO:P14:SR185","EARLIER_NONTRANSFERABLE_CLOCK_BRANCH"),
        edge("C241-L61","RU301:SC8:14881-14902","STATION_CONTEXT_NOT_528_MEASUREMENT"),
        edge("DOC:SAO:P17:SR275","H:P17_528_UNLISTED","SELECTIVE_CATALOG_SCOPE"),
        edge("H:P17_528_UNLISTED","LATENT:RAW_528_IDENTIFICATION","GLOBAL_OBSERVATIONS_UNKNOWN"),
        edge("LATENT:RAW_528_IDENTIFICATION","LEAN:candidateSaoClockCompatibility","IDENTITY_REQUIRED"),
        edge("LATENT:WWV_EMITTED_TO_UTC","LEAN:candidateSaoClockCompatibility","TIME_CONVERSION_REQUIRED"),
        edge("LEAN:candidateSaoClockCompatibility","PARAM:orbit_measurement_epoch_528","NOT_COMPILED_NOT_ACTIVATED"),
    ]
    require(len({(x["source"], x["target"], x["relation"]) for x in links}) == len(links),
            "duplicate directed graph edge")
    return {
        "schema": "conde.sao-p17-nov-source-dependencies/v1",
        "id": "ABELHA-C241-L61-01",
        "source_lineage": [
            {"occurrence_id": sid, "manifest": name, "manifest_sha256": digest,
             "original_pdf_url": sources[sid]["source"]["url"],
             "original_pdf_sha256": sources[sid]["source"]["sha256"],
             "independent_instrumental_measurement_528": False}
            for sid, (name, digest) in SOURCES.items()
        ],
        "parent_bridge": {"path": "public/data/conde-sao-clock-methods-bridge.json",
                          "sha256": PRIOR_SHA256, "shares_method_family_not_independent_sensor": True},
        "dependencies": ["C241-L44", "C241-L59", "C241-L61", "RU301:SC8:14881-14902"],
        "matrix_snapshot_ref": None, "matrix_line": None, "row_sha256": None,
        "clock": {"published_output": "SMOOTHED_PRELIMINARY_A1",
                  "published_input": "WWV_EMITTED_NOT_UTC",
                  "mjd_nov_transition": "38334.0",
                  "difference_at_boundary_seconds": "0.100000",
                  "mjd_1963_11_08_example": "38341.0",
                  "a1_minus_wwv_example_seconds": tick,
                  "example_is_not_a_528_observation": True,
                  "utc_transform_calibrated": False},
        "graph": links,
        "hypotheses": ["H:P17_528_UNLISTED", "H:528_INSTRUMENTAL_OBSERVATION_UNKNOWN"],
        "lean_candidate": "candidateSaoClockCompatibility",
        "lean_status": "CANDIDATE_ONLY_NOT_COMPILED",
        "lean_required_premises": ["original_identified_528_frame", "sensor_station",
                                  "WWV_emission_to_UTC_calibration", "target_epoch_and_scale",
                                  "reference_frame_transform", "covariance_and_dependency"],
        "latents": [
            {"id": item, "value": None, "activation": False}
            for item in ("LATENT:WWV_EMITTED_TO_UTC", "LATENT:RAW_528_IDENTIFICATION",
                         "LATENT:RAW_528_FRAME", "LATENT:RAW_528_STATION",
                         "LATENT:RAW_528_COVARIANCE")
        ],
        "simulator_parameters": [
            {"id": item, "value": None, "activation": False}
            for item in ("PARAM:orbit_measurement_epoch_528",
                         "PARAM:orbit_line_of_sight_528",
                         "PARAM:measurement_independence_weight_528")
        ],
        "new_independent_instrumental_measurements_528": 0,
        "new_activated_physical_constraints": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "observations_528_elsewhere_count": None,
        "next_falsifiable_test": "Recover a 528-identified primary optical frame/ledger and its station, clock-to-UTC chain and covariance before assigning an orbital constraint."
    }

def render(root=ROOT):
    require(root == ROOT, "parent bridge render must use canonical root")
    parent = render_prior()
    require((ROOT / "public/data/conde-sao-clock-methods-bridge.json").read_bytes() == parent,
            "parent bridge not reproducible")
    return (json.dumps(build(load(root), parent), ensure_ascii=False,
                       indent=2, sort_keys=True) + "\n").encode("utf-8")

def main():
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--write-site", action="store_true")
    choice.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    result = render()
    if args.write_site:
        OUT.write_bytes(result)
    elif args.check_site:
        require(OUT.read_bytes() == result, "published JSON diverged from source")
    else:
        print(result.decode("utf-8"), end="")

if __name__ == "__main__":
    main()

