#!/usr/bin/env python3
"""C241-P23: source-locked UN January cutoff vs nine NASA SSR print tables.

This is an explicitly CROSS-AGENCY common-offset nuisance hypothesis,
not a historical orbit, independent tracking source or error calibration.
UN A/AC.105/INF.30 was issued in March with a Jan 31 administrative cutoff.
"""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from formal.scripts import compile_ssr_nine_editions as nasa

ROOT = Path(__file__).resolve().parents[2]
UN = ROOT / 'research/tle_custody/un_1963_registration_C241-L33.json'
REPORT = ROOT / 'research/constraints/C241-P23_un_ssr_cross_compilation.json'
LEAN = ROOT / 'formal/Conde1963/UnSsrCrossCompilation.lean'
CUTOFF_KEY = '1963-01-31_UN_ASOF_NOT_PUBLICATION'
UN_LOCK = {
    'number': '30',
    'url': 'https://www.unoosa.org/documents/pdf/inf030E.pdf',
    'sha256': 'fbee0e928a2d81e62c97c102eef70d4f4931dd500372a4bf735bd8891c6188b8',
    'document_day': '1963-03-13',
    'letter_day': '1963-03-12',
    'report_cutoff_printed': '2400Z 31 JANUARY 1963',
}
# Literal printed values, kept separately from the archival ledger to catch
# coordinated corruption of crosswalk or decimal data.
UN_PERIOD_LOCK = ((527, '1963-3-A', '94.7'),
                  (528, '1963-3-B', '94.5'),
                  (529, '1963-3-C', '94.7'))


def source_rows(un=None, nasa_model=None, nasa_ledgers=None, nasa_decay=None):
    cells, nasa_sources = nasa.source_rows(nasa_model, nasa_ledgers, nasa_decay)
    if un is None:
        un = json.loads(UN.read_text(encoding='utf-8'))
    if (un.get('schema') != 'conde.c241-l33-un-1963-registration/v1'
            or un.get('id') != 'C241-L33'
            or un.get('source_role') !=
            'ORIGINAL_US_GOVERNMENT_REGISTRATION_TO_UN_NOT_INDEPENDENT_SENSOR'
            or len(un.get('docs', [])) != 4):
        raise ValueError('UN source schema, identity or independence changed')
    doc = un['docs'][0]
    if any(doc.get(k) != v for k, v in UN_LOCK.items()):
        raise ValueError('UN pdf, custodial hash, issue date or cutoff changed')
    if (doc.get('kind') != 'JAN31_FULL_NEW_REGISTRATION'
            or doc.get('relevant_pdf_page_index') != 1
            or doc.get('visual_check') != 'MANUAL_IMAGE_INSPECTION_2026-11-13'):
        raise ValueError('UN page/custody metadata changed')
    rows = doc.get('printed_rows', [])
    if len(rows) != 3:
        raise ValueError('expected exactly three UN designators')
    for row, (obj, designator, period) in zip(rows, UN_PERIOD_LOCK):
        if (row.get('norad_from_nasa_1977'), row.get('printed_designator'),
                row.get('nodal_period_min_printed')) != (obj, designator, period):
            raise ValueError('UN identity/period transcription mismatch')
        if (row.get('launch_day') != '1963-01-16'
                or row.get('category') not in ('A', 'D')):
            raise ValueError('UN object launch provenance changed')
        cells[obj, CUTOFF_KEY] = int(Decimal(period) * 100)
    interpretation = un.get('interpretation', {})
    if (interpretation.get('crosswalk_kind') !=
            'NASA_INSTITUTIONAL_RETROSPECTIVE_1977_NOT_PRINTED_NORAD_IN_1963_UN_DOC'
            or interpretation.get('un_cutoff_is_sensor_epoch') is not False
            or interpretation.get('conditional_physical_interval_activated') is not False
            or interpretation.get('physical_constraints_activated') != 0
            or interpretation.get('independent_sensor_observations_added') != 0):
        raise ValueError('UN administrative cutoff converted into physical observation')
    if len(cells) != 26 or len(nasa_sources) != 9:
        raise ValueError('unexpected combined cell set')
    return cells, nasa_sources


