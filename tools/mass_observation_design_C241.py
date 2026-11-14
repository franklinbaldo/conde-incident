#!/usr/bin/env python3
"""C241: exact, counterfactual design for mass observability with nuisance terms.

This is not a measurement, likelihood, historical inventory, or MCMC fit.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction

from tools.mass_identifiability_C241 import (
    GCAT, catalog_is_not_mass_inventory, rank,
)

COORDINATES = ("m527", "m528", "m529", "X", "L", "epsilon")
# All rows are proposed independent observations, not claims about 1963.
CHANNELS = {
    "mass_527": (1, 0, 0, 0, 0, 0),
    "mass_528": (0, 1, 0, 0, 0, 0),
    "mass_529": (0, 0, 1, 0, 0, 0),
    "residual_X": (0, 0, 0, 1, 0, 0),
    "loss_L": (0, 0, 0, 0, 1, 0),
    "catalog_bias_epsilon": (0, 0, 0, 0, 0, 1),
}
# T is known ONLY in a hypothetical same-epoch closed-accounting scenario.
CONDITIONAL_TOTAL_ROW = (1, 1, 1, 1, 1, 1)
TARGET_528 = CHANNELS["mass_528"]


def design(*, total_validated=False, candidate_channels=()):
    """Rank and 528 estimability, assuming independent calibrated channels."""
    names = tuple(candidate_channels)
    if len(set(names)) != len(names) or any(n not in CHANNELS for n in names):
        raise ValueError("Unknown or repeated candidate measurement channel")
    rows = ([CONDITIONAL_TOTAL_ROW] if total_validated else []) + [
        CHANNELS[n] for n in names
    ]
    r = rank(rows, columns=len(COORDINATES))
    return {
        "rank": r,
        "nullity": len(COORDINATES) - r,
        "m528_estimable": rank(rows + [TARGET_528], columns=len(COORDINATES)) == r,
        "entire_ledger_identified": r == len(COORDINATES),
        "candidate_channels": list(names),
        "total_validated": total_validated,
        "scenario_only": True,
    }


def witnesses():
    """Two exact indistinguishability constructions in a hypothetical ledger."""
    baseline = (500, 200, 100, 300, 76, 0)
    residual_to_loss = (500, 200, 100, 290, 86, 0)
    m528_to_residual = (500, 210, 100, 290, 76, 0)
    for row in (baseline, residual_to_loss, m528_to_residual):
        if sum(map(Fraction, row)) != 1176 or min(row[:5]) < 0:
            raise ValueError("Invalid rational counterexample")
    if not (baseline[1] == residual_to_loss[1]
            and baseline[3:5] != residual_to_loss[3:5]
            and baseline[1] != m528_to_residual[1]):
        raise ValueError("No non-identifiability demonstrated")
    return {
        "hypothetical_total_kg": "1176",
        "baseline_kg": list(baseline),
        "same_528_different_X_L_kg": list(residual_to_loss),
        "different_528_same_total_527_529_L_epsilon_kg": list(m528_to_residual),
        "is_historical_measurement": False,
    }


def audit():
    raw = GCAT.read_bytes()
    catalog_is_not_mass_inventory(json.loads(raw))
    scenarios = {
        "catalog_only": design(),
        "total_only": design(total_validated=True),
        "total_plus_527_529": design(
            total_validated=True, candidate_channels=("mass_527", "mass_529")),
        "total_plus_three_objects": design(
            total_validated=True,
            candidate_channels=("mass_527", "mass_528", "mass_529")),
        "total_plus_three_objects_X": design(
            total_validated=True,
            candidate_channels=("mass_527", "mass_528", "mass_529",
                                "residual_X")),
        "independent_528_only": design(candidate_channels=("mass_528",)),
        "total_plus_five_other_channels": design(
            total_validated=True,
            candidate_channels=("mass_527", "mass_529", "residual_X",
                                "loss_L", "catalog_bias_epsilon")),
    }
    if scenarios["catalog_only"]["rank"] != 0:
        raise ValueError("Historical 1963 mass observation invented")
    return {
        "id": "C241-CERVO-MASS-NUISANCE-DESIGN",
        "source_occurrence": "C241-L40",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "source_family_independent_mass_measurements": 0,
        "parameters": list(COORDINATES),
        "scenarios": scenarios,
        "witnesses": witnesses(),
        "observation_priority": [
            "primary dated 2313 engineering inventory and NORAD component crosswalk",
            "independent same-epoch direct 528 mass or calibrated external constraint",
            "separate bounded X, L and catalog reconciliation errors",
            "validated Cd, projected area, atmosphere and tracking before B inversion",
        ],
        "mass_total_1176_as_closed_inventory_validated": False,
        "historical_constraint_active": False,
        "historical_mcmc": "NOT_RUN",
        "historical_mass_posterior": None,
        "historical_domain_reduction": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
