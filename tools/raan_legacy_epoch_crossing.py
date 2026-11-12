#!/usr/bin/env python3
"""C241-P5: test epoch-confusion hypothesis for legacy 284.1520 deg.

A crossing in a secondary catalogue is a conditional interpolation, never
proof of the epoch or source of a constructed legacy TLE, nor a physical limit.
"""
from __future__ import annotations

import argparse
from datetime import timedelta
import json
import math
from pathlib import Path

from cross_object_epoch_support import (FIELDS, EXPECTED_CSV_SHA256,
                                        SOURCE_SHA256, SOURCE_URL,
                                        normalize, read_pinned_csv)
from tle_cross_catalog_legacy_audit import LEGACY, LEGACY_LINE1, LEGACY_LINE2
from tle_literal_layout import audit_pair, audit_literal_file

IDS = (527, 528, 529)
TARGET = float(LEGACY['raan'])
EXPECTED = {527: 20, 528: 45, 529: 54}
FRACTION_MARGIN = 1e-12


def arc(a: float, b: float) -> float:
    if not all(math.isfinite(x) and 0 <= x < 360 for x in (a, b)):
        raise ValueError('nonfinite or out-of-circle angle')
    delta = (b - a + 180) % 360 - 180
    if abs(delta) == 180:
        raise ValueError('ambiguous half-circle arc')
    return delta


def pair_crossing(one: dict, two: dict, target: float = TARGET) -> dict | None:
    left = float(one['state'][FIELDS.index('raan')]); right = float(two['state'][FIELDS.index('raan')])
    if not one['epoch'] < two['epoch']:
        raise ValueError('non-increasing UTC epochs')
    delta = arc(left, right)
    if not delta:
        return None
    fraction = arc(left, target) / delta
    if not -FRACTION_MARGIN <= fraction <= 1 + FRACTION_MARGIN:
        return None
    fraction = max(0., min(1., fraction))
    gap = (two['epoch']-one['epoch']).total_seconds()
    estimated = one['epoch'] + timedelta(seconds=gap*fraction)
    return {'start_epoch_utc': one['epoch'].isoformat().replace('+00:00','Z'),
            'end_epoch_utc': two['epoch'].isoformat().replace('+00:00','Z'),
            'start_source_rows': one['source_rows'], 'end_source_rows': two['source_rows'],
            'start_raan_deg': left, 'end_raan_deg': right,
            'signed_delta_deg': delta, 'gap_days': gap/86400,
            'secant_deg_per_day': delta/(gap/86400),
            'fraction': fraction,
            'crossing_utc_IF_LINEAR_WITHIN_BRACKET': estimated.isoformat(timespec='microseconds').replace('+00:00','Z')}


def validate_groups(groups: dict, counts: dict) -> None:
    if counts != {527:21, 528:45, 529:57} or {k:len(v) for k,v in groups.items()} != EXPECTED:
        raise ValueError('pinned source inventory mismatch')
    for sid, rows in groups.items():
        if not all(rows[i]['epoch'] < rows[i+1]['epoch'] for i in range(len(rows)-1)):
            raise ValueError(f'non-increasing epochs {sid}')


def secondary_interpolation_control(rows: list[dict], max_span_days: float = 30.) -> dict:
    """Leave-one-epoch-out catalogue interpolation against nearest-epoch persistence.

    This is intentionally two-sided, not time-forward validation or sigma.
    """
    errs, baseline = [], []
    for left, mid, right in zip(rows, rows[1:], rows[2:]):
        dt = (right['epoch'] - left['epoch']).total_seconds()
        if not (0 < dt <= 86400*max_span_days):
            continue
        fraction = (mid['epoch']-left['epoch']).total_seconds()/dt
        if not 0 < fraction < 1:
            raise ValueError('invalid held-out mid epoch')
        ra = [float(r['state'][FIELDS.index('raan')]) for r in (left, mid, right)]
        estimate = (ra[0] + fraction*arc(ra[0], ra[2])) % 360
        closest = ra[0] if fraction <= 0.5 else ra[2]
        errs.append(abs(arc(estimate,ra[1])))
        baseline.append(abs(arc(closest,ra[1])))
    return {'n':len(errs),'max_bracket_gap_days':max_span_days,
            'method':'TWO_SIDED_CATALOG_INTERPOLATION_NOT_FORWARD_HOLDOUT',
            'interpolation_mae_deg':math.fsum(errs)/len(errs) if errs else 'NOT_EVALUABLE',
            'nearest_catalogue_mae_deg':math.fsum(baseline)/len(baseline) if baseline else 'NOT_EVALUABLE'}


