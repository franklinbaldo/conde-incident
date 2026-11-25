#!/usr/bin/env python3
"""C241: Physical Cd (Sentman+SESAM+Knudsen), engineering priors, and storm-gamma audit (637 & 528)."""
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
KB = 1.380649e-23
AMU = 1.66053906660e-27
SPECIES_MASS_AMU = np.array([28.0134, 31.9988, 15.999, 4.0026, 1.0079, 39.948, 14.0067])
T_WALL_K = 300.0
ERF_V = np.vectorize(math.erf)


def sesam_alpha_e(n_O: np.ndarray, T_amb: np.ndarray, K_ads: float = 3.0e6) -> np.ndarray:
    p_o = np.maximum(0.0, n_O) * KB * np.maximum(150.0, T_amb)
    return 0.70 + 0.28 * (K_ads * p_o) / (1.0 + K_ads * p_o)


def sentman_sphere(s: np.ndarray, vr_v: np.ndarray) -> np.ndarray:
    s2 = s * s
    return ((2.0 * s2 + 1.0) / (math.sqrt(math.pi) * s**3) * np.exp(-s2)
            + (4.0 * s**4 + 4.0 * s2 - 1.0) / (2.0 * s**4) * ERF_V(s)
            + (2.0 * math.sqrt(math.pi) / (3.0 * s)) * vr_v)


def _sentman_elem(s: np.ndarray, sg: float, vr_v: np.ndarray) -> np.ndarray:
    su = s * sg
    return ((2.0 / (math.sqrt(math.pi) * s)) * np.exp(-su * su)
            + 2.0 * sg * (1.0 + 0.5 / (s * s)) * ERF_V(su)
            + math.sqrt(math.pi) * vr_v * sg * sg)


def sentman_plate_tumble(s: np.ndarray, vr_v: np.ndarray) -> np.ndarray:
    u = np.linspace(0.04, 0.96, 12)
    return sum(_sentman_elem(s, float(sg), vr_v) for sg in u) / (0.5 * len(u))


def sentman_cyl_perp(s: np.ndarray, vr_v: np.ndarray) -> np.ndarray:
    phi = np.linspace(0.04, math.pi / 2.0 - 0.04, 12)
    return sum(_sentman_elem(s, math.cos(float(p)), vr_v) for p in phi) * (math.pi / (2.0 * len(phi)))


def knudsen_bridge(cd_fm: np.ndarray, cd_cont: float, n_tot: np.ndarray, L_char: float) -> np.ndarray:
    lam = 1.0 / (math.sqrt(2.0) * math.pi * (3.7e-10) ** 2 * np.maximum(1e6, n_tot))
    kn = lam / max(0.05, L_char)
    return cd_cont + (cd_fm - cd_cont) / (1.0 + (0.5 / np.maximum(1e-6, kn)) ** 0.8)


def compute_physical_cd(out: np.ndarray, v_rel: np.ndarray, shape: str, L_char: float) -> np.ndarray:
    n_sp = np.maximum(0.0, out[:, 1:8])
    n_tot = np.maximum(1.0, np.sum(n_sp, axis=1))
    m_avg = (np.sum(n_sp * SPECIES_MASS_AMU[None, :], axis=1) / n_tot) * AMU
    T_amb = np.maximum(150.0, out[:, 10])
    s = v_rel / np.sqrt(2.0 * KB * T_amb / m_avg)
    alpha = sesam_alpha_e(out[:, 3], T_amb)
    T_kin = (m_avg * v_rel * v_rel) / (3.0 * KB)
    vr_v = np.sqrt(np.maximum(1e-4, (T_kin * (1.0 - alpha) + alpha * T_WALL_K) / T_kin))
    if shape == 'sphere':
        cd_fm, cd_c = sentman_sphere(s, vr_v), 0.92
    elif shape == 'plate_tumble':
        cd_fm, cd_c = sentman_plate_tumble(s, vr_v), 1.15
    elif shape == 'cyl_tumble':
        cd_fm = 0.85 * sentman_cyl_perp(s, vr_v) + 0.15 * sentman_plate_tumble(s, vr_v)
        cd_c = 1.15
    else:
        raise ValueError(f'unknown shape: {shape}')
    return knudsen_bridge(cd_fm, cd_c, n_tot, L_char)


