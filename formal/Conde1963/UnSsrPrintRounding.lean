import Lean

namespace Conde1963.UnSsrPrintRounding

/-! C241-P34. Documentary UN/NASA COMMON-offset thought experiment.
Centiminute is 0.01 minute. Each printed tenth-minute value may differ by
at most 5 centiminutes from an unobserved table input (rounding assumption).
This is NOT a bound on orbital sensor errors. March UN publication and
January administrative cutoff are NOT instrumental observation times.
No physical-domain reduction, independence claim, or decay location. -/

def withinPrinted (printed latent baseline offset E R : Int) : Prop :=
  -R ≤ printed - latent ∧ printed - latent ≤ R ∧
  -E ≤ latent - baseline - offset ∧ latent - baseline - offset ≤ E

/-- Four contrasting UN/December printed values force E+R >= 135,
even after allowing a symmetric rounding margin R at EACH cell. -/
theorem round_robust_lower_bound
    (b527 b529 hUn hDec : Int)
    (aUn aDec cUn cDec eaUn eaDec ecUn ecDec E R : Int)
    (aUnDef : aUn = b527 + hUn + eaUn)
    (aDecDef : aDec = b527 + hDec + eaDec)
    (cUnDef : cUn = b529 + hUn + ecUn)
    (cDecDef : cDec = b529 + hDec + ecDec)
    (aUnRoundLo : -R ≤ 9470 - aUn) (aUnRoundHi : 9470 - aUn ≤ R)
    (aDecRoundLo : -R ≤ 9460 - aDec) (aDecRoundHi : 9460 - aDec ≤ R)
    (cUnRoundLo : -R ≤ 9470 - cUn) (cUnRoundHi : 9470 - cUn ≤ R)
    (cDecRoundLo : -R ≤ 8920 - cDec) (cDecRoundHi : 8920 - cDec ≤ R)
    (eaUnLo : -E ≤ eaUn) (eaUnHi : eaUn ≤ E)
    (eaDecLo : -E ≤ eaDec) (eaDecHi : eaDec ≤ E)
    (ecUnLo : -E ≤ ecUn) (ecUnHi : ecUn ≤ E)
    (ecDecLo : -E ≤ ecDec) (ecDecHi : ecDec ≤ E) :
    135 ≤ E + R := by
  omega

/-- Under R=5, at least 130 centiminutes = 78 seconds remain
unexplained by a single additive offset per publication. -/
theorem rounded_half_step_lower_bound
    (b527 b529 hUn hDec : Int)
    (aUn aDec cUn cDec eaUn eaDec ecUn ecDec E : Int)
    (aUnDef : aUn = b527 + hUn + eaUn)
    (aDecDef : aDec = b527 + hDec + eaDec)
    (cUnDef : cUn = b529 + hUn + ecUn)
    (cDecDef : cDec = b529 + hDec + ecDec)
    (aUnRoundLo : -5 ≤ 9470 - aUn) (aUnRoundHi : 9470 - aUn ≤ 5)
    (aDecRoundLo : -5 ≤ 9460 - aDec) (aDecRoundHi : 9460 - aDec ≤ 5)
    (cUnRoundLo : -5 ≤ 9470 - cUn) (cUnRoundHi : 9470 - cUn ≤ 5)
    (cDecRoundLo : -5 ≤ 8920 - cDec) (cDecRoundHi : 8920 - cDec ≤ 5)
    (eaUnLo : -E ≤ eaUn) (eaUnHi : eaUn ≤ E)
    (eaDecLo : -E ≤ eaDec) (eaDecHi : eaDec ≤ E)
    (ecUnLo : -E ≤ ecUn) (ecUnHi : ecUn ≤ E)
    (ecDecLo : -E ≤ ecDec) (ecDecHi : ecDec ≤ E) :
    130 ≤ E := by
  omega

/-- A SINGLE baseline/offset set and 26 separate rounding inputs attain
E=130 simultaneously; no observational validity is asserted. -/
theorem all_26_cells_attain_130 :
    ∃ (b527 b528 b529 hUn h0430 h0630 h0731 h0815 h1015 h1115 h1130 h1215 h1231 x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 x16 x17 x18 x19 x20 x21 x22 x23 x24 x25 : Int),
      withinPrinted 9470 x0 b527 hUn 130 5
      ∧ withinPrinted 9460 x1 b527 h0430 130 5
      ∧ withinPrinted 9460 x2 b527 h0630 130 5
      ∧ withinPrinted 9460 x3 b527 h0731 130 5
      ∧ withinPrinted 9460 x4 b527 h0815 130 5
      ∧ withinPrinted 9460 x5 b527 h1015 130 5
      ∧ withinPrinted 9460 x6 b527 h1115 130 5
      ∧ withinPrinted 9460 x7 b527 h1130 130 5
      ∧ withinPrinted 9460 x8 b527 h1215 130 5
      ∧ withinPrinted 9460 x9 b527 h1231 130 5
      ∧ withinPrinted 9450 x10 b528 hUn 130 5
      ∧ withinPrinted 9410 x11 b528 h0430 130 5
      ∧ withinPrinted 9370 x12 b528 h0630 130 5
      ∧ withinPrinted 9360 x13 b528 h0731 130 5
      ∧ withinPrinted 9330 x14 b528 h0815 130 5
      ∧ withinPrinted 9240 x15 b528 h1015 130 5
      ∧ withinPrinted 9470 x16 b529 hUn 130 5
      ∧ withinPrinted 9430 x17 b529 h0430 130 5
      ∧ withinPrinted 9400 x18 b529 h0630 130 5
      ∧ withinPrinted 9390 x19 b529 h0731 130 5
      ∧ withinPrinted 9380 x20 b529 h0815 130 5
      ∧ withinPrinted 9330 x21 b529 h1015 130 5
      ∧ withinPrinted 9260 x22 b529 h1115 130 5
      ∧ withinPrinted 9220 x23 b529 h1130 130 5
      ∧ withinPrinted 9160 x24 b529 h1215 130 5
      ∧ withinPrinted 8920 x25 b529 h1231 130 5 := by
  refine ⟨9470, 9380, 9200, 135, 95, 65, 55, 45, -5, -75, -115, -145, -145, 9475, 9460, 9460, 9460, 9460, 9460, 9460, 9460, 9455, 9455, 9450, 9410, 9370, 9360, 9330, 9245, 9465, 9425, 9395, 9385, 9375, 9325, 9255, 9215, 9160, 8925, ?_⟩
  simp only [withinPrinted]
  omega

end Conde1963.UnSsrPrintRounding
