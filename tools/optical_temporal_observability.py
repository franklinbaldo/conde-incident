"""Exact rational observability for synthetic optical bearings, not 1963 data."""
from fractions import Fraction
import json


def projector(direction):
    if not isinstance(direction, (tuple, list)) or len(direction) != 3:
        raise ValueError("3D direction required")
    if any(isinstance(x, bool) or not isinstance(x, (int, Fraction))
           for x in direction):
        raise ValueError("exact rational components required")
    d = tuple(Fraction(x) for x in direction)
    norm2 = sum(x*x for x in d)
    if not norm2:
        raise ValueError("zero direction")
    return [[Fraction(i == j)-d[i]*d[j]/norm2 for j in range(3)]
            for i in range(3)]


def bearing_matrix(observations):
    if not isinstance(observations, (tuple, list)) or not observations:
        raise ValueError("observations required")
    rows = []
    for time, direction in observations:
        if isinstance(time, bool) or not isinstance(time, (int, Fraction)):
            raise ValueError("exact rational epoch required")
        for row in projector(direction):
            rows.append(row + [Fraction(time)*x for x in row])
    return rows


def rank(rows):
    if not rows:
        return 0
    n = len(rows[0])
    if any(len(row) != n for row in rows):
        raise ValueError("ragged matrix")
    a = [[Fraction(x) for x in row] for row in rows]
    r = 0
    for j in range(n):
        pivot = next((i for i in range(r, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        p = a[r][j]
        a[r] = [x/p for x in a[r]]
        for i in range(len(a)):
            if i != r and a[i][j]:
                f = a[i][j]
                a[i] = [x-f*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def assess(observations):
    """Six-state affine model r(t)=r0+v*t; rank over Q, no likelihood.

    rank([A;selector])-rank(A) is the projection dimension of ker A
    onto the selected position or velocity component.
    """
    a = bearing_matrix(observations)
    total = rank(a)
    pos = [[Fraction(i == j) for j in range(6)] for i in range(3)]
    vel = [[Fraction(i+3 == j) for j in range(6)] for i in range(3)]
    return {
        "bearings": len(observations), "rank_of_six_state_columns": total,
        "nullity": 6-total,
        "unidentified_initial_position_dimensions": rank(a+pos)-total,
        "unidentified_velocity_dimensions": rank(a+vel)-total,
    }


def witness(initial_range, final_range):
    """Two arbitrary positive ranges reproduce exactly the same LOS pair."""
    if any(isinstance(x, bool) or not isinstance(x, int) or x <= 0
           for x in (initial_range, final_range)):
        raise ValueError("positive integer synthetic ranges required")
    s0, s1 = (0, 0, 0), (10, 0, 0)
    u0, u1 = (0, 1, 0), (0, 0, 1)
    r0 = tuple(s0[i]+initial_range*u0[i] for i in range(3))
    x1 = tuple(s1[i]+final_range*u1[i] for i in range(3))
    return {
        "initial_position": r0,
        "constant_velocity_per_time_unit": tuple(x1[i]-r0[i] for i in range(3)),
        "first_station": s0, "second_station": s1,
        "first_line_of_sight": u0, "second_line_of_sight": u1,
        "epochs": (0, 1), "ranges": (initial_range, final_range),
    }


def report():
    x, y, z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
    cases = {
        "one_bearing": ((0, x),),
        "two_simultaneous_nonparallel": ((0, x), (0, y)),
        "two_asynchronous_nonparallel": ((0, x), (1, y)),
        "three_asynchronous_orthogonal": ((0, x), (1, y), (2, z)),
        "three_asynchronous_collinear": ((0, x), (1, x), (2, x)),
        "two_simultaneous_plus_later": ((0, x), (0, y), (1, z)),
        "two_stereo_epochs": ((0, x), (0, y), (1, y), (1, z)),
    }
    return {
        "scope": "SYNTHETIC_AFFINE_DESIGN_ONLY",
        "assumed_forward_model": "r(t)=r0+v*t, free 3D position and velocity",
        "units": "arbitrary exact length/time units, NOT 1963 sensor data",
        "designs": {name: assess(obs) for name, obs in cases.items()},
        "explicit_range_ambiguity": [witness(100, 100), witness(200, 300)],
        "dependency": "C241-P14 / optical-parallax PR #463",
        "historical_observation_status": "NOT_AUTHENTICATED",
        "constraint_status": "CONNECTED_PENDING_CALIBRATION",
        "historical_mcmc": "NOT_RUN", "impact_inference": "NOT_SUPPORTED",
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
