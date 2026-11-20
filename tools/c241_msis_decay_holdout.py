#!/usr/bin/env python3
"""C241: Exploratory NRLMSIS-2.1/NRLMSISE-00 orbital decay holdout & calibrators.
Retrospective analysis on SHA-pinned 1963 TLE Parquet + GFZ F10.7/ap; NOT a calibrated impact predictor.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
from statistics import median

PARQUET_SHA256 = 'c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09'
PARQUET_URL = (
    'https://huggingface.co/datasets/oxzoid/space-track-tle-history/'
    'blob/4b4fb3a/data/tle_1963.parquet'
)
GFZ_URL = 'https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt'

MU_KM3_S2 = 398600.4418
RE_KM = 6378.137
J2 = 0.00108262668
OMEGA_EARTH_RAD_S = 7.2921150e-5
SEC_PER_DAY = 86400.0

R68_CONTROLS = (
    (637, '1963-11-07', 'NASA_SSR_19631115',
     ('1963-10-18', '1963-10-23', '1963-10-27', '1963-10-30')),
    (292, '1963-11-26', 'SECONDARY_KEEPTRACK',
     ('1963-11-12', '1963-11-16', '1963-11-20', '1963-11-23')),
    (565, '1963-11-24', 'SECONDARY_KEEPTRACK',
     ('1963-11-10', '1963-11-14', '1963-11-18', '1963-11-21')),
    (308, '1963-10-30', 'SECONDARY_CONDITIONAL_OMEGA1',
     ('1963-10-16', '1963-10-20', '1963-10-24', '1963-10-27')),
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def mean_motion_to_a(n_rev_day: float) -> float:
    if not math.isfinite(n_rev_day) or n_rev_day <= 0:
        raise ValueError('mean_motion must be finite and positive')
    n_rad_s = math.tau * n_rev_day / SEC_PER_DAY
    return (MU_KM3_S2 / (n_rad_s * n_rad_s)) ** (1.0 / 3.0)


def gmst_rad(dt: datetime) -> float:
    if dt.utcoffset() != timedelta(0):
        raise ValueError('dt must be UTC')
    j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    days = (dt - j2000).total_seconds() / SEC_PER_DAY
    return math.radians((280.46061837 + 360.98564736629 * days) % 360.0)


def j2_rates_deg_day(a_km: float, e: float, inc_deg: float) -> tuple[float, float]:
    if a_km <= RE_KM or not (0.0 <= e < 1.0):
        raise ValueError('invalid orbital elements for J2 rates')
    inc = math.radians(inc_deg)
    n_rad_s = math.sqrt(MU_KM3_S2 / (a_km ** 3))
    p = a_km * (1.0 - e * e)
    fac = 1.5 * J2 * n_rad_s * ((RE_KM / p) ** 2)
    draan = -fac * math.cos(inc)
    dargp = fac * (2.0 - 2.5 * (math.sin(inc) ** 2))
    return math.degrees(draan) * SEC_PER_DAY, math.degrees(dargp) * SEC_PER_DAY


def strict_training_cutoff(records: list[dict], cutoff_utc: datetime) -> list[dict]:
    if cutoff_utc.utcoffset() != timedelta(0):
        raise ValueError('cutoff must be UTC')
    for a, b in zip(records, records[1:]):
        if a['epoch'] >= b['epoch']:
            raise ValueError('epochs must be strictly increasing')
    for r in records:
        if r['epoch'].utcoffset() != timedelta(0):
            raise ValueError('record epoch must be UTC')
    return [r for r in records if r['epoch'] < cutoff_utc]


def assumed_utc_day_error(pred_utc: datetime, label_yyyy_mm_dd: str) -> list[float]:
    if pred_utc.utcoffset() != timedelta(0):
        raise ValueError('prediction must be UTC')
    if len(label_yyyy_mm_dd) != 10 or label_yyyy_mm_dd[4] != '-' or label_yyyy_mm_dd[7] != '-':
        raise ValueError('label must be YYYY-MM-DD civil date')
    start = datetime.fromisoformat(label_yyyy_mm_dd).replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return [
        round((pred_utc - end).total_seconds() / SEC_PER_DAY, 4),
        round((pred_utc - start).total_seconds() / SEC_PER_DAY, 4),
    ]


class SpaceWeather1963:
    """GFZ Potsdam definitive daily Ap, 3-hour ap, and observed F10.7 (1962-1964)."""

    def __init__(self, path: Path):
        self.sha256 = sha256_file(path)
        self.daily: dict[datetime, tuple[float, list[float], float]] = {}
        self.ap_3h: dict[datetime, float] = {}
        with path.open() as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                p = line.split()
                y, m, d = int(p[0]), int(p[1]), int(p[2])
                if y < 1962 or y > 1964:
                    continue
                dt_day = datetime(y, m, d, tzinfo=timezone.utc)
                aps = [float(x) for x in p[15:23]]
                ap_day = float(p[23])
                f107 = float(p[25])
                self.daily[dt_day] = (ap_day, aps, f107)
                for k, ap_val in enumerate(aps):
                    self.ap_3h[dt_day + timedelta(hours=3 * k)] = ap_val

        self.f107a: dict[datetime, float] = {}
        for dt_day in sorted(self.daily):
            vals = [
                self.daily[dt_day + timedelta(days=delta)][2]
                for delta in range(-40, 41)
                if (dt_day + timedelta(days=delta)) in self.daily
                and self.daily[dt_day + timedelta(days=delta)][2] > 0
            ]
            self.f107a[dt_day] = sum(vals) / len(vals)

    def msis_inputs(self, dt: datetime) -> tuple[float, float, list[float]]:
        day = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
        f107, f107a = self.daily[day - timedelta(days=1)][2], self.f107a[day]
        ap_day = self.daily[day][0]
        bt = day + timedelta(hours=(dt.hour // 3) * 3)
        a = self.ap_3h
        m1 = sum(a[bt - timedelta(hours=h)] for h in range(12, 36, 3)) / 8.0
        m2 = sum(a[bt - timedelta(hours=h)] for h in range(36, 60, 3)) / 8.0
        return f107, f107a, [ap_day, a[bt], a[bt - timedelta(hours=3)],
                             a[bt - timedelta(hours=6)], a[bt - timedelta(hours=9)], m1, m2]

    def storm_summary(self, start_str: str, end_str: str) -> list[dict]:
        t = datetime.fromisoformat(start_str).replace(tzinfo=timezone.utc)
        t1 = datetime.fromisoformat(end_str).replace(tzinfo=timezone.utc)
        rows = []
        anchors = (datetime(1963, 10, 27, tzinfo=timezone.utc), datetime(1963, 11, 8, tzinfo=timezone.utc))
        while t <= t1:
            ap_day, aps, f107 = self.daily[t]
            if ap_day >= 30 or t in anchors:
                rows.append({'date_utc': t.strftime('%Y-%m-%d'), 'Ap_daily': int(ap_day),
                             'max_3h_ap': int(max(aps)), 'f107_obs': round(f107, 1)})
            t += timedelta(days=1)
        return rows


def orbit_averaged_drag_rates(
    dt: datetime, a_km: float, e: float, inc_deg: float, raan_deg: float,
    argp_deg: float, sw: SpaceWeather1963, version: float = 2.1, n_pts: int = 24,
) -> tuple[float, float]:
    """Return orbit-averaged (da/dt, de/dt) per unit B=Cd*A/m (m^2/kg) in (km/d, 1/d)."""
    import numpy as np
    import pymsis

    inc = math.radians(inc_deg)
    raan = math.radians(raan_deg)
    argp = math.radians(argp_deg)
    gmst = gmst_rad(dt)

    E = np.linspace(0.0, math.tau, n_pts, endpoint=False)
    cosE, sinE = np.cos(E), np.sin(E)
    one_minus_ecosE = 1.0 - e * cosE
    r_km = a_km * one_minus_ecosE
    sqrt_1me2 = math.sqrt(max(1e-12, 1.0 - e * e))
    cos_nu = (cosE - e) / one_minus_ecosE
    sin_nu = (sqrt_1me2 * sinE) / one_minus_ecosE
    u = argp + np.arctan2(sin_nu, cos_nu)

    sin_lat = math.sin(inc) * np.sin(u)
    lat_deg = np.degrees(np.arcsin(np.clip(sin_lat, -1.0, 1.0)))
    x_eci = np.cos(raan) * np.cos(u) - np.sin(raan) * np.sin(u) * math.cos(inc)
    y_eci = np.sin(raan) * np.cos(u) + np.cos(raan) * np.sin(u) * math.cos(inc)
    lon_deg = (np.degrees(np.arctan2(y_eci, x_eci) - gmst) + 180.0) % 360.0 - 180.0
    alt_km = np.maximum(80.0, r_km - RE_KM * (1.0 - 0.00335281 * (sin_lat ** 2)))

    f107, f107a, ap_vec = sw.msis_inputs(dt)
    dates = np.array([np.datetime64(dt.replace(tzinfo=None))] * n_pts)
    rho = pymsis.calculate(
        dates, lon_deg, lat_deg, alt_km,
        np.full(n_pts, f107), np.full(n_pts, f107a),
        np.tile(np.array(ap_vec, dtype=float), (n_pts, 1)),
        version=version,
    )[:, 0]

    v_km_s = np.sqrt(MU_KM3_S2 * (2.0 / r_km - 1.0 / a_km))
    h_ang = math.sqrt(MU_KM3_S2 * a_km * max(1e-12, 1.0 - e * e))
    corot = np.maximum(0.85, 1.0 - (OMEGA_EARTH_RAD_S * h_ang * math.cos(inc)) / (v_km_s ** 2))
    v_rel_m_s = v_km_s * corot * 1000.0
    a_drag_km_s2 = 0.5e-3 * rho * (v_rel_m_s ** 2)

    da_dt_s = -(2.0 * (a_km ** 2) * v_km_s / MU_KM3_S2) * a_drag_km_s2
    de_dt_s = -(2.0 * (e + cos_nu) / v_km_s) * a_drag_km_s2
    weights = one_minus_ecosE / np.sum(one_minus_ecosE)
    return float(np.sum(weights * da_dt_s)) * SEC_PER_DAY, float(np.sum(weights * de_dt_s)) * SEC_PER_DAY


def propagate_decay(
    t0: datetime, a0: float, e0: float, inc_deg: float, raan0: float, argp0: float,
    B: float, sw: SpaceWeather1963, version: float = 2.1, max_days: float = 35.0,
    stop_alt_km: float = 120.0, q_scale: float = 1.0,
) -> tuple[datetime | None, list[dict]]:
    t, a, e, raan, argp, elapsed = t0, a0, e0, raan0, argp0, 0.0
    def entry(dt_val, a_val, e_val):
        return {'utc': dt_val.strftime('%Y-%m-%dT%H:%MZ'),
                'hp_km': round(a_val * (1.0 - e_val) - RE_KM, 1),
                'ha_km': round(a_val * (1.0 + e_val) - RE_KM, 1)}
    daily_profile, last_day = [entry(t, a, e)], t.date()

    while elapsed < max_days:
        hp = a * (1.0 - e) - RE_KM
        if hp <= stop_alt_km:
            return t, daily_profile
        step = 0.25 if hp > 200.0 else (0.1 if hp > 160.0 else 0.02)
        da1, de1 = orbit_averaged_drag_rates(t, a, e, inc_deg, raan, argp, sw, version=version)
        dr1, dw1 = j2_rates_deg_day(a, e, inc_deg)
        da1, de1 = da1 * B * q_scale, de1 * B * q_scale

        t_mid = t + timedelta(days=0.5 * step)
        a_mid = max(RE_KM + 80.0, a + 0.5 * step * da1)
        e_mid = max(1e-5, min(0.9, e + 0.5 * step * de1))
        da2, de2 = orbit_averaged_drag_rates(
            t_mid, a_mid, e_mid, inc_deg,
            (raan + 0.5 * step * dr1) % 360.0, (argp + 0.5 * step * dw1) % 360.0,
            sw, version=version,
        )
        dr2, dw2 = j2_rates_deg_day(a_mid, e_mid, inc_deg)
        a_new = a + step * da2 * B * q_scale
        e_new = max(1e-5, min(0.9, e + step * de2 * B * q_scale))
        hp_new = a_new * (1.0 - e_new) - RE_KM
        if hp_new <= stop_alt_km:
            frac = (hp - stop_alt_km) / max(1e-9, hp - hp_new)
            t_end = t + timedelta(days=step * frac)
            daily_profile.append({'utc': t_end.strftime('%Y-%m-%dT%H:%MZ'),
                                  'hp_km': round(stop_alt_km, 1), 'ha_km': round(stop_alt_km, 1)})
            return t_end, daily_profile

        t, a, e = t + timedelta(days=step), a_new, e_new
        raan, argp = (raan + step * dr2) % 360.0, (argp + step * dw2) % 360.0
        elapsed += step
        if t.date() != last_day:
            daily_profile.append(entry(t, a, e))
            last_day = t.date()
    return None, daily_profile


def estimate_interval_B(r1: dict, r2: dict, sw: SpaceWeather1963, version: float = 2.1) -> dict | None:
    dt_days = (r2['epoch'] - r1['epoch']).total_seconds() / SEC_PER_DAY
    if dt_days <= 0.1:
        return None
    a1, a2 = mean_motion_to_a(r1['mean_motion']), mean_motion_to_a(r2['mean_motion'])
    da_obs = a2 - a1
    n_sub = max(2, int(math.ceil(dt_days * 4)))
    da_per_B_total = 0.0
    draan = ((r2['raan'] - r1['raan'] + 180.0) % 360.0) - 180.0
    dargp = ((r2['arg_perigee'] - r1['arg_perigee'] + 180.0) % 360.0) - 180.0
    for k in range(n_sub):
        frac = (k + 0.5) / n_sub
        da_rate, _ = orbit_averaged_drag_rates(
            r1['epoch'] + timedelta(days=dt_days * frac),
            a1 + (a2 - a1) * frac,
            r1['eccentricity'] + (r2['eccentricity'] - r1['eccentricity']) * frac,
            0.5 * (r1['inclination'] + r2['inclination']),
            (r1['raan'] + draan * frac) % 360.0,
            (r1['arg_perigee'] + dargp * frac) % 360.0,
            sw, version=version, n_pts=16,
        )
        da_per_B_total += da_rate * (dt_days / n_sub)
    if da_per_B_total >= 0:
        return None
    return {
        't1': r1['epoch'].strftime('%Y-%m-%dT%H:%MZ'),
        't2': r2['epoch'].strftime('%Y-%m-%dT%H:%MZ'),
        'dt_days': round(dt_days, 3),
        'hp_km': round(a1 * (1.0 - r1['eccentricity']) - RE_KM, 1),
        'da_obs_km': round(da_obs, 4),
        'B_eff_m2_kg': round(da_obs / da_per_B_total, 5),
        '_t2_dt': r2['epoch'],
    }


def load_parquet_by_id(parquet_path: Path) -> dict[int, list[dict]]:
    if sha256_file(parquet_path) != PARQUET_SHA256:
        raise ValueError('Parquet SHA-256 mismatch against pinned corpus')
    import pyarrow.parquet as pq
    table = pq.read_table(parquet_path)
    if table.num_rows != 4567:
        raise ValueError('Parquet row count drift')
    by_id: dict[int, list[dict]] = defaultdict(list)
    for r in table.to_pylist():
        by_id[r['norad_id']].append(r)
    clean: dict[int, list[dict]] = {}
    for nid, recs in by_id.items():
        recs.sort(key=lambda x: x['epoch'])
        dedup = []
        for r in recs:
            if not dedup or dedup[-1]['epoch'] != r['epoch']:
                dedup.append(r)
        clean[nid] = dedup
    return clean


def run_experiment(parquet_path: Path, gfz_path: Path) -> dict:
    sw = SpaceWeather1963(gfz_path)
    by_id = load_parquet_by_id(parquet_path)

    calibrators = {}
    for nid, label in ((81, 'Explorer 9 (1961-004A, 3.66m balloon)'), (529, 'NORAD 529 (1963-003C, inc 81.9 deg)')):
        t_lo, t_hi = datetime(1963, 9, 15, tzinfo=timezone.utc), datetime(1963, 11, 20, tzinfo=timezone.utc)
        recs = [r for r in by_id[nid] if t_lo <= r['epoch'] <= t_hi]
        ests = [e for r1, r2 in zip(recs[:-1], recs[1:]) if (e := estimate_interval_B(r1, r2, sw, 2.1))]
        pre = [x['B_eff_m2_kg'] for x in ests if x['_t2_dt'] <= datetime(1963, 10, 28, tzinfo=timezone.utc) and x['B_eff_m2_kg'] > 0]
        med_pre = round(median(pre), 5)
        gap_rows = []
        for x in ests:
            if x.pop('_t2_dt') > datetime(1963, 10, 27, 15, tzinfo=timezone.utc):
                x['ratio_vs_pre_oct28'] = round(x['B_eff_m2_kg'] / med_pre, 3)
                gap_rows.append(x)
        calibrators[str(nid)] = {'description': label, 'model': 'MSIS-2.1',
                                 'pre_oct28_median_B_m2_kg': med_pre, 'post_oct27_intervals': gap_rows}

    holdouts = []
    for nid, label, label_class, cutoffs in R68_CONTROLS:
        recs = by_id[nid]
        for cut_str in cutoffs:
            train = strict_training_cutoff(recs, datetime.fromisoformat(cut_str).replace(tzinfo=timezone.utc))
            window = [r for r in train if (train[-1]['epoch'] - r['epoch']).total_seconds() <= 35 * SEC_PER_DAY]
            if len(window) < 2:
                window = train[-2:]
            orig = train[-1]
            a0 = mean_motion_to_a(orig['mean_motion'])
            for ver, mname in ((2.1, 'MSIS-2.1'), (0, 'NRLMSISE-00')):
                bs = [e['B_eff_m2_kg'] for r1, r2 in zip(window[:-1], window[1:])
                      if (e := estimate_interval_B(r1, r2, sw, ver)) and e['B_eff_m2_kg'] > 0]
                b_fit = round(median(bs), 5)
                pred_dt, _ = propagate_decay(orig['epoch'], a0, orig['eccentricity'], orig['inclination'],
                                             orig['raan'], orig['arg_perigee'], b_fit, sw, version=ver)
                err = assumed_utc_day_error(pred_dt, label) if pred_dt else None
                holdouts.append({
                    'norad': nid, 'label_day': label, 'label_class': label_class,
                    'cutoff_utc': cut_str + 'T00:00:00Z',
                    'train_last_epoch_utc': orig['epoch'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'model': mname, 'B_fit_m2_kg': b_fit,
                    'predicted_decay_utc': pred_dt.strftime('%Y-%m-%dT%H:%M:%SZ') if pred_dt else None,
                    'assumed_utc_day_error_interval': err,
                    'hits_assumed_utc_day': bool(err and err[0] <= 0.0 <= err[1]),
                })

    recs528 = by_id[528]
    orig528 = recs528[-1]
    a0_528 = mean_motion_to_a(orig528['mean_motion'])
    sep_oct = [r for r in recs528 if r['epoch'] >= datetime(1963, 9, 1, tzinfo=timezone.utc)]
    scenarios_528, alt_profile = [], None
    for ver, mname in ((2.1, 'MSIS-2.1'), (0, 'NRLMSISE-00')):
        ests = [e for r1, r2 in zip(sep_oct[:-1], sep_oct[1:]) if (e := estimate_interval_B(r1, r2, sw, ver))]
        b_all = [x['B_eff_m2_kg'] for x in ests if x['B_eff_m2_kg'] > 0]
        b_oct = [x['B_eff_m2_kg'] for x in ests if x['B_eff_m2_kg'] > 0 and x['t1'] >= '1963-10-01']
        for tag, b_val, q_scale in (
            ('median_sep_oct', round(median(b_all), 5), 1.0),
            ('median_oct', round(median(b_oct), 5), 1.0),
            ('median_last_3', round(median(b_all[-3:]), 5), 1.0),
            ('median_sep_oct_q115', round(median(b_all), 5), 1.15),
        ):
            pred_dt, prof = propagate_decay(orig528['epoch'], a0_528, orig528['eccentricity'], orig528['inclination'],
                                            orig528['raan'], orig528['arg_perigee'], b_val, sw, version=ver, q_scale=q_scale)
            scenarios_528.append({'model': mname, 'scenario': tag, 'B_fit_m2_kg': b_val, 'q_density_scale': q_scale,
                                  'predicted_decay_utc_EXPLORATORY': pred_dt.strftime('%Y-%m-%dT%H:%MZ') if pred_dt else None})
            if ver == 2.1 and tag == 'median_oct':
                alt_profile = prof

    return {
        'experiment_id': 'C241-MSIS-DECAY-HOLDOUT-20261120',
        'verification_status': 'RETROSPECTIVE_EXPLORATORY_NOT_CALIBRATED_FOR_IMPACT',
        'provenance': {'tle_parquet_url': PARQUET_URL, 'tle_parquet_sha256': PARQUET_SHA256,
                       'gfz_space_weather_url': GFZ_URL, 'gfz_space_weather_sha256': sw.sha256,
                       'pymsis_versions_tested': ['2.1', '0 (NRLMSISE-00)']},
        'epistemic_contract': {'historical_event_time_utc': None, 'terminal_time_sigma_hours': None,
                               'calibrated_terminal_holdouts': 0, 'historical_mcmc': 'NOT_RUN',
                               'active_constraint_528': False, 'impact_geography': None},
        'space_weather_storms_oct18_nov12': sw.storm_summary('1963-10-18', '1963-11-12'),
        'density_calibrators': calibrators,
        'control_holdouts': holdouts,
        'norad_528_exploratory': {
            'origin_epoch_utc': orig528['epoch'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'origin_a_km': round(a0_528, 3),
            'origin_hp_km': round(a0_528 * (1.0 - orig528['eccentricity']) - RE_KM, 1),
            'origin_ha_km': round(a0_528 * (1.0 + orig528['eccentricity']) - RE_KM, 1),
            'nasa_catalog_day_label': '1963-11-08',
            'scenarios': scenarios_528,
            'msis21_median_oct_daily_altitude_profile': alt_profile,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Run C241 MSIS-2.1/NRLMSISE-00 decay holdout.')
    parser.add_argument('--parquet', type=Path, required=True, help='Path to SHA-pinned tle_1963.parquet')
    parser.add_argument('--gfz', type=Path, required=True, help='Path to GFZ Kp_ap_Ap_SN_F107_since_1932.txt')
    parser.add_argument('--output', type=Path, required=True, help='Path to output JSON ledger')
    args = parser.parse_args()

    result = run_experiment(args.parquet, args.gfz)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(',', ':'), indent=1) + '\n', encoding='utf-8')
    print(f'Wrote {args.output} ({args.output.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
