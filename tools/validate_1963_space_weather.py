#!/usr/bin/env python3
"""Offline verification of historical model drivers; no fabricated weather or trajectories.

Usage: python3 tools/validate_1963_space_weather.py research/meteorology/space_weather_msise_inputs_1963_11_07_09.json
"""
import datetime as dt
import json
import math
import sys
from pathlib import Path

def load_and_validate(path):
    doc=json.loads(Path(path).read_text(encoding='utf-8'))
    assert doc['schema']=='conde.1963-conditional-msise-drivers/v1'
    assert doc['physical_constraint_status']=='CONNECTED_PENDING_CALIBRATION'
    raw=doc['raw_series']
    sources=doc['source_documents']
    assert set(sources)=={'F107','Ap','ap','Kp'}
    assert len({sources[n]['sha256'] for n in sources})==4
    assert sources['F107']['url'].startswith('https://www.spaceweather.gc.ca/')
    assert all(sources[key]['url'].startswith('https://kp.gfz.de/app/json/') for key in ('Ap','ap','Kp'))
    assert len(doc['model_inputs'])==3
    assert len(raw['ap'])==56 and len(raw['Kp'])==56 and len(raw['Ap'])==7
    days=raw['F107_observed_daily']
    assert len(days)==85
    assert '1963-09-27' in days and '1963-12-20' in days
    for day,row in days.items():
        assert float(row['observed_sfu'])>0,day
        assert float(row['adjusted_sfu'])>0,day
        assert float(row['ursi_d_sfu'])>0,day
    assert set(raw['Kp'])==set(raw['ap'])
    for index in raw['ap']:
        assert int(raw['ap'][index])>=0
        assert 0<=float(raw['Kp'][index])<=9
        assert index.endswith(':00:00Z')
    for day,value in raw['Ap'].items():
        base=dt.datetime.fromisoformat(day.replace('Z','+00:00'))
        parts=[raw['ap'][(base+dt.timedelta(hours=3*i)).strftime('%Y-%m-%dT%H:%M:%SZ')] for i in range(8)]
        assert abs(float(value)-sum(parts)/8.0)<=0.5+1e-12,day
    for rec in doc['model_inputs']:
        t=dt.datetime.fromisoformat(rec['epoch_utc'].replace('Z','+00:00'))
        d=t.date()
        assert t.hour==12 and t.minute==0 and t.second==0
        assert d in (dt.date(1963,11,7),dt.date(1963,11,8),dt.date(1963,11,9))
        assert rec['location'] is None and rec['altitude_km'] is None
        assert rec['density_kg_m3'] is None and rec['density_uncertainty'] is None
        assert rec['input_uncertainty'] is None and rec['local_apparent_solar_time_hours'] is None
        assert 'NOT_REENTRY' in rec['epoch_role']
        expected_prev=days[str(d-dt.timedelta(days=1))]['observed_sfu']
        assert rec['F107_previous_day_observed_sfu']==expected_prev
        window=[days[str(d+dt.timedelta(days=i))]['observed_sfu'] for i in range(-40,41)]
        assert len(window)==81
        assert math.isclose(rec['F107A_81day_centered_observed_sfu'],sum(window)/81,rel_tol=0,abs_tol=0.00000051)
        label=lambda epoch:epoch.strftime('%Y-%m-%dT%H:%M:%SZ')
        ap_at=lambda lag:float(raw['ap'][label(t-dt.timedelta(hours=lag))])
        ap_day=float(raw['Ap'][label(t.replace(hour=0))])
        history=[ap_day,*[ap_at(i*3) for i in range(4)],
                 sum(ap_at(h) for h in range(12,34,3))/8,
                 sum(ap_at(h) for h in range(36,58,3))/8]
        assert len(history)==7
        for actual,expected in zip(rec['ap_history_planetary'],history):
            assert math.isclose(actual,expected,abs_tol=0.00000051,rel_tol=0)
        assert rec['Ap_daily_planetary']==ap_day
        assert rec['Kp_at_epoch']==raw['Kp'][rec['epoch_utc']]
        assert rec['status']=='DRIVERS_READY_POSITION_AND_MODEL_PARAMETERS_UNKNOWN_NO_DENSITY_INFERENCE'
    # Known direct 1963 record points are guardrails against a daylight/UTC or wrong-column shift.
    assert raw['F107_observed_daily']['1963-11-08']['observed_sfu']==75.4
    assert raw['Ap']['1963-11-08T00:00:00Z']==46
    assert raw['ap']['1963-11-08T06:00:00Z']==80
    assert raw['Kp']['1963-11-08T06:00:00Z']==6.0
    return doc
if __name__=='__main__':
    p=sys.argv[1] if len(sys.argv)>1 else 'research/meteorology/space_weather_msise_inputs_1963_11_07_09.json'
    doc=load_and_validate(p)
    print('OK: GFZ definitive 3h Kp/ap, daily Ap, Canada observed F10.7 + 81d centered; epochs=',','.join(x['epoch_utc'] for x in doc['model_inputs']))
    print('PHYSICAL CONSTRAINT: only CONNECTED_PENDING_CALIBRATION; no density or local Conde wind assigned.')
    # Keep the existing offline CI command as the sole gate for both products.
    from derive_1963_nov8_epoch_grid import validate_grid
    base = Path(__file__).resolve().parents[1] / 'research/meteorology'
    validate_grid(
        json.loads((base / 'space_weather_msise_inputs_1963_11_07_09.json').read_text()),
        json.loads((base / 'space_weather_nov08_3h_epoch_grid.json').read_text()),
    )
    print('PASS: eight 3h conditional index bins; no observed reentry')
