import Lean

/-!
Exact scaled-integer ballistic-geometry bounds for NORAD 528 (`1963-003B`).

Connects the 10-month MSIS-2.1 MCMC ballistic-coefficient range
`B = Cd * <A> / m ∈ [0.180, 0.300] m^2/kg` (`B_milli ∈ [180, 300]`,
median `0.236 m^2/kg`) to three exact physical geometries under `Cd ≤ 2.60`
(`Cd_centi ≤ 260`):

1. Solid metallic sphere (`rho ≥ 2700 kg/m^3`): diameter `d_mm ≤ 8 mm`;
   any macroscopic solid metallic sphere (`d_mm ≥ 100 mm`) is excluded.
2. Thin hollow spherical shell (`B = Cd / (4 * t * rho)`): radius cancels;
   aluminum shell wall thickness `t_um ≤ 1337 um` (`1.34 mm`), and any
   thick-walled titanium/steel pressure vessel (`rho ≥ 4500`, `t_um ≥ 3000 um`)
   is excluded.
3. Uniformly tumbling thin sheet / fairing panel (Cauchy's projection theorem
   `<A> = S_total / 4 = S_0 / 2`, so `B = Cd / (2 * t * rho)`): non-vacuity
   witnesses for `1.73 mm` aluminum (`rho = 2700`) and `2.59 mm` composite/Mg
   (`rho = 1800`) match `B ≈ 0.236 m^2/kg`.

All proofs use only `Nat.mul_le_mul` and `omega` (zero custom axioms, complete proofs).
-/

namespace Conde1963.BallisticGeometryBound

private theorem mul4_le {a1 b1 a2 b2 a3 b3 a4 b4 : Nat}
    (h1 : a1 ≤ b1) (h2 : a2 ≤ b2) (h3 : a3 ≤ b3) (h4 : a4 ≤ b4) :
    a1 * a2 * a3 * a4 ≤ b1 * b2 * b3 * b4 :=
  Nat.mul_le_mul (Nat.mul_le_mul (Nat.mul_le_mul h1 h2) h3) h4

/-- Solid sphere law: `2 * B_milli * d_mm * rho ≤ 3 * Cd_centi * 10000`.
If `B_milli ≥ 180`, `rho ≥ 2700` (aluminum or denser), and `Cd_centi ≤ 260`,
then the sphere diameter cannot exceed `8 mm`. -/
theorem solid_sphere_diameter_le_8mm
    (B_milli d_mm rho Cd_centi : Nat)
    (hB : 180 ≤ B_milli)
    (hRho : 2700 ≤ rho)
    (hCd : Cd_centi ≤ 260)
    (hLaw : 2 * B_milli * d_mm * rho ≤ 3 * Cd_centi * 10000) :
    d_mm ≤ 8 := by
  by_contra hGt
  have hD : 9 ≤ d_mm := by omega
  have hLow : 2 * 180 * 9 * 2700 ≤ 2 * B_milli * d_mm * rho :=
    mul4_le (Nat.le_refl 2) hB hD hRho
  have hHigh : 3 * Cd_centi * 10000 ≤ 3 * 260 * 10000 :=
    Nat.mul_le_mul_right 10000 (Nat.mul_le_mul_left 3 hCd)
  omega

/-- Any macroscopic solid metallic sphere (`d_mm ≥ 100`, i.e., ≥ 10 cm, `rho ≥ 2700`)
is mathematically incompatible with `B_milli ≥ 180` under `Cd_centi ≤ 260`. -/
theorem macroscopic_solid_metal_sphere_excluded
    (B_milli d_mm rho Cd_centi : Nat)
    (hB : 180 ≤ B_milli)
    (hD : 100 ≤ d_mm)
    (hRho : 2700 ≤ rho)
    (hCd : Cd_centi ≤ 260)
    (hLaw : 2 * B_milli * d_mm * rho ≤ 3 * Cd_centi * 10000) :
    False := by
  have hLe8 := solid_sphere_diameter_le_8mm B_milli d_mm rho Cd_centi hB hRho hCd hLaw
  omega

