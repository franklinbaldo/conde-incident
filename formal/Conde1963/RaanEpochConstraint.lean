import Conde1963.TruthBridge

/-!
# C241-T10: explicit numerical obstruction to an epoch-offset-only RAAN explanation

Inputs are transcribed from the *secondary* NORAD 528 comparison in
PR #14, commit 1934198e260b9dae8c056587cc7a16c777d58d25.
The 198.5261° TLE mirror has SHA-256
18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd.
The legacy 284.1520° vector is NOT authenticated as a primary TLE.
The two interpreted UTC epochs are separated by 16.132608 seconds.
Each RAAN is printed to 4 decimal places; the total rounding
allowance is 0.0001° (one unit of 10^-4 degree).

This is an exact rational inequality on the *transcribed numerals*.
The only scientific consequence is: under a SAME-FRAME, SAME-NODE,
EPOCH-OFFSET-ONLY model, a nodal-rate envelope smaller than the
calculated threshold cannot reconcile both records. No such empirical
rate envelope, source authenticity or physical-frame equivalence is
certified by Lean. It does not choose a true element set or predict impact.
-/

namespace Conde1963

/-- Fixed secondary transcription, in ten-thousandths of a degree. -/
def c241LegacyRaanE4 : Nat := 2841520
def c241MirrorRaanE4 : Nat := 1985261
def c241EpochSeparationUs : Nat := 16132608
def c241OneDayUs : Nat := 86400000000
def c241CombinedRoundingE4 : Nat := 1

/-- Shortest circular distance is 85.6259°, so the ROUNDING-RESISTANT
    distance floor is 85.6258°. No orbital inference is hidden here. -/
def c241GapFloorE4 : Nat :=
  c241LegacyRaanE4 - c241MirrorRaanE4 - c241CombinedRoundingE4

/-- Exact numerical transcription check (C241-T10). -/
theorem c241_raan_gap_floor_is_856258 :
    c241GapFloorE4 = 856258 := by decide

/-- Rate in 10^-4 degrees/day can cover the *minimum* gap only if
    rate * Δepoch >= gapFloor * day. This is a conditional model gate,
    not an asserted physical equation for NORAD 528. -/
def c241RateCanExplain (rateE4PerDay : Nat) : Prop :=
  c241GapFloorE4 * c241OneDayUs ≤
    rateE4PerDay * c241EpochSeparationUs

/-- At most 458,578 degrees/day is mathematically insufficient. -/
theorem c241_rate_458578_deg_day_cannot_explain :
    ¬ c241RateCanExplain (458578 * 10000) := by decide

/-- 458,579 degrees/day crosses the numeric threshold. Neither
    bound is an estimated or observed physical precession rate. -/
theorem c241_rate_458579_deg_day_passes_numeric_gate :
    c241RateCanExplain (458579 * 10000) := by decide

end Conde1963
