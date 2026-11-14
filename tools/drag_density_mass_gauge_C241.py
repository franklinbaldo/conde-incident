#!/usr/bin/env python3
"""C241: exact structural observability of log-mass under a drag-density gauge.

All drag observations and calibration rows below are counterfactual. The GCAT
record is a provenance veto, never a measured mass or atmospheric density.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction

from tools.mass_identifiability_C241 import (
    GCAT, catalog_is_not_mass_inventory, rank,
)

OBJECTS = ("527", "528", "529")
EPOCHS = ("e0", "e1")
COORDINATES = ("q527", "q528", "q529", "g527", "g528", "g529", "s0", "s1")
TARGET = (0, 1, 0, 0, 0, 0, 0, 0)


def drag_row(obj: str, epoch: str) -> tuple[int, ...]:
    """z(i,t) = -q(i) + g(i) + s(t); abstract same-density log model."""
    if obj not in OBJECTS or epoch not in EPOCHS:
        raise ValueError("Unknown object or epoch")
    row = [0] * len(COORDINATES)
    i = OBJECTS.index(obj)
    row[i] = -1
    row[3 + i] = 1
    row[6 + EPOCHS.index(epoch)] = 1
    return tuple(row)


def anchor_row(name: str) -> tuple[int, ...]:
    if name not in COORDINATES:
        raise ValueError("Unknown calibrated coordinate")
    return tuple(int(x == name) for x in COORDINATES)


def observable(rows, target=TARGET):
    """Exact rational row-space test, not a precision or Bayesian diagnostic."""
    n = len(COORDINATES)
    r = rank(rows, columns=n)
    return rank([*rows, target], columns=n) == r


def drag_design(*, anchors=()):
    """Hypothetical calibrated anchors only; never historical observations."""
    names = tuple(anchors)
    if len(names) != len(set(names)):
        raise ValueError("Duplicate anchor names do not add independent data")
    rows = [drag_row(obj, ep) for obj in OBJECTS for ep in EPOCHS]
    rows.extend(anchor_row(name) for name in names)
    r = rank(rows, columns=len(COORDINATES))
    return {
        "rank": r, "nullity": len(COORDINATES) - r,
        "q528_estimable": observable(rows),
        "anchors": list(names), "counterfactual": True,
    }


def gauge_witnesses():
    """Two independent exact null vectors with nonzero q528 component."""
    mass_area = (0, 1, 0, 0, 1, 0, 0, 0)
    mass_density = (1, 1, 1, 0, 0, 0, 1, 1)
    rows = [drag_row(obj, ep) for obj in OBJECTS for ep in EPOCHS]
    for null in (mass_area, mass_density):
        if null[1] == 0 or any(
            sum(Fraction(a) * b for a, b in zip(row, null)) != 0
            for row in rows
        ):
            raise AssertionError("Invalid exact mass non-identification witness")
    return {
        "q528_g528_joint_shift": list(mass_area),
        "all_mass_density_joint_shift": list(mass_density),
        "both_change_q528_without_changing_drag": True,
    }


def holdout_design():
    """Predictability of one synthetic future row, not of NORAD reentry."""
    train = [drag_row(obj, "e0") for obj in OBJECTS]
    future = drag_row("528", "e1")
    return {
        "future_528_from_e0_alone": observable(train, future),
        "future_528_with_527_e1_control": observable(
            [*train, drag_row("527", "e1")], future
        ),
        "future_528_with_529_e1_control": observable(
            [*train, drag_row("529", "e1")], future
        ),
        "q528_from_e0_plus_527_e1_control": observable(
            [*train, drag_row("527", "e1")]
        ),
        "shared_density_and_exact_operator_assumed": True,
        "historical_holdout": "NOT_RUN",
    }


def audit():
    raw = GCAT.read_bytes()
    catalog_is_not_mass_inventory(json.loads(raw))
    scenarios = {
        "drag_only": drag_design(),
        "density_s0_only": drag_design(anchors=("s0",)),
        "geometry_528_only": drag_design(anchors=("g528",)),
        "density_s0_plus_geometry_528": drag_design(
            anchors=("s0", "g528")
        ),
        "control_527_mass_and_geometry": drag_design(
            anchors=("q527", "g527")
        ),
        "control_527_plus_geometry_528": drag_design(
            anchors=("q527", "g527", "g528")
        ),
    }
    if scenarios["drag_only"]["rank"] != 4:
        raise AssertionError("Unexpected structural rank")
    if not scenarios["density_s0_plus_geometry_528"]["q528_estimable"]:
        raise AssertionError("Two calibrated anchors failed")
    return {
        "id": "C241-CERVO-DRAG-DENSITY-GAUGE",
        "source_occurrence": "C241-L40",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "parameters": list(COORDINATES),
        "equation": "z(i,t) = -q(i) + g(i) + s(t)",
        "interpretation": {
            "q": "log mass relative to fixed reference",
            "g": "log Cd times projected area relative to fixed reference",
            "s": "log common effective atmospheric density relative to reference",
            "z": "hypothetical calibrated normalized drag proxy, not TLE Bstar",
        },
        "scenarios": scenarios,
        "gauge_witnesses": gauge_witnesses(),
        "holdout_design": holdout_design(),
        "historical_528_drag_measurements": 0,
        "historical_density_calibrations": 0,
        "historical_geometry_528_calibrations": 0,
        "historical_mass_observation_rank": 0,
        "historical_constraint_active": False,
        "historical_mcmc": "NOT_RUN",
        "historical_mass_posterior": None,
        "impact_probability": None,
        "historical_domain_reduction": False,
        "limitations": (
            "All drag rows are synthetic design channels, not reconstructed "
            "1963 observations. Common effective density at both bodies "
            "requires co-location or validated transport; per-body density, "
            "velocity and acceleration operators, attitude, Cd, instrument "
            "error and temporal covariance are not calibrated. Local log "
            "rank does not settle global nonlinear or circular aliases."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
