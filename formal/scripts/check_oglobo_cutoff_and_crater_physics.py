#!/usr/bin/env python3
"""Reproducible check of O Globo 1963-11-08 temporal cutoff and 4 m crater energy bound."""
from __future__ import annotations
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "research/constraints/oglobo_cutoff_and_crater_physics.json"

G = 9.80665
RHO_AIR = 1.225
RHO_SOIL = 1600.0
Y_LOOSE_SAND = 50_000.0  # Pa (50 kPa, conservative loose coastal sand)


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(f"EXP-OGLOBO-CUTOFF-CRATER-20261119: {msg}")


def min_hemisphere_work_kj(depth_m: float, y_pa: float, rho_soil: float = RHO_SOIL) -> float:
    w_strength = (2.0 / 3.0) * math.pi * (depth_m ** 3) * y_pa
    w_overburden = (math.pi / 4.0) * rho_soil * G * (depth_m ** 4)
    return (w_strength + w_overburden) / 1000.0


def solve_max_depth_m(ek_kj: float, y_pa: float, rho_soil: float = RHO_SOIL) -> float:
    lo, hi = 0.0, 20.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if min_hemisphere_work_kj(mid, y_pa, rho_soil) < ek_kj:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    require(data["id"] == "EXP-OGLOBO-CUTOFF-CRATER-20261119", "id")

    # 1. Verify temporal cutoff arithmetic
    tc = data["temporal_cutoff"]
    require(tc["afternoon_cutoff_utc_min"] == 1260, "afternoon cutoff 21:00 UTC")
    require(tc["norad_528_desc_pass_utc_min"] == 1425, "528 evening pass 23:45 UTC")
    require(tc["norad_528_asc_pass_utc_min"] == 694, "528 morning pass 11:34 UTC")
    require(tc["pass_margin_min"] == 90, "margin 90 min")
    require(tc["afternoon_cutoff_utc_min"] + tc["pass_margin_min"] <= tc["norad_528_desc_pass_utc_min"],
            "evening pass must be strictly after afternoon cutoff + margin")
    require(tc["norad_528_asc_pass_utc_min"] < tc["afternoon_cutoff_utc_min"],
            "morning pass remains before afternoon cutoff")

    # 2. Verify crater work-energy bounds
    w_overburden_4m = min_hemisphere_work_kj(4.0, 0.0)
    w_soft_sand_4m = min_hemisphere_work_kj(4.0, Y_LOOSE_SAND)
    require(abs(w_overburden_4m - 3154.7) < 1.0, f"overburden 4m mismatch: {w_overburden_4m}")
    require(abs(w_soft_sand_4m - 9856.8) < 1.0, f"soft sand 4m mismatch: {w_soft_sand_4m}")

    cb = data["crater_energy_bound"]
    require(abs(cb["min_work_4m_overburden_only_kj"] - round(w_overburden_4m, 1)) < 0.2, "json overburden")
    require(abs(cb["min_work_4m_soft_sand_50kpa_kj"] - round(w_soft_sand_4m, 1)) < 0.2, "json soft sand")

    for case in cb["cases"]:
        m = case["mass_kg"]
        d_obj = case["diameter_m"]
        cd = case["cd"]
        area = math.pi * (0.5 * d_obj) ** 2
        beta = m / (cd * area)
        vt = math.sqrt(2.0 * G * beta / RHO_AIR)
        ek_kj = 0.5 * m * (vt ** 2) / 1000.0
        d_max_50kpa = solve_max_depth_m(ek_kj, Y_LOOSE_SAND)
        d_max_y0 = solve_max_depth_m(ek_kj, 0.0)
        require(abs(case["terminal_velocity_m_s"] - round(vt, 1)) <= 0.2, f"vt mismatch {case['name']}")
        require(abs(case["kinetic_energy_kj"] - round(ek_kj, 1)) <= 2.0, f"ek mismatch {case['name']}")
        require(abs(case["max_depth_soft_sand_m"] - round(d_max_50kpa, 2)) <= 0.02, f"d_50kpa {case['name']}")
        require(abs(case["max_depth_frictionless_y0_m"] - round(d_max_y0, 2)) <= 0.02, f"d_y0 {case['name']}")
        require(d_max_50kpa < 4.0, f"expected < 4m soft sand for {case['name']}")

    print(
        f"EXP-OGLOBO-CUTOFF-CRATER-20261119 PASS | "
        f"528_evening=EXCLUDED_CONDITIONAL | "
        f"W_4m(Y=0)={w_overburden_4m:.1f} kJ | W_4m(50kPa)={w_soft_sand_4m:.1f} kJ | "
        f"all {len(cb['cases'])} Agena/globe cases < 4.0 m"
    )


if __name__ == "__main__":
    main()
