#!/usr/bin/env python3
"""R53 five-row numerical crosscheck -> custody DAG -> inactive Lean/simulation."""
import argparse
import hashlib
import json
from pathlib import Path
from audit_stl_unit_crosscheck_r53 import audit as audit_r53
from export_stl_r51_dependency_bridge import render as render_r51

ROOT = Path(__file__).resolve().parents[1]
R53_PATH = "research/tle_custody/stl_unit_crosscheck_C241_LONTRA_R53.json"
R53_SHA = "65c2db57f9ee7c573d07b360623b79656895c9a1513e8dfc3857daf18b643454"
PARENT_PATH = "public/data/conde-stl-space-log-dependency-bridge.json"
PARENT_SHA = "38c62a9d5ac1f090489fc175c098332dcf7cf6ef25a3808c54d31ecd5d2a7571"
OUT = ROOT / "public/data/conde-stl-mile-subtype-bridge.json"

def require(ok, msg):
    if not ok:
        raise ValueError("STL-mile-bridge: " + msg)

def unique_json(pairs):
    d = {}
    for k, v in pairs:
        require(k not in d, "duplicate JSON key " + k)
        d[k] = v
    return d

def pinned(root, path, digest):
    data = (root / path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, "SHA drift: " + path)
    return json.loads(data, object_pairs_hook=unique_json)

def load(root=ROOT):
    r53 = pinned(root, R53_PATH, R53_SHA)
    parent = pinned(root, PARENT_PATH, PARENT_SHA)
    require((root / PARENT_PATH).read_bytes() == render_r51(), "R51 regeneration mismatch")
    return r53, parent

def edge(a, b, r):
    return {"source": a, "target": b, "relation": r,
            "documentary_only": True, "activation": False}

