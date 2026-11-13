"""Exact local clock-offset identifiability, for synthetic affine optics only.

A shared clock offset shifts BOTH target and calibrated observer ephemerides.
This is a design diagnostic, never a likelihood or a fit to 1963 data.
"""
from fractions import Fraction
import json

from optical_temporal_observability import projector, rank


def exact_vector(values):
    if not isinstance(values, (list, tuple)) or len(values) != 3:
        raise ValueError("three vector components required")
    if any(isinstance(v, bool) or not isinstance(v, (int, Fraction))
           for v in values):
        raise ValueError("exact integer or rational components required")
    return tuple(Fraction(v) for v in values)


def clock_matrix(observations, velocity, observer_velocities):
    """Local tangent matrix for q=(r0[3], v[3], delta).

    In a common inertial frame, r(t)=r0+v*t and
    s_i(t)=s_i0+w_i*t, with t=t_reported+delta.
    For u_i=(r-s_i)/|r-s_i|, each P_i=I-u_i*u_i^T has row space
    of bearing derivatives, up to a nonzero common row scaling.
    The clock column is P_i*(v-w_i); all inputs exact rational.
    """
    if not isinstance(observations, (list, tuple)) or not observations:
        raise ValueError("at least one bearing required")
    if not isinstance(observer_velocities, (list, tuple)) or len(observer_velocities) != len(observations):
        raise ValueError("one observer velocity per observation required")
    v = exact_vector(velocity)
    rows = []
    for observation, observer_velocity in zip(observations, observer_velocities):
        if not isinstance(observation, (tuple, list)) or len(observation) != 2:
            raise ValueError("(epoch,direction) observation required")
        epoch, direction = observation
        if isinstance(epoch, bool) or not isinstance(epoch, (int, Fraction)):
            raise ValueError("exact epoch required")
        w = exact_vector(observer_velocity)
        for p in projector(direction):
            delta = sum(p[j]*(v[j]-w[j]) for j in range(3))
            rows.append(p+[Fraction(epoch)*x for x in p]+[delta])
    return rows


def assess(observations, velocity, observer_velocities):
    a = clock_matrix(observations, velocity, observer_velocities)
    full_rank = rank(a)
    # Separate estimability of parameters from the rank of the full state.
    clock_selector = [[Fraction(0)]*6+[Fraction(1)]]
    position_selector = [[Fraction(i == j) for j in range(7)]
                         for i in range(3)]
    velocity_selector = [[Fraction(i+3 == j) for j in range(7)]
                         for i in range(3)]
    return {
        "bearings": len(observations),
        "rank_of_seven_parameters": full_rank,
        "nullity": 7-full_rank,
        "unidentified_clock_dimensions": rank(a+clock_selector)-full_rank,
        "unidentified_position_dimensions": rank(a+position_selector)-full_rank,
        "unidentified_velocity_dimensions": rank(a+velocity_selector)-full_rank,
    }


def report():
    x,y,z,u = (1,0,0),(0,1,0),(0,0,1),(1,1,1)
    observations = ((0,x),(1,y),(2,z),(3,u))
    still = ((0,0,0),)*4
    moved = still[:3]+((1,0,0),)
    radial = still[:3]+((1,1,1),)
    velocity = (2,-1,3)
    return {
        "scope": "SYNTHETIC_LOCAL_AFFINE_CLOCK_DESIGN_ONLY",
        "parameters": ["initial_position_xyz", "velocity_xyz", "common_clock_offset"],
        "model": "r(t)=r0+v*t; s_i(t)=s_i0+w_i*t; t=t_reported+delta",
        "frame": "hypothetical shared inertial Cartesian coordinates",
        "calibration_assumption": "observer positions and velocities externally known in absolute time",
        "designs": {
            "three_stationary": assess(observations[:3], velocity, still[:3]),
            "four_stationary": assess(observations, velocity, still),
            "four_one_transverse_motion": assess(observations, velocity, moved),
            "four_one_radial_motion": assess(observations, velocity, radial),
        },
        "historical_sensor_data": "NOT_AUTHENTICATED",
        "historical_clock_calibration": "NOT_AVAILABLE",
        "historical_mcmc": "NOT_RUN",
        "historical_geography": "NOT_CONSTRAINED",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
