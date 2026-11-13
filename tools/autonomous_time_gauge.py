"""Exact structural time gauge for a general autonomous flow.

The theorem uses phi_(t+h)(phi_(-h)(x)) = phi_t(x); the executable
witness uses constant acceleration (NOT an orbital propagation of 1963).
"""
from __future__ import annotations

from fractions import Fraction as F
import json


def vec(values):
    if len(values) != 3:
        raise ValueError("expected a three-dimensional vector")
    return tuple(F(v) for v in values)


def flow(state, acceleration, t):
    """Autonomous, accelerating 6-state flow; every operation is rational."""
    p, v = (vec(part) for part in state)
    a, t = vec(acceleration), F(t)
    return (tuple(p[i] + v[i]*t + a[i]*t*t/2 for i in range(3)),
            tuple(v[i] + a[i]*t for i in range(3)))


def station(coefficients, t):
    """Station ephemeris may itself be nonlinear and externally dated."""
    base, velocity, curvature = (vec(part) for part in coefficients)
    t = F(t)
    return tuple(base[i] + velocity[i]*t + curvature[i]*t*t/2 for i in range(3))


def sightline(state, acceleration, coefficients, epoch, delta, epsilon):
    """Unnormalised sightline; equality implies equality of angular data."""
    target = flow(state, acceleration, F(epoch) + F(delta))[0]
    site = station(coefficients, F(epoch) + F(delta) + F(epsilon))
    return tuple(target[i] - site[i] for i in range(3))


def shifted_configuration(state, acceleration, delta, epsilon, h):
    """Gauge x0->phi_-h(x0), delta->delta+h, epsilon->epsilon-h."""
    return flow(state, acceleration, -F(h)), F(delta) + F(h), F(epsilon) - F(h)


def forced_position(x0, v0, dated_jerk, t):
    """Externally dated, nonautonomous q''(t)=jerk*t, scalar example."""
    t = F(t)
    return F(x0) + F(v0)*t + F(dated_jerk)*t*t*t/6


def shifted_forced_residual(t, h, jerk, x0=2, v0=3, new_x0=5, new_v0=7):
    """Difference between two shifted candidate target trajectories."""
    return (forced_position(new_x0, new_v0, jerk, F(t)+F(h))
            - forced_position(x0, v0, jerk, t))


def forced_second_difference(h, jerk, *, new_x0=5, new_v0=7):
    """Three equally spaced observations: residual(2)-2r(1)+r(0)."""
    r = [shifted_forced_residual(t, h, jerk,
                                 new_x0=new_x0, new_v0=new_v0) for t in range(3)]
    return r[2] - 2*r[1] + r[0]


def report():
    state = ((11, 17, -2), (3, -1, 4))
    acceleration = (2, 1, -3)
    coefficients = ((1, 3, 2), (4, 5, -2), (1, -2, 3))
    delta, epsilon, h = F(1, 3), F(-1, 7), F(2, 5)
    shifted, new_delta, new_epsilon = shifted_configuration(
        state, acceleration, delta, epsilon, h)
    epochs = [F(0), F(1, 2), F(2), F(5)]
    witness = [sightline(state, acceleration, coefficients, t, delta, epsilon)
               == sightline(shifted, acceleration, coefficients, t,
                             new_delta, new_epsilon) for t in epochs]
    assert all(witness) and shifted != state
    assert forced_second_difference(h, F(3)) == F(3)*h
    return {
        "id": "C241-P18-AUTONOMOUS-FLOW-TIME-GAUGE",
        "classification": "EXACT_CONDITIONAL_STRUCTURAL_ONLY",
        "general_proof": "phi_(t+delta+h)(phi_-h(x0))=phi_(t+delta)(x0); station time t+delta+epsilon unchanged",
        "exact_gauge": "(x0,delta,epsilon)->(phi_-h(x0),delta+h,epsilon-h)",
        "required_assumptions": ["autonomous time-translation-equivariant target flow",
                                 "freely estimated target initial state",
                                 "unanchored target clock and station-ephemeris epoch"],
        "witness": {"dynamics": "three-dimensional constant acceleration, not inertial straight-line motion",
                    "station": "arbitrary quadratic ephemeris",
                    "four_distinct_epochs": [str(t) for t in epochs],
                    "sightlines_identical_exactly": witness,
                    "different_initial_states": True},
        "externally_dated_forcing_counterexample": {
            "model": "q''(t)=g*t; g calibrated in absolute time",
            "shift": str(h), "jerk": "3",
            "second_difference_of_shift_residual": str(forced_second_difference(h, 3)),
            "symbolic_difference": "g*h for observations t=0,1,2; nonzero forbids identical 3-point positions",
            "interpretation": "THIS gauge can fail under an externally anchored nonautonomous force; neither full observability nor physical validity follows"},
        "historical_instrument_data": "NOT_AVAILABLE",
        "historical_physical_model_validation": "NOT_RUN",
        "historical_mcmc": "NOT_RUN",
        "conde_geographic_reduction": "NOT_EVALUABLE",
        "dependencies": ["C241-P16", "C241-P17", "Tartaruga #396", "Castor #4"],
        "active_historical_constraint": False,
    }


if __name__ == "__main__":
    print(json.dumps(report(), ensure_ascii=False, sort_keys=True, indent=2))
