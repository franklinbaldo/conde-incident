#!/usr/bin/env python3
"""Connect conditional NASA SSR J2 print boxes to custody, Lean, and latent Θ.

Not a tracking epoch, RAAN observation, physical covariance or orbit fit.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'research/constraints/C241-P11_november_historical_printings.json'
UPSTREAM = ROOT / 'public/data/conde-ssr-kepler-provenance.json'
G35 = ROOT / 'research/constraints/C241-P13_ssr_j2_print_rates_g35.json'
SIM = ROOT / 'research/constraints/C241-P10_three_object_relative_trajectories.json'
OUT = ROOT / 'public/data/conde-ssr-j2-provenance.json'
A, C = '1963-003A', '1963-003C'


def rate(hp: float, ha: float, inclination: float, constants: dict) -> float:
    re = constants['earth_radius_km']
    rp, ra = re + hp, re + ha
    a, p = (rp + ra) / 2, 2 * rp * ra / (rp + ra)
    return (-1.5 * math.sqrt(constants['mu_km3_s2'] / a**3) * constants['j2']
            * (re / p)**2 * math.cos(math.radians(inclination))
            * constants['day_seconds'] * 180 / math.pi)


def build(ledger: dict, provenance: dict, j2: dict, simulator: dict) -> dict:
    if (ledger.get('id') != 'C241-P11' or provenance.get('id') != 'ABELHA-G34-SSR-PRINTED-UNITS'
            or j2.get('id') != 'CASTOR-G35-C241-P13-PRINTED-J2-INTERVALS'
            or j2.get('classification') != 'CONDITIONAL_COMPUTATIONAL_PRINT_BOX_NOT_HISTORICAL_ORBIT'
            or simulator.get('id') != 'C241-P10-three-object-relative-trajectories'):
        raise ValueError('upstream identity mismatch')
    if (provenance.get('active_physical_constraint') is not False
            or provenance.get('simulator_parameter_values') is not None
            or provenance.get('physical_domain_effect') != 'THETA_UNCHANGED'
            or provenance.get('publication_dates_are_sensor_epochs') is not False
            or ledger.get('same_compilation_not_independent_sensors') is not True
            or ledger.get('quantization_units') != {
                'apogee_km': 'half-kilometer', 'perigee_km': 'half-kilometer',
                'period_min': 'centiminute', 'inclination_deg': 'centidegree'
            }):
        raise ValueError('provenance/units cannot establish observed orbit')
    const = j2.get('constants')
    if const != {'mu_km3_s2': 398600.4418, 'earth_radius_km': 6378.137,
                 'j2': 0.00108262668, 'day_seconds': 86400}:
        raise ValueError('J2 model constants changed')
    if (j2.get('print_intervals') != {
            'perigee_apogee_half_width_km': 0.5, 'inclination_half_width_deg': 0.005,
            'box_corner_count': 8, 'not_instrument_sigma': True,
        } or j2.get('limitations') != {
            'original_instrument_epoch': None, 'original_covariance': None, 'raan': None,
            'osculating_element_convention': 'UNVERIFIED', 'validation': 'NOT_RUN',
            'historical_domain_reduction': 'NONE', 'impact_inference': 'NOT_SUPPORTED',
            'publication_dates_are_not_tracking_epochs': True,
            'shared_source_family': 'NASA_GODDARD_COMPILED_FROM_TRACKING',
            'not_probability': True,
        } or simulator.get('active_physical_domain_reduction') != 'NOT_EVALUABLE'):
        raise ValueError('false observational promotion or changed box semantics')
    dates, ids, hashes = ledger['publication_dates'], ledger['source_ids'][:3], ledger['source_sha256']
    if (len(dates) != 3 or len(ids) != 3 or len(hashes) != 3
            or ledger['source_ids'] != [*ids, 'C197#1']
            or ids != ['C241-L12', 'C241-L19#1', 'C241-L18:19640002493']
            or len(set(zip(dates, ids, hashes))) != 3
            or len(provenance.get('cells', [])) != 6 or len(j2.get('results', [])) != 6
            or len(j2.get('paired_model_contrasts', [])) != 3):
        raise ValueError('source cardinality or genealogy changed')
    if [x['designator'] for x in ledger['objects']] != [A, C]:
        raise ValueError('only the 527/529 paired controls, not the 528')
    cells, contrasts = [], []
    used = set()
    for obj in ledger['objects']:
        if len(obj['printed_values_scaled']) != 3:
            raise ValueError('expected three source publications')
        for index, printed in enumerate(obj['printed_values_scaled']):
            date, source, digest = dates[index], ids[index], hashes[index]
            key = (date, source, digest, obj['designator'])
            upstream = [x for x in provenance['cells'] if (
                x['report_publication_date_not_epoch'], x['source_occurrence'],
                x['source_pdf_sha256'], x['object']) == key]
            derived = [x for x in j2['results'] if (
                x['publication_date'], x['source_id'],
                x['source_pdf_sha256'], x['designator']) == key]
            if len(upstream) != 1 or len(derived) != 1 or key in used:
                raise ValueError('missing, duplicate or unproven source/object pairing')
            used.add(key)
            up, got = upstream[0], derived[0]
            if (up['perigee_half_km'], up['apogee_half_km'], up['period_centimin']) != (
                    printed['perigee_km'], printed['apogee_km'], printed['period_min']):
                raise ValueError('G34 unit/custody mismatch')
            if up['instrument_epoch'] is not None or up['covariance'] is not None or up['active_physical_constraint'] is not False:
                raise ValueError('G34 physical promotion forbidden')
            hp, ha = printed['perigee_km']/2, printed['apogee_km']/2
            inc = printed['inclination_deg']/100
            nominal = rate(hp, ha, inc, const)
            corners = [rate(hp+dp, ha+da, inc+di, const)
                       for dp in (-.5, .5) for da in (-.5, .5) for di in (-.005, .005)]
            bounds = [min(corners), max(corners)]
            if (not math.isclose(got['nominal_deg_day'], nominal, rel_tol=0, abs_tol=1e-8)
                    or len(got['print_only_signed_deg_day']) != 2
                    or any(not math.isclose(v, w, rel_tol=0, abs_tol=1e-8)
                           for v, w in zip(got['print_only_signed_deg_day'], bounds))):
                raise ValueError('conditional J2 rate differs from independently computed 8 corners')
            cells.append({
                'source_occurrence': source, 'source_pdf_sha256': digest,
                'publication_date_not_epoch': date, 'object': obj['designator'],
                'upstream_cell': up['id'], 'derived_model': j2['id'],
                'conditional_j2_deg_day': got['nominal_deg_day'],
                'print_box_only_deg_day_not_sigma': got['print_only_signed_deg_day'],
                'instrument_epoch_utc': None, 'instrument_covariance': None,
                'raan_deg': None, 'status': 'CONNECTED_PENDING_CALIBRATION',
            })
    for date in dates:
        a, c = [next(x for x in cells if x['publication_date_not_epoch'] == date and x['object'] == obj)
                for obj in (A, C)]
        av, cv = a['print_box_only_deg_day_not_sigma'], c['print_box_only_deg_day_not_sigma']
        bounds = [av[0] - cv[1], av[1] - cv[0]]
        matched = [x for x in j2['paired_model_contrasts'] if x['publication_date'] == date]
        if (len(matched) != 1 or matched[0]['sign_positive_under_print_box'] is not True
                or matched[0]['historical_ordering_in_time'] != 'NOT_INFERRED'
                or len(matched[0]['a_minus_c_deg_day']) != 2
                or any(not math.isclose(v, w, rel_tol=0, abs_tol=2e-8)
                       for v, w in zip(matched[0]['a_minus_c_deg_day'], bounds))
                or bounds[0] <= 0):
            raise ValueError('same-edition J2 contrast not justified by boxes')
        contrasts.append({
            'publication_date_not_epoch': date, 'source_occurrence': a['source_occurrence'],
            'source_pdf_sha256': a['source_pdf_sha256'],
            'object_pair': [A, C], 'conditional_a_minus_c_deg_day': matched[0]['a_minus_c_deg_day'],
            'activation': False, 'not_an_observed_temporal_drift': True,
        })
    if len(used) != 6:
        raise ValueError('six and only six source-locked cells')
    return {
        'schema': 'conde.ssr-j2-print-bridge/v1', 'id': 'ABELHA-G35-C241-P13-J2-CUSTODY-BRIDGE',
        'parents': [str(LEDGER.relative_to(ROOT)), str(UPSTREAM.relative_to(ROOT)),
                    str(G35.relative_to(ROOT)), str(SIM.relative_to(ROOT))],
        'source_family': 'NASA_GODDARD_COMPILED_SHARED_TRACKING_NOT_SIX_SENSORS',
        'source_to_model': 'NASA_SSR_PRINTED_ELEMENTS -> PRINT_BOX -> J2_FIRST_ORDER -> SAME_EDITION_CONTRAST',
        'cells': cells, 'contrasts': contrasts,
        'lean_related_existing_theorem': 'Conde1963.SsrEditionOffset.no_shared_additive_edition_offset',
        'lean_existing_theorem_scope': 'printed_period_arithmetic_only_not_J2',
        'lean_j2_proof': None, 'lean_j2_status': 'CANDIDATE_NOT_PROMOTED',
        'simulator_contract': str(SIM.relative_to(ROOT)),
        'conditional_forward_operator': 'src/lib/orbitSsrJ2PrintIntervals.ts:firstOrderJ2RateDegDay',
        'latent_parameters': {
            'original_observation_epochs_utc': None, 'inertial_frame': None,
            'osculating_vs_mean_element_mapping': None, 'instrument_covariance': None,
            'absolute_raan_of_controls': None, 'observed_528_state': None,
        },
        'missing_activation_prerequisites': [
            'original_time_tagged_tracking', 'source_specific_genealogy', 'inertial_frame',
            'instrument_calibration_and_covariance', 'mean_osculating_convention',
            'validated_propagator_and_independent_holdout',
        ],
        'simulator_calibrated_values': None, 'active_physical_constraint': False,
        'physical_domain_effect': 'THETA_UNCHANGED',
        'historical_raan_or_overflight_inference': 'NOT_SUPPORTED',
    }


def render() -> str:
    data = [json.loads(p.read_text()) for p in (LEDGER, UPSTREAM, G35, SIM)]
    return json.dumps(build(*data), ensure_ascii=False, indent=2) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-site', action='store_true')
    parser.add_argument('--check-site', action='store_true')
    args = parser.parse_args()
    value = render()
    if args.write_site:
        OUT.write_text(value)
    if args.check_site and OUT.read_text() != value:
        raise SystemExit('J2 source-to-science bridge stale')
    print('Six custody-locked conditional J2 rows / three within-edition contrasts; Θ unchanged')


if __name__ == '__main__':
    main()