def build(r53, parent):
    rows = audit_r53(r53)
    require(parent["id"] == "ABELHA-C241-LONTRA-R51-01", "parent identity")
    require(parent["custody"]["pdf_sha256"] == r53["source"]["pdf_sha256"], "PDF ancestry")
    require(parent["custody"]["url"] == r53["source"]["url"], "PDF URL ancestry")
    require(parent["custody"]["pdf_page_one_based"] == r53["source"]["pdf_page_one_based"], "PDF page")
    require(parent["printed_identity"] == "1963 3A", "printed identity")
    require(parent["altitude_unit_verified"] == "miles", "NASA caption")
    require(parent["altitude_mile_subtype_verified"] is None, "subtype cannot be certified")
    require(parent["stl_original_issue_observed"] is False, "original issue missing")
    require(parent["pair_mapping_proven"] is False, "column mapping unknown")
    require(parent["activation"] is False and parent["physical_domain_effect"] == "THETA_UNCHANGED", "parent not activated")
    require(parent["independent_instrumental_observations_added"] == 0
            and parent["new_confirmed_norad_528_observations"] == 0
            and parent["new_activated_physical_constraints"] == 0, "parent no sensors")
    require(parent["lean_status"] == "CANDIDATE_ONLY_NOT_COMPILED", "no Lean proof")
    require(len(rows) == 5 and [r["designation"] for r in rows] ==
            ["1963 3A", "1963 3A", "1963 6A", "1963 4A", "1963 4A"], "five rows")
    require(all(r["miles_residual_minutes"] < min(r["km_residual_minutes"],
                r["nautical_residual_minutes"]) for r in rows), "unit consistency")
    edges = [
        edge("C241-LONTRA-R53", "DOC:NASA-TMX59315:B12", "SAME_PDF_AS_R51_NOT_NEW_SENSOR"),
        edge("C241-LONTRA-R51", "DOC:NASA-TMX59315:B12", "PARENT_CUSTODY"),
        edge("DOC:NASA-TMX59315:B12", "WORK:STL-SPACE-LOG:v3:n4", "REPRODUCTION_CREDIT_NOT_ORIGINAL"),
        edge("C241-LONTRA-R53", "DIAGNOSTIC:STL_UNIT_R53", "FIVE_ROWS_ONE_EDITORIAL_PAGE"),
        edge("DIAGNOSTIC:STL_UNIT_R53", "H:STATUTE_MILE_CONSISTENCY", "LOW_AND_HIGH_ORBIT_CONTROLS"),
        edge("H:STATUTE_MILE_CONSISTENCY", "LATENT:mile_subtype", "NUMERICAL_NOT_TEXTUAL"),
        edge("WORK:STL-SPACE-LOG:v3:n4", "LATENT:original_STL_legend", "FASCICLE_UNRECOVERED"),
        edge("DIAGNOSTIC:STL_UNIT_R53", "LATENT:two_body_assumption", "FIXED_R_AND_MU"),
        edge("LATENT:mile_subtype", "LEAN:candidateStlEpochAndUnitConsistency", "UNCERTIFIED_PREMISE"),
        edge("LATENT:original_STL_legend", "LEAN:candidateStlEpochAndUnitConsistency", "UPSTREAM_MISSING"),
        edge("H:STATUTE_MILE_CONSISTENCY", "MODEL:historical_unit_translation", "CONDITIONAL_ONLY"),
        edge("MODEL:historical_unit_translation", "PARAM:historical_printed_altitude_scale", "NOT_ACTIVATED"),
        edge("LEAN:candidateStlEpochAndUnitConsistency", "PARAM:orbit_prior_528", "NO_NOVEMBER_528_OBSERVATION"),
        edge("DOC:NASA-TMX59315:B12", "H:JANUARY_PRINT_CONTEXT_ONLY", "NOT_NOVEMBER_1963"),
        edge("H:JANUARY_PRINT_CONTEXT_ONLY", "PARAM:orbit_prior_527", "NO_PHYSICAL_TRANSFER")
    ]
    latents = [{"id": k, "unit": u, "value": None, "activation": False}
               for k, u in (
                   ("LATENT:mile_subtype", "statute_or_nautical_not_certified"),
                   ("LATENT:original_STL_legend", "facsimile_with_caption"),
                   ("LATENT:two_body_assumption", "model_bias_rounded_elements"),
                   ("LATENT:paired_columns", "unknown_semantics"),
                   ("LATENT:measurement_utc", "UTC"),
                   ("LATENT:station", "instrument_id"),
                   ("LATENT:reference_frame", "frame_id"),
                   ("LATENT:covariance", "covariance_matrix"))]
    return {
        "schema": "conde.stl-mile-subtype-dependency/v1",
        "id": "ABELHA-C241-LONTRA-R53-01",
        "sources": [
            {"occurrence_id": "C241-LONTRA-R53", "path": R53_PATH,
             "sha256": R53_SHA, "role": "numerical_crosscheck_not_new_sensor"},
            {"occurrence_id": "C241-LONTRA-R51", "path": PARENT_PATH,
             "sha256": PARENT_SHA, "role": "custody_not_independent_sensor"}],
        "custody": {"url": r53["source"]["url"],
                    "pdf_sha256": r53["source"]["pdf_sha256"],
                    "pdf_page_one_based": 105, "print_page": "B-12",
                    "printed_unit": "miles", "original_stl_issue_retrieved": False},
        "source_class": "INFERENCE_ON_SINGLE_HISTORICAL_EDITORIAL_REPRODUCTION",
        "printed_target": "1963 3A",
        "not_equivalent_to": ["1963-003B", "NORAD 528"],
        "independent_from_R51": False,
        "physical_observation_count_in_corpus": None,
        "new_independent_instrumental_observations": 0,
        "new_november_observations_527_528_529": 0,
        "printed_unit_verified": "miles",
        "original_STL_unit_subtype_certified": False,
        "numerically_favoured_subtype": "statute_miles",
        "subtype_inferred_not_authenticated": True,
        "subtype_value_for_orbit_simulation": None,
        "diagnostics": {"method": "two_body_kepler_fixed_radius_mu",
                        "data_family": "NASA_TM_X59315_B12_REPRINT",
                        "rows": rows, "conditional_comparison_not_sensor": True},
        "hypotheses": ["H:STATUTE_MILE_CONSISTENCY", "H:JANUARY_PRINT_CONTEXT_ONLY"],
        "graph": edges,
        "lean_candidate": "candidateStlEpochAndUnitConsistency",
        "lean_status": "CANDIDATE_ONLY_NOT_COMPILED",
        "latents": latents,
        "simulator_parameters": [
            {"id": "PARAM:historical_printed_altitude_scale", "value": None, "activation": False},
            {"id": "PARAM:orbit_prior_527", "value": None, "activation": False},
            {"id": "PARAM:orbit_prior_528", "value": None, "activation": False}],
        "new_activated_physical_constraints": 0,
        "activation": False, "physical_domain_effect": "THETA_UNCHANGED",
        "next_falsifiable_test": "Obtain original STL Space Log v3 n4 legend, paired columns and epoch; do not transfer to 528 without target, UTC, station, frame, covariance."
    }

def render(root=ROOT):
    r53, parent = load(root)
    return (json.dumps(build(r53, parent), sort_keys=True, indent=2,
                       ensure_ascii=False) + "\n").encode()

def main():
    p = argparse.ArgumentParser()
    modes = p.add_mutually_exclusive_group()
    modes.add_argument("--write-site", action="store_true")
    modes.add_argument("--check-site", action="store_true")
    a = p.parse_args()
    raw = render()
    if a.write_site:
        OUT.write_bytes(raw)
    elif a.check_site:
        require(OUT.read_bytes() == raw, "export drift")
    else:
        print(raw.decode(), end="")

if __name__ == "__main__":
    main()
