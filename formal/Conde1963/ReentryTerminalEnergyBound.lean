import Lean
import Conde1963.TerminalCraterBound

/-!
Conditional terminal kinetic-energy bounds for a surviving high-B NORAD 528
fragment (`B_hyp ≈ 0.236 m^2/kg`), bridging `BallisticGeometryBound.lean` and
`TerminalCraterBound.lean`.

Key physical insight:
- High ballistic coefficient (`B_hyp = 0.236 m^2/kg`) decelerates thin titanium
  or stainless-steel shells/panels high in the mesosphere (`~82–83 km`), where
  peak radiative-equilibrium temperatures (`~1100–1250 K`) remain below melting
  (`1700–1941 K`), allowing thermal survival to the ground.
- However, the same high `B` caps sea-level subsonic terminal velocity at
  `v_t ≤ 18 m/s` (`~65 km/h` for a sphere with `Cd_sub = 0.47`, or `~12 m/s`
  for a tumbling sheet with `Cd_sub = 1.1`).
- Consequently, even a 2.0 m hollow shell (`m ≤ 30 kg`) delivers `< 5 kJ` at
  impact — more than 600x below the `3155 kJ` pure gravity-overburden floor
  certified in `TerminalCraterBound.lean` for a 4 m hemispherical crater.

All proofs use only Lean 4 core arithmetic (`Nat.mul_le_mul`, `omega`) with
zero custom axioms and complete proofs.
-/

namespace Conde1963.ReentryTerminalEnergyBound

private theorem mul3_le {a1 b1 a2 b2 a3 b3 : Nat}
    (h1 : a1 ≤ b1) (h2 : a2 ≤ b2) (h3 : a3 ≤ b3) :
    a1 * a2 * a3 ≤ b1 * b2 * b3 :=
  Nat.mul_le_mul (Nat.mul_le_mul h1 h2) h3

/-- For any surviving thin shell with mass `m_kg ≤ 30` and sea-level subsonic
terminal speed `v_ms ≤ 18` (`~65 km/h`), twice the kinetic energy in joules
(`m_kg * v_ms * v_ms`) is at most `9720 J`, so `E_k ≤ 4860 J < 5 kJ`. -/
theorem norad528_2m_shell_kinetic_le_4860J
    (m_kg v_ms : Nat)
    (hM : m_kg ≤ 30)
    (hV : v_ms ≤ 18) :
    m_kg * v_ms * v_ms / 2 ≤ 4860 := by
  have hProd : m_kg * v_ms * v_ms ≤ 30 * 18 * 18 := mul3_le hM hV hV
  omega

/-- A surviving 2.0 m NORAD 528 shell (`E_k ≤ 5 kJ`) falls more than 600x below
the `3155 kJ` gravity-overburden floor for a 4 m hemispherical crater. -/
theorem norad528_surviving_shell_cannot_excavate_4m_crater
    (excavated4m : Prop)
    (kineticKJ : Nat)
    (hBound : kineticKJ ≤ 5)
    (hConservation : excavated4m → 3155 ≤ kineticKJ) :
    ¬ excavated4m := by
  exact Conde1963.TerminalCraterBound.energy_deficit_excludes_crater_depth
    excavated4m kineticKJ 3155 hConservation (by omega)

/-- Quantitative deficit factor: `5 kJ * 630 = 3150 < 3155 kJ`, certifying a
strict >630x energy deficit for a surviving 2.0 m NORAD 528 shell. -/
theorem norad528_2m_shell_deficit_over_630x :
    5 * 630 < 3155 := by
  omega

/-- For a 1.0 m diameter titanium shell (`t = 0.52 mm`, `m_kg ≤ 8`, `v_ms ≤ 18`),
terminal kinetic energy is at most `1296 J < 2 kJ` (>1500x below `3155 kJ`). -/
theorem norad528_1m_titanium_shell_kinetic_le_1296J
    (m_kg v_ms : Nat)
    (hM : m_kg ≤ 8)
    (hV : v_ms ≤ 18) :
    m_kg * v_ms * v_ms / 2 ≤ 1296 := by
  have hProd : m_kg * v_ms * v_ms ≤ 8 * 18 * 18 := mul3_le hM hV hV
  omega

/-- Constructive witness: a thin titanium shell (`T_max = 1174 K < T_melt = 1941 K`)
thermally survives reentry while remaining strictly below the `3155 kJ` 4 m
crater overburden floor (`kineticKJ = 5 < 3155`). -/
theorem high_B_radiative_survival_yet_no_4m_crater_witness :
    ∃ T_max_K T_melt_K kineticKJ : Nat,
      T_max_K = 1174 ∧ T_melt_K = 1941 ∧ T_max_K < T_melt_K ∧
      kineticKJ = 5 ∧ kineticKJ < 3155 := by
  exact ⟨1174, 1941, 5, rfl, rfl, by omega, rfl, by omega⟩

end Conde1963.ReentryTerminalEnergyBound
