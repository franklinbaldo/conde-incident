"""Station ephemeris epoch gauge in synthetic affine optical designs.

All ranks and null witnesses are rational-exact; never 1963 observations.
"""
from fractions import Fraction
import json

from optical_clock_bias_observability import clock_matrix, exact_vector
from optical_temporal_observability import projector, rank


def alignment_matrix(observations, velocity, observer_velocities):
    """Jacobian: (r0[3], v[3], target_delta, station_epsilon).

    Target epoch is t+delta; station ephemeris epoch t+delta+epsilon.
    The final column is -P_i*w_i (P_i projects transverse to bearing).
    """
    base = clock_matrix(observations, velocity, observer_velocities)
    rows = []
    cursor = 0
    for (_, direction), motion in zip(observations, observer_velocities):
        w = exact_vector(motion)
        for p in projector(direction):
            station_epoch = -sum(p[j]*w[j] for j in range(3))
            rows.append(base[cursor] + [station_epoch])
            cursor += 1
    return rows


def exact_gauge(velocity):
    """Nonzero null vector: (-v, 0_velocity, +delta, -epsilon)."""
    v = exact_vector(velocity)
    return [-x for x in v] + [Fraction(0)]*3 + [Fraction(1), Fraction(-1)]


def assess(observations, velocity, observer_velocities, *, station_epoch_calibrated=False):
    a = alignment_matrix(observations, velocity, observer_velocities)
    gauge = exact_gauge(velocity)
    if any(sum(x*y for x, y in zip(row, gauge)) for row in a):
        raise AssertionError("station epoch gauge identity failed")
    if station_epoch_calibrated:
        # An externally supplied epoch anchor, NOT a prior or 1963 datum.
        a.append([Fraction(0)]*7 + [Fraction(1)])
    r = rank(a)
    delta = [[Fraction(0)]*6 + [Fraction(1), Fraction(0)]]
    epsilon = [[Fraction(0)]*7 + [Fraction(1)]]
    return {
        "bearings": len(observations),
        "externally_calibrated_station_epoch": station_epoch_calibrated,
        "rank_of_eight_parameters": r,
        "nullity": 8-r,
        "unidentified_target_clock_dimensions": rank(a+delta)-r,
        "unidentified_station_clock_dimensions": rank(a+epsilon)-r,
    }


def report():
    x,y,z,u = (1,0,0),(0,1,0),(0,0,1),(1,1,1)
    obs = ((0,x),(1,y),(2,z),(3,u))
    still = ((0,0,0),)*4
    transverse = still[:3]+((1,0,0),)
    radial = still[:3]+((1,1,1),)
    v = (2,-1,3)
    return {
        "scope": "SYNTHETIC_AFFINE_STATION_EPOCH_GAUGE_ONLY",
        "parameters": ["r0_xyz", "v_xyz", "target_clock_delta", "station_epoch_epsilon"],
        "model": "target=r0+v*(t+delta); station=s0+w*(t+delta+epsilon)",
        "frame": "hypothetical shared inertial Cartesian frame",
        "designs": {
            "four_stationary_free_epoch": assess(obs,v,still),
            "four_transverse_free_epoch": assess(obs,v,transverse),
            "four_transverse_calibrated_epoch": assess(
                obs,v,transverse,station_epoch_calibrated=True),
            "four_radial_calibrated_epoch": assess(
                obs,v,radial,station_epoch_calibrated=True),
        },
        "exact_gauge": [str(x) for x in exact_gauge(v)],
        "historical_station_time_calibration": "NOT_AVAILABLE",
        "historical_sensor_data": "NOT_AUTHENTICATED",
        "historical_mcmc": "NOT_RUN",
        "historical_geography": "NOT_CONSTRAINED",
    }


if __name__ == "__main__":
    print(json.dumps(report(), sort_keys=True, indent=2))
