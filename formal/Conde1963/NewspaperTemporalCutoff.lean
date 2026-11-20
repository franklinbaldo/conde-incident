import Lean

/-!
Conditional causal temporal cutoff from primary newspaper publication/query.

Motivated by primary 1963 facsimiles `C241-OGLOBO-19631108-P01` (*O Globo*,
8 Nov 1963, p. 1) and `C241-OGLOBO-19631109-P04` (*O Globo*, 9 Nov 1963, p. 4,
stating *"No Ministério da Aeronáutica, até ontem à tarde também não havia
qualquer notícia a respeito"*).

All timestamps here are integer minutes since `1963-11-08 00:00 UTC`.
Lean certifies only the logical implications of these premises, not primary
press-closing clocks or orbital determination.
-/

namespace Conde1963.NewspaperTemporalCutoff

/-- A candidate orbital pass window `[tPass - delta, tPass + delta]` in integer
minutes since `1963-11-08 00:00 UTC`. -/
def inPassWindow (tEvent tPass delta : Int) : Prop :=
  tPass - delta ≤ tEvent ∧ tEvent ≤ tPass + delta

/-- Conditional causal exclusion: if a physical event `tEvent` caused a report
already queried/closed at `tCutoff` (`tEvent < tCutoff`), and a candidate
orbital pass `tPass` with half-width `delta` satisfies `tCutoff + delta ≤ tPass`,
then `tEvent` cannot lie inside the pass window `[tPass - delta, tPass + delta]`. -/
theorem causal_report_excludes_later_pass
    (tEvent tCutoff tPass delta : Int)
    (hCausal : tEvent < tCutoff)
    (hAfter : tCutoff + delta ≤ tPass) :
    ¬ inPassWindow tEvent tPass delta := by
  intro hIn
  dsimp [inPassWindow] at hIn
  omega

/-- Concrete instantiation for 1963-11-08:
- Conservative upper bound for "ontem à tarde" (18:00 BA = 21:00 UTC): `tCutoff = 1260`
  (note: Rio daylight saving UTC-2 would make 18:00 Rio = 20:00 UTC = `1200`, even earlier).
- Nominal NORAD 528 descending plane pass over Conde (`23:45 UTC` = `20:45 BA`): `tPass = 1425`.
- Generous uncertainty half-width `delta = 90` minutes (`±1.5 h`).
Under these premises, the evening NORAD 528 pass is strictly excluded as the
cause of *O Globo*'s 1963-11-08 report. -/
theorem oglobo_afternoon_excludes_nov08_evening_528
    (tEvent tCutoff : Int)
    (hCausal : tEvent < tCutoff)
    (hAfternoon : tCutoff ≤ 1260) :
    ¬ inPassWindow tEvent 1425 90 := by
  have hAfter : tCutoff + 90 ≤ 1425 := by omega
  exact causal_report_excludes_later_pass tEvent tCutoff 1425 90 hCausal hAfter

/-- Honest boundary / non-vacuity witness: the morning NORAD 528 plane pass
over Conde (`11:34 UTC` = `08:34 BA`, minute `694`) is NOT excluded by an
afternoon cutoff (`tCutoff = 1260`). Narrowing that branch further requires
calibrating the exact press-closing clock of *O Globo* edition `PRM1`. -/
theorem morning_528_pass_remains_before_afternoon_cutoff :
    ∃ tEvent : Int, tEvent < 1260 ∧ inPassWindow tEvent 694 90 := by
  refine ⟨694, by omega, ?_⟩
  dsimp [inPassWindow]
  omega

end Conde1963.NewspaperTemporalCutoff