def audit(groups: dict, *, expected: bool = True) -> dict:
    if expected and {k:len(v) for k,v in groups.items()} != EXPECTED:
        raise ValueError('incorrect unique epoch inventory')
    legacy = audit_pair(LEGACY_LINE1, LEGACY_LINE2)
    literal = audit_literal_file(Path(__file__).resolve().parents[1] / 'research/tle_custody/mirror_528_1963-10-27.tle')
    legacy_epoch = legacy['epoch_utc']; literal_epoch = literal['epoch_utc']
    delta = arc(float(literal['values']['raan']['decimal']), TARGET)
    result = {
        'schema':'conde.legacy-raan-epoch-forensics/v1',
        'question':'Can a change of catalogue epoch alone reconcile legacy 284.1520 with secondary 528 198.5261?',
        'provenance':{'derived_csv_sha256':EXPECTED_CSV_SHA256,'parquet_sha256':SOURCE_SHA256,
                      'parquet_url':SOURCE_URL,'source_family':'ONE_SECONDARY_MIRROR',
                      'legacy_origin':'site src/lib/constants.ts git blob 0284f1217557b0ea891b5e51b6ac56bd13529d3f',
                      'original_tle_pair_and_frame':'NOT_RECOVERED'},
        'constructed_legacy':{'raan_deg':TARGET,'printed_epoch_utc':legacy_epoch,
                              'source_type':'UNVERIFIED_CONSTRUCTED_TLE'},
        'secondary_literal_528':{'raan_deg':float(literal['values']['raan']['decimal']),
                                 'epoch_utc':literal_epoch},
        'signed_legacy_minus_secondary_RAAN_deg':delta,
        'matched_epoch_hypothesis':'REJECTED_WITHIN_PINNED_SECONDARY_CATALOGUE',
        'objects':{},'physical_feasible_domain_reduction':'NONE_NO_SENSOR_FRAME_COVARIANCE',
        'lean_physics_predicate':'NOT_PROMOTED', 'place_of_reentry':'INDETERMINATE'
    }
    for sid in IDS:
        rows=groups[sid]
        candidates=[x for a,b in zip(rows,rows[1:]) if (x:=pair_crossing(a,b)) is not None]
        result['objects'][str(sid)]={'catalogue_epochs':len(rows),
                                     'catalogue_bracket_count':len(candidates),
                                     'crossings':candidates,
                                     'interpolation_control': secondary_interpolation_control(rows)}
        if sid == 528 and candidates:
            t = candidates[0]['crossing_utc_IF_LINEAR_WITHIN_BRACKET']
            from datetime import datetime
            crossed=datetime.fromisoformat(t.replace('Z','+00:00'))
            claimed=datetime.fromisoformat(legacy_epoch.replace('Z','+00:00'))
            result['objects'][str(sid)]['days_between_legacy_printed_epoch_and_catalog_crossing'] = (claimed-crossed).total_seconds()/86400
    # A secondary crossing exists at a different epoch, not at the printed epoch.
    if expected and any(result['objects'][str(x)]['catalogue_bracket_count'] != 1 for x in IDS):
        raise ValueError('unexpected crossing count for pinned mirror')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    groups,counts=normalize(read_pinned_csv(args.csv))
    validate_groups(groups,counts)
    result=audit(groups)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    for sid in IDS:
        row=result['objects'][str(sid)]['crossings'][0]
        print(sid,row['crossing_utc_IF_LINEAR_WITHIN_BRACKET'],row['gap_days'],row['secant_deg_per_day'])

if __name__=='__main__':main()
