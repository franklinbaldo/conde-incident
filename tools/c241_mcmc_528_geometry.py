#!/usr/bin/env python3
"""C241: 10-month MSIS-2.1 MCMC on NORAD 528 (Jan-Oct 1963) + geometry bounds.

Directly models observed semi-major axis change da_obs (km) across all 43 valid
TLE intervals of NORAD 528 under MSIS-2.1 with GFZ 3-hour ap + F10.7 storms to
separate TLE noise (sigma_a), residual atm/tumble scatter (sigma_f), and test
three physical geometry models (M1 isotropic/fast-tumbling, M2 altitude-trend,
M3 non-spherical RAAN-modulated aspect ratio).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c241_msis_decay_holdout as m


def extract_528_intervals(by_id: dict[int, list[dict]], sw: m.SpaceWeather1963) -> list[dict]:
    recs = by_id[528]
    ivs = []
    for r1, r2 in zip(recs[:-1], recs[1:]):
        dt_d = (r2['epoch'] - r1['epoch']).total_seconds() / m.SEC_PER_DAY
        if dt_d < 0.25:
            continue
        est = m.estimate_interval_B(r1, r2, sw, version=2.1)
        if not est or est['B_eff_m2_kg'] == 0:
            continue
        a1, a2 = m.mean_motion_to_a(r1['mean_motion']), m.mean_motion_to_a(r2['mean_motion'])
        da_obs = a2 - a1
        da_per_B = da_obs / est['B_eff_m2_kg']
        t_mid = r1['epoch'] + (r2['epoch'] - r1['epoch']) / 2
        doy = (t_mid - datetime(1963, 1, 1, tzinfo=timezone.utc)).total_seconds() / m.SEC_PER_DAY
        hp_mid = 0.5 * (a1 * (1 - r1['eccentricity']) + a2 * (1 - r2['eccentricity'])) - m.RE_KM
        d0 = datetime(r1['epoch'].year, r1['epoch'].month, r1['epoch'].day, tzinfo=timezone.utc)
        d1 = datetime(r2['epoch'].year, r2['epoch'].month, r2['epoch'].day, tzinfo=timezone.utc)
        max_ap, cur = 0.0, d0
        while cur <= d1:
            if cur in sw.daily:
                max_ap = max(max_ap, sw.daily[cur][0])
            cur += timedelta(days=1)
        ivs.append({
            't1': r1['epoch'].strftime('%Y-%m-%dT%H:%MZ'),
            't2': r2['epoch'].strftime('%Y-%m-%dT%H:%MZ'),
            'dt_d': round(dt_d, 3), 'doy': round(doy, 2), 'hp_km': round(hp_mid, 1),
            'raan_deg': round(r1['raan'], 2), 'max_Ap': int(max_ap),
            'da_obs': da_obs, 'da_per_B': da_per_B, 'B_est': est['B_eff_m2_kg'],
        })
    return ivs


def run_mh(log_post, x0, step_scales, n_steps=16000, burn=4000, seed=42):
    rng = np.random.default_rng(seed)
    x = np.array(x0, dtype=float)
    lp = log_post(x)
    samples, lps, acc = [], [], 0
    for i in range(n_steps):
        prop = x + rng.normal(0.0, step_scales)
        lp_prop = log_post(prop)
        if math.isfinite(lp_prop) and math.log(rng.random()) < (lp_prop - lp):
            x, lp = prop, lp_prop
            acc += 1
        if i >= burn and (i - burn) % 4 == 0:
            samples.append(x.copy())
            lps.append(lp)
    return np.array(samples), np.array(lps), acc / n_steps


def run_analysis(parquet_path: Path, gfz_path: Path) -> dict:
    sw = m.SpaceWeather1963(gfz_path)
    by_id = m.load_parquet_by_id(parquet_path)
    ivs = extract_528_intervals(by_id, sw)
    n = len(ivs)

    da_obs = np.array([x['da_obs'] for x in ivs])
    da_per_B = np.array([x['da_per_B'] for x in ivs])
    hp = np.array([x['hp_km'] for x in ivs])
    doy = np.array([x['doy'] for x in ivs])
    raan = np.radians([x['raan_deg'] for x in ivs])
    max_ap = np.array([x['max_Ap'] for x in ivs])

    seasons = []
    for name, mask in (
        ('Jan-Mar', doy < 90), ('Apr-Jun', (doy >= 90) & (doy < 181)),
        ('Jul-Aug', (doy >= 181) & (doy < 243)), ('Sep-Oct', doy >= 243),
    ):
        seasons.append({
            'season': name, 'n_intervals': int(np.sum(mask)),
            'total_da_km': round(float(np.sum(da_obs[mask])), 2),
            'weighted_B_m2_kg': round(float(np.sum(da_obs[mask]) / np.sum(da_per_B[mask])), 5),
        })

    storm_mask = max_ap >= 30
    storm_check = {
        'quiet_n': int(np.sum(~storm_mask)),
        'quiet_weighted_B_m2_kg': round(float(np.sum(da_obs[~storm_mask]) / np.sum(da_per_B[~storm_mask])), 5),
        'storm_n': int(np.sum(storm_mask)),
        'storm_weighted_B_m2_kg': round(float(np.sum(da_obs[storm_mask]) / np.sum(da_per_B[storm_mask])), 5),
    }

    def lp_m1(th):
        b0, lsa, lsf = th
        if not (0.05 < b0 < 1.0 and -4.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
            return -np.inf
        sa, sf = math.exp(lsa), math.exp(lsf)
        pred = b0 * da_per_B
        var = 2.0 * sa * sa + (sf * pred) ** 2
        return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))

    def lp_m2(th):
        b0, beta, lsa, lsf = th
        if not (0.05 < b0 < 1.0 and -1.5 < beta < 1.5 and -4.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
            return -np.inf
        sa, sf = math.exp(lsa), math.exp(lsf)
        pred = b0 * np.exp(beta * (hp - 350.0) / 100.0) * da_per_B
        var = 2.0 * sa * sa + (sf * pred) ** 2
        return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))

    def lp_m3(th):
        b0, amp, phi, lsa, lsf = th
        if not (0.05 < b0 < 1.0 and 0.0 <= amp < 0.75 and -math.pi <= phi <= math.pi
                and -4.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
            return -np.inf
        sa, sf = math.exp(lsa), math.exp(lsf)
        pred = b0 * (1.0 + amp * np.cos(2.0 * (raan - phi))) * da_per_B
        var = 2.0 * sa * sa + (sf * pred) ** 2
        return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))

    s1, l1, a1 = run_mh(lp_m1, [0.22, math.log(0.4), math.log(0.15)], [0.008, 0.12, 0.12])
    s2, l2, a2 = run_mh(lp_m2, [0.23, -0.1, math.log(0.4), math.log(0.15)], [0.008, 0.06, 0.12, 0.12])
    s3, l3, a3 = run_mh(lp_m3, [0.22, 0.15, 0.0, math.log(0.4), math.log(0.15)], [0.008, 0.05, 0.25, 0.12, 0.12])

    bic1 = round(float(3 * math.log(n) - 2.0 * np.max(l1)), 2)
    bic2 = round(float(4 * math.log(n) - 2.0 * np.max(l2)), 2)
    bic3 = round(float(5 * math.log(n) - 2.0 * np.max(l3)), 2)

    orig528 = by_id[528][-1]
    a0 = m.mean_motion_to_a(orig528['mean_motion'])
    rng = np.random.default_rng(123)
    ref_t = datetime(1963, 11, 8, 0, 0, tzinfo=timezone.utc)
    p_only, p_full = [], []
    for idx in rng.choice(len(s1), size=60, replace=False):
        b_d, sf_d = float(s1[idx, 0]), float(math.exp(s1[idx, 2]))
        tp, _ = m.propagate_decay(orig528['epoch'], a0, orig528['eccentricity'], orig528['inclination'],
                                  orig528['raan'], orig528['arg_perigee'], b_d, sw, version=2.1)
        if tp:
            p_only.append((tp - ref_t).total_seconds() / m.SEC_PER_DAY)
        tf, _ = m.propagate_decay(orig528['epoch'], a0, orig528['eccentricity'], orig528['inclination'],
                                  orig528['raan'], orig528['arg_perigee'], b_d, sw, version=2.1,
                                  q_scale=float(math.exp(rng.normal(0.0, sf_d))))
        if tf:
            p_full.append((tf - ref_t).total_seconds() / m.SEC_PER_DAY)

    def summarize_pred(arr):
        q5, q25, q50, q75, q95 = np.percentile(arr, [5, 25, 50, 75, 95])
        fmt = lambda d: (ref_t + timedelta(days=float(d))).strftime('%Y-%m-%dT%H:%MZ')
        return {'median_utc': fmt(q50), 'ci50_utc': [fmt(q25), fmt(q75)], 'ci90_utc': [fmt(q5), fmt(q95)],
                'ci50_width_hours': round(float((q75 - q25) * 24.0), 1),
                'ci90_width_days': round(float(q95 - q5), 2)}

    return {
        'experiment_id': 'C241-MCMC-528-GEOMETRY-20261120',
        'verification_status': 'EXPLORATORY_MCMC_AND_LEAN4_GEOMETRY_BOUNDS',
        'lean_certificate_ref': 'formal/Conde1963/BallisticGeometryBound.lean',
        'provenance': {'tle_parquet_sha256': m.PARQUET_SHA256, 'gfz_space_weather_sha256': sw.sha256,
                       'n_intervals_jan_oct_1963': n, 'total_da_km': round(float(np.sum(da_obs)), 2)},
        'seasonal_stability': seasons,
        'storm_vs_quiet_consistency': storm_check,
        'mcmc_models': {
            'M1_isotropic_fast_tumbling': {
                'k': 3, 'accept_rate': round(a1, 3), 'max_loglik': round(float(np.max(l1)), 2), 'bic': bic1,
                'B0_median_m2_kg': round(float(np.median(s1[:, 0])), 5),
                'B0_ci90_m2_kg': [round(float(np.percentile(s1[:, 0], 5)), 5), round(float(np.percentile(s1[:, 0], 95)), 5)],
                'sigma_a_median_km': round(float(np.median(np.exp(s1[:, 1]))), 3),
                'sigma_f_median_frac': round(float(np.median(np.exp(s1[:, 2]))), 4),
            },
            'M2_altitude_trend': {
                'k': 4, 'accept_rate': round(a2, 3), 'max_loglik': round(float(np.max(l2)), 2),
                'bic': bic2, 'delta_bic_vs_M1': round(bic2 - bic1, 2),
                'B350_median_m2_kg': round(float(np.median(s2[:, 0])), 5),
                'beta_per_100km_median': round(float(np.median(s2[:, 1])), 3),
                'beta_per_100km_ci90': [round(float(np.percentile(s2[:, 1], 5)), 3), round(float(np.percentile(s2[:, 1], 95)), 3)],
            },
            'M3_nonspherical_raan_modulation': {
                'k': 5, 'accept_rate': round(a3, 3), 'max_loglik': round(float(np.max(l3)), 2),
                'bic': bic3, 'delta_bic_vs_M1': round(bic3 - bic1, 2),
                'amp_median': round(float(np.median(s3[:, 1])), 4),
                'aspect_ratio_median': round(float(np.median((1 + s3[:, 1]) / (1 - s3[:, 1]))), 3),
            },
        },
        'posterior_predictive_decay_M1': {
            'parameter_only': summarize_pred(p_only),
            'full_predictive_with_sigma_f': summarize_pred(p_full),
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description='Run C241 10-month MSIS-2.1 MCMC on NORAD 528.')
    p.add_argument('--parquet', type=Path, required=True)
    p.add_argument('--gfz', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    res = run_analysis(args.parquet, args.gfz)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(res, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {args.output} ({args.output.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
