#!/usr/bin/env python3
"""Exact prior-only mass sensitivity; never an estimate of NORAD masses."""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction

from tools.mass_identifiability_C241 import GCAT, OBJECTS, catalog_is_not_mass_inventory
from tools.mass_partition_C241_L39 import LEDGER, audit_ledger

# Scenarios inherited from draft #634; none has an empirical justification.
PROFILES = {
    "exchangeable": ("1", "1", "1", "1"),
    "small_residual_assumed": ("1", "1", "1", "1/4"),
    "large_527_assumed": ("4", "1", "1", "1/4"),
}


def dirichlet_moments(alpha, total_kg):
    """E[T*f_i], Var[T*f_i] for a *hypothetical* fixed T and Dirichlet f."""
    if len(alpha) != 4 or any(isinstance(x, (bool, float)) for x in alpha):
        raise ValueError("Four exact positive Dirichlet concentrations required")
    try:
        a = tuple(Fraction(x) for x in alpha)
        t = Fraction(total_kg)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError("Invalid exact Dirichlet profile or mass") from exc
    if not all(x > 0 for x in a) or t <= 0:
        raise ValueError("Concentrations and scenario mass must be positive")
    a0 = sum(a)
    means = tuple(t * x / a0 for x in a)
    variances = tuple(t*t*x*(a0-x)/(a0*a0*(a0+1)) for x in a)
    return means, variances


def audit_sources(catalog=None):
    # Auditors raise on scientific source promotion, including under python -O.
    audit_ledger()
    if catalog is None:
        catalog = json.loads(GCAT.read_text(encoding="utf-8"))
    catalog_is_not_mass_inventory(catalog)
    return catalog


def report():
    catalog = audit_sources()
    scenario_total = Fraction(1176)
    if catalog["rows"]["S00527"]["total_mass_kg"] != 1176:
        raise ValueError("Scenario label changed")
    profiles = {}
    for label, alpha in PROFILES.items():
        means, variances = dirichlet_moments(alpha, scenario_total)
        profiles[label] = {
            "alpha_assumed": list(alpha),
            "prior_means_kg_exact": {k: str(v) for k,v in zip(OBJECTS, means)},
            "prior_variances_kg2_exact": {k: str(v) for k,v in zip(OBJECTS, variances)},
        }
    base = tuple(Fraction(x) for x in PROFILES["exchangeable"])
    low, var_low = dirichlet_moments(base, scenario_total)
    high, var_high = dirichlet_moments(tuple(10*x for x in base), scenario_total)
    if low != high or not all(a > b for a,b in zip(var_low,var_high)):
        raise ValueError("Concentration-scale stress check failed")
    return {
        "id": "C241-CERVO-PRIOR-ONLY",
        "source_occurrence": "C241-L40",
        "source_sha256": hashlib.sha256(GCAT.read_bytes()).hexdigest(),
        "conditional_ledger": "C241-L39",
        "ledger_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
        "reference_total_kg": "1176 (scenario input, NOT a measured closed inventory)",
        "profiles": profiles,
        "concentration_stress": {
            "same_prior_means": low == high,
            "variance_reduced_by_assumed_concentration": all(a > b for a,b in zip(var_low,var_high)),
            "new_observations": 0,
        },
        "source_family_independent_mass_measurements": 0,
        "historical_likelihood": None,
        "historical_mcmc": "NOT_RUN",
        "historical_mass_posterior": None,
        "preferred_allocation": None,
        "historical_constraint_active": False,
        "physical_domain_reduction": False,
        "warning": "Prior moments only. All totals, alpha and allocations are hypothetical, not evidence or posterior probabilities.",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
