#!/usr/bin/env python3
"""C241: exact-rank counterfactual transport holdouts for NORAD 528.

This is a symbolic *design*, not a calibrated 1963 drag observation,
instrumental covariance, orbit propagation, or geographic posterior.
"""
from __future__ import annotations

import hashlib
import json

from tools.drag_density_mass_gauge_C241 import (
    EPOCHS, OBJECTS, COORDINATES as SHARED_COORDS,
    drag_row as shared_row,
)
from tools.mass_identifiability_C241 import GCAT, catalog_is_not_mass_inventory, rank


def coordinates(model: str) -> tuple[str, ...]:
    """Three nested, deliberately stylized density transport hypotheses."""
    if model == "shared":
        return SHARED_COORDS
    if model == "static_offset":
        return SHARED_COORDS + ("d528", "d529")
    if model == "epoch_offset":
        return SHARED_COORDS + ("d528_e0", "d528_e1", "d529_e0", "d529_e1")
    raise ValueError("Unknown transport hypothesis")


def row(model: str, obj: str, epoch: str) -> tuple[int, ...]:
    if obj not in OBJECTS or epoch not in EPOCHS:
        raise ValueError("Unknown object/epoch")
    names = coordinates(model)
    result = list(shared_row(obj, epoch)) + [0] * (len(names) - 8)
    if obj != "527" and model != "shared":
        extra = "d" + obj + ("_" + epoch if model == "epoch_offset" else "")
        result[names.index(extra)] = 1
    return tuple(result)


def anchor(model: str, name: str) -> tuple[int, ...]:
    names = coordinates(model)
    if name not in names:
        raise ValueError("Unknown anchor")
    return tuple(int(n == name) for n in names)


def contrast(model: str) -> tuple[int, ...]:
    """Transport drift: (z528,e1-z528,e0)-(z527,e1-z527,e0)."""
    a, b = row(model, "528", "e1"), row(model, "528", "e0")
    c, d = row(model, "527", "e1"), row(model, "527", "e0")
    return tuple(x - y - u + v for x, y, u, v in zip(a, b, c, d))


def estimable(rows: list[tuple[int, ...]], target: tuple[int, ...]) -> bool:
    n = len(target)
    if any(len(a) != n for a in rows):
        raise ValueError("Inconsistent parameter dimensions")
    return rank(rows, columns=n) == rank(rows + [target], columns=n)


def design(model: str, *, anchors: tuple[str, ...] = (),
           transport_drift_known: bool = False) -> dict:
    """Prove prediction/parameter observability by rational row space."""
    names = coordinates(model)
    if len(anchors) != len(set(anchors)) or any(x not in names for x in anchors):
        raise ValueError("Unvalidated, duplicate, or unknown calibrations")
    if transport_drift_known and model != "epoch_offset":
        raise ValueError("Drift channel applies only to time-dependent offset")
    train = [row(model, obj, "e0") for obj in OBJECTS]
    control = row(model, "527", "e1")
    target_future = row(model, "528", "e1")
    obs = [row(model, obj, t) for obj in OBJECTS for t in EPOCHS]
    external = [anchor(model, name) for name in anchors]
    if transport_drift_known:
        external.append(contrast(model))
    mass_528 = anchor(model, "q528")
    training = train + [control] + external
    return {
        "model": model,
        "coordinates": list(names),
        "six_proxy_rank": rank(obs, columns=len(names)),
        "six_proxy_nullity": len(names) - rank(obs, columns=len(names)),
        "future_528_proxy_estimable_from_e0_and_527_e1": estimable(training, target_future),
        "q528_estimable_after_calibrations": estimable(obs + external, mass_528),
        "anchors": list(anchors),
        "transport_drift_known": transport_drift_known,
        "counterfactual": True,
    }


def audit() -> dict:
    raw = GCAT.read_bytes()
    catalog_is_not_mass_inventory(json.loads(raw))
    reference_anchors = ("q527", "g527", "g528")
    scenarios = {
        "shared": design("shared", anchors=reference_anchors),
        "static_offset_uncalibrated": design("static_offset", anchors=reference_anchors),
        "static_offset_calibrated": design(
            "static_offset", anchors=reference_anchors + ("d528",)),
        "epoch_offset_uncalibrated": design("epoch_offset", anchors=reference_anchors),
        "epoch_offset_with_drift": design(
            "epoch_offset", anchors=reference_anchors, transport_drift_known=True),
        "epoch_offset_with_target_density": design(
            "epoch_offset", anchors=reference_anchors + ("d528_e0",)),
    }
    if not scenarios["shared"]["q528_estimable_after_calibrations"]:
        raise AssertionError("Shared-density reference contract changed")
    if scenarios["epoch_offset_uncalibrated"]["future_528_proxy_estimable_from_e0_and_527_e1"]:
        raise AssertionError("Uncalibrated transport promoted to observation")
    return {
        "id": "C241-CERVO-TRANSPORT-DIFFERENCE-IN-DIFFERENCES",
        "source_occurrence": "C241-L40",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "equation": "z(i,t)=-q(i)+g(i)+s(t)+delta(i,t)",
        "reference_delta_527": "0 by arbitrary gauge convention, not zero measured discrepancy",
        "contrast_528_minus_527": {
            model: list(contrast(model)) for model in
            ("shared", "static_offset", "epoch_offset")
        },
        "scenarios": scenarios,
        "historical_calibrated_drag_observations": 0,
        "historical_transport_drift_calibrations": 0,
        "historical_constraint_active": False,
        "historical_mcmc": "NOT_RUN",
        "mass_posterior_528": None,
        "conde_impact_probability": None,
        "geographic_domain_reduced": False,
        "limits": "Synthetic coeval log-drag proxy, not TLE Bstar; assumes known velocity and "
                  "dynamics. Time-changing projected area/Cd or measurement bias can "
                  "also cause the contrast, so nonzero drift alone cannot identify air density.",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), sort_keys=True, indent=2))
