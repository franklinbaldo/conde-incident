#!/usr/bin/env python3
"""C241: dual catalog mass bases cannot date a breakup or identify fuel burn."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction

from tools.mass_identifiability_C241 import GCAT, catalog_is_not_mass_inventory


def exact_mass(value):
    """Exact nonnegative scenarios, not floating-point physical measurements."""
    if isinstance(value, (float, bool)):
        raise ValueError("Use exact masses, not floats or booleans")
    try:
        number = Fraction(value)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("Invalid mass") from exc
    if number < 0:
        raise ValueError("Mass must be nonnegative")
    return number


def audit_catalog(catalog):
    """Fail closed if the GCAT source contract has been promoted or changed."""
    catalog_is_not_mass_inventory(catalog)
    p = catalog["rows"]["S00527"]
    stage = catalog["rows"]["A00324"]
    dry, wet = (exact_mass(stage[name]) for name in ("dry_mass_kg", "mass_kg"))
    payload, total = (exact_mass(p[name]) for name in ("mass_kg", "total_mass_kg"))
    if not (wet >= dry and payload + dry == total):
        raise ValueError("C241: nominal catalog identity or ordering changed")
    return payload, dry, wet, total


def hypothetical_stage_at_event(catalog, remaining):
    """Conditional only: same dry baseline, no mass losses or additions."""
    _payload, dry, wet, _total = audit_catalog(catalog)
    f = exact_mass(remaining)
    if f > wet - dry:
        raise ValueError("Scenario exceeds nominal mass difference")
    return dry + f


def closed_inventory_with_527_equals_total(total, m528, m529, residual):
    """Algebraic counterexample to assigning *both* roles to one catalog field."""
    total, a, b, x = map(exact_mass, (total, m528, m529, residual))
    return total + a + b + x == total


def audit():
    original = GCAT.read_bytes()
    catalog = json.loads(original)
    payload, dry, wet, total = audit_catalog(catalog)
    low = hypothetical_stage_at_event(catalog, 0)
    high = hypothetical_stage_at_event(catalog, wet - dry)
    if low == high or closed_inventory_with_527_equals_total(total, 1, 1, 0):
        raise ValueError("Counterfactual witnesses failed")
    return {
        "id": "C241-CERVO-STAGE-EPOCH-CONTRAST",
        "source_occurrence": "C241-L40",
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "source_kind": "MODERN_SECONDARY_CATALOG_NOT_1963_MASS_OBSERVATION",
        "catalog_payload_mass_kg": str(payload),
        "catalog_stage_dry_mass_kg": str(dry),
        "catalog_stage_mass_kg": str(wet),
        "catalog_total_mass_kg": str(total),
        "catalog_nominal_difference_kg": str(wet - dry),
        "identity_payload_plus_stage_dry": payload + dry == total,
        "hypothetical_stage_event_mass_witnesses_kg": [str(low), str(high)],
        "event_mass_and_epoch_identified_by_catalog": False,
        "fuel_consumed_identified_by_catalog": False,
        "contradiction_if_527_equals_full_total_and_positive_fragments_close_same_total": True,
        "document_needed": [
            "dated engineering mass and propellant record at breakup",
            "component-to-NORAD mapping with common mass reference epoch",
            "validated loss/residual accounting and uncertainty"
        ],
        "historical_constraint_active": False,
        "historical_mcmc": "NOT_RUN",
        "historical_posterior": None,
        "historical_domain_reduction": False,
        "qualification": "Witnesses assume dry baseline and retained nominal propellant; neither is measured for the breakup. Numeric coincidence is not a closed three-object inventory."
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
