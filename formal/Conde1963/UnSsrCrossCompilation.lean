import Lean

namespace Conde1963.UnSsrCrossCompilation

/-! C241-P23: conditional, CROSS-AGENCY documentary test (26 printed cells).
UN A/AC.105/INF.30 was issued March 13, with administrative cutoff Jan 31.
The nine NASA SSR dates are publication/report dates, not sensor epochs.
Assuming a shared additive document convention across these chains is an
untested hypothesis. No covariance, sensor independence or Theta reduction. -/

def within (p base offset E : Int) : Prop :=
  -E ≤ p - base - offset ∧ p - base - offset ≤ E

/-- UN Jan31-cutoff printed 527/529 gap is 0; NASA Dec31 is 540.
A common baseline and one offset per document require 4E >= 540. -/
theorem cross_agency_lower_bound
    (b527 b529 hUn hDec eaUn eaDec ecUn ecDec E : Int)
    (aUn : 9470 = b527 + hUn + eaUn)
    (aDec : 9460 = b527 + hDec + eaDec)
    (cUn : 9470 = b529 + hUn + ecUn)
    (cDec : 8920 = b529 + hDec + ecDec)
    (eaUnLo : -E ≤ eaUn) (eaUnHi : eaUn ≤ E)
    (eaDecLo : -E ≤ eaDec) (eaDecHi : eaDec ≤ E)
    (ecUnLo : -E ≤ ecUn) (ecUnHi : ecUn ≤ E)
    (ecDecLo : -E ≤ ecDec) (ecDecHi : ecDec ≤ E) :
    135 ≤ E := by
  omega

/-- Attaining witness covers all 26 printed periods simultaneously,
including every printed 528 cell and the full NASA-only control panel. -/
theorem cross_agency_attaining_witness :
    ∃ (b527 b528 b529 hUn h0430 h0630 h0731 h0815 h1015 h1115 h1130 h1215 h1231 : Int),
           within 9470 b527 hUn 135 ∧
      within 9460 b527 h0430 135 ∧
      within 9460 b527 h0630 135 ∧
      within 9460 b527 h0731 135 ∧
      within 9460 b527 h0815 135 ∧
      within 9460 b527 h1015 135 ∧
      within 9460 b527 h1115 135 ∧
      within 9460 b527 h1130 135 ∧
      within 9460 b527 h1215 135 ∧
      within 9460 b527 h1231 135 ∧
      within 9450 b528 hUn 135 ∧
      within 9410 b528 h0430 135 ∧
      within 9370 b528 h0630 135 ∧
      within 9360 b528 h0731 135 ∧
      within 9330 b528 h0815 135 ∧
      within 9240 b528 h1015 135 ∧
      within 9470 b529 hUn 135 ∧
      within 9430 b529 h0430 135 ∧
      within 9400 b529 h0630 135 ∧
      within 9390 b529 h0731 135 ∧
      within 9380 b529 h0815 135 ∧
      within 9330 b529 h1015 135 ∧
      within 9260 b529 h1115 135 ∧
      within 9220 b529 h1130 135 ∧
      within 9160 b529 h1215 135 ∧
      within 8920 b529 h1231 135 := by
  refine ⟨9470, 9380, 9200, 135, 95, 65, 55, 45, -5, -75, -115, -145, -145, ?_⟩
  simp only [within]
  omega

end Conde1963.UnSsrCrossCompilation