def _msis_orbit_sample(dt, a_km, e, inc_deg, raan_deg, argp_deg, sw, n_pts=16):
    import pymsis
    inc, raan, argp, gmst = math.radians(inc_deg), math.radians(raan_deg), math.radians(argp_deg), m.gmst_rad(dt)
    E = np.linspace(0.0, math.tau, n_pts, endpoint=False)
    cosE, sinE = np.cos(E), np.sin(E)
    om = 1.0 - e * cosE
    r_km = a_km * om
    sq = math.sqrt(max(1e-12, 1.0 - e * e))
    cos_nu, sin_nu = (cosE - e) / om, (sq * sinE) / om
    u = argp + np.arctan2(sin_nu, cos_nu)
    sin_lat = math.sin(inc) * np.sin(u)
    lat_deg = np.degrees(np.arcsin(np.clip(sin_lat, -1.0, 1.0)))
    x_eci = np.cos(raan) * np.cos(u) - np.sin(raan) * np.sin(u) * math.cos(inc)
    y_eci = np.sin(raan) * np.cos(u) + np.cos(raan) * np.sin(u) * math.cos(inc)
    lon_deg = (np.degrees(np.arctan2(y_eci, x_eci) - gmst) + 180.0) % 360.0 - 180.0
    alt_km = np.maximum(80.0, r_km - m.RE_KM * (1.0 - 0.00335281 * (sin_lat ** 2)))

    f107, f107a, ap_vec = sw.msis_inputs(dt)
    dates = np.array([np.datetime64(dt.replace(tzinfo=None))] * n_pts)
    out = pymsis.calculate(
        dates, lon_deg, lat_deg, alt_km,
        np.full(n_pts, f107), np.full(n_pts, f107a),
        np.tile(np.array(ap_vec, dtype=float), (n_pts, 1)), version=2.1,
    )
    v_km_s = np.sqrt(m.MU_KM3_S2 * (2.0 / r_km - 1.0 / a_km))
    h_ang = math.sqrt(m.MU_KM3_S2 * a_km * max(1e-12, 1.0 - e * e))
    corot = np.maximum(0.85, 1.0 - (m.OMEGA_EARTH_RAD_S * h_ang * math.cos(inc)) / (v_km_s ** 2))
    v_rel = v_km_s * corot * 1000.0
    w = om / np.sum(om)
    return out, v_km_s, v_rel, cos_nu, w, float(np.mean(ap_vec[1:5]))


def precompute_intervals(recs, sw, shape: str, L_char: float, filter_pos: bool = False) -> list[dict]:
    ivs = []
    for r1, r2 in zip(recs[:-1], recs[1:]):
        dt_d = (r2['epoch'] - r1['epoch']).total_seconds() / m.SEC_PER_DAY
        if dt_d < 0.25:
            continue
        a1, a2 = m.mean_motion_to_a(r1['mean_motion']), m.mean_motion_to_a(r2['mean_motion'])
        da_obs = a2 - a1
        if filter_pos and da_obs >= 0.0:
            continue
        n_sub = max(2, int(math.ceil(dt_d * 4)))
        draan = ((r2['raan'] - r1['raan'] + 180.0) % 360.0) - 180.0
        dargp = ((r2['arg_perigee'] - r1['arg_perigee'] + 180.0) % 360.0) - 180.0
        sub_fix, sub_phy, sub_ap, cds = [], [], [], []
        for k in range(n_sub):
            frac = (k + 0.5) / n_sub
            dt = r1['epoch'] + timedelta(days=dt_d * frac)
            a_km = a1 + (a2 - a1) * frac
            e = r1['eccentricity'] + (r2['eccentricity'] - r1['eccentricity']) * frac
            out, v_km_s, v_rel, _, w, ap_eff = _msis_orbit_sample(
                dt, a_km, e, 0.5 * (r1['inclination'] + r2['inclination']),
                (r1['raan'] + draan * frac) % 360.0, (r1['arg_perigee'] + dargp * frac) % 360.0, sw, n_pts=12,
            )
            cd_phy = compute_physical_cd(out, v_rel, shape, L_char)
            cds.append(float(np.mean(cd_phy)))
            fac = -(2.0 * a_km**2 * v_km_s / m.MU_KM3_S2) * 0.5e-3 * out[:, 0] * (v_rel ** 2)
            step = m.SEC_PER_DAY * (dt_d / n_sub)
            sub_fix.append(float(np.sum(w * fac * 2.2)) * step)
            sub_phy.append(float(np.sum(w * fac * cd_phy)) * step)
            sub_ap.append(ap_eff)
        hp_mid = 0.5 * (a1 * (1.0 - r1['eccentricity']) + a2 * (1.0 - r2['eccentricity'])) - m.RE_KM
        ivs.append({
            't1': r1['epoch'], 't2': r2['epoch'], 'hp_km': hp_mid, 'da_obs': da_obs,
            'cd_mean': float(np.mean(cds)),
            'sub_fix': np.array(sub_fix), 'sub_phy': np.array(sub_phy), 'sub_ap': np.array(sub_ap),
        })
    return ivs


