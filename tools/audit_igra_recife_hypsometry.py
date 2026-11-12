#!/usr/bin/env python3
"""Audited conditional hypsometric thickness check for NOAA/IGRA Recife levels."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from audit_igra_recife_dry_density import DRY_R, extract
from audit_igra_recife_window import DAYS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / 'meteorology'
G0 = 9.80665  # m/s², standard gravity consistent with geopotential meters


def pair(lower: dict, upper: dict) -> dict:
    p1, p2 = lower['pressure_hpa'], upper['pressure_hpa']
    z1, z2 = lower['geopotential_height_m_asl'], upper['geopotential_height_m_asl']
    t1, t2 = lower['temperature_deg_c'] + 273.15, upper['temperature_deg_c'] + 273.15
    values = (p1,p2,z1,z2,t1,t2)
    if not all(math.isfinite(v) for v in values) or p1 <= p2 or p2 <= 0 or z2 <= z1 or min(t1,t2) <= 0:
        raise ValueError('invalid observed pressure, geopotential height or absolute temperature')
    log_ratio = math.log(p1/p2)
    actual = z2-z1
    mean_endpoint_temp = (t1+t2)/2
    predicted = (DRY_R/G0)*mean_endpoint_temp*log_ratio
    implied = G0*actual/(DRY_R*log_ratio)
    return {
        'lower_level_index':lower['source_level_index'],
        'upper_level_index':upper['source_level_index'],
        'lower_pressure_hpa':p1, 'upper_pressure_hpa':p2,
        'lower_geopotential_m':z1, 'upper_geopotential_m':z2,
        'lower_temperature_c':lower['temperature_deg_c'],
        'upper_temperature_c':upper['temperature_deg_c'],
        'observed_geopotential_thickness_m':actual,
        'conditional_dry_endpoint_mean_k':round(mean_endpoint_temp,5),
        'conditional_dry_thickness_m':round(predicted,6),
        'conditional_residual_observed_minus_dry_m':round(actual-predicted,6),
        'hypsometric_implied_layer_mean_virtual_k':round(implied,6),
        'rh_available_both_endpoints':all(x['reported_rh_percent'] is not None for x in (lower,upper))
    }


def build(day: str) -> dict:
    if day not in DAYS:raise ValueError('unsupported IGRA nominal date')
    origin=extract(day)  # loads original excerpt and verifies SHA-256, station and date
    rows=origin['levels']
    layers=[pair(a,b) for a,b in zip(rows,rows[1:])]
    errors=[abs(a['conditional_residual_observed_minus_dry_m']) for a in layers]
    return {
        'schema':'conde.igra-recife-hypsometric-consistency/v1',
        'source':origin['source'],
        'epoch':origin['epoch'],
        'interpretation':{
            'observed':'p, T, GPH and flags from same NOAA/IGRA sounding',
            'model':'dry-endpoint-mean hypsometric thickness assumes hydrostatic balance, dry air and endpoint averaging',
            'equation':'delta_H_dry = (R_d/g0) * (T1_K+T2_K)/2 * ln(p1/p2)',
            'implied_layer_mean_virtual_T':'g0 * delta_H_observed / (R_d * ln(p1/p2)); derived from same p/H, NOT measured independent temperature',
            'gravity_m_s2':G0, 'gas_constant_dry_J_kgK':DRY_R,
            'reported_height_type':'geopotential meters ASL, not geometric height',
            'independent_instrumental_sources':1,
            'physical_link':'C149-C151 -> pressure/temperature/geopotential layer consistency -> local conditional density check; C17-C23/C144-C146/C193 context only',
            'unknown_instrumental_uncertainty_m':None,
            'unknown_virtual_temperature_correction_k':None,
            'unknown_recife_conde_transfer_error_m':None,
            'unknown_time_transfer_error_m':None,
            'active_theta_constraint':False,
            'inference_of_conde':False,
            'inference_of_norad528_thermosphere':False,
            'residual_is_measurement_error':False,
            'status':'RECIFE_HYPSOMETRIC_CONDITIONAL_CHECK_NO_TRANSFER'
        },
        'source_levels':len(rows),'adjacent_layers':len(layers),
        'mean_abs_model_residual_m':round(sum(errors)/len(errors),6),
        'max_abs_model_residual_m':round(max(errors),6),
        'layers':layers
    }


def target(day: str) -> Path:
    return OUT/f'igra_recife_196311{day}_hypsometric_consistency.json'


def check() -> None:
    for day in DAYS:
        expected=build(day)
        if json.loads(target(day).read_text(encoding='utf-8'))!=expected:
            raise ValueError('source-derived hypsometry mismatch on 1963-11-'+day)
    print('PASS 78 adjacent source-pinned pressure-height layers; 1 NOAA family, no Conde transfer')


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--check',action='store_true')
    ap.add_argument('--day',choices=DAYS)
    args=ap.parse_args()
    if args.check:check()
    elif args.day:print(json.dumps(build(args.day),indent=2,ensure_ascii=False)+'\n')
    else:ap.error('--check or --day')

if __name__=='__main__':main()
