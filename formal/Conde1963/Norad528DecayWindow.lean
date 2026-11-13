import Lean

/-!
C241: conditional UTC calendar-day scenario for NORAD 528.

NASA/Goddard SSR of 15 Nov 1963 catalogues "1963 3B" as decayed
"8 NOV 63" (C197#1). Its reporting method, timezone, and temporal
classification error for this object are NOT recovered.

The only additional premise below is hypothetical: assume the reported
calendar day can be zero or one UTC day LATER than the actual decay day,
never earlier. This is not a fact about NASA/NORAD in 1963.
Theorems constrain a scenario, NOT authenticated historical state.
-/

namespace Conde1963.Norad528DecayWindow

def catalogDay : Int := 8

/-- If catalog-date delay is either 0 or 1 complete UTC day, the actual
decay calendar day is 7 or 8 November. This DOES NOT derive the delay
hypothesis from the NASA source. -/
theorem assumed_catalog_delay_limits_day
    (actualDay : Int)
    (hNonnegative : 0 ≤ catalogDay - actualDay)
    (hAtMostOne : catalogDay - actualDay ≤ 1) :
    actualDay = 7 ∨ actualDay = 8 := by
  dsimp [catalogDay] at *
  omega

/-- Same explicitly assumed reporting rule excludes 9 November or later. -/
theorem assumed_catalog_delay_excludes_nov9
    (actualDay : Int)
    (hNonnegative : 0 ≤ catalogDay - actualDay)
    (hAtMostOne : catalogDay - actualDay ≤ 1) :
    actualDay < 9 := by
  have cases := assumed_catalog_delay_limits_day actualDay hNonnegative hAtMostOne
  omega

/-- The conditional scenario is internally nonempty; 8 November is a witness. -/
theorem scenario_nonempty :
    ∃ actualDay : Int,
      0 ≤ catalogDay - actualDay ∧ catalogDay - actualDay ≤ 1 := by
  refine ⟨8, ?_⟩
  dsimp [catalogDay]
  omega

/-- Without a reporting-delay assumption, the source's mere label "8"
is compatible with a DIFFERENT physical date. This is a countermodel to
any attempt to make the NASA day an unconditional terminal timestamp. -/
theorem label_alone_does_not_prove_no_nov9 :
    ∃ actualDay : Int, catalogDay = 8 ∧ actualDay = 9 := by
  exact ⟨9, rfl, rfl⟩

end Conde1963.Norad528DecayWindow
