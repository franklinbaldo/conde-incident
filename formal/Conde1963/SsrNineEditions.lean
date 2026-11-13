import Lean

namespace Conde1963.SsrNineEditions

/-! C241-P20: 23 printed period cells of nine compiled NASA SSR publications.
Publication date is NOT instrument epoch, and no error below is sensor σ.
The 528 is absent from four late in-orbit lists, never assigned zero.
This proof is conditional on the explicit common-additive editorial model;
it does not restrict any physical orbit or location (Theta unchanged). -/

/-- April and December 527-minus-529 printed gaps differ by 510 centimin.
Four bounded residual terms must absorb that difference; E is integral. -/
theorem nine_edition_lower_bound
    (b527 b529 hApr hDec eaApr eaDec ecApr ecDec E : Int)
    (aApr : 9460 = b527 + hApr + eaApr)
    (aDec : 9460 = b527 + hDec + eaDec)
    (cApr : 9430 = b529 + hApr + ecApr)
    (cDec : 8920 = b529 + hDec + ecDec)
    (aAprLo : -E ≤ eaApr) (aAprHi : eaApr ≤ E)
    (aDecLo : -E ≤ eaDec) (aDecHi : eaDec ≤ E)
    (cAprLo : -E ≤ ecApr) (cAprHi : ecApr ≤ E)
    (cDecLo : -E ≤ ecDec) (cDecHi : ecDec ≤ E)
    : 128 ≤ E := by
  omega

/-- The exact bound is attained *simultaneously* by all 23 printed cells,
with one baseline per object and one shared bias per edition. -/
theorem nine_edition_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0731 h0815 h1015 h1115 h1130 h1215 h1231 : Int),
      (-128 ≤ (9460 - b527 - h0430) ∧ (9460 - b527 - h0430) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h0630) ∧ (9460 - b527 - h0630) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h0731) ∧ (9460 - b527 - h0731) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h0815) ∧ (9460 - b527 - h0815) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h1015) ∧ (9460 - b527 - h1015) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h1115) ∧ (9460 - b527 - h1115) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h1130) ∧ (9460 - b527 - h1130) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h1215) ∧ (9460 - b527 - h1215) ≤ 128) ∧
      (-128 ≤ (9460 - b527 - h1231) ∧ (9460 - b527 - h1231) ≤ 128) ∧
      (-128 ≤ (9410 - b528 - h0430) ∧ (9410 - b528 - h0430) ≤ 128) ∧
      (-128 ≤ (9370 - b528 - h0630) ∧ (9370 - b528 - h0630) ≤ 128) ∧
      (-128 ≤ (9360 - b528 - h0731) ∧ (9360 - b528 - h0731) ≤ 128) ∧
      (-128 ≤ (9330 - b528 - h0815) ∧ (9330 - b528 - h0815) ≤ 128) ∧
      (-128 ≤ (9240 - b528 - h1015) ∧ (9240 - b528 - h1015) ≤ 128) ∧
      (-128 ≤ (9430 - b529 - h0430) ∧ (9430 - b529 - h0430) ≤ 128) ∧
      (-128 ≤ (9400 - b529 - h0630) ∧ (9400 - b529 - h0630) ≤ 128) ∧
      (-128 ≤ (9390 - b529 - h0731) ∧ (9390 - b529 - h0731) ≤ 128) ∧
      (-128 ≤ (9380 - b529 - h0815) ∧ (9380 - b529 - h0815) ≤ 128) ∧
      (-128 ≤ (9330 - b529 - h1015) ∧ (9330 - b529 - h1015) ≤ 128) ∧
      (-128 ≤ (9260 - b529 - h1115) ∧ (9260 - b529 - h1115) ≤ 128) ∧
      (-128 ≤ (9220 - b529 - h1130) ∧ (9220 - b529 - h1130) ≤ 128) ∧
      (-128 ≤ (9160 - b529 - h1215) ∧ (9160 - b529 - h1215) ≤ 128) ∧
      (-128 ≤ (8920 - b529 - h1231) ∧ (8920 - b529 - h1231) ≤ 128) := by
  refine ⟨9460, 9342, 9176, 126, 96, 86, 76, 26, -44, -84, -128, -128, ?_⟩
  omega

end Conde1963.SsrNineEditions
