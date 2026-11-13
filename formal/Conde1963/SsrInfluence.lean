import Lean

namespace Conde1963.SsrInfluence

/-! C241-P18 conditional *documentary* source-deletion sensitivity.
The dates are editions, not sensor epochs. No physical Theta filter. -/

/-- Conditional extremal pair: no tracking epoch or sensor precision. -/
theorem without_april_needs_ten
    (baseA baseB hFirst hLast eaFirst eaLast ebFirst ebLast E : Int)
    (aFirst : 9460 = baseA + hFirst + eaFirst)
    (aLast : 9460 = baseA + hLast + eaLast)
    (bFirst : 9370 = baseB + hFirst + ebFirst)
    (bLast : 9330 = baseB + hLast + ebLast)
    (eaFirstLo : -E ≤ eaFirst)
    (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast)
    (eaLastHi : eaLast ≤ E)
    (ebFirstLo : -E ≤ ebFirst)
    (ebFirstHi : ebFirst ≤ E)
    (ebLastLo : -E ≤ ebLast)
    (ebLastHi : ebLast ≤ E)
    : 10 ≤ E := by
  omega

/-- All retained cells attain the certified integer minimax radius. -/
theorem without_april_attains_ten :
    ∃ (baseA baseB baseC h0 h1 h2 : Int),
      (9460 = baseA + h0 + (-10)) ∧      (9460 = baseA + h1 + (0)) ∧      (9460 = baseA + h2 + (10)) ∧      (9370 = baseB + h0 + (10)) ∧      (9360 = baseB + h1 + (10)) ∧      (9330 = baseB + h2 + (-10)) ∧      (9400 = baseC + h0 + (-10)) ∧      (9390 = baseC + h1 + (-10)) ∧      (9380 = baseC + h2 + (-10)) := by
  refine ⟨0, -110, -60, 9470, 9460, 9450, ?_⟩
  omega

/-- Conditional extremal pair: no tracking epoch or sensor precision. -/
theorem without_august_needs_thirteen
    (baseA baseB hFirst hLast eaFirst eaLast ebFirst ebLast E : Int)
    (aFirst : 9460 = baseA + hFirst + eaFirst)
    (aLast : 9460 = baseA + hLast + eaLast)
    (bFirst : 9410 = baseB + hFirst + ebFirst)
    (bLast : 9360 = baseB + hLast + ebLast)
    (eaFirstLo : -E ≤ eaFirst)
    (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast)
    (eaLastHi : eaLast ≤ E)
    (ebFirstLo : -E ≤ ebFirst)
    (ebFirstHi : ebFirst ≤ E)
    (ebLastLo : -E ≤ ebLast)
    (ebLastHi : ebLast ≤ E)
    : 13 ≤ E := by
  omega

/-- All retained cells attain the certified integer minimax radius. -/
theorem without_august_attains_thirteen :
    ∃ (baseA baseB baseC h0 h1 h2 : Int),
      (9460 = baseA + h0 + (-11)) ∧      (9460 = baseA + h1 + (13)) ∧      (9460 = baseA + h2 + (13)) ∧      (9410 = baseB + h0 + (13)) ∧      (9370 = baseB + h1 + (-3)) ∧      (9360 = baseB + h2 + (-13)) ∧      (9430 = baseC + h0 + (3)) ∧      (9400 = baseC + h1 + (-3)) ∧      (9390 = baseC + h2 + (-13)) := by
  refine ⟨0, -74, -44, 9471, 9447, 9447, ?_⟩
  omega

end Conde1963.SsrInfluence
