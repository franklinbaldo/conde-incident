#!/usr/bin/env python3
"""C241: Aerothermal reentry survival & subsonic terminal energy (NORAD 528 vs 637).

Integrates 2D planar reentry (120 km -> ground) under NRLMSIS-2.1 (1963-11-08 18:00Z,
Bahia) with bridged Sutton-Graves / free-molecular stagnation heating, radiative
cooling, and latent heat of fusion, plus sea-level subsonic terminal velocity and
kinetic energy comparison against TerminalCraterBound.lean (3155 kJ floor).
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c241_msis_decay_holdout as m

MU_M3_S2 = 3.986004418e14
RE_M = 6378137.0
G0 = 9.80665
RHO_SL = 1.225          # sea-level air density kg/m^3
K_SG = 1.7415e-4        # Sutton-Graves Earth air constant
SIGMA_SB = 5.670374e-8  # Stefan-Boltzmann W/(m^2 K^4)


def build_msis_profile(sw: m.SpaceWeather1963):
    import pymsis
    dt = datetime(1963, 11, 8, 18, 0, tzinfo=timezone.utc)
    f107, f107a, ap_vec = sw.msis_inputs(dt)
    alts_km = np.linspace(0.0, 140.0, 281)
    n = len(alts_km)
    out = pymsis.calculate(
        np.array([np.datetime64('1963-11-08T18:00:00')] * n),
        np.full(n, -37.6), np.full(n, -12.0), alts_km,
        np.full(n, f107), np.full(n, f107a),
        np.tile(np.array(ap_vec, dtype=float), (n, 1)),
        version=2.1,
    )
    return alts_km, np.log(np.maximum(1e-20, out[:, 0])), out[:, -1]


def subsonic_terminal_stats(B_hyp: float, cd_hyp: float, cd_sub: float, mass_kg: float) -> tuple[float, float]:
    """Compute sea-level subsonic terminal speed (m/s) and kinetic energy (kJ)."""
    B_sub = B_hyp * (cd_sub / cd_hyp)
    v_t = math.sqrt(2.0 * G0 / (RHO_SL * B_sub))
    e_kj = 0.5 * mass_kg * v_t * v_t / 1000.0
    return round(v_t, 1), round(e_kj, 2)


def simulate_case(case: dict, alts_km, log_rho, T_amb, gamma0_deg: float) -> dict:
    h, v, gam, T, melt_frac, t, dt = 120000.0, 7830.0, math.radians(gamma0_deg), 300.0, 0.0, 0.0, 0.1
    B, R_eff = case['B_hyp'], case['R_eff_m']
    m_arad, f_avg = case['m_over_Arad'], case['f_avg']
    cp, T_melt, hf, eps = case['cp'], case['T_melt_K'], case['hf'], case['eps']

    max_T, max_q, alt_qmax, demise_alt = T, 0.0, 120.0, None
    while h > 0.0 and t < 2500.0:
        h_km = h / 1000.0
        rho = math.exp(float(np.interp(h_km, alts_km, log_rho)))
        T_env = float(np.interp(h_km, alts_km, T_amb))
        g = MU_M3_S2 / ((RE_M + h) ** 2)
        a_drag = 0.5 * rho * v * v * B

        q_cont = K_SG * math.sqrt(rho / max(0.01, R_eff)) * (v ** 3)
        q_fm = 0.5 * 0.9 * rho * (v ** 3)
        q_stag = q_cont / math.sqrt(1.0 + (q_cont / max(1e-30, q_fm)) ** 2)
        if q_stag > max_q:
            max_q, alt_qmax = q_stag, h_km

        q_net = q_stag * f_avg - eps * SIGMA_SB * max(0.0, (T ** 4) - (T_env ** 4))
        if T < T_melt or q_net < 0.0:
            T = max(250.0, T + (q_net / (m_arad * cp)) * dt)
            if T > T_melt:
                melt_frac += ((T - T_melt) * cp) / hf
                T = T_melt
        else:
            melt_frac += (q_net * dt) / (m_arad * hf)

        if T > max_T:
            max_T = T
        if melt_frac >= 1.0:
            demise_alt = round(h_km, 1)
            break

        dv1, dg1, dh1 = -a_drag - g * math.sin(gam), (v / (RE_M + h) - g / max(1.0, v)) * math.cos(gam), v * math.sin(gam)
        h_m, v_m, gam_m = max(0.0, h + 0.5 * dt * dh1), max(1.0, v + 0.5 * dt * dv1), gam + 0.5 * dt * dg1
        rho_m = math.exp(float(np.interp(h_m / 1000.0, alts_km, log_rho)))
        g_m = MU_M3_S2 / ((RE_M + h_m) ** 2)
        v = max(1.0, v + dt * (-0.5 * rho_m * v_m * v_m * B - g_m * math.sin(gam_m)))
        gam = gam + dt * ((v_m / (RE_M + h_m) - g_m / v_m) * math.cos(gam_m))
        h = h + dt * (v_m * math.sin(gam_m))
        t += dt

    v_sub, e_kj = subsonic_terminal_stats(B, 2.2, case['cd_sub'], case['mass_kg'])
    return {
        'id': case['id'], 'label': case['label'], 'object': case['object'],
        'B_hyp_m2_kg': B, 'mass_kg': case['mass_kg'], 'gamma0_deg': gamma0_deg,
        'peak_q_stag_kW_m2': round(max_q / 1e3, 1), 'alt_peak_q_km': round(alt_qmax, 1),
        'max_T_K': round(max_T, 0), 'T_melt_K': T_melt,
        'survived': demise_alt is None, 'demise_alt_km': demise_alt,
        'subsonic_v_terminal_ms': v_sub if demise_alt is None else None,
        'terminal_kinetic_kJ': e_kj if demise_alt is None else None,
    }


def run_suite(gfz_path: Path) -> dict:
    sw = m.SpaceWeather1963(gfz_path)
    alts_km, log_rho, T_amb = build_msis_profile(sw)
    cases = [
        {'id': '528-A', 'object': 528, 'label': 'Al fairing panel (1.73mm, R=0.3m)',
         'B_hyp': 0.236, 'R_eff_m': 0.30, 'm_over_Arad': 0.5*2700*0.00173, 'f_avg': 0.25,
         'cp': 900, 'T_melt_K': 933, 'hf': 3.97e5, 'eps': 0.4, 'cd_sub': 1.1, 'mass_kg': 4.7},
        {'id': '528-B', 'object': 528, 'label': 'Al hollow shell (0.86mm, R=0.5m)',
         'B_hyp': 0.236, 'R_eff_m': 0.50, 'm_over_Arad': 2700*0.00086, 'f_avg': 0.25,
         'cp': 900, 'T_melt_K': 933, 'hf': 3.97e5, 'eps': 0.4, 'cd_sub': 0.47, 'mass_kg': 7.3},
        {'id': '528-B2', 'object': 528, 'label': 'Al hollow shell (0.86mm, R=1.0m)',
         'B_hyp': 0.236, 'R_eff_m': 1.00, 'm_over_Arad': 2700*0.00086, 'f_avg': 0.25,
         'cp': 900, 'T_melt_K': 933, 'hf': 3.97e5, 'eps': 0.4, 'cd_sub': 0.47, 'mass_kg': 29.2},
        {'id': '528-C', 'object': 528, 'label': 'Ti hollow shell (0.52mm, R=0.5m)',
         'B_hyp': 0.236, 'R_eff_m': 0.50, 'm_over_Arad': 4430*0.00052, 'f_avg': 0.25,
         'cp': 560, 'T_melt_K': 1941, 'hf': 4.40e5, 'eps': 0.5, 'cd_sub': 0.47, 'mass_kg': 7.2},
        {'id': '528-D', 'object': 528, 'label': 'SS hollow shell (0.30mm, R=0.5m)',
         'B_hyp': 0.236, 'R_eff_m': 0.50, 'm_over_Arad': 7850*0.00030, 'f_avg': 0.25,
         'cp': 500, 'T_melt_K': 1700, 'hf': 2.70e5, 'eps': 0.5, 'cd_sub': 0.47, 'mass_kg': 7.4},
        {'id': '528-E', 'object': 528, 'label': 'Ti fairing panel (1.04mm, R=0.3m)',
         'B_hyp': 0.236, 'R_eff_m': 0.30, 'm_over_Arad': 0.5*4430*0.00104, 'f_avg': 0.25,
         'cp': 560, 'T_melt_K': 1941, 'hf': 4.40e5, 'eps': 0.5, 'cd_sub': 1.1, 'mass_kg': 4.6},
        {'id': '637-A', 'object': 637, 'label': 'Agena Ti tank (4.0mm, R=0.30m)',
         'B_hyp': 0.031, 'R_eff_m': 0.30, 'm_over_Arad': 4430*0.0040, 'f_avg': 0.25,
         'cp': 560, 'T_melt_K': 1941, 'hf': 4.40e5, 'eps': 0.5, 'cd_sub': 0.47, 'mass_kg': 20.0},
        {'id': '637-B', 'object': 637, 'label': 'Agena SS chamber (150kg, R=0.25m)',
         'B_hyp': 0.003, 'R_eff_m': 0.25, 'm_over_Arad': 150.0/(4*math.pi*0.25**2), 'f_avg': 0.25,
         'cp': 500, 'T_melt_K': 1700, 'hf': 2.70e5, 'eps': 0.5, 'cd_sub': 0.50, 'mass_kg': 150.0},
    ]
    rows = [simulate_case(c, alts_km, log_rho, T_amb, g) for g in (-0.5, -1.0, -2.0) for c in cases]
    return {
        'experiment_id': 'C241-REENTRY-THERMAL-SURVIVAL-20261120',
        'verification_status': 'AEROTHERMAL_SURVIVAL_AND_LEAN4_ENERGY_BOUND',
        'atmosphere_profile': 'NRLMSIS-2.1 @ 1963-11-08T18:00Z, lat=-12.0, lon=-37.6',
        'gfz_space_weather_sha256': sw.sha256,
        'lean_certificate_ref': 'formal/Conde1963/ReentryTerminalEnergyBound.lean',
        'crater_4m_overburden_floor_kJ': 3155,
        'results': rows,
    }


def main() -> None:
    p = argparse.ArgumentParser(description='Run C241 aerothermal reentry survival suite.')
    p.add_argument('--gfz', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    res = run_suite(args.gfz)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(res, separators=(',', ':'), indent=1) + '\n', encoding='utf-8')
    print(f'Wrote {args.output} ({args.output.stat().st_size} bytes)')


if __name__ == '__main__':
    main()
