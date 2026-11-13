#!/usr/bin/env python3
"""C241-P12: falsify one additive edition offset for 527/529 printed periods.

Quantifiers refer to nearest-0.1-minute *printing*, never instrument errors.
Bulletin dates are not observed epochs. Source audit must precede arithmetic.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from formal.scripts.compile_ssr_november import validate as validate_november  # noqa: E402
from tools.tle_nasa_ssr_dec15_audit import validate as validate_december  # noqa: E402
from tools.export_ssr_kepler_provenance import build as audit_g34  # noqa: E402

NOV = ROOT / 'research/tle_custody/nasa_ssr_nov15_1963_C241-L19.json'
OCT = ROOT / 'research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json'
SUR = ROOT / 'research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json'
DEC = ROOT / 'research/tle_custody/nasa_ssr_dec15_1963_C241-L21.json'
GRAPH = ROOT / 'research/constraints/ssr_dec15_1963_observables_C241-L21.json'
G34 = ROOT / 'public/data/conde-ssr-kepler-provenance.json'
G34LED = ROOT / 'research/constraints/C241-P11_november_historical_printings.json'
G34AUD = ROOT / 'research/constraints/C241-P11_kepler_unit_audit_g34.json'
G34LOCK = ROOT / 'public/data/conde-ssr-source-locked-links.json'
REPORT = ROOT / 'research/constraints/C241-P12_edition_offset.json'
LEAN = ROOT / 'formal/Conde1963/SsrEditionOffset.lean'
DATES = ('1963-11-15', '1963-11-30', '1963-12-15')
LABELS = ('nov15_to_nov30', 'nov30_to_dec15', 'nov15_to_dec15')


def centiminutes(value: object) -> int:
    d = Decimal(str(value)) * 100
    if not d.is_finite() or d != d.to_integral_value() or int(d) % 10:
        raise ValueError('period is not printed to one decimal minute')
    return int(d)


def contrast(a0: int, c0: int, a1: int, c1: int) -> dict:
    """Shared endpoints, four ±5-centiminute printing intervals."""
    change = (a1 - c1) - (a0 - c0)
    return {'center_centimin': change,
            'nearest_tenth_conditional_interval_centimin': [change - 20, change + 20],
            'common_additive_edition_offset_rejected': abs(change) > 20}


def bind_g34(bundle: dict, audited: dict, a: list[int], c: list[int],
             nov: dict, survivors: dict) -> dict:
    """Bind six *documentary* Kepler cells by all four identity keys.

    A residual from a 2-body diagnostic is not a sensor sigma; six cells come
    from three compiled editions, never six independent tracking stations.
    """
    if bundle != audited or bundle.get('active_physical_constraint') is not False:
        raise ValueError('G34 output differs from independently audited inputs')
    if (bundle.get('publication_dates_are_sensor_epochs') is not False
        or bundle.get('not_an_observation_of_528') is not True
        or bundle.get('source_family') !=
           'SHARED_NASA_NORAD_COMPILED_NOT_SIX_SENSORS'
        or bundle.get('physical_domain_effect') != 'THETA_UNCHANGED'
        or bundle.get('simulator_parameter_values') is not None):
        raise ValueError('G34 Kepler diagnostics promoted into observations')
    cells = bundle.get('cells', [])
    if len(cells) != 6:
        raise ValueError('G34 missing six cells')
    keys = []
    expected_by_date = {
        '1963-11-15': (nov['documents'][0]['sha256'],
                       'C241-L19#1', a[0], c[0]),
        '1963-11-30': (next(z['sha256'] for z in survivors['sources']
                            if z['published'] == '1963-11-30'),
                       'C241-L18:19640002493', a[1], c[1]),
    }
    for cell in cells:
        key = tuple(cell.get(k) for k in (
            'source_occurrence', 'report_publication_date_not_epoch',
            'source_pdf_sha256', 'object'))
        if not all(isinstance(x, str) and x for x in key):
            raise ValueError('incomplete four-key G34 identity')
        keys.append(key)
        if (cell.get('id') != f'{key[0]}:{key[3]}:period_apogee_perigee'
                or key[3] not in ('1963-003A', '1963-003C')
                or cell.get('instrument_epoch') is not None
                or cell.get('covariance') is not None
                or cell.get('active_physical_constraint') is not False):
            raise ValueError('Kepler diagnostic has incorrect identity/scope')
        if key[1] in expected_by_date:
            sha, occurrence, pa, pc = expected_by_date[key[1]]
            if key[0] != occurrence or key[2] != sha or (
                cell['period_centimin'] !=
                (pa if key[3] == '1963-003A' else pc)):
                raise ValueError('published cell and Polvo printed period disagree')
    if len(set(keys)) != 6 or len(set(x[2] for x in keys)) != 3:
        raise ValueError('G34 duplicate cells or false source independence')
    return {
        'source': 'public/data/conde-ssr-kepler-provenance.json',
        'id': bundle['id'], 'cell_keys': [list(k) for k in keys],
        'six_documentary_cells_three_compiled_editions': True,
        'independent_sensor_provenance_established': False,
        'residual_seconds_are_instrument_sigma': False,
        'not_a_528_measurement': True,
        'pending_calibration': bundle['latent_requirements'],
    }


def build(nov: dict, octo: dict, survivors: dict, dec: dict, graph: dict,
          g34_bundle: dict | None = None, g34_inputs: tuple | None = None) -> dict:
    nov_rows = validate_november(nov, octo, survivors)
    validate_december(dec, graph, nov, survivors)
    a = [nov_rows[k]['1963-003A']['period_min'] for k in DATES[:2]]
    c = [nov_rows[k]['1963-003C']['period_min'] for k in DATES[:2]]
    dec_rows = {row['designator']: row for row in dec['rows']}
    a.append(centiminutes(dec_rows['1963-003A']['period_min']))
    c.append(centiminutes(dec_rows['1963-003C']['period_min']))
    if a != [9460, 9460, 9460] or c != [9260, 9220, 9160]:
        raise ValueError('not verified NASA table cells 527/529')
    sources = [
        {'occurrence': 'C241-L19#1', 'ntrs': nov['documents'][0]['ntrs'],
         'sha256': nov['documents'][0]['sha256'], 'page_index': 6,
         'publication_date_not_epoch': DATES[0]},
        {'occurrence': 'C241-L18:19640002493',
         'ntrs': next(s['ntrs_id'] for s in survivors['sources']
                      if s['published'] == DATES[1]),
         'sha256': next(s['sha256'] for s in survivors['sources']
                        if s['published'] == DATES[1]),
         'page_index': 6, 'publication_date_not_epoch': DATES[1]},
        {'occurrence': 'C241-L21', 'ntrs': dec['source']['ntrs_id'],
         'sha256': dec['source']['sha256'], 'page_index': 6,
         'publication_date_not_epoch': DATES[2]},
    ]
    original_g34_inputs = tuple(json.loads(p.read_text())
                                for p in (G34LED, G34AUD, G34LOCK))
    audited_g34 = audit_g34(*(original_g34_inputs if g34_inputs is None
                              else g34_inputs))
    g34_link = bind_g34(json.loads(G34.read_text()) if g34_bundle is None
                        else g34_bundle, audited_g34, a, c, nov, survivors)
    changes = [contrast(a[i], c[i], a[j], c[j])
               for i, j in ((0, 1), (1, 2), (0, 2))]
    if not all(x['common_additive_edition_offset_rejected'] for x in changes):
        raise ValueError('cannot reject shared additive edition offset')
    return {
        'id': 'C241-P12', 'schema': 'conde.ssr-edition-offset-test/v1',
        'source_editions': sources, 'g34_documentary_diagnostics': g34_link,
        'dates_are_publication_not_tracking_epochs': True,
        'source_family': 'NASA_NORAD_SAO_COMPILED_NOT_INDEPENDENT_SENSORS',
        'object_ids': {'1963-003A': 527, '1963-003C': 529},
        'printed_period_centimin': {'527': a, '529': c},
        'printed_527_minus_529_centimin': [x-y for x, y in zip(a, c)],
        'contrast_labels': list(LABELS), 'printed_contrasts': changes,
        'intermediate_edition_cancels_in_endpoint_contrast': True,
        'model_tested': 'P_{object,edition}=base_object+offset_edition+rounding_error',
        'conditional_printing_error_centimin': [-5, 5],
        'result': 'REJECT_SHARED_ADDITIVE_EDITION_OFFSET_UNDER_PRINTING_ASSUMPTION',
        'not_tested': ['object_specific_edits', 'dynamical_forces',
                       'sensor_epochs', 'tracking_error', 'terminal_geography'],
        'provenance_dependency': 'C241-L20#1',
        'simulation_latent_variables': ['state_527(t)', 'state_529(t)',
            'sensor_epoch_per_row', 'report_latency_per_row',
            'force_model', 'ballistic_coefficients', 'sensor_covariance'],
        'observation_epoch_utc': None, 'instrument_covariance': None,
        'source_independence_verified': False,
        'physical_constraint_active': False, 'admissible_domain': 'THETA_UNCHANGED',
        'status': 'CONNECTED_PENDING_CALIBRATION',
        'lean_contract': 'formal/Conde1963/SsrEditionOffset.lean',
    }


def render_lean(report: dict) -> str:
    periods = report['printed_period_centimin']
    a, c = periods['527'], periods['529']
    names = ['a15', 'a30', 'aDec', 'c15', 'c30', 'cDec']
    centers = a + c
    lines = [
        'import Lean', '', 'namespace Conde1963.SsrEditionOffset', '',
        '/-! Generated from source-audited C241-L19, C241-L18 and C241-L21.',
        'All units: 0.01 minute. Rounding ±5 is a *conditional printing*',
        'hypothesis, not sensor covariance. Dates are publication dates;',
        'nothing below implies orbital drift, reentry time, or location. -/', '',
        '/-- Individual printed periods share an exact publication-edition index. -/',
        'theorem object_specific_printed_contrasts',
        '    (a15 a30 aDec c15 c30 cDec : Int)',
    ]
    for name, center in zip(names, centers):
        lines.append(f'    (h_{name} : {center-5} ≤ {name} ∧ {name} ≤ {center+5})')
    changes = report['printed_contrasts']
    comparisons = [
        '(a30 - c30) - (a15 - c15)',
        '(aDec - cDec) - (a30 - c30)',
        '(aDec - cDec) - (a15 - c15)',
    ]
    props = []
    for field, change in zip(comparisons, changes):
        lo, hi = change['nearest_tenth_conditional_interval_centimin']
        props.append(f'({lo} ≤ {field} ∧ {field} ≤ {hi})')
    lines.append('    : ' + ' ∧\n      '.join(props) + ' := by')
    for name in names:
        lines.append(f'  rcases h_{name} with ⟨h_{name}_lo, h_{name}_hi⟩')
    lines.extend(['  omega', '',
        '/-- A common additive edition offset would force identical printed',
        '    changes for both objects, contrary to the source-locked bounds. -/',
        'theorem no_shared_additive_edition_offset',
        '    (a15 aDec c15 cDec : Int)',
    ])
    for name, center in ((names[i], centers[i]) for i in (0, 2, 3, 5)):
        lines.append(f'    (h_{name} : {center-5} ≤ {name} ∧ {name} ≤ {center+5})')
    lines.extend([
        '    : ¬ ∃ (baseA baseC bias15 biasDec : Int),',
        '        a15 = baseA + bias15 ∧ c15 = baseC + bias15 ∧',
        '        aDec = baseA + biasDec ∧ cDec = baseC + biasDec := by',
        '  intro h',
        '  rcases h with ⟨baseA, baseC, bias15, biasDec, h1, h2, h3, h4⟩',
    ])
    for name in ('a15', 'aDec', 'c15', 'cDec'):
        lines.append(f'  rcases h_{name} with ⟨h_{name}_lo, h_{name}_hi⟩')
    lines.extend(['  omega', '', 'end Conde1963.SsrEditionOffset', ''])
    return '\n'.join(lines)


def run(check: bool) -> None:
    args = [json.loads(p.read_text()) for p in (NOV, OCT, SUR, DEC, GRAPH)]
    report = build(*args)
    blob = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + '\n'
    lean = render_lean(report)
    if check:
        if REPORT.read_text() != blob or LEAN.read_text() != lean:
            raise SystemExit('C241-P12 generated output drift; regenerate and review')
        print('C241-P12 PASS: 3 NASA editions; shared additive offset falsified conditionally')
    else:
        REPORT.write_text(blob)
        LEAN.write_text(lean)
        print('C241-P12 generated')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    run(p.parse_args().check)
