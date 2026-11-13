import Lean

namespace Conde1963.SsrFourEditions

/-! C241-P16 documentary model only; 0.01-minute units. Four publication
dates do not specify 12 independent orbital measurements, and this
minimax bound does not restrict any physical state or terminal location. -/

/-- April/August 527-minus-528 gaps change from 50 to 130 centimin.
A shared edition bias cancels; four bounded residuals must absorb 80. -/
theorem shared_edition_model_needs_twenty
    (baseA baseB hApr hAug eaApr eaAug ebApr ebAug E : Int)
    (aApr : 9460 = baseA + hApr + eaApr)
    (aAug : 9460 = baseA + hAug + eaAug)
    (bApr : 9410 = baseB + hApr + ebApr)
    (bAug : 9330 = baseB + hAug + ebAug)
    (eaAprLo : -E ≤ eaApr)
    (eaAprHi : eaApr ≤ E)
    (eaAugLo : -E ≤ eaAug)
    (eaAugHi : eaAug ≤ E)
    (ebAprLo : -E ≤ ebApr)
    (ebAprHi : ebApr ≤ E)
    (ebAugLo : -E ≤ ebAug)
    (ebAugHi : ebAug ≤ E)
    : 20 ≤ E := by
  omega

/-- All twelve cells admit E=20 with one object baseline each and
one shared bias per publication. Thus the lower bound is sharp. -/
theorem all_twelve_cells_attain_twenty :
    ∃ (baseA baseB baseC hApr hJun hJul hAug : Int),
      (9460 = baseA + hApr + (-20)) ∧      (9460 = baseA + hJun + (0)) ∧      (9460 = baseA + hJul + (0)) ∧      (9460 = baseA + hAug + (20)) ∧      (9410 = baseB + hApr + (20)) ∧      (9370 = baseB + hJun + (0)) ∧      (9360 = baseB + hJul + (-10)) ∧      (9330 = baseB + hAug + (-20)) ∧      (9430 = baseC + hApr + (5)) ∧      (9400 = baseC + hJun + (-5)) ∧      (9390 = baseC + hJul + (-15)) ∧      (9380 = baseC + hAug + (-5)) := by
  refine ⟨9460, 9370, 9405, 20, 0, 0, -20, ?_⟩
  omega

end Conde1963.SsrFourEditions
