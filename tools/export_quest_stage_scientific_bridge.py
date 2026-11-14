#!/usr/bin/env python3
"""C241-L50: conflicting editorial stage labels to inactive science hypotheses."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "public/data/conde-quest-stage-scientific-bridge.json"
Q = "research/tle_custody/quest_stage_C241-L50.json"
N = "research/tle_custody/nasa_sp4004_1963_group_custody_C241-L15.json"
R = "research/tle_custody/nro_7153_mission_scope_C241-L48.json"
G = "research/tle_custody/gcat_mass_semantics_C241-L40.json"
PINS = {
 Q: "b2932319722baef5119aec1332a4d353ed3f62415e6e545d8558a14c64a8678c",
 N: "fdfe30eb79febb998f5eae8b206a86175696218d6b332b38cdf24e00c15932b7",
 R: "ca257c02142276a68ad8d7c0c585045784fc39f0d176663232cfbcbce7dedebd",
 G: "f8c1c6e1d2c7fdc6e2226934b6835c6bcca116c2c566eaa9214617f3cd53edf4",
}


def require(test, message):
    if not test:
        raise ValueError("C241-L50 bridge: " + message)


def unique_keys(pairs):
    output = {}
    for k, v in pairs:
        require(k not in output, "duplicate key")
        output[k] = v
    return output


def sources(root=ROOT):
    result = {}
    for rel, digest in PINS.items():
        content = (root / rel).read_bytes()
        require(hashlib.sha256(content).hexdigest() == digest, "source hash drift: " + rel)
        result[rel] = json.loads(content, object_pairs_hook=unique_keys)
    return result


def build(data):
    from tools.tle_quest_stage_c241_l50 import audit as quest_audit
    q, n, r, g = (data[k] for k in (Q, N, R, G))
    quest_audit(q)
    require(n["record_id"] == "C241-L15"
        and n["annual_row_extracted_text"]["scope"] == "LAUNCH_GROUP_UNRESOLVED_CHILD"
        and n["annual_row_extracted_text"]["vehicle_printed"] == "Thor-Agena D."
        and n["annual_row_extracted_text"]["child_piece_identifier"] is None
        and n["methodological_note"]["specific_upstream_for_1963_3"] is None
        and n["inference_guard"]["physical_identity_528"] is None
        and n["inference_guard"]["can_infer_terminal_time_or_place"] is False
        and n["publication"]["page_image_verified"] is True, "NASA group scope changed")
    require(r["id"] == "C241-L48" and r["mission"]["vehicle"] == "2313"
        and r["mission"]["number"] == 7153
        and r["source"]["retrieval"] == "WEB_TEXT_EXCERPT_ONLY"
        and r["source"]["pdf_sha256"] is None
        and r["identity"]["debris_identity_verified_by_nro_history"] is False
        and r["mission"]["orbit_decay_timestamp_utc"] is None
        and r["scientific_readiness"]["physical_constraint_active"] is False,
        "NRO operational context incorrectly promoted")
    require(g["id"] == "C241-L40"
        and g["rows"]["A00324"]["name"] == "Agena B 2313"
        and g["rows"]["1963-003"]["launch_type"] == "Thor Agena B"
        and g["rows"]["S00528"]["piece"] == "1963-003B"
        and g["rows"]["S00528"]["mass_kg"] is None
        and g["derived_checks"]["three_norad_objects_mass_sum_kg"] is None
        and g["source_kind"] == "DERIVED_SECONDARY_CATALOG_NOT_ENGINEERING_MASS_SHEET",
        "GCAT stage or mass scope changed")
    row = next(x for x in q["rows"] if x["vehicle"] == "2313")
    require(row["stage"] == "Thor Agena D"
            and q["norad528"]["object_hardware"] is None,
            "Quest stage does not identify debris hardware")
    def edge(a, b, relation):
        return {"from": a, "to": b, "relation": relation,
                "independent_instrumental_observation": False, "activation": False}
    graph = [
        edge("C241-L50", "QUEST1995:2313:p40", "EDITORIAL_TABLE_VISUALLY_CHECKED"),
        edge("QUEST1995:2313:p40", "LAUNCH:1963-003", "VEHICLE_ASSOCIATION_NOT_PIECE"),
        edge("C241-L15", "LAUNCH:1963-003", "NASA1964_AGGREGATE_LABEL_D"),
        edge("C241-L48", "VEHICLE:2313", "NRO1994_RETROSPECTIVE_TEXT_ONLY"),
        edge("C241-L40", "VEHICLE:2313", "MODERN_GCAT_LABEL_B"),
        edge("QUEST1995:2313:p40", "C241-L15", "AGREES_ON_D_INDEPENDENCE_UNKNOWN"),
        edge("QUEST1995:2313:p40", "C241-L40", "CONFLICTS_ON_B_AUTHOR_OVERLAP"),
        edge("QUEST1995:2313:p40", "C241-L48", "SAME_MISSION_CONTEXT_NOT_SENSOR"),
        edge("LAUNCH:1963-003", "NORAD:528/1963-003B", "LAUNCH_MEMBERSHIP_NOT_HARDWARE_ID"),
        edge("NORAD:528/1963-003B", "H:528_PIECE_IDENTITY", "UNVERIFIED_PHYSICAL_MAPPING"),
        edge("H:528_PIECE_IDENTITY", "LATENT:528:hardware", "ENGINEERING_PIECE_RECORD_MISSING"),
        edge("C241-L40", "LATENT:528:mass", "CATALOG_ZERO_NOT_A_MEASUREMENT"),
        edge("C241-L50", "H:2313_B_OR_D", "CONFLICT_OPEN"),
        edge("H:2313_B_OR_D", "LATENT:2313:stage", "ENGINEERING_CONFIGURATION_MISSING"),
    ]
    latent = [
        ("2313:stage", "B_VS_D_UNRESOLVED", "1963 engineering configuration"),
        ("528:hardware", "UNKNOWN_PIECE", "piece-specific structural attribution"),
        ("528:mass", "NOT_MEASURED", "piece-specific mass and error"),
        ("528:separation_utc", "NOT_OBSERVED", "breakup epoch"),
        ("528:tracking_utc", "NOT_OBSERVED", "instrumental epoch"),
        ("528:tracking_station", "NOT_OBSERVED", "station and location"),
        ("528:tracking_frame", "NOT_OBSERVED", "reference frame and time scale"),
        ("528:tracking_covariance", "NOT_OBSERVED", "sensor uncertainty"),
    ]
    return {
        "schema": "conde.quest-stage-scientific-bridge/v1",
        "id": "ABELHA-C241-L50-01",
        "source_occurrences": ["C241-L50", "C241-L15", "C241-L48", "C241-L40"],
        "related_matrix_occurrence": "C197#1",
        "matrix_relationship": "NASA_DECAY_DATE_CONTEXT_NOT_LAUNCH_STAGE_PROOF",
        "input_sha256": PINS,
        "quest_source": {
            "url": q["source"]["url"], "pdf_sha256": q["source"]["sha256"],
            "bytes": q["source"]["bytes"], "printed_page": q["source"]["printed_page"],
            "pdf_page_index": q["source"]["pdf_page_index_zero_based"],
            "hash_scope": "WHOLE_1995_PDF_VISUALLY_CHECKED_ROW",
            "vehicle": row["vehicle"], "stage": row["stage"],
            "orbit_as_printed": row["orbit_as_printed"],
            "period_as_printed": row["period_as_printed"],
            "has_1963_instrument_epoch_or_sigma": False,
        },
        "stage_conflict": [
            {"source": "C241-L15", "label": "Thor-Agena D", "scope": "NASA1964_LAUNCH_GROUP"},
            {"source": "C241-L50", "label": "Thor Agena D", "scope": "QUEST1995_VEHICLE2313"},
            {"source": "C241-L40", "label": "Thor Agena B", "scope": "GCAT2026_LAUNCH_GROUP"},
        ],
        "dependency_graph": graph,
        "independence": {
            "agreement_d_is_two_independent_instruments": False,
            "quest_gcat_author_overlap": True,
            "nasa_underlying_data_source_for_row": None,
            "nro_pdf_verified": False,
        },
        "hypotheses": [
            {"id": "H:2313_B_OR_D", "status": "OPEN_UNDISCRIMINATED"},
            {"id": "H:528_PIECE_IDENTITY", "status": "OPEN_UNVERIFIED"},
            {"id": "H:NASA_D_IMPLIES_528_MASS", "status": "REJECTED_UNSUPPORTED_TRANSFER"},
        ],
        "lean_candidate": "Conde1963.stage2313RequiresEngineeringIdentity",
        "lean_status": "DOCUMENTARY_CANDIDATE_NOT_COMPILED_ORBITAL_PROOF",
        "simulator_latent_parameters": [
            {"id": name, "value": None, "uncertainty": uncertainty,
             "required_evidence": evidence, "activation": False}
            for name, uncertainty, evidence in latent
        ],
        "new_528_instrumental_observations": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_test": "Find 1963 hardware configuration for 2313 and a debris-piece mapping for NORAD 528; obtain calibrated observation with UTC/station/frame/covariance.",
    }


def render(root=ROOT):
    return (json.dumps(build(sources(root)), ensure_ascii=False,
                       indent=2, sort_keys=True) + "\n").encode()


def main():
    p = argparse.ArgumentParser()
    modes = p.add_mutually_exclusive_group()
    modes.add_argument("--write-site", action="store_true")
    modes.add_argument("--check-site", action="store_true")
    args = p.parse_args()
    content = render()
    if args.write_site:
        OUT.write_bytes(content)
    elif args.check_site:
        require(OUT.read_bytes() == content, "published bytes differ from source")
    else:
        print(content.decode(), end="")


if __name__ == "__main__":
    main()

