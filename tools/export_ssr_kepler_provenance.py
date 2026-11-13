#!/usr/bin/env python3
"""Custody-bound link from six NASA SSR printed cells to a conditional Kepler audit.

Publication dates, table units, and rounded diagnostics are not sensor epochs,
independent measurements, instrumental uncertainties or orbital constraints.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'research/constraints/C241-P11_november_historical_printings.json'
AUDIT = ROOT / 'research/constraints/C241-P11_kepler_unit_audit_g34.json'
LOCK = ROOT / 'public/data/conde-ssr-source-locked-links.json'
OUT = ROOT / 'public/data/conde-ssr-kepler-provenance.json'
DESIGNATORS = ('1963-003A', '1963-003C')
DATES = ('1963-10-15', '1963-11-15', '1963-11-30')
SOURCES = ('C241-L12', 'C241-L19#1', 'C241-L18:19640002493')


def build(ledger: dict, audit: dict, lock: dict) -> dict:
    if (ledger.get('id') != 'C241-P11' or audit.get('id') !=
        'CASTOR-G34-C241-P11-SSR-PERIOD-DIMENSIONAL-AUDIT'):
        raise ValueError('upstream identity mismatch')
    if (ledger.get('publication_dates') != list(DATES)
        or ledger.get('source_ids', [])[:3] != list(SOURCES)
        or len(ledger.get('source_sha256', [])) != 3
        or len(ledger.get('objects', [])) != 2
        or [x.get('designator') for x in ledger['objects']] != list(DESIGNATORS)):
        raise ValueError('publication order / NASA object identity changed')
    if ledger.get('source_ids') != [*SOURCES, 'C197#1']:
        raise ValueError('C197 is context, not a fourth observation row')
    if (ledger.get('quantization_units') != {
        'apogee_km': 'half-kilometer', 'perigee_km': 'half-kilometer',
        'period_min': 'centiminute', 'inclination_deg': 'centidegree'
        } or ledger.get('same_compilation_not_independent_sensors') is not True
        or ledger.get('physical_admissible_domain_change') != 'NONE'):
        raise ValueError('table units or scientific scope changed')
    if (audit.get('classification') !=
        'SOURCE_LOCKED_CONDITIONAL_KEPLER_PLAUSIBILITY_NOT_OBSERVATIONAL_VALIDATION'
        or audit.get('provenance', {}).get('ledger') != LEDGER.relative_to(ROOT).as_posix()
        or audit.get('conclusions', {}).get('active_domain_reduction') is not False
        or audit.get('conclusions', {}).get('instrumental_covariance') is not None
        or audit.get('conclusions', {}).get('frame_and_observation_epoch') is not None
        or audit.get('conclusions', {}).get('independent_sensor_validation') is not False
        or audit.get('historical_holdout') != 'NOT_RUN'):
        raise ValueError('dimensional audit promoted to instrumental validation')
    # No independent source: November's locked bridge must agree with both editions.
    linked = lock.get('linked_sources', [])
    if (len(linked) != 2 or lock.get('canonical_value_min') != '94.6'
        or lock.get('active_physical_constraint') is not False
        or lock.get('physical_domain_effect') != 'THETA_UNCHANGED'):
        raise ValueError('November source lock changed')
    for source, sha in zip(SOURCES[1:], ledger['source_sha256'][1:]):
        if sum(x.get('occurrence_id') == source and x.get('pdf_sha256') == sha
               for x in linked) != 1:
            raise ValueError(f'NASA edition digest not source-locked: {source}')
    source_hashes = ledger['source_sha256']
    if any(not isinstance(h, str) or len(h) != 64 or
           any(c not in '0123456789abcdef' for c in h) for h in source_hashes):
        raise ValueError('invalid source sha256')
    rows = audit.get('cross_field_diagnostics', [])
    if not isinstance(rows, list) or len(rows) != 6:
        raise ValueError('expected six audited cells')
    constants = audit.get('constants', {})
    if constants != {'earth_radius_km': 6378.137, 'earth_mu_km3_per_s2': 398600.4418}:
        raise ValueError('Kepler model constants changed')
    if (audit.get('input_units', {}).get('period_min_field') !=
        'ledger integer counts of 1/100 minute'
        or audit.get('input_units', {}).get('perigee_km_and_apogee_km_field') !=
        'ledger integer counts of HALF-km, not literal km'):
        raise ValueError('dimensional unit contract changed')
    out_rows = []
    for obj in ledger['objects']:
        for i, values in enumerate(obj['printed_values_scaled']):
            date, source_id, digest = DATES[i], SOURCES[i], source_hashes[i]
            matches = [r for r in rows if r.get('object') == obj['designator']
                       and r.get('report_date') == date]
            if len(matches) != 1:
                raise ValueError('missing/duplicated NASA object/publication pair')
            r = matches[0]
            if (r.get('source_occurrence'), r.get('source_pdf_sha256')) != (source_id, digest):
                raise ValueError('PDF provenance mismatch')
            if r.get('observational_epoch') is not None or r.get('sensor_sigma') is not None:
                raise ValueError('sensor epoch/sigma falsely asserted')
            if (not all(isinstance(values[k], int) for k in ('apogee_km','perigee_km','period_min'))
                or values['period_min'] <= 0 or values['apogee_km'] < values['perigee_km']):
                raise ValueError('invalid printed values')
            altitude = (values['apogee_km'] + values['perigee_km']) / 4
            printed = values['period_min'] / 100
            predicted = 2 * math.pi * math.sqrt((6378.137 + altitude)**3 / 398600.4418) / 60
            checks = {
                'altitude_mean_km': altitude,
                'printed_period_min': printed,
                'two_body_period_min': predicted,
                'printed_minus_two_body_seconds': 60 * (printed - predicted),
            }
            for key, expected in checks.items():
                if not isinstance(r.get(key), (int, float)) or not math.isclose(r[key], expected, abs_tol=0.00002):
                    raise ValueError(f'unit/Kepler diagnostic drift: {key}')
            # Validate the audit's printed-precision bounds as well as its center.
            kepler = lambda a: 2 * math.pi * math.sqrt(a**3 / 398600.4418) / 60
            bounds = [60 * (printed - .05 - kepler(6378.137 + altitude + .5)),
                      60 * (printed + .05 - kepler(6378.137 + altitude - .5))]
            if (not isinstance(r.get('print_rounding_residual_seconds'), list)
                or len(r['print_rounding_residual_seconds']) != 2
                or any(not isinstance(got, (int, float)) or not math.isclose(got, want, abs_tol=.00002)
                       for got, want in zip(r['print_rounding_residual_seconds'], bounds))):
                raise ValueError('printed precision was mistaken for sensor uncertainty')
            wrong_unit = 60 * (printed - kepler(6378.137 + 2*altitude))
            if not isinstance(r.get('incorrect_unscaled_height_residual_seconds'), (int,float)) or not math.isclose(
                wrong_unit, r['incorrect_unscaled_height_residual_seconds'], abs_tol=.00006):
                raise ValueError('half-km negative control was altered')
            # Strictly a diagnostic on compiled printed cells, never an observation.
            out_rows.append({
                'id': f'{source_id}:{obj["designator"]}:period_apogee_perigee',
                'source_occurrence': source_id, 'report_publication_date_not_epoch': date,
                'source_pdf_sha256': digest, 'object': obj['designator'],
                'period_centimin': values['period_min'],
                'perigee_half_km': values['perigee_km'], 'apogee_half_km': values['apogee_km'],
                'two_body_residual_seconds': r['printed_minus_two_body_seconds'],
                'print_rounding_residual_seconds_not_sigma': r['print_rounding_residual_seconds'],
                'instrument_epoch': None, 'covariance': None,
                'active_physical_constraint': False,
            })
    if len({r['id'] for r in out_rows}) != 6:
        raise ValueError('duplicate source-object cells')
    return {
        'schema': 'conde.ssr-kepler-documentary-provenance/v1',
        'id': 'ABELHA-G34-SSR-PRINTED-UNITS',
        'ledger': LEDGER.relative_to(ROOT).as_posix(),
        'calculation_audit': AUDIT.relative_to(ROOT).as_posix(),
        'upstream_custody_bridge': LOCK.relative_to(ROOT).as_posix(),
        'source_family': 'SHARED_NASA_NORAD_COMPILED_NOT_SIX_SENSORS',
        'cells': out_rows,
        'publication_dates_are_sensor_epochs': False,
        'related_lean_contract': 'formal/Conde1963/SsrNovember.lean',
        'related_lean_theorem': 'printed_november_period_3c_gt_3a',
        'lean_claim_scope': 'related_printed_period_arithmetic_not_kepler_theorem',
        'lean_kepler_proof': None,
        'simulation_contract': 'research/constraints/C241-P10_three_object_relative_trajectories.json',
        'latent_requirements': [
            'instrumental_observation_epochs', 'reference_frame', 'period_convention',
            'independent_calibration_and_covariance', 'model_discrepancy',
            'aerodynamic_drag_and_atmosphere', 'source_specific_tracking_genealogy'
        ],
        'simulator_parameter_values': None,
        'active_physical_constraint': False,
        'physical_domain_effect': 'THETA_UNCHANGED',
        'status': 'CONNECTED_PENDING_CALIBRATION',
        'not_an_observation_of_528': True,
    }


def render() -> str:
    return json.dumps(build(json.loads(LEDGER.read_text()), json.loads(AUDIT.read_text()),
                            json.loads(LOCK.read_text())), ensure_ascii=False, indent=2) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-site', action='store_true')
    parser.add_argument('--check-site', action='store_true')
    args = parser.parse_args()
    payload = render()
    if args.write_site:
        OUT.write_text(payload, encoding='utf-8')
    if args.check_site and OUT.read_text(encoding='utf-8') != payload:
        raise SystemExit('SSR Kepler source bridge stale')
    print('Six source-locked NASA printed cells; no 528 sensor, Θ unchanged')


if __name__ == '__main__':
    main()
