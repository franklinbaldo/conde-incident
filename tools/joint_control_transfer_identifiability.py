#!/usr/bin/env python3
"""Exact counterexample to inferring a missing object's path from sibling controls.

No historical observations, orbital propagator, noise model or likelihood.
The scalar polynomial here is a transparent *toy design*, not RAAN physics.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path

from raan_lineage_identifiability import matrix_rank_exact

OBJECTS = (527, 528, 529)
N = 10  # (position, rate, object curvature) for each + shared curvature
OUT = Path('research/statistics/joint_control_transfer_identifiability_C241.json')
SCHEMA = 'conde.joint-control-identifiability-counterexample/v1'


def row(obj: int, t: Fraction) -> tuple[Fraction, ...]:
    """Toy y_j(t)=a_j+v_j*t+(g+b_j)*t^2/2, with exact rational time."""
    if type(obj) is not int or obj not in OBJECTS:
        raise ValueError('expected one of NORAD 527, 528, 529')
    if not isinstance(t, Fraction) or isinstance(t, bool) or t < 0:
        raise ValueError('t must be a nonnegative rational toy time')
    values = [Fraction(0) for _ in range(N)]
    offset = 3 * OBJECTS.index(obj)
    values[offset] = 1
    values[offset + 1] = t
    values[offset + 2] = t*t/2
    values[-1] = t*t/2
    return tuple(values)


def basis(i: int) -> tuple[Fraction, ...]:
    if type(i) is not int or not 0 <= i < N:
        raise ValueError('basis column outside design')
    return tuple(Fraction(int(k == i)) for k in range(N))


def dot(xs: tuple[Fraction, ...], ys: tuple[Fraction, ...]) -> Fraction:
    if len(xs) != N or len(ys) != N:
        raise ValueError('ten-column vectors required')
    return sum((a*b for a, b in zip(xs, ys)), Fraction(0))


def estimable(training: list[tuple[Fraction, ...]], target: tuple[Fraction, ...]) -> bool:
    if not training or len(target) != N or any(len(r) != N for r in training):
        raise ValueError('ten-column nonempty training design required')
    return matrix_rank_exact(training + [target]) == matrix_rank_exact(training)


def observations() -> list[tuple[Fraction, ...]]:
    return ([row(obj, Fraction(t)) for obj in (527, 529) for t in (0, 1, 2)]
            + [row(528, Fraction(t)) for t in (0, 1)])


def build() -> dict:
    train = observations()
    target = row(528, Fraction(3))
    more_controls = train + [row(obj, Fraction(3)) for obj in (527, 529)]
    third_528 = train + [row(528, Fraction(2))]
    known_control_drag = train + [basis(2)]
    known_shared_and_528_drag = train + [basis(9), basis(5)]
    # Gauge: global curvature increased and each object's b_j decreased.
    shared_gauge = tuple(Fraction(-1) if i in (2, 5, 8) else
                         Fraction(1) if i == 9 else Fraction(0)
                         for i in range(N))
    # Change b_528 and v_528 without changing its t=0,1 readings.
    missing_528 = tuple(Fraction(-1, 2) if i == 4 else
                        Fraction(1) if i == 5 else Fraction(0)
                        for i in range(N))
    if any(dot(r, shared_gauge) for r in more_controls + [target]):
        raise AssertionError('global curvature gauge incorrectly specified')
    if any(dot(r, missing_528) for r in more_controls):
        raise AssertionError('missing-body witness must fit training and controls')
    if dot(target, missing_528) != 3:
        raise AssertionError('missing-body witness must change target prediction')
    if (matrix_rank_exact(train), matrix_rank_exact(more_controls),
            matrix_rank_exact(third_528)) != (8, 8, 9):
        raise AssertionError('design or witness drift')
    return {
        'schema': SCHEMA,
        'classification': 'COUNTERFACTUAL_EXACT_LINEAR_MODEL_NOT_AN_ORBITAL_INFERENCE',
        'source_context': {
            'issue': 'https://github.com/franklinbaldo/conde-incident/issues/396',
            'occurrence_ids': ['C241-L18', 'C241-P10'],
            'source_status': 'ISSUE_CONTEXT_ONLY_NOT_INPUT_OBSERVATIONS',
            'historical_observations_loaded': 0,
        },
        'model': {
            'equation': 'y_j(t)=a_j+v_j*t+(g+b_j)*t^2/2',
            'columns': ['a527', 'v527', 'b527', 'a528', 'v528', 'b528',
                        'a529', 'v529', 'b529', 'g'],
            'time': 'exact dimensionless rational times 0,1,2,3 (DESIGN ONLY)',
            'shared_term': 'g is common, b_j is object-specific unconstrained curvature',
            'not_a_physical_operator': True,
        },
        'scenarios': {
            'baseline': {
                'training_rows': len(train), 'rank': matrix_rank_exact(train),
                'unknown_columns': N, 'terminal_528_row_estimable': estimable(train, target),
            },
            'additional_control_after_missing_body': {
                'training_rows': len(more_controls),
                'rank': matrix_rank_exact(more_controls),
                'terminal_528_row_estimable': estimable(more_controls, target),
                'observation_status': 'HYPOTHETICAL_NOT_A_RECOVERED_TRACK',
            },
            'additional_528_epoch_before_holdout': {
                'training_rows': len(third_528), 'rank': matrix_rank_exact(third_528),
                'terminal_528_row_estimable': estimable(third_528, target),
                'observation_status': 'HYPOTHETICAL_NOT_A_RECOVERED_TRACK',
            },
            'known_control_specific_curvature': {
                'rank': matrix_rank_exact(known_control_drag),
                'terminal_528_row_estimable': estimable(known_control_drag, target),
                'status': 'INDEPENDENT_CALIBRATION_ASSUMED_NOT_DOCUMENTED',
            },
            'known_shared_and_528_specific_curvature': {
                'rank': matrix_rank_exact(known_shared_and_528_drag),
                'terminal_528_row_estimable': estimable(known_shared_and_528_drag, target),
                'status': 'TWO_INDEPENDENT_CALIBRATIONS_ASSUMED_NOT_DOCUMENTED',
            },
        },
        'witnesses': {
            'shared_curvature_gauge': {
                'delta_g': '1', 'delta_each_b': '-1',
                'training_and_target_changes': '0',
                'shared_g_separately_identified': False,
            },
            'missing_528_curvature': {
                'delta_v528': '-1/2', 'delta_b528': '1',
                'training_and_control_changes': '0',
                'target_528_t3_change': '3',
            },
        },
        'decision': {
            'holdout_rule': 'exclude all evaluation 528 rows from training; no post-528 sibling track is a 528 measurement',
            'discriminating_inputs': [
                'an authenticated calibrated extra 528 track at a distinct pre-holdout time',
                'independent physical bounds on 528-specific ballistic/initial state parameters',
                'validated shared dynamics, atmosphere and sensor covariance for 527/529 controls',
            ],
            'historical_mcmc': 'NOT_RUN',
            'historical_terminal_time': 'NOT_IDENTIFIED',
            'geographic_exclusion': 'NOT_AUTHORIZED',
            'active_constraint': False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    encoded = (json.dumps(build(), sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()
    if args.check:
        if not OUT.exists() or OUT.read_bytes() != encoded:
            raise SystemExit('joint-control report drift; regenerate and review')
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(encoded)


if __name__ == '__main__':
    main()
