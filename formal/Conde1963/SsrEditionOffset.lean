import Lean

namespace Conde1963.SsrEditionOffset

/-! Generated from source-audited C241-L19, C241-L18 and C241-L21.
All units: 0.01 minute. Rounding ±5 is a *conditional printing*
hypothesis, not sensor covariance. Dates are publication dates;
nothing below implies orbital drift, reentry time, or location. -/

/-- Individual printed periods share an exact publication-edition index. -/
theorem object_specific_printed_contrasts
    (a15 a30 aDec c15 c30 cDec : Int)
    (h_a15 : 9455 ≤ a15 ∧ a15 ≤ 9465)
    (h_a30 : 9455 ≤ a30 ∧ a30 ≤ 9465)
    (h_aDec : 9455 ≤ aDec ∧ aDec ≤ 9465)
    (h_c15 : 9255 ≤ c15 ∧ c15 ≤ 9265)
    (h_c30 : 9215 ≤ c30 ∧ c30 ≤ 9225)
    (h_cDec : 9155 ≤ cDec ∧ cDec ≤ 9165)
    : (20 ≤ (a30 - c30) - (a15 - c15) ∧ (a30 - c30) - (a15 - c15) ≤ 60) ∧
      (40 ≤ (aDec - cDec) - (a30 - c30) ∧ (aDec - cDec) - (a30 - c30) ≤ 80) ∧
      (80 ≤ (aDec - cDec) - (a15 - c15) ∧ (aDec - cDec) - (a15 - c15) ≤ 120) := by
  rcases h_a15 with ⟨h_a15_lo, h_a15_hi⟩
  rcases h_a30 with ⟨h_a30_lo, h_a30_hi⟩
  rcases h_aDec with ⟨h_aDec_lo, h_aDec_hi⟩
  rcases h_c15 with ⟨h_c15_lo, h_c15_hi⟩
  rcases h_c30 with ⟨h_c30_lo, h_c30_hi⟩
  rcases h_cDec with ⟨h_cDec_lo, h_cDec_hi⟩
  omega

/-- A common additive edition offset would force identical printed
    changes for both objects, contrary to the source-locked bounds. -/
theorem no_shared_additive_edition_offset
    (a15 aDec c15 cDec : Int)
    (h_a15 : 9455 ≤ a15 ∧ a15 ≤ 9465)
    (h_aDec : 9455 ≤ aDec ∧ aDec ≤ 9465)
    (h_c15 : 9255 ≤ c15 ∧ c15 ≤ 9265)
    (h_cDec : 9155 ≤ cDec ∧ cDec ≤ 9165)
    : ¬ ∃ (baseA baseC bias15 biasDec : Int),
        a15 = baseA + bias15 ∧ c15 = baseC + bias15 ∧
        aDec = baseA + biasDec ∧ cDec = baseC + biasDec := by
  intro h
  rcases h with ⟨baseA, baseC, bias15, biasDec, h1, h2, h3, h4⟩
  rcases h_a15 with ⟨h_a15_lo, h_a15_hi⟩
  rcases h_aDec with ⟨h_aDec_lo, h_aDec_hi⟩
  rcases h_c15 with ⟨h_c15_lo, h_c15_hi⟩
  rcases h_cDec with ⟨h_cDec_lo, h_cDec_hi⟩
  omega

end Conde1963.SsrEditionOffset
