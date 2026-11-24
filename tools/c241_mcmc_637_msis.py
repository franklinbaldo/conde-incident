#!/usr/bin/env python3
"""C241: 23-interval MSIS-2.1 & NRLMSISE-00 MCMC on NORAD 637 (1963-035A, Thor Agena D 1169).

Models observed semi-major axis change da_obs (km) across the 23 pure-decay TLE intervals
(Aug 30 - Nov 5, 1963) under NRLMSIS-2.1 and NRLMSISE-00 with GFZ Potsdam 3-hour ap + F10.7,
evaluates posterior predictive reentry windows from the last TLE (1963-11-05T07:54:43Z),
and maps the conditional Conde orbital-plane crossings on 1963-11-07 against those windows.
NOT an impact predictor or phase reconstruction.
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
import c241_mcmc_528_geometry as g

UTC = timezone.utc
# Modern camera proxy CGEO15-CAMERA-01 (Vila do Conde, Sep 2022) — NOT a 1963 impact point.
CONDE_PROXY_LAT_DEG = -11.7988
CONDE_PROXY_LON_DEG = -37.621475
CONDE_PROXY_ID = 'CGEO15-CAMERA-01'
EARTH_FLATTENING_B_KM = 6356.752314245


def surface_radius_km(lat_rad: float) -> float:
    a, b = m.RE_KM, EARTH_FLATTENING_B_KM
    x, y = math.cos(lat_rad), math.sin(lat_rad)
    return math.hypot(a * a * x, b * b * y) / math.hypot(a * x, b * y)


def signed_plane_distance_km(dt: datetime, raan_deg: float, inc_deg: float,
                             lat_deg: float = CONDE_PROXY_LAT_DEG,
                             lon_deg: float = CONDE_PROXY_LON_DEG) -> float:
    """Signed normal distance n . r_ECI (km) from Conde proxy to orbital plane."""
    lat = math.radians(lat_deg)
    theta = m.gmst_rad(dt) + math.radians(lon_deg)
    raan = math.radians(raan_deg)
    inc = math.radians(inc_deg)
    proj = (math.sin(inc) * math.cos(lat) * math.sin(raan - theta)
            + math.cos(inc) * math.sin(lat))
    return surface_radius_km(lat) * proj


def propagate_raan_track(
    t0: datetime, a0: float, e0: float, inc_deg: float, raan0: float, argp0: float,
    B: float, sw: m.SpaceWeather1963, version: float, end_utc: datetime,
) -> list[tuple[datetime, float, float]]:
    """Integrate (t, raan_deg, hp_km) with MSIS drag + J2 through end_utc (clamping at 120 km)."""
    t, a, e, raan, argp = t0, a0, e0, raan0, argp0
    track = [(t, raan, a * (1.0 - e) - m.RE_KM)]
    while t < end_utc:
        hp = a * (1.0 - e) - m.RE_KM
        step = min(0.05 if hp > 160.0 else 0.02, (end_utc - t).total_seconds() / m.SEC_PER_DAY)
        if step <= 1e-6:
            break
        dr1, dw1 = m.j2_rates_deg_day(a, e, inc_deg)
        if hp > 120.0:
            da1, de1 = m.orbit_averaged_drag_rates(t, a, e, inc_deg, raan, argp, sw, version=version)
            da1, de1 = da1 * B, de1 * B
        else:
            da1, de1 = 0.0, 0.0
        a_mid = max(m.RE_KM + 120.0, a + 0.5 * step * da1)
        e_mid = max(1e-5, min(0.9, e + 0.5 * step * de1))
        dr2, dw2 = m.j2_rates_deg_day(a_mid, e_mid, inc_deg)
        if hp > 120.0:
            da2, de2 = m.orbit_averaged_drag_rates(
                t + timedelta(days=0.5 * step), a_mid, e_mid, inc_deg,
                (raan + 0.5 * step * dr1) % 360.0, (argp + 0.5 * step * dw1) % 360.0,
                sw, version=version,
            )
            a = max(m.RE_KM + 120.0, a + step * da2 * B)
            e = max(1e-5, min(0.9, e + step * de2 * B))
        t = t + timedelta(days=step)
        raan = (raan + step * dr2) % 360.0
        argp = (argp + step * dw2) % 360.0
        track.append((t, raan, a * (1.0 - e) - m.RE_KM))
    return track


def interp_raan_deg(track: list[tuple[datetime, float, float]], dt: datetime) -> float:
    ts = np.array([(p[0] - track[0][0]).total_seconds() for p in track])
    raans = np.degrees(np.unwrap(np.radians([p[1] for p in track])))
    q = (dt - track[0][0]).total_seconds()
    return float(np.interp(q, ts, raans)) % 360.0


def find_plane_crossings_nov7(
    track: list[tuple[datetime, float, float]], inc_deg: float,
    pred_param: list[float], pred_full: list[float], ref_t: datetime,
) -> list[dict]:
    """Find Conde-proxy orbital-plane crossings on 1963-11-07 UTC with 50/100/200 km widths."""
    day_start = datetime(1963, 11, 7, 0, 0, tzinfo=UTC)
    day_end = datetime(1963, 11, 8, 0, 0, tzinfo=UTC)
    grid = [day_start + timedelta(minutes=3 * k) for k in range(481)]
    vals = [signed_plane_distance_km(t, interp_raan_deg(track, t), inc_deg) for t in grid]

    crossings = []
    for t_a, t_b, v_a, v_b in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if v_a * v_b > 0:
            continue
        lo, hi, vlo = t_a, t_b, v_a
        for _ in range(30):
            mid = lo + (hi - lo) / 2
            vm = signed_plane_distance_km(mid, interp_raan_deg(track, mid), inc_deg)
            if vlo * vm <= 0:
                hi = mid
            else:
                lo, vlo = mid, vm
        t_cross = lo + (hi - lo) / 2
        if not (day_start <= t_cross < day_end):
            continue
        raan_c = interp_raan_deg(track, t_cross)
        # Numeric slope km/min around crossing to get exact 50/100/200 km window widths
        dt_eps = timedelta(seconds=10)
        d_plus = signed_plane_distance_km(t_cross + dt_eps, interp_raan_deg(track, t_cross + dt_eps), inc_deg)
        d_minus = signed_plane_distance_km(t_cross - dt_eps, interp_raan_deg(track, t_cross - dt_eps), inc_deg)
        slope_km_min = abs(d_plus - d_minus) / (20.0 / 60.0)
        # Ascending vs descending pass: theta_site = gmst + lon; at ascending node theta ~ raan
        theta_deg = math.degrees(m.gmst_rad(t_cross) + math.radians(CONDE_PROXY_LON_DEG)) % 360.0
        d_ang = ((theta_deg - raan_c + 180.0) % 360.0) - 180.0
        pass_dir = 'ascending_south_to_north' if abs(d_ang) < 90.0 else 'descending_north_to_south'

        t_rel_days = (t_cross - ref_t).total_seconds() / m.SEC_PER_DAY
        p_param = float(np.mean(np.array(pred_param) <= t_rel_days)) if pred_param else None
        p_full = float(np.mean(np.array(pred_full) <= t_rel_days)) if pred_full else None
        bahia = t_cross - timedelta(hours=3)
        crossings.append({
            'crossing_utc': t_cross.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'crossing_bahia_utc_minus_3': bahia.strftime('%Y-%m-%d %H:%M:%S'),
            'pass_direction': pass_dir,
            'raan_deg': round(raan_c, 4),
            'window_width_min': {
                str(d_km): round(2.0 * d_km / slope_km_min, 3) for d_km in (50, 100, 200)
            },
            'cdf_in_param_only_predictive': round(p_param, 3) if p_param is not None else None,
            'cdf_in_full_predictive': round(p_full, 3) if p_full is not None else None,
        })
    return crossings


def extract_637_intervals(by_id: dict[int, list[dict]], sw: m.SpaceWeather1963, version: float) -> tuple[list[dict], list[dict]]:
    recs = by_id[637]
    valid, excluded = [], []
    for r1, r2 in zip(recs[:-1], recs[1:]):
        dt_d = (r2['epoch'] - r1['epoch']).total_seconds() / m.SEC_PER_DAY
        est = m.estimate_interval_B(r1, r2, sw, version=version)
        if not est or est['B_eff_m2_kg'] == 0:
            continue
        a1, a2 = m.mean_motion_to_a(r1['mean_motion']), m.mean_motion_to_a(r2['mean_motion'])
        da_obs = a2 - a1
        da_per_B = da_obs / est['B_eff_m2_kg']
        hp_mid = 0.5 * (a1 * (1.0 - r1['eccentricity']) + a2 * (1.0 - r2['eccentricity'])) - m.RE_KM
        d0 = datetime(r1['epoch'].year, r1['epoch'].month, r1['epoch'].day, tzinfo=UTC)
        d1 = datetime(r2['epoch'].year, r2['epoch'].month, r2['epoch'].day, tzinfo=UTC)
        max_ap, cur = 0.0, d0
        while cur <= d1:
            if cur in sw.daily:
                max_ap = max(max_ap, sw.daily[cur][0])
            cur += timedelta(days=1)
        row = {
            't1': r1['epoch'].strftime('%Y-%m-%dT%H:%MZ'),
            't2': r2['epoch'].strftime('%Y-%m-%dT%H:%MZ'),
            'dt_d': round(dt_d, 3), 'hp_km': round(hp_mid, 1),
            'raan_deg': round(r1['raan'], 2), 'max_Ap': int(max_ap),
            'da_obs': da_obs, 'da_per_B': da_per_B, 'B_est': est['B_eff_m2_kg'],
        }
        if da_obs < 0.0:
            valid.append(row)
        else:
            excluded.append({
                't1': row['t1'], 't2': row['t2'], 'dt_d': row['dt_d'],
                'da_obs_km': round(da_obs, 4), 'reason': 'positive_da_non_decay_early_mission_or_tle_noise',
            })
    return valid, excluded


def fit_model_suite(ivs: list[dict], sw: m.SpaceWeather1963, orig: dict, version: float) -> dict:
    n = len(ivs)
    da_obs = np.array([x['da_obs'] for x in ivs])
    da_per_B = np.array([x['da_per_B'] for x in ivs])
    hp = np.array([x['hp_km'] for x in ivs])
    raan = np.radians([x['raan_deg'] for x in ivs])
    max_ap = np.array([x['max_Ap'] for x in ivs])

    phases = []
    for name, lo, hi in (('Aug30-Sep30', 0, 9), ('Sep30-Oct22', 9, 17), ('Oct22-Nov05', 17, n)):
        sl = slice(lo, hi)
        phases.append({
            'phase': name, 'n_intervals': int(len(da_obs[sl])),
            'total_da_km': round(float(np.sum(da_obs[sl])), 2),
            'weighted_B_m2_kg': round(float(np.sum(da_obs[sl]) / np.sum(da_per_B[sl])), 5),
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
        if not (0.002 < b0 < 0.15 and -5.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
            return -np.inf
        sa, sf = math.exp(lsa), math.exp(lsf)
        pred = b0 * da_per_B
        var = 2.0 * sa * sa + (sf * pred) ** 2
        return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))

    def lp_m2(th):
        b0, beta, lsa, lsf = th
        if not (0.002 < b0 < 0.15 and -2.0 < beta < 2.0 and -5.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
            return -np.inf
        sa, sf = math.exp(lsa), math.exp(lsf)
        pred = b0 * np.exp(beta * (hp - 260.0) / 100.0) * da_per_B
        var = 2.0 * sa * sa + (sf * pred) ** 2
        return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))

    def lp_m3(th):
        b0, amp, phi, lsa, lsf = th
        if not (0.002 < b0 < 0.15 and 0.0 <= amp < 0.75 and -math.pi <= phi <= math.pi
                and -5.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
            return -np.inf
        sa, sf = math.exp(lsa), math.exp(lsf)
        pred = b0 * (1.0 + amp * np.cos(2.0 * (raan - phi))) * da_per_B
        var = 2.0 * sa * sa + (sf * pred) ** 2
        return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))

    b_init = float(np.sum(da_obs) / np.sum(da_per_B))
    s1, l1, a1 = g.run_mh(lp_m1, [b_init, math.log(0.4), math.log(0.12)], [0.0008, 0.15, 0.15], 20000, 4000, 42)
    s2, l2, a2 = g.run_mh(lp_m2, [b_init, 0.0, math.log(0.4), math.log(0.12)], [0.0008, 0.15, 0.15, 0.15], 20000, 4000, 42)
    s3, l3, a3 = g.run_mh(lp_m3, [b_init, 0.10, 0.0, math.log(0.4), math.log(0.12)], [0.0008, 0.06, 0.30, 0.15, 0.15], 20000, 4000, 42)

    bic1 = round(float(3 * math.log(n) - 2.0 * np.max(l1)), 2)
    bic2 = round(float(4 * math.log(n) - 2.0 * np.max(l2)), 2)
    bic3 = round(float(5 * math.log(n) - 2.0 * np.max(l3)), 2)

    a0 = m.mean_motion_to_a(orig['mean_motion'])
    rng = np.random.default_rng(123)
    ref_t = datetime(1963, 11, 7, 0, 0, tzinfo=UTC)
    p_only, p_full = [], []
    for idx in rng.choice(len(s1), size=100, replace=False):
        b_d, sf_d = float(s1[idx, 0]), float(math.exp(s1[idx, 2]))
        tp, _ = m.propagate_decay(
            orig['epoch'], a0, orig['eccentricity'], orig['inclination'],
            orig['raan'], orig['arg_perigee'], b_d, sw, version=version, max_days=10.0,
        )
        if tp:
            p_only.append((tp - ref_t).total_seconds() / m.SEC_PER_DAY)
        tf, _ = m.propagate_decay(
            orig['epoch'], a0, orig['eccentricity'], orig['inclination'],
            orig['raan'], orig['arg_perigee'], b_d, sw, version=version, max_days=10.0,
            q_scale=float(math.exp(rng.normal(0.0, sf_d))),
        )
        if tf:
            p_full.append((tf - ref_t).total_seconds() / m.SEC_PER_DAY)

    def summarize(arr: list[float]) -> dict:
        a_np = np.array(arr)
        q5, q25, q50, q75, q95 = np.percentile(a_np, [5, 25, 50, 75, 95])
        fmt = lambda d: (ref_t + timedelta(days=float(d))).strftime('%Y-%m-%dT%H:%MZ')
        return {
            'median_utc': fmt(q50),
            'ci50_utc': [fmt(q25), fmt(q75)],
            'ci90_utc': [fmt(q5), fmt(q95)],
            'ci50_width_hours': round(float((q75 - q25) * 24.0), 1),
            'ci90_width_hours': round(float((q95 - q5) * 24.0), 1),
            'frac_in_nov07_utc': round(float(np.mean((a_np >= 0.0) & (a_np < 1.0))), 3),
            'frac_in_nov07_bahia': round(float(np.mean((a_np >= 0.125) & (a_np < 1.125))), 3),
        }

    b0_med = float(np.median(s1[:, 0]))
    track = propagate_raan_track(
        orig['epoch'], a0, orig['eccentricity'], orig['inclination'],
        orig['raan'], orig['arg_perigee'], b0_med, sw, version,
        datetime(1963, 11, 8, 1, 0, tzinfo=UTC),
    )
    crossings = find_plane_crossings_nov7(track, orig['inclination'], p_only, p_full, ref_t)

    return {
        'weighted_B_all_23_m2_kg': round(b_init, 5),
        'phase_stability': phases,
        'storm_vs_quiet_consistency': storm_check,
        'mcmc_models': {
            'M1_isotropic_fast_tumbling': {
                'k': 3, 'accept_rate': round(a1, 3), 'max_loglik': round(float(np.max(l1)), 2), 'bic': bic1,
                'B0_median_m2_kg': round(b0_med, 5),
                'B0_ci90_m2_kg': [round(float(np.percentile(s1[:, 0], 5)), 5), round(float(np.percentile(s1[:, 0], 95)), 5)],
                'sigma_a_median_km': round(float(np.median(np.exp(s1[:, 1]))), 3),
                'sigma_f_median_frac': round(float(np.median(np.exp(s1[:, 2]))), 4),
            },
            'M2_altitude_trend': {
                'k': 4, 'accept_rate': round(a2, 3), 'max_loglik': round(float(np.max(l2)), 2),
                'bic': bic2, 'delta_bic_vs_M1': round(bic2 - bic1, 2),
                'B260_median_m2_kg': round(float(np.median(s2[:, 0])), 5),
                'beta_per_100km_median': round(float(np.median(s2[:, 1])), 3),
                'beta_per_100km_ci90': [round(float(np.percentile(s2[:, 1], 5)), 3), round(float(np.percentile(s2[:, 1], 95)), 3)],
            },
            'M3_nonspherical_raan_modulation': {
                'k': 5, 'accept_rate': round(a3, 3), 'max_loglik': round(float(np.max(l3)), 2),
                'bic': bic3, 'delta_bic_vs_M1': round(bic3 - bic1, 2),
                'amp_median': round(float(np.median(s3[:, 1])), 4),
                'aspect_ratio_median': round(float(np.median((1.0 + s3[:, 1]) / (1.0 - s3[:, 1]))), 3),
            },
        },
        'posterior_predictive_reentry_M1': {
            'origin_tle_utc': orig['epoch'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'origin_hp_ha_km': [round(a0 * (1.0 - orig['eccentricity']) - m.RE_KM, 1),
                                round(a0 * (1.0 + orig['eccentricity']) - m.RE_KM, 1)],
            'parameter_only': summarize(p_only),
            'full_predictive_with_sigma_f': summarize(p_full),
        },
        'conde_plane_crossings_1963_11_07': crossings,
    }


def run_analysis(parquet_path: Path, gfz_path: Path) -> dict:
    sw = m.SpaceWeather1963(gfz_path)
    by_id = m.load_parquet_by_id(parquet_path)
    recs = by_id[637]
    orig = recs[-1]

    ivs21, excl21 = extract_637_intervals(by_id, sw, version=2.1)
    ivs00, _ = extract_637_intervals(by_id, sw, version=0)

    res21 = fit_model_suite(ivs21, sw, orig, version=2.1)
    res00 = fit_model_suite(ivs00, sw, orig, version=0)

    return {
        'experiment_id': 'C241-MCMC-637-MSIS-20261124',
        'object': {'norad_id': 637, 'cospar': '1963-035A', 'name': 'Thor Agena D 1169 (CORONA KH-4 9058A)'},
        'verification_status': 'EXPLORATORY_MCMC_SECONDARY_TLE_NOT_IMPACT_PROOF',
        'provenance': {
            'tle_parquet_url': m.PARQUET_URL,
            'tle_parquet_sha256': m.PARQUET_SHA256,
            'gfz_space_weather_url': m.GFZ_URL,
            'gfz_space_weather_sha256': sw.sha256,
            'n_unique_tles': len(recs),
            'n_decay_intervals_used': len(ivs21),
            'total_da_km_23_intervals': round(float(sum(x['da_obs'] for x in ivs21)), 2),
            'excluded_intervals': excl21,
            'nasa_ssr_decay_day_utc': '1963-11-07',
            'plane_proxy_site': {'id': CONDE_PROXY_ID, 'lat_deg': CONDE_PROXY_LAT_DEG,
                                 'lon_deg': CONDE_PROXY_LON_DEG, 'status': 'MODERN_CAMERA_PROXY_NOT_IMPACT_SITE'},
        },
        'epistemic_contract': {
            'historical_event_time_utc': None,
            'terminal_time_sigma_hours': None,
            'calibrated_terminal_holdouts': 0,
            'phase_constraint': 'NOT_EVALUATED',
            'active_constraint_637': False,
            'impact_geography': None,
        },
        'models': {
            'NRLMSIS_2_1': res21,
            'NRLMSISE_00': res00,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description='Run C241 23-interval MSIS MCMC for NORAD 637.')
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
