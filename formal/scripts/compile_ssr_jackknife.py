#!/usr/bin/env python3
"""C241-P22: exact leave-one-publication-out sensitivity of SSR print-only model.

The nine editions are NASA compilations, NOT tracking epochs or independent
sensors. Radius E measures only residual of a deliberately restrictive
editorial nuisance model. Do not construe this as drag, error sigma or Theta.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from formal.scripts import compile_ssr_nine_editions as parent

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'research/constraints/C241-P22_ssr_jackknife.json'
LEAN = ROOT / 'formal/Conde1963/SsrJackknife.lean'
# Independent lower-bound witnesses via 527-minus-529, each difference in
# centiminutes. Exhaustiveness: every deletion leaves one of these pairs.
ANCHORS = {
    '1963-04-30': ('1963-06-30', '1963-12-31', 120),
    '1963-12-31': ('1963-04-30', '1963-12-15', 68),
}


def without_date(cells, day):
    return {key: val for key, val in cells.items() if key[1] != day}


def bound_from_contrast(cells, first, last):
    first_gap = cells[527, first] - cells[529, first]
    last_gap = cells[527, last] - cells[529, last]
    return (abs(first_gap - last_gap) + 3) // 4


def build(model=None, ledgers=None, decay=None):
    cells, sources = parent.source_rows(model, ledgers, decay)
    dates = [x['publication'] for x in sources]
    if len(dates) != 9 or len(cells) != 23:
        raise ValueError('unexpected source edition set')
    results = []
    for removed in dates:
        reduced = without_date(cells, removed)
        e, (bases, offsets, residuals) = parent.minimize(reduced)
        first, last, expected = ANCHORS.get(
            removed, ('1963-04-30', '1963-12-31', 128))
        assert first != removed and last != removed
        lower = bound_from_contrast(reduced, first, last)
        if e != lower or e != expected or len(reduced) not in (20, 21):
            raise ValueError('jackknife classification no longer source-locked')
        results.append({
            'removed_publication': removed,
            'retained_publications': [d for d in dates if d != removed],
            'retained_printed_cells': len(reduced),
            'minimum_residual_centiminute': e,
            'minimum_residual_seconds': f'{e * 3 / 5:.1f}',
            'lower_bound_contrast': {
                'objects': [527, 529], 'publications': [first, last],
                'gap_centiminute': [reduced[527, first] - reduced[529, first],
                                   reduced[527, last] - reduced[529, last]],
                'gap_change_centiminute': abs(
                    (reduced[527, first] - reduced[529, first]) -
                    (reduced[527, last] - reduced[529, last])),
                'necessary_inequality': '4*E >= absolute gap change',
                'integral_bound': lower,
            },
            'attaining_witness': {
                'object_baselines': {str(o): bases[o] for o in parent.OBJECTS},
                'publication_offsets': offsets,
                'max_abs_residual': max(map(abs, residuals.values())),
            },
        })
    return {
        'schema': 'conde.ssr-jackknife-print-model/v1', 'id': 'C241-P22',
        'parent_evidence': ['C241-L27', 'C241-P20', 'C241-P21'],
        'source_editions': sources, 'unit': 'centiminute (0.01 minute)',
        'model': 'printed(obj,publication) = baseline_obj + offset_publication + residual',
        'baseline_all_nine_centiminute': 128,
        'delete_one': results,
        'highest_leverage_deleted_publication': '1963-12-31',
        'highest_leverage_decrease_centiminute': 60,
        'interpretation': 'Dec31 omission reduces minimum E from 128 to 68 centimin; Apr30 omission only to 120; every other single omission leaves 128. This prioritizes auditing the Dec31 facsimile, NOT labeling it an erratum or inferring physics.',
        'source_family': 'NASA_GODDARD_NORAD_SAO_COMPILED_SAME_UPSTREAM',
        'publication_is_instrument_epoch': False,
        'instrument_error_sigma': None,
        'new_independent_instrument_observations': 0,
        'physical_domain': 'THETA_UNCHANGED',
    }


def render_lean(result):
    dates = [d['publication'] for d in result['source_editions']]
    objnames = ['b527', 'b528', 'b529']
    hnames = {date: 'h' + date[5:].replace('-', '') for date in dates}
    lines = [
        'import Lean', '', 'namespace Conde1963.SsrJackknife', '',
        '/-! C241-P22. Source-locked publication leave-one-out editorial',
        'model; not instrument errors, not tracking epochs, Theta unchanged.',
        'The independently established 527/529 contrast supplies each lower',
        'bound; an explicit witness attains it for every retained printed cell. -/', '',
        'def within (value baseline offset radius : Int) : Prop :=',
        '  -radius ≤ value - baseline - offset ∧',
        '  value - baseline - offset ≤ radius', '',
    ]
    for row in result['delete_one']:
        removed = row['removed_publication']
        key = removed[5:].replace('-', '')
        r = row['minimum_residual_centiminute']
        f, l = row['lower_bound_contrast']['publications']
        cells, _ = parent.source_rows()
        valaf, valal = cells[527, f], cells[527, l]
        valcf, valcl = cells[529, f], cells[529, l]
        lines.extend([
            f'/-- Deleting {removed} still forces E >= {r} centiminutes. -/',
            f'theorem without_{key}_lower_bound',
            '    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)',
            f'    (aFirst : {valaf} = b527 + hFirst + eaFirst)',
            f'    (aLast : {valal} = b527 + hLast + eaLast)',
            f'    (cFirst : {valcf} = b529 + hFirst + ecFirst)',
            f'    (cLast : {valcl} = b529 + hLast + ecLast)',
            '    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)',
            '    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)',
            '    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)',
            '    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :',
            f'    {r} ≤ E := by',
            '  omega', '',
        ])
        w = row['attaining_witness']
        vars_ = objnames + [hnames[d] for d in row['retained_publications']]
        vals = [w['object_baselines'][str(o)] for o in parent.OBJECTS]
        vals += [w['publication_offsets'][d] for d in row['retained_publications']]
        expressions = [
            f'within {value} b{obj} {hnames[day]} {r}'
            for (obj, day), value in sorted(without_date(cells, removed).items())
        ]
        lines.extend([
            f'/-- Exact attaining witness for all {len(expressions)} retained cells. -/',
            f'theorem without_{key}_witness :',
            f"    ∃ ({' '.join(vars_)} : Int),",
            '      ' + ' ∧\n      '.join(expressions) + ' := by',
            '  refine ⟨' + ', '.join(map(str, vals)) + ', ?_⟩',
            '  simp only [within]',
            '  omega', '',
        ])
    lines.extend(['end Conde1963.SsrJackknife', ''])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = build()
    body = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    lean = render_lean(report)
    if args.check:
        if not REPORT.is_file() or REPORT.read_text() != body:
            raise SystemExit('C241-P22 report mismatch')
        if not LEAN.is_file() or LEAN.read_text() != lean:
            raise SystemExit('C241-P22 Lean mismatch')
    else:
        REPORT.write_text(body)
        LEAN.write_text(lean)
    print('C241-P22: 9 deletions certified; Dec31 128->68, Apr30 128->120; Theta unchanged')


if __name__ == '__main__':
    main()
