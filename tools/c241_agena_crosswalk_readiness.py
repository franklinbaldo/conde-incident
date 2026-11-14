#!/usr/bin/env python3
"""C241: distinguish flight hardware nomenclature from mass evidence for 528.

No model likelihood, NASA/NORAD measurement or historical posterior is created.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / (
    "research/tle_custody/c241_agena_2313_name_claims_20261114.json"
)
EXPECTED = {
    "NASA-SP4004-1964": ("launch_vehicle_label", "Thor-Agena D"),
    "NSA-1975-INDEX": ("launch_vehicle_label", "Thor-Agena D"),
    "GCAT-AUXCAT": ("upper_stage_label", "Agena B"),
    "GUNTER-1963": ("launch_vehicle_label", "Thor Agena B"),
}


def valid_sha(value):
    return (isinstance(value, str) and len(value) == 64
            and any(char != "0" for char in value)
            and all(char in "0123456789abcdef" for char in value.lower()))


def utc_epoch(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        t = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return t.tzinfo == timezone.utc


def positive_finite(value):
    return (type(value) in (float, int) and math.isfinite(value)
            and value > 0)


def qualified_mass_record(mass, crosswalk=None):
    """Test *potential* observability, not historical admissibility.

    Two routes only: mass directly catalog-mapped to 528, or a component mass
    joined to 528 by an independently documented, same-epoch physical link.
    Neither route is historical evidence without external source verification.
    """
    if not isinstance(mass, dict):
        return False
    common = (mass.get("measurement_basis") in {"direct_mass", "component_mass"}
              and positive_finite(mass.get("mass_kg"))
              and positive_finite(mass.get("uncertainty_kg"))
              and valid_sha(mass.get("document_sha256"))
              and utc_epoch(mass.get("epoch_utc"))
              and mass.get("mass_convention") in {"wet", "dry", "as_observed"}
              and bool(mass.get("calibration_reference"))
              and bool(mass.get("source_family")))
    if not common:
        return False
    if mass["measurement_basis"] == "direct_mass":
        return (mass.get("catalog_object") == "528"
                and mass.get("catalog_identity_verified") is True
                and mass["mass_convention"] == "as_observed")
    if (mass.get("component") is None
            or not isinstance(crosswalk, dict)
            or mass["measurement_basis"] != "component_mass"):
        return False
    return (
        crosswalk.get("catalog_object") == "528"
        and crosswalk.get("component") == mass["component"]
        and crosswalk.get("launch") == "1963-003"
        and crosswalk.get("epoch_utc") == mass["epoch_utc"]
        and crosswalk.get("physical_continuity_verified") is True
        and crosswalk.get("flight_specific") is True
        and valid_sha(crosswalk.get("document_sha256"))
    )


def audit(source=None):
    data = json.loads(SOURCE.read_text(encoding="utf-8")) if source is None else source
    if data.get("launch") != "1963-003" or len(data.get("claims", [])) != 4:
        raise ValueError("C241 source census changed")
    claims = {c["id"]: c for c in data["claims"]}
    if set(claims) != set(EXPECTED):
        raise ValueError("missing or duplicated source claims")
    for key, (scope, label) in EXPECTED.items():
        item = claims[key]
        if (item.get("scope") != scope or item.get("label") != label
                or item.get("independent_mass_measurement") is not False
                or not str(item.get("source", "")).startswith("https://")
                or not item.get("source_family")):
            raise ValueError("source claim promoted or corrupted")
    if (data.get("engineering_component_to_norad_528_crosswalk") is not None
            or data.get("mass_528_measurement") is not None
            or data.get("historical_mass_constraint_active") is not False
            or data.get("historical_mcmc") != "NOT_RUN"
            or data.get("posterior_mass_528") is not None
            or data.get("domain_reduction") is not False):
        raise ValueError("unverified source promoted to historical inference")
    return {
        "id": data["id"],
        "launch": data["launch"],
        "source_claim_count": len(claims),
        "launch_vehicle_labels": sorted(set(
            c["label"] for c in claims.values()
            if c["scope"] == "launch_vehicle_label"
        )),
        "upper_stage_labels": sorted(set(
            c["label"] for c in claims.values()
            if c["scope"] == "upper_stage_label"
        )),
        "labels_not_same_semantic_scope": True,
        "independent_528_mass_observations": 0,
        "engineering_to_catalog_crosswalk": "MISSING",
        "discriminating_record_needed": (
            "dated 2313 flight hardware inventory plus component-to-528 "
            "crosswalk and calibrated mass, or calibrated direct mass 528"
        ),
        "counterfactual_target_rank_gain_if_qualified_mass": 1,
        "historical_target_rank_gain": 0,
        "historical_constraint_active": False,
        "historical_mcmc": "NOT_RUN",
        "historical_mass_posterior": None,
        "domain_reduction": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