def build(un=None, nasa_model=None, nasa_ledgers=None, nasa_decay=None):
    cells, nasa_sources = source_rows(un, nasa_model, nasa_ledgers, nasa_decay)
    radius, (bases, offsets, residuals) = nasa.minimize(cells)
    first, last = CUTOFF_KEY, '1963-12-31'
    gap_first = cells[527, first] - cells[529, first]
    gap_last = cells[527, last] - cells[529, last]
    if (gap_first, gap_last, radius) != (0, 540, 135):
        raise ValueError('cross-document gap and sharp optimum changed')
    if max(abs(r) for r in residuals.values()) != radius:
        raise ValueError('attaining witness did not attain exact minimax')
    return {
        'schema': 'conde.un-ssr-cross-compilation-print-model/v1',
        'id': 'C241-P23',
        'parents': ['C241-L33', 'C241-L27', 'C241-P20', 'C241-P22'],
        'un_source': {**UN_LOCK, 'cutoff_key_NOT_publication': CUTOFF_KEY,
                      'source_ledger': str(UN.relative_to(ROOT)),
                      'pdf_page_index': 1},
        'nasa_sources': nasa_sources,
        'unit': 'centiminute (0.01 minute)',
        'cross_agency_model_ASSUMED':
            'P(object,document) = common_object_baseline + per_document_offset + residual; assumes a shared convention across US→UN and NASA/NORAD compilations',
        'printed_period_cells': [
            {'object': o, 'document_or_cutoff': d, 'period_centiminute': val,
             'residual_centiminute': residuals[o, d]}
            for (o, d), val in sorted(cells.items())],
        'minimum_uniform_residual_centiminute': radius,
        'minimum_uniform_residual_seconds': '81.0',
        'prior_nasa_only_minimum_centiminute': 128,
        'added_threshold_centiminute': 7,
        'contrasting_cells': {
            'objects': [527, 529],
            'keys': [first, last],
            'gaps_centiminute': [gap_first, gap_last],
            'inequality': '4*E >= 540; E >= 135'},
        'attaining_witness': {
            'baselines': {str(o): bases[o] for o in nasa.OBJECTS},
            'document_offsets': offsets,
            'max_abs_residual': radius},
        'print_half_step_ASSUMED_not_instrument_sigma': 5,
        'un_cutoff_is_publication': False,
        'un_cutoff_is_tracking_epoch': False,
        'cross_agency_printing_convention_validated': False,
        'source_families_are_independent_sensors': False,
        'instrument_epochs': None,
        'instrument_covariances': None,
        'new_instrument_observations': 0,
        'physical_domain': 'THETA_UNCHANGED',
        'interpretation': 'A stricter conditional test of an over-simple common document-offset model across two linked US reporting chains, NOT new calibrated orbital evidence. The March UN document has a January administrative cutoff, not a January publication or instrument epoch.'
    }


def render_lean(r):
    rows = r['printed_period_cells']
    offsets = r['attaining_witness']['document_offsets']
    baselines = r['attaining_witness']['baselines']
    days = sorted(offsets)
    offset_names = {d: 'hUn' if d == CUTOFF_KEY
                    else 'h' + d[5:].replace('-', '') for d in days}
    terms = [f'within {c["period_centiminute"]} b{c["object"]} '
             f'{offset_names[c["document_or_cutoff"]]} 135'
             for c in rows]
    variables = ' '.join(['b527', 'b528', 'b529', *[offset_names[d] for d in days]])
    witness = ', '.join(map(str, [*[baselines[str(o)] for o in nasa.OBJECTS],
                                 *[offsets[d] for d in days]]))
    return f'''import Lean

namespace Conde1963.UnSsrCrossCompilation

/-! C241-P23: conditional, CROSS-AGENCY documentary test (26 printed cells).
UN A/AC.105/INF.30 was issued March 13, with administrative cutoff Jan 31.
The nine NASA SSR dates are publication/report dates, not sensor epochs.
Assuming a shared additive document convention across these chains is an
untested hypothesis. No covariance, sensor independence or Theta reduction. -/

def within (p base offset E : Int) : Prop :=
  -E ≤ p - base - offset ∧ p - base - offset ≤ E

/-- UN Jan31-cutoff printed 527/529 gap is 0; NASA Dec31 is 540.
A common baseline and one offset per document require 4E >= 540. -/
theorem cross_agency_lower_bound
    (b527 b529 hUn hDec eaUn eaDec ecUn ecDec E : Int)
    (aUn : 9470 = b527 + hUn + eaUn)
    (aDec : 9460 = b527 + hDec + eaDec)
    (cUn : 9470 = b529 + hUn + ecUn)
    (cDec : 8920 = b529 + hDec + ecDec)
    (eaUnLo : -E ≤ eaUn) (eaUnHi : eaUn ≤ E)
    (eaDecLo : -E ≤ eaDec) (eaDecHi : eaDec ≤ E)
    (ecUnLo : -E ≤ ecUn) (ecUnHi : ecUn ≤ E)
    (ecDecLo : -E ≤ ecDec) (ecDecHi : ecDec ≤ E) :
    135 ≤ E := by
  omega

/-- Attaining witness covers all 26 printed periods simultaneously,
including every printed 528 cell and the full NASA-only control panel. -/
theorem cross_agency_attaining_witness :
    ∃ ({variables} : Int),
      {' ∧'.join(chr(10) + '      ' + t for t in terms)[2:]} := by
  refine ⟨{witness}, ?_⟩
  simp only [within]
  omega

end Conde1963.UnSsrCrossCompilation
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    r = build()
    report = json.dumps(r, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    lean = render_lean(r)
    if args.check:
        if not REPORT.exists() or REPORT.read_text() != report:
            raise SystemExit('C241-P23 report no longer source-locked')
        if not LEAN.exists() or LEAN.read_text() != lean:
            raise SystemExit('C241-P23 Lean no longer source-locked')
    else:
        REPORT.write_text(report)
        LEAN.write_text(lean)
    print('C241-P23: 26 cells, E=135 centimin=81 s; Theta unchanged')

if __name__ == '__main__':
    main()