/-- Thin hollow spherical shell law: `4 * B_milli * t_um * rho ≤ Cd_centi * 10000000`.
Radius `R` cancels identically. Under `B_milli ≥ 180`, `rho ≥ 2700`, `Cd_centi ≤ 260`,
wall thickness is strictly bounded by `t_um ≤ 1337` (`1.34 mm`). -/
theorem hollow_metal_shell_thickness_le_1337um
    (B_milli t_um rho Cd_centi : Nat)
    (hB : 180 ≤ B_milli)
    (hRho : 2700 ≤ rho)
    (hCd : Cd_centi ≤ 260)
    (hLaw : 4 * B_milli * t_um * rho ≤ Cd_centi * 10000000) :
    t_um ≤ 1337 := by
  by_contra hGt
  have hT : 1338 ≤ t_um := by omega
  have hLow : 4 * 180 * 1338 * 2700 ≤ 4 * B_milli * t_um * rho :=
    mul4_le (Nat.le_refl 4) hB hT hRho
  have hHigh : Cd_centi * 10000000 ≤ 260 * 10000000 :=
    Nat.mul_le_mul_right 10000000 hCd
  omega

/-- A thick-walled titanium or steel spherical vessel (`rho ≥ 4500 kg/m^3`,
wall thickness `t_um ≥ 3000 um = 3 mm`) cannot satisfy `B_milli ≥ 180` under `Cd_centi ≤ 260`. -/
theorem thick_titanium_or_steel_shell_excluded
    (B_milli t_um rho Cd_centi : Nat)
    (hB : 180 ≤ B_milli)
    (hT : 3000 ≤ t_um)
    (hRho : 4500 ≤ rho)
    (hCd : Cd_centi ≤ 260)
    (hLaw : 4 * B_milli * t_um * rho ≤ Cd_centi * 10000000) :
    False := by
  have hLow : 4 * 180 * 3000 * 4500 ≤ 4 * B_milli * t_um * rho :=
    mul4_le (Nat.le_refl 4) hB hT hRho
  have hHigh : Cd_centi * 10000000 ≤ 260 * 10000000 :=
    Nat.mul_le_mul_right 10000000 hCd
  omega

/-- Non-vacuity witness (Cauchy uniform-tumbling thin aluminum fairing sheet):
`rho = 2700 kg/m^3`, `t_um = 1726 um` (`1.73 mm`), `Cd_centi = 220` yields
`B_milli ∈ [236, 237]`, strictly inside `[180, 300]` and matching the MCMC median `0.236`. -/
theorem tumbling_aluminum_sheet_witness :
    ∃ B_milli t_um rho Cd_centi : Nat,
      180 ≤ B_milli ∧ B_milli ≤ 300 ∧
      rho = 2700 ∧ t_um = 1726 ∧ Cd_centi = 220 ∧
      2 * B_milli * t_um * rho ≤ Cd_centi * 10000000 ∧
      Cd_centi * 10000000 ≤ 2 * (B_milli + 1) * t_um * rho := by
  exact ⟨236, 1726, 2700, 220, by omega, by omega, rfl, rfl, rfl, by omega, by omega⟩

/-- Non-vacuity witness (Cauchy uniform-tumbling magnesium/composite fairing sheet):
`rho = 1800 kg/m^3`, `t_um = 2590 um` (`2.59 mm`), `Cd_centi = 220` yields
`B_milli ∈ [235, 236]`, strictly inside `[180, 300]`. -/
theorem tumbling_composite_fairing_witness :
    ∃ B_milli t_um rho Cd_centi : Nat,
      180 ≤ B_milli ∧ B_milli ≤ 300 ∧
      rho = 1800 ∧ t_um = 2590 ∧ Cd_centi = 220 ∧
      2 * B_milli * t_um * rho ≤ Cd_centi * 10000000 ∧
      Cd_centi * 10000000 ≤ 2 * (B_milli + 1) * t_um * rho := by
  exact ⟨235, 2590, 1800, 220, by omega, by omega, rfl, rfl, rfl, by omega, by omega⟩

end Conde1963.BallisticGeometryBound
