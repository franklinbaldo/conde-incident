#!/usr/bin/env python3
"""C241-L40 GCAT catalogue semantics -> pending mass and drag parameters.

Pure offline export. Original six GCAT downloads are validated by the C241-L40
custodian in a separate replay workflow, not re-downloaded or treated as sensors.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from gcat_mass_semantics_C241_L40 import validate_claims

ROOT = Path(__file__).resolve().parents[1]
GCAT = "research/tle_custody/gcat_mass_semantics_C241-L40.json"
PARTITION = "research/tle_custody/mass_partition_C241-L39.json"
BUDGET = "research/constraints/C241_mass_budget_residual_2026-11-13.json"
OUT = ROOT / "public/data/conde-gcat-mass-semantic-bridge.json"
DIGESTS = {
    GCAT: "f8c1c6e1d2c7fdc6e2226934b6835c6bcca116c2c566eaa9214617f3cd53edf4",
    PARTITION: "f3dc00fdaaed4454c29c462a23ce5444f3ffac696605d4858dd7d37fd81c7831",
    BUDGET: "e70c294f409a72f423c873119adaa82cba5987c2a3bdda86e3cf701fa81f52a4",
}
EXPECTED_FILES = {
    "satcat.html", "auxcat.html", "psatcat.html",
    "Thor.html", "cols.html", "lcols.html",
}
EXPECTED_GCAT_FILE_SHA256 = {'satcat.html': '5151ca4fcd90cb468b06d0fcf8b0fc12f8598e0eaade0e91d0af40e39816685c', 'auxcat.html': '3ddb08c124f73c362bd6b97366eab2b86e0dad72e531e5a830225383fd893560', 'Thor.html': '8fef9461664bad2d5d06f5fa4167cc66f7f8ca98ae81eb7b2af8488fbce50901', 'psatcat.html': 'b90f43b3d97a1ee297ff7140ea8405d57273f0ddba2fb56ea6e750f5cae7032a', 'cols.html': '2866c9e7c67362883461b56b0891b29479177425108a598e345d458d4db20ec1', 'lcols.html': '971e11c1ea903237c21a34e7513e1382cd7b2d724003a8d9fdf942201087a42a'}



def require(value: bool, message: str) -> None:
    if not value:
        raise ValueError("GCAT scientific bridge: " + message)


def build(gcat: dict, partition: dict, budget: dict, digests: dict) -> dict:
    require(digests == DIGESTS, "upstream input hashes changed")
    require(gcat["schema"] == "conde.gcat-mass-semantics-audit/v1"
            and gcat["id"] == "C241-L40"
            and gcat["source_kind"] ==
            "DERIVED_SECONDARY_CATALOG_NOT_ENGINEERING_MASS_SHEET",
            "GCAT source identity or epistemic class")
    validate_claims(gcat)
    require(set(gcat["files"]) == EXPECTED_FILES
            and all(v["bytes"] > 10000 and len(v["sha256"]) == 64
                    and v["url"].startswith("https://planet4589.org/")
                    for v in gcat["files"].values()),
            "six original bytes/digest scopes missing")
    require({k: v["sha256"] for k, v in gcat["files"].items()} == EXPECTED_GCAT_FILE_SHA256,
            "source download digest substituted")
    rows = gcat["rows"]
    require(rows["S00527"]["piece"] == "1963-003A"
            and rows["S00528"]["piece"] == "1963-003B"
            and rows["S00529"]["piece"] == "1963-003C"
            and rows["A00324"]["name"] == "Agena B 2313"
            and rows["S00527"]["mass_kg"] == 306
            and rows["S00527"]["total_mass_kg"] == 1176
            and rows["A00324"]["mass_kg"] == 900
            and rows["A00324"]["dry_mass_kg"] == 870
            and rows["S00528"]["mass_catalog_value_kg"] == 0
            and rows["S00529"]["mass_catalog_value_kg"] == 0,
            "object mass labels or placeholders changed")
    require(gcat["dependency"] == ["C241-L14", "C241-L39",
                                    "C241_mass_budget_residual_2026-11-13"],
            "parent lineage altered")
    require(partition["schema"] == "conde.mass-partition-proposal/v1"
            and partition["id"] == "C241-L39"
            and partition["object_ids"] == [527, 528, 529]
            and partition["epistemic_grade"] == "USER_HYPOTHESIS_UNVERIFIED"
            and partition["nominal_total_kg"] == 1176
            and all(v is None for v in partition["unknowns_kg"].values())
            and partition["activation"]["physical_constraint_active"] is False
            and partition["activation"]["used_for_lean_historical_facts"] is False
            and partition["source"]["object_coverage_confirmed"] is False,
            "hypothetical mass partition promoted to evidence")
    require(budget["schema"] == "conde.mass-budget-527-529-residual/v1"
            and budget["id"] == "C241-MASS-X-20261113"
            and budget["source"]["matrix_occurrence"] == "C61"
            and budget["source"]["observed_individual_mass_of_528_kg"] is None
            and budget["source"]["reference_mass_epoch_utc"] is None
            and budget["source"]["claim_that_1176_is_closed_orbital_mass_for_three"] is False
            and budget["conditional_budget"]["closed_three_body_equation_activated"] is False
            and budget["conditional_budget"]["physically_calibrated_historical_constraint"] is False
            and budget["conditional_budget"]["mass_accounting_epoch_utc"] is None
            and budget["conditional_derived_bounds"]["numeric_historical_domain_reduction"] is False,
            "budget was changed into a historical constraint")
    require(budget["conditional_budget"]["equation"] ==
            "m_527 + m_528 + m_529 + X_untracked = 1176 kg + epsilon_reference",
            "conditional equation drift")
    require({v["id"] for v in budget["variables"]} ==
            {"mass_527", "mass_528", "mass_529", "X_untracked", "epsilon_reference"},
            "missing conditional mass variables")
    edges = [
        {"from": "C61#1", "to": "C241-L40",
         "relation": "GCAT_SECONDARY_CLAIM_SEMANTICS_RECHECKED", "independent_sensor": False},
        {"from": "C241-L40", "to": "GCAT:S00527:TotMass",
         "relation": "1176_KG_CATALOG_ATTACHED_TOTAL_NOT_527_528_529_PARTITION",
         "independent_sensor": False},
        {"from": "C241-L40", "to": "GCAT:S00528,S00529:mass",
         "relation": "CATALOG_ZERO_PLACEHOLDERS_NOT_PHYSICAL_ZERO",
         "independent_sensor": False},
        {"from": "C241-L40", "to": "GCAT:A00324:dry_mass",
         "relation": "870_KG_STAGE_DRY_LABEL_SECONDARY", "independent_sensor": False},
        {"from": "C241-L40", "to": "GCAT:A00324:mass",
         "relation": "900_KG_STAGE_MASS_LABEL_SECONDARY", "independent_sensor": False},
        {"from": "C241-L40", "to": "GCAT:1963-003:OrbPay",
         "relation": "1176_KG_AUTOGENERATED_ORBITAL_PAYLOAD", "independent_sensor": False},
        {"from": "C241-L40", "to": "C241-L39",
         "relation": "CORRECTS_UNVERIFIED_CLOSED_PARTITION_PREMISE",
         "independent_sensor": False},
        {"from": "C241-L40", "to": "C241-MASS-X-20261113",
         "relation": "CONDITIONAL_MASS_BUDGET_NEEDS_REFERENCE_EPOCH",
         "independent_sensor": False},
        {"from": "C241-MASS-X-20261113", "to": "latent_mass_528_kg",
         "relation": "REQUIRES_PRIMARY_COMPONENT_INVENTORY_AND_ERROR",
         "independent_sensor": False},
        {"from": "latent_mass_528_kg", "to": "latent_CdA_over_m_528_m2_per_kg",
         "relation": "DRAG_MODEL_REQUIRES_AREA_CD_AND_DENSITY_GAUGE",
         "independent_sensor": False},
    ]
    latent = [
        {"name": name, "value": None, "uncertainty": None,
         "activation": False, "unit": unit, "requires": pending}
        for name, unit, pending in (
            ("latent_mass_528_kg", "kg",
             ["original_breakup_inventory", "reference_epoch", "mass_measurement_error"]),
            ("latent_mass_529_kg", "kg",
             ["original_breakup_inventory", "reference_epoch", "mass_measurement_error"]),
            ("latent_mass_527_kg", "kg",
             ["engineering_mass_sheet", "mass_definition", "reference_epoch"]),
            ("latent_X_untracked_kg", "kg",
             ["exhaustive_components_and_losses", "mass_epoch"]),
            ("latent_epsilon_reference_kg", "kg",
             ["catalogue_total_to_true_inventory_calibration"]),
            ("latent_CdA_over_m_528_m2_per_kg", "m2/kg",
             ["projected_area", "drag_coefficient", "drag_density_scale"]),
        )
    ]
    return {
        "schema": "conde.gcat-mass-semantic-scientific-bridge/v1",
        "id": "ABELHA-C241-L40-MASS-01",
        "source_occurrence": "C241-L40",
        "matrix_context": "C61#1",
        "upstream_sha256": digests,
        "source_class": gcat["source_kind"],
        "catalogue_version": gcat["citation"],
        "catalogue_snapshots": [
            {"file": k, "url": v["url"], "bytes": v["bytes"],
             "sha256": v["sha256"], "hash_scope": "COMPLETE_DOWNLOADED_FILE"}
            for k, v in sorted(gcat["files"].items())
        ],
        "documentary_observables": {
            "s00527_mass_catalog_kg": 306,
            "s00527_total_attached_mass_catalog_kg": 1176,
            "stage_A00324_dry_mass_catalog_kg": 870,
            "stage_A00324_mass_catalog_kg": 900,
            "orbpay_autogenerated_kg": 1176,
            "s00528_mass_catalog_placeholder_kg": 0,
            "s00529_mass_catalog_placeholder_kg": 0,
            "s00528_mass_observed_kg": None,
            "s00529_mass_observed_kg": None,
            "catalog_dry_plus_payload_kg": 1176,
            "catalog_mass_plus_payload_kg": 1206,
            "difference_mechanism": None,
        },
        "dependency_graph": edges,
        "hypotheses": [
            "H_1176_MEANS_ATTACHED_TOTAL_527_NOT_VERIFIED_THREE_BODY_INVENTORY",
            "H_CATALOG_ZERO_IS_MISSING_MASS_NOT_MASS_ZERO",
            "H_30KG_DIFFERENCE_HAS_UNKNOWN_ACCOUNTING_CAUSE",
        ],
        "conditional_equation": budget["conditional_budget"]["equation"],
        "conditional_equation_historical_activation": False,
        "lean_candidate": "Conde1963.gcatMassSemanticsCandidate",
        "lean_status": "DOCUMENTARY_TYPED_CANDIDATE_NOT_COMPILED_PHYSICAL_THEOREM",
        "simulator_latent_parameters": latent,
        "independent_instrumental_observations_added": 0,
        "activation": False,
        "physical_domain_effect": "THETA_UNCHANGED",
        "next_falsifier": "Primary breakup/mass sheet for 1963-003 with same-epoch object coverage, errors and upstream sensor identification",
    }


def render(root: Path = ROOT) -> bytes:
    raw = {path: (root / path).read_bytes() for path in DIGESTS}
    digests = {path: hashlib.sha256(data).hexdigest() for path, data in raw.items()}
    require(digests == DIGESTS, "source audit or budget bytes differ from pinned digest")
    gcat, partition, budget = (json.loads(raw[p]) for p in (GCAT, PARTITION, BUDGET))
    record = build(gcat, partition, budget, digests)
    return (json.dumps(record, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-site", action="store_true")
    parser.add_argument("--check-site", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.write_site:
        OUT.write_bytes(content)
    elif args.check_site:
        require(OUT.read_bytes() == content, "exported site JSON stale")
    else:
        print(content.decode(), end="")


if __name__ == "__main__":
    main()