def _pack_subs(ivs: list[dict], use_phy: bool):
    key = 'sub_phy' if use_phy else 'sub_fix'
    da_obs = np.array([x['da_obs'] for x in ivs])
    subs = np.concatenate([x[key] for x in ivs])
    aps = np.concatenate([x['sub_ap'] for x in ivs])
    offsets = np.cumsum([0] + [len(x[key]) for x in ivs[:-1]])
    dp0 = np.add.reduceat(subs, offsets)
    return da_obs, subs, (aps - 10.0) / 100.0, offsets, dp0


def eval_ll_vec(da_obs, subs, ap_scaled, offsets, dp0, am: float, sa: float, sf: float, gamma: float) -> float:
    pred = am * (dp0 if gamma == 0.0 else np.add.reduceat(subs * np.exp(gamma * ap_scaled), offsets))
    var = 2.0 * sa * sa + (sf * pred) ** 2
    return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))


def fit_cd_suite(ivs: list[dict], use_phy: bool, free_gamma: bool = False) -> dict:
    n = len(ivs)
    da_obs, subs, ap_sc, offsets, dp0 = _pack_subs(ivs, use_phy)
    am0 = float(np.sum(da_obs) / np.sum(dp0))
    hps = np.array([x['hp_km'] for x in ivs])
    hp_med = float(np.median(hps))

    if not free_gamma:
        def lp(th):
            am, lsa, lsf = th
            if not (1e-4 < am < 5.0 and -5.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
                return -np.inf
            return eval_ll_vec(da_obs, subs, ap_sc, offsets, dp0, am, math.exp(lsa), math.exp(lsf), 0.0)
        s, l, _ = g.run_mh(lp, [am0, math.log(0.35), math.log(0.12)], [am0 * 0.04, 0.15, 0.15], 14000, 3500, 42)
        bic = round(float(3 * math.log(n) - 2.0 * np.max(l)), 2)

        def lp_beta(th):
            am, beta, lsa, lsf = th
            if not (1e-4 < am < 5.0 and -2.0 < beta < 2.0 and -5.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
                return -np.inf
            sa, sf = math.exp(lsa), math.exp(lsf)
            pred = am * np.exp(beta * (hps - hp_med) / 100.0) * dp0
            var = 2.0 * sa * sa + (sf * pred) ** 2
            return float(-0.5 * np.sum(np.log(2.0 * math.pi * var) + ((da_obs - pred) ** 2) / var))
        sb, _, _ = g.run_mh(lp_beta, [am0, 0.0, math.log(0.35), math.log(0.12)], [am0 * 0.04, 0.12, 0.15, 0.15], 12000, 3000, 42)
        cds = [x['cd_mean'] for x in ivs] if use_phy else [2.2]
        return {
            'cd_range': [round(min(cds), 3), round(max(cds), 3)],
            'Am_median_m2_kg': round(float(np.median(s[:, 0])), 5),
            'sigma_a_km': round(float(np.median(np.exp(s[:, 1]))), 3),
            'sigma_f_frac': round(float(np.median(np.exp(s[:, 2]))), 4),
            'bic': bic,
            'beta_res_per_100km': round(float(np.median(sb[:, 1])), 3),
        }

    def lp_g(th):
        am, gam, lsa, lsf = th
        if not (1e-4 < am < 5.0 and -1.0 < gam < 1.5 and -5.0 < lsa < 1.5 and -4.5 < lsf < 0.5):
            return -np.inf
        return eval_ll_vec(da_obs, subs, ap_sc, offsets, dp0, am, math.exp(lsa), math.exp(lsf), gam)
    s, l, _ = g.run_mh(lp_g, [am0, 0.15, math.log(0.35), math.log(0.12)], [am0 * 0.04, 0.08, 0.15, 0.15], 14000, 3500, 42)
    return {
        'Am_median_m2_kg': round(float(np.median(s[:, 0])), 5),
        'gamma_median': round(float(np.median(s[:, 1])), 3),
        'gamma_ci90': [round(float(np.percentile(s[:, 1], 5)), 3), round(float(np.percentile(s[:, 1], 95)), 3)],
        'sigma_f_frac': round(float(np.median(np.exp(s[:, 3]))), 4),
        'bic': round(float(4 * math.log(n) - 2.0 * np.max(l)), 2),
    }


def propagate_physical(orig: dict, sw: m.SpaceWeather1963, Am: float, shape: str, L_char: float,
                       fixed_cd: float | None = None, max_days: float = 20.0) -> tuple[str | None, float]:
    t = orig['epoch']
    a = m.mean_motion_to_a(orig['mean_motion'])
    e, inc, raan, argp = orig['eccentricity'], orig['inclination'], orig['raan'], orig['arg_perigee']
    elapsed, cd_last = 0.0, 2.2
    while elapsed < max_days:
        hp = a * (1.0 - e) - m.RE_KM
        if hp <= 120.0:
            return t.strftime('%Y-%m-%dT%H:%MZ'), round(cd_last, 2)
        step = 0.25 if hp > 200.0 else (0.1 if hp > 160.0 else 0.02)
        def rates(dt_v, a_v, e_v, r_v, w_v):
            out, v_km_s, v_rel, cos_nu, wt, _ = _msis_orbit_sample(dt_v, a_v, e_v, inc, r_v, w_v, sw, n_pts=24)
            cd = np.full(24, fixed_cd) if fixed_cd is not None else compute_physical_cd(out, v_rel, shape, L_char)
            ad = 0.5e-3 * out[:, 0] * cd * Am * (v_rel ** 2)
            da = float(np.sum(wt * (-(2.0 * a_v**2 * v_km_s / m.MU_KM3_S2) * ad))) * m.SEC_PER_DAY
            de = float(np.sum(wt * (-(2.0 * (e_v + cos_nu) / v_km_s) * ad))) * m.SEC_PER_DAY
            return da, de, float(np.mean(cd))
        da1, de1, _ = rates(t, a, e, raan, argp)
        dr1, dw1 = m.j2_rates_deg_day(a, e, inc)
        a_m = max(m.RE_KM + 80.0, a + 0.5 * step * da1)
        e_m = max(1e-5, min(0.9, e + 0.5 * step * de1))
        da2, de2, cd2 = rates(t + timedelta(days=0.5 * step), a_m, e_m,
                              (raan + 0.5 * step * dr1) % 360.0, (argp + 0.5 * step * dw1) % 360.0)
        dr2, dw2 = m.j2_rates_deg_day(a_m, e_m, inc)
        a_new, e_new = a + step * da2, max(1e-5, min(0.9, e + step * de2))
        hp_new = a_new * (1.0 - e_new) - m.RE_KM
        cd_last = cd2
        if hp_new <= 120.0:
            frac = (hp - 120.0) / max(1e-9, hp - hp_new)
            t_end = t + timedelta(days=step * frac)
            return t_end.strftime('%Y-%m-%dT%H:%MZ'), round(cd2, 2)
        t, a, e = t + timedelta(days=step), a_new, e_new
        raan, argp = (raan + step * dr2) % 360.0, (argp + step * dw2) % 360.0
        elapsed += step
    return None, round(cd_last, 2)


def engineering_priors_summary(am_637_phys: float) -> dict:
    D = 1.524
    a637 = []
    for L in (6.0, 7.1, 7.6):
        A_tumble = (math.pi * D * L + 0.5 * math.pi * D * D) / 4.0
        A_perp = D * L
        A_axial = 0.25 * math.pi * D * D
        cd_axial = 2.0 + (4.0 / (math.sqrt(math.pi) * 9.0)) * (L / D)
        a637.append({
            'length_m': L,
            'mass_uniform_tumbling_kg': round(A_tumble / am_637_phys, 1),
            'mass_gravity_gradient_kg': round(A_perp / am_637_phys, 1),
            'mass_axial_flow_aligned_kg': round((cd_axial * A_axial) / (am_637_phys * 2.28), 1),
        })
    m528 = []
    for mat, rho in (('Mg_HK31A', 1780), ('Composite_FRP', 1800), ('Al_2024', 2700), ('Ti_6Al_4V', 4430), ('SS_304', 7850)):
        m528.append({
            'material': mat, 'density_kg_m3': rho,
            'plate_t_mm_fixed_Cd22': round(2.2 / (2.0 * rho * 0.2361) * 1000.0, 2),
            'plate_t_mm_phys_Cd248': round(2.48 / (2.0 * rho * 0.2361) * 1000.0, 2),
            'shell_t_mm_fixed_Cd22': round(2.2 / (4.0 * rho * 0.2361) * 1000.0, 2),
            'shell_t_mm_phys_Cd210': round(2.10 / (4.0 * rho * 0.2361) * 1000.0, 2),
        })
    return {'norad_637_agena_d_dry_floor_kg': 670.0, 'norad_637_attitude_mass_map': a637,
            'norad_528_thickness_map': m528}


def run_analysis(parquet_path: Path, gfz_path: Path) -> dict:
    sw = m.SpaceWeather1963(gfz_path)
    by_id = m.load_parquet_by_id(parquet_path)
    sep1, nov15 = datetime(1963, 9, 1, tzinfo=UTC), datetime(1963, 11, 15, tzinfo=UTC)
    cutoff = datetime(1963, 10, 28, tzinfo=UTC)

    ivs637 = precompute_intervals(by_id[637], sw, 'cyl_tumble', 3.5, filter_pos=True)
    ivs528_pl = precompute_intervals(by_id[528], sw, 'plate_tumble', 0.8)
    ivs528_sp = precompute_intervals(by_id[528], sw, 'sphere', 0.8)
    ivs81 = precompute_intervals([r for r in by_id[81] if sep1 <= r['epoch'] <= nov15], sw, 'sphere', 3.66)
    ivs529 = precompute_intervals([r for r in by_id[529] if sep1 <= r['epoch'] <= nov15], sw, 'sphere', 0.8)

    c637_fix, c637_phy = fit_cd_suite(ivs637, False), fit_cd_suite(ivs637, True)
    c528_fix = fit_cd_suite(ivs528_sp, False)
    c528_pl, c528_sp = fit_cd_suite(ivs528_pl, True), fit_cd_suite(ivs528_sp, True)

    t637_fix, _ = propagate_physical(by_id[637][-1], sw, c637_fix['Am_median_m2_kg'], 'cyl_tumble', 3.5, fixed_cd=2.2)
    t637_phy, cd637_end = propagate_physical(by_id[637][-1], sw, c637_phy['Am_median_m2_kg'], 'cyl_tumble', 3.5)
    t637_phy_sm, cd637_sm = propagate_physical(by_id[637][-1], sw, c637_phy['Am_median_m2_kg'], 'cyl_tumble', 1.52)
    t528_fix, _ = propagate_physical(by_id[528][-1], sw, c528_fix['Am_median_m2_kg'], 'sphere', 0.8, fixed_cd=2.2)
    t528_pl, cd528_pl = propagate_physical(by_id[528][-1], sw, c528_pl['Am_median_m2_kg'], 'plate_tumble', 0.8)
    t528_sp, cd528_sp = propagate_physical(by_id[528][-1], sw, c528_sp['Am_median_m2_kg'], 'sphere', 0.8)

    def dhours(a_s, b_s):
        ta = datetime.strptime(a_s, '%Y-%m-%dT%H:%MZ').replace(tzinfo=UTC)
        tb = datetime.strptime(b_s, '%Y-%m-%dT%H:%MZ').replace(tzinfo=UTC)
        return round((ta - tb).total_seconds() / 3600.0, 2)

    # Storm-gamma individual tests
    storm_indiv = {}
    for name, ivs in (('81_Exp9', ivs81), ('529', ivs529), ('637', ivs637), ('528', ivs528_sp)):
        r0, r1 = fit_cd_suite(ivs, True, False), fit_cd_suite(ivs, True, True)
        storm_indiv[name] = {
            'n_intervals': len(ivs), 'bic_gamma0': r0['bic'], 'bic_free_gamma': r1['bic'],
            'delta_bic': round(r1['bic'] - r0['bic'], 2), 'sf_gamma0': r0['sigma_f_frac'],
            'sf_free_gamma': r1['sigma_f_frac'], 'gamma_median': r1['gamma_median'], 'gamma_ci90': r1['gamma_ci90'],
        }

    # Strict pre-Oct28 train -> post-Oct27 out-of-sample holdout
    tr_sets = {k: [x for x in v if x['t2'] < cutoff] for k, v in (('81_Exp9', ivs81), ('529', ivs529), ('637', ivs637))}
    te_sets = {k: [x for x in v if x['t2'] >= cutoff] for k, v in (('81_Exp9', ivs81), ('529', ivs529), ('637', ivs637))}
    packed_tr = {k: _pack_subs(v, True) for k, v in tr_sets.items()}
    best_g, best_ll = 0.0, -1e18
    for gam in np.linspace(-0.20, 0.80, 41):
        tot = 0.0
        for da_o, subs, ap_s, offs, dp0 in packed_tr.values():
            dp = dp0 if gam == 0.0 else np.add.reduceat(subs * np.exp(gam * ap_s), offs)
            tot += eval_ll_vec(da_o, subs, ap_s, offs, dp0, float(np.sum(da_o) / np.sum(dp)), 0.35, 0.12, float(gam))
        if tot > best_ll:
            best_ll, best_g = tot, round(float(gam), 3)

    oos = {}
    for k in ('81_Exp9', '529', '637'):
        tr, te = tr_sets[k], te_sets[k]
        da_o, subs, ap_s, offs, dp0 = packed_tr[k]
        row = {'n_train': len(tr), 'n_test': len(te)}
        for lbl, gam in (('gamma0', 0.0), ('joint_gamma', best_g)):
            dp = dp0 if gam == 0.0 else np.add.reduceat(subs * np.exp(gam * ap_s), offs)
            am = float(np.sum(da_o) / np.sum(dp))
            errs = [(iv['da_obs'] - am * float(np.sum(iv['sub_phy'] * np.exp(gam * (iv['sub_ap'] - 10.0) / 100.0)))) / abs(iv['da_obs']) for iv in te]
            row[f'rel_rmse_{lbl}'] = round(float(np.sqrt(np.mean(np.array(errs) ** 2))), 3)
            row[f'mean_bias_{lbl}'] = round(float(np.mean(errs)), 3)
        oos[k] = row

    return {
        'experiment_id': 'C241-PHYSICAL-CD-PRIORS-20261124',
        'verification_status': 'EXPLORATORY_PHYSICAL_CD_AND_NEGATIVE_STORM_GAMMA_CONTROL',
        'provenance': {'tle_parquet_sha256': m.PARQUET_SHA256, 'gfz_space_weather_sha256': sw.sha256,
                       'atmosphere': 'NRLMSIS-2.1 (pymsis 0.13.0)'},
        'epistemic_contract': {
            'historical_event_time_utc': None, 'mass_528_identified': False,
            'storm_gamma_promoted': False, 'impact_geography': None,
        },
        'cd_regime_comparison': {
            '637_fixed_Cd22': {**c637_fix, 'reentry_utc': t637_fix, 'delta_hours_vs_fixed': 0.0},
            '637_phys_cyl_L35': {**c637_phy, 'reentry_utc': t637_phy, 'delta_hours_vs_fixed': dhours(t637_phy, t637_fix), 'cd_at_120km': cd637_end},
            '637_phys_cyl_L152': {'reentry_utc': t637_phy_sm, 'delta_hours_vs_fixed': dhours(t637_phy_sm, t637_fix), 'cd_at_120km': cd637_sm},
            '528_fixed_Cd22': {**c528_fix, 'reentry_utc': t528_fix, 'delta_hours_vs_fixed': 0.0},
            '528_phys_plate_tumble': {**c528_pl, 'reentry_utc': t528_pl, 'delta_hours_vs_fixed': dhours(t528_pl, t528_fix), 'cd_at_120km': cd528_pl},
            '528_phys_sphere': {**c528_sp, 'reentry_utc': t528_sp, 'delta_hours_vs_fixed': dhours(t528_sp, t528_fix), 'cd_at_120km': cd528_sp},
        },
        'engineering_priors': engineering_priors_summary(c637_phy['Am_median_m2_kg']),
        'storm_gamma_negative_control': {
            'individual_fits': storm_indiv,
            'joint_pre_oct28_mle_gamma': best_g,
            'post_oct27_out_of_sample': oos,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description='Run C241 physical Cd, priors, and storm-gamma audit.')
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
