#!/usr/bin/env python3
"""G38: falsify 'nodal versus Kepler' as the sole Dec-1963 SSR gap.

First-order J2 only: not historical orbit determination or instrument calibration.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

try:
    from tools.ssr_crossfield_screen_g37 import build as audit_source
except ModuleNotFoundError as exc:
    if exc.name != 'tools':
        raise
    from ssr_crossfield_screen_g37 import build as audit_source

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json'
OUTPUT = ROOT / 'research/constraints/CASTOR-G38_ssr_dec31_nodal_scale.json'


def period_models_min(apogee_km: float, perigee_km: float,
                      inclination_deg: float) -> tuple[float, float]:
    """Independent analytic Kepler/J2 draconitic proxy in minutes (not SGP4)."""
    radius, mu, j2 = 6378.137, 398600.4418, 1.08262668e-3
    if not (all(map(math.isfinite, (apogee_km, perigee_km, inclination_deg)))
            and 0 <= perigee_km <= apogee_km
            and 0 <= inclination_deg <= 180):
        raise ValueError('invalid mean-orbit proxy inputs')
    a = radius + (apogee_km + perigee_km) / 2
    e = (apogee_km - perigee_km) / (2 * a)
    n = math.sqrt(mu / a**3)
    ci2 = math.cos(math.radians(inclination_deg)) ** 2
    common = 0.75 * j2 * n * (radius / a)**2
    omega_dot = common * (5 * ci2 - 1) / (1 - e*e)**2
    mean_anomaly_dot = n + common * (3 * ci2 - 1) / (1 - e*e)**1.5
    if omega_dot + mean_anomaly_dot <= 0:
        raise ValueError('nonpositive nodal rate')
    return 2 * math.pi / n / 60, 2 * math.pi / (omega_dot + mean_anomaly_dot) / 60


def evaluate(ledger: dict) -> dict:
    """Zero-fit first-order J2 screen, with source-locked print boxes."""
    audited = audit_source(ledger)  # pins all seven cells and source metadata
    records = []
    for source in ledger['sources']:
        for row in source['rows']:
            apo, peri = row['apogee_km'], row['perigee_km']
            inc = float(row['inclination_deg'])
            printed = float(row['period_min'])
            kepler, nodal = period_models_min(apo, peri, inc)
            corner_models = [
                period_models_min(apo + da, peri + dp, inc + di)
                for da, dp, di in itertools.product((-0.5, 0.5), (-0.5, 0.5), (-0.005, 0.005))
            ]
            corner_j2 = [x[1] for x in corner_models]
            # These are bounded editorial rounding boxes only, not sigma,
            # and they do not bound modeling errors or observational latency.
            residual_bounds = [
                60 * (printed - 0.05 - max(corner_j2)),
                60 * (printed + 0.05 - min(corner_j2)),
            ]
            if not all(map(math.isfinite, residual_bounds)) or residual_bounds[0] > residual_bounds[1]:
                raise ValueError('bad J2 residual interval')
            records.append({
                'source_occurrence': f"C241-L18:{source['ntrs_id']}:{row['designator']}",
                'publication_NOT_instrument_epoch': source['published'],
                'designator': row['designator'],
                'printed_nodal_period_min': printed,
                'kepler_two_body_min': round(kepler, 9),
                'first_order_J2_nodal_proxy_min': round(nodal, 9),
                'J2_minus_kepler_sec': round(60 * (nodal - kepler), 6),
                'printed_minus_J2_proxy_sec': round(60 * (printed - nodal), 6),
                'print_box_only_residual_sec_NOT_sigma': [round(v, 6) for v in residual_bounds],
                'model_is_conditional': True,
                'instrument_epoch_utc': None,
                'instrumental_uncertainty': None,
                'historical_orbit_fit': False,
            })
    dec = {r['designator']: r for r in records
           if r['publication_NOT_instrument_epoch'] == '1963-12-31'}
    if len(records) != len(audited['cells']) or set(dec) != {'1963-003A', '1963-003C'}:
        raise ValueError('missing or duplicated pinned NASA cells')
    a, c = dec['1963-003A'], dec['1963-003C']
    if not (a['print_box_only_residual_sec_NOT_sigma'][0] < 0 <
            a['print_box_only_residual_sec_NOT_sigma'][1]
            and c['print_box_only_residual_sec_NOT_sigma'][1] < -100):
        raise ValueError('model contrast changed; audit assumptions')
    return {
        'schema': 'conde.ssr-nodal-convention-falsification/v1',
        'id': 'CASTOR-G38-DEC31-PRINTED-NODAL-J2',
        'epistemic_status': 'COMPUTED_CONDITIONAL_NO_OBSERVED_ORBIT',
        'depends_on': ['C241-L18', 'CASTOR-G37-DEC31-SSR-CROSSFIELD', 'C241-P7'],
        'source_ledger': 'research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json',
        'document_family': 'NASA_GODDARD_COMPILED_SSR_NOT_INDEPENDENT_SENSORS',
        'source_pdf_sha256': {s['ntrs_id']: s['sha256'] for s in ledger['sources']},
        'model': 'first-order J2 secular draconitic proxy using omega_dot + M_dot; printed heights conditionally taken as coepoch mean-orbit apsidal altitudes',
        'assumption_details': {
            'earth_radius_km': 6378.137, 'earth_mu_km3_s2': 398600.4418,
            'J2': 0.00108262668, 'period_print_half_width_min': 0.05,
            'height_print_half_width_km': 0.5, 'inclination_print_half_width_deg': 0.005,
            'eight_box_corners': True, 'box_is_not_instrumental_sigma': True,
            'nodal_model_convention_proven_historical': False,
            'same_epoch_hypothesis_proven': False, 'calibrated_model_error_bound': None,
        },
        'records': records,
        'december_31_contrast': {
            '529_J2_minus_kepler_seconds': c['J2_minus_kepler_sec'],
            '529_printed_minus_J2_seconds': c['printed_minus_J2_proxy_sec'],
            '529_printing_box_excludes_zero': c['print_box_only_residual_sec_NOT_sigma'][1] < 0,
            '527_printed_minus_J2_seconds': a['printed_minus_J2_proxy_sec'],
            'first_order_J2_alone_reconciles_529': False,
            'this_does_not_prove_NASA_error': True,
        },
        'uncertainty': {
            'source_instrument_epoch': None, 'instrument_station': None,
            'source_covariance': None, 'historical_element_convention': None,
            'residual_causes_unresolved': ['heterogeneous update epoch', 'mean vs osculating elements', 'compiled field provenance', 'model convention'],
        },
        'source_raw_instrument_observations': 0,
        'independent_527_529_holdout': 'NOT_RUN',
        'activated_historical_restriction': False,
        'conde_impact_hour_place_probability': 'NOT_DETERMINED',
    }


def render(ledger: dict) -> str:
    return json.dumps(evaluate(ledger), ensure_ascii=False, indent=2) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = render(json.loads(SOURCE.read_text(encoding='utf-8')))
    if args.write:
        OUTPUT.write_text(content, encoding='utf-8')
    elif OUTPUT.read_text(encoding='utf-8') != content:
        raise SystemExit('G38 output drift')
    print('G38: first-order J2 tested on seven pinned NASA rows; 529 December gap persists')


if __name__ == '__main__':
    main()
