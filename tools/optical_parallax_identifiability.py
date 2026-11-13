"""Conditional, calibration-free observability of a point from two optical stations.

No historical observation, station, likelihood, or impact position is inferred.
Both stations and the target MUST be at the same epoch and in one Cartesian frame.
"""
import argparse
import json
from math import atan2, hypot, isfinite, sqrt
from pathlib import Path


def _vec(value):
    if (not isinstance(value, (list, tuple)) or len(value) != 3 or
            any(isinstance(x, bool) or not isinstance(x, (int, float)) or
                not isfinite(x) for x in value)):
        raise ValueError('Expected finite three-dimensional Cartesian vector in km')
    return tuple(float(x) for x in value)


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def assess_geometry(station_a_km, station_b_km, target_km):
    """Return rank and angular-only Jacobian condition, never a statistical posterior.

    A single optical direction has position Jacobian (I - uu^T)/range, rank 2.
    For two directions at one instant the weighted normal matrix has eigenvalues
    a+b and (a+b ± sqrt((a-b)^2 + 4ab cos(theta)^2))/2,
    where a=1/range_a^2 and b=1/range_b^2. The smallest eigenvalue is
    evaluated by its determinant to avoid cancellation at narrow parallax.
    """
    sa, sb, target = map(_vec, (station_a_km, station_b_km, target_km))
    da, db = _sub(target, sa), _sub(target, sb)
    ra, rb = hypot(*da), hypot(*db)
    if not ra or not rb or not (isfinite(ra) and isfinite(rb)):
        raise ValueError('Target must be distinct from both stations with finite ranges')
    ua, ub = tuple(x/ra for x in da), tuple(x/rb for x in db)
    dot = max(-1.0, min(1.0, _dot(ua, ub)))
    sin_angle = min(1.0, hypot(*_cross(ua, ub)))
    angle = atan2(sin_angle, dot)
    a, b = 1/(ra*ra), 1/(rb*rb)
    # Recovered lower eigenvalue from determinant ab*sin^2(theta).
    upper_plane = (a+b + hypot(a-b, 2*sqrt(a*b)*abs(dot))) / 2
    lower_plane = a*b*sin_angle*sin_angle / upper_plane
    max_eigen = a+b
    return {
        'classification': 'CONDITIONAL_GEOMETRIC_DESIGN_NOT_HISTORICAL_INFERENCE',
        'one_station_rank': 2,
        'two_station_structural_rank': 2 if sin_angle == 0 else 3,
        'parallax_angle_deg': angle * 180 / 3.141592653589793,
        'squared_singular_values_per_km2': [lower_plane, upper_plane, max_eigen],
        'angular_jacobian_condition': (sqrt(max_eigen/lower_plane)
                                       if lower_plane else None),
        'sensor_covariance': None,
        'physical_orbit_model': None,
        'instrument_authentication': 'NOT_ASSESSED',
        'historical_mcmc': 'NOT_RUN',
        'impact_inference': 'NOT_SUPPORTED',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True,
                        help='JSON with station_a_km, station_b_km, target_km')
    args = parser.parse_args()
    record = json.loads(args.input.read_text(encoding='utf-8'))
    if set(record) != {'station_a_km', 'station_b_km', 'target_km'}:
        parser.error('Only explicit same-epoch same-frame vectors are accepted')
    print(json.dumps(assess_geometry(**record), indent=2, sort_keys=True,
                     allow_nan=False))


if __name__ == '__main__':
    main()
