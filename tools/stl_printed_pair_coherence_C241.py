#!/usr/bin/env python3
"""Source-pinned, unit-invariant diagnostic of a 1963 STL editorial pair.

Never infers an observation epoch, measurement uncertainty, physical units or orbit.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/tle_custody/stl_space_log_nasa_r51.json'
REPORT = ROOT / 'research/statistics/C241_stl_printed_pair_coherence.json'


def require(condition: bool, msg: str) -> None:
    if not condition:
        raise ValueError(msg)


def round_nearest_tenth_positive(value: Fraction, *, tie: str) -> Fraction:
    """Exact decimal quantization: no binary floats or inferred sensor sigma.

    The two documented policies give different outputs only at an exact tie.
    They are *counterfactual conventions*, not verified STL editorial rules.
    """
    if not isinstance(value, Fraction) or value < 0 or tie not in ('half-even', 'half-up'):
        raise ValueError('positive rational and supported deterministic tie policy required')
    units = 10 * value
    lower = units.numerator // units.denominator
    remainder = units - lower
    if remainder > Fraction(1, 2) or (remainder == Fraction(1, 2) and
        (tie == 'half-up' or (tie == 'half-even' and lower % 2 != 0))):
        lower += 1
    return Fraction(lower, 10)


def inspect(doc: dict, source_bytes: bytes) -> dict:
    # An existing independently tested audit pins the editorial transcription.
    from tools.audit_stl_space_log_r51 import audit
    require(audit(doc) == 'EDITORIAL_REPRODUCTION_MILES_PRINTED_SUBTYPE_PENDING_ZERO_CONSTRAINTS',
            'STL R51 provenance not validated')
    row = doc['printed_row']
    p = row['perigee_altitudes_in_printed_order']
    a = row['apogee_altitudes_in_printed_order']
    period = row['period_minutes_in_printed_order']
    require(len(p) == len(a) == len(period) == 2, 'two printed columns required')
    require(all(type(x) is int and x > 0 for x in p + a), 'integer altitudes required')
    require(all(type(x) is float and x > 0 for x in period), 'printed decimal periods required')
    # Decimal floats are parsed as exact display strings, never as measurement precision.
    t = [Fraction(str(x)) for x in period]
    sums = [p[i] + a[i] for i in range(2)]
    half = [Fraction(s, 2) for s in sums]
    require(sums == [620, 620], 'printed sums drifted')
    require(half == [310, 310], 'printed mean-altitude proxy drifted')
    require((p[1] - p[0], a[1] - a[0]) == (-12, 12),
            'perigee/apogee compensating change drifted')
    require((t[0] - t[1]) * 60 == 6, 'printed nominal period difference drifted')
    # Rounding to a tenth is a proposed, explicitly conditional display model:
    # [v-.05,v+.05], with unknown tie policy; adjacent intervals meet at a boundary.
    display_half_unit = Fraction(1, 20)
    intervals = [(x - display_half_unit, x + display_half_unit) for x in t]
    intersect_at = max(intervals[0][0], intervals[1][0])
    require(intersect_at == min(intervals[0][1], intervals[1][1]),
            'printed period rounding intervals no longer touch')
    # At their shared boundary x=94.65, two *different* deterministic tie
    # conventions produce the adjacent printed values. No *single* deterministic
    # convention can map one identical input to two different printed outputs.
    tie_witness = intersect_at
    tie_results = {}
    for mode in ('half-even', 'half-up'):
        rounded_tenths = int(10 * round_nearest_tenth_positive(tie_witness, tie=mode))
        tie_results[mode] = f'{rounded_tenths // 10}.{rounded_tenths % 10}'
    require(tie_results == {'half-even': '94.6', 'half-up': '94.7'},
            'tenth-minute quantization witness drifted')
    return {
        'id': 'C241-CERVO-STL-PAIR-COHERENCE',
        'classification': 'DOCUMENTARY_INTERNAL_CONSISTENCY_NOT_INSTRUMENT_TRACK',
        'pinned_source_id': doc['id'],
        'source_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'source_pdf_sha256': doc['pdf_sha256'],
        'printed_designation': row['international_designation_as_printed'],
        'printed_altitude_unit': 'miles',
        'original_stl_issue_retrieved': False,
        'columns_are_coepoch': None,
        'period_and_altitude_element_conventions_equal': None,
        'printed_altitude_sum': sums,
        'printed_mean_altitude_in_printed_miles': [str(v) for v in half],
        'perigee_difference_second_minus_first_printed_units': p[1]-p[0],
        'apogee_difference_second_minus_first_printed_units': a[1]-a[0],
        'period_nominal_difference_first_minus_second_seconds': str((t[0]-t[1])*60),
        'conditional_rounding_model': {
            'hypothesis': 'each displayed tenth of a minute rounds an unknown underlying period',
            'display_half_width_seconds': '3',
            'first_possible_minutes_closed_envelope': [f'{float(v):.2f}' for v in intervals[0]],
            'second_possible_minutes_closed_envelope': [f'{float(v):.2f}' for v in intervals[1]],
            'intervals_touch_at_minutes': f'{float(intersect_at):.2f}',
            'tie_handling_unknown': True,
            'zero_underlying_difference_excluded': False,
            'same_input_distinct_prints_under_one_deterministic_rule': False,
            'same_input_distinct_prints_under_different_tie_rules': True,
            'counterfactual_shared_boundary_minutes': str(tie_witness),
            'counterfactual_tie_policy_outputs_minutes': tie_results,
            'printed_periods_not_proven_same_physical_observable': True,
            'no_published_rounding_policy_authenticated': True,
        },
        'two_body_invariance': {
            'claim': 'same printed mean height implies same Kepler period for any common unit scale, GM and Earth radius, if the columns are comparable',
            'not_a_fit_to_the_periods': True,
            'actual_semimajor_axes_equal': None,
            'actual_physical_periods_equal': None,
        },
        'observational_design': {
            'acquire': [
                'original STL SPACE LOG volume 3 issue 4 table caption, legend, unit and paired-column headings',
                'time-tagged source observations and definitions of period and altitude fields',
                'separate original sensor provenance and measurement covariance',
                'catalog-to-piece crosswalk for NORAD 528, independent orbital observations near terminal epoch',
            ],
            'new_528_tracking_observations': 0,
            'new_instrumental_sensors': 0,
            'historical_mass_rank_gain': 0,
            'historical_mcmc': 'NOT_RUN',
            'active_constraint': False,
            'condes_geographic_domain_reduced': False,
        },
    }


def report() -> dict:
    original = SOURCE.read_bytes()
    return inspect(json.loads(original), original)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    payload = (json.dumps(report(), indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()
    if args.check:
        require(REPORT.is_file() and REPORT.read_bytes() == payload, 'report drift')
    else:
        REPORT.write_bytes(payload)


if __name__ == '__main__':
    main()

