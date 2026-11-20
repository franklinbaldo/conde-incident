import Lean

/-!
Conditional work-energy upper bound for subsonic terminal-velocity crater depth.

Motivated by *O Globo* 1963-11-08 p. 1 (`C241-OGLOBO-19631108-P01`, claiming a
"buraco de quatro metros de profundidade") and Agena D physical scale (`1201 kg`
post-insertion mass for NORAD 637 / Mission 9058A with SRV recovered on 1 Sep 1963;
no armored SRV attached at November reentry).

All energies here are integer **kilojoules (`kJ`)**. Conservation of energy
requires `kineticEnergyKJ ≥ minExcavationWorkKJ` to excavate a hemispherical
crater of depth `d` against soil overburden + shear resistance (even at 100%
mechanical efficiency, zero heat/sound/deformation loss). Lean certifies only
the logical implications of these premises, not 1963 soil geotechnical assays.
-/

namespace Conde1963.TerminalCraterBound

/-- Conditional energy-deficit exclusion: if excavating a crater of target depth
requires at least `minWorkKJ` kilojoules, and the impactor's terminal kinetic
energy `kineticKJ` is strictly smaller (`kineticKJ < minWorkKJ`), then the
target crater depth cannot be excavated by that impactor. -/
theorem energy_deficit_excludes_crater_depth
    (excavated : Prop) (kineticKJ minWorkKJ : Nat)
    (hConservation : excavated → minWorkKJ ≤ kineticKJ)
    (hDeficit : kineticKJ < minWorkKJ) :
    ¬ excavated := by
  intro hExc
  have hNeed := hConservation hExc
  omega

/-- Monotonicity of work threshold: if a deeper or stronger-soil crater requires
more energy (`w1 ≤ w2`), any energy budget unable to meet `w1` is also unable
to meet `w2`. -/
theorem higher_work_threshold_preserves_deficit
    (kineticKJ w1 w2 : Nat)
    (hDef : kineticKJ < w1)
    (hMono : w1 ≤ w2) :
    kineticKJ < w2 := by
  omega

/-- Concrete scaled-integer witness (in `kJ`):
- A 300 kg, 2.0 m diameter hollow metallic globe (`Cd = 0.47`) at sea-level
  terminal velocity (`v_t ≈ 57.0 m/s`) has `E_k ≈ 488 kJ`.
- Pure gravity-overburden work alone (`Y = 0`, `rho_soil = 1600 kg/m^3`) for a
  `d = 4.0 m` hemispherical crater is `(pi/4) * 1600 * 9.80665 * 4^4 ≈ 3155 kJ`.
- With modest loose-sand resistance (`Y = 50 kPa`), total minimum work is
  `≈ 9857 kJ`.
Therefore `488 < 3155 ≤ 9857`, excluding a 4 m hemispherical crater under
conservation of energy. -/
theorem hollow_globe_cannot_excavate_4m_crater
    (excavated4m : Prop)
    (hConservation : excavated4m → 3155 ≤ 488) :
    ¬ excavated4m := by
  exact energy_deficit_excludes_crater_depth excavated4m 488 3155 hConservation (by omega)

/-- Even a dense 150 kg Agena thrust-chamber fragment (`0.5 m` dia, `Cd = 0.50`,
`v_t ≈ 156.4 m/s`, `E_k ≈ 1835 kJ`) falls strictly below the `3155 kJ` pure
gravity-overburden floor for a 4 m hemispherical crater. -/
theorem dense_agena_fragment_below_4m_overburden_floor
    (excavated4m : Prop)
    (hConservation : excavated4m → 3155 ≤ 1835) :
    ¬ excavated4m := by
  exact energy_deficit_excludes_crater_depth excavated4m 1835 3155 hConservation (by omega)

/-- Non-vacuity witness: a high-energy impactor (e.g., hypervelocity meteoroid
or massive solid projectile with `E_k = 10000 kJ`) satisfies the `9857 kJ` soft-sand
4 m excavation threshold, proving the energy predicate is satisfiable. -/
theorem high_energy_impactor_satisfies_4m_bound :
    ∃ kineticKJ : Nat, 9857 ≤ kineticKJ := by
  exact ⟨10000, by omega⟩

end Conde1963.TerminalCraterBound
