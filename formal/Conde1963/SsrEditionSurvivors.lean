import Lean

namespace Conde1963.SsrEditionSurvivors

/-! C241-P21: conditional print-only NASA SSR compilation test.
Publication is NOT an instrument epoch. Missing 528 is never treated as zero.
The gapAB fallback is inaccessible to the tested case (indices both < 5).
No seven real errata demonstrated; Theta remains unchanged. -/

def gapAC (i : Fin 9) : Int :=
  if i.val = 0 then 30 else
    if i.val = 1 then 60 else
    if i.val = 2 then 70 else
    if i.val = 3 then 80 else
    if i.val = 4 then 130 else
    if i.val = 5 then 200 else
    if i.val = 6 then 240 else
    if i.val = 7 then 300 else
    if i.val = 8 then 540 else 0

def gapAB (i : Fin 9) : Int :=
  if i.val = 0 then 50 else
    if i.val = 1 then 90 else
    if i.val = 2 then 100 else
    if i.val = 3 then 130 else
    if i.val = 4 then 220 else 0

def within20 (x y : Int) : Prop := -20 ≤ x - y ∧ x - y ≤ 20

/-- If 2 objects share a publication offset at 2 editions, then 4
residuals each bounded by 5 centimin imply a gap change at most 20. -/
theorem gap_change_necessary
    (a1 c1 a2 c2 ba bc h1 h2 : Int)
    (ha1lo : -5 ≤ a1 - ba - h1) (ha1hi : a1 - ba - h1 ≤ 5)
    (hc1lo : -5 ≤ c1 - bc - h1) (hc1hi : c1 - bc - h1 ≤ 5)
    (ha2lo : -5 ≤ a2 - ba - h2) (ha2hi : a2 - ba - h2 ≤ 5)
    (hc2lo : -5 ≤ c2 - bc - h2) (hc2hi : c2 - bc - h2 ≤ 5) :
    within20 (a1 - c1) (a2 - c2) := by
  dsimp [within20]
  omega

/-- Exhaustive classification of all 36 ordered publication pairs, using
527/529 always and 527/528 only when both publications list object 528. -/
theorem unique_pair_under_necessary_screens :
    ∀ (i j : Fin 9), i.val < j.val →
      within20 (gapAC i) (gapAC j) →
      ((i.val < 5 ∧ j.val < 5) → within20 (gapAB i) (gapAB j)) →
      i.val = 1 ∧ j.val = 2 := by
  intro i j hij hac hab
  have hi : i.val < 9 := i.isLt
  have hj : j.val < 9 := j.isLt
  simp only [gapAC, gapAB, within20] at hac hab
  split_ifs at hac hab <;> omega

/-- Any three survivors would contain two different ordered pairs, each
forced to be indices 1 and 2, contradiction. -/
theorem no_three_screened
    (i j k : Fin 9)
    (hij : i.val < j.val) (hjk : j.val < k)
    (acij : within20 (gapAC i) (gapAC j))
    (acjk : within20 (gapAC j) (gapAC k))
    (abij : (i.val < 5 ∧ j.val < 5) → within20 (gapAB i) (gapAB j))
    (abjk : (j.val < 5 ∧ k.val < 5) → within20 (gapAB j) (gapAB k)) :
    False := by
  have h1 := unique_pair_under_necessary_screens i j hij acij abij
  have h2 := unique_pair_under_necessary_screens j k hjk acjk abjk
  omega

/-- Constructive witness for all six printed Jun30/Jul31 cells. -/
theorem june_july_attaining_witness :
    ∃ (b527 b528 b529 hJun hJul : Int),
      (-5 ≤ (9460 - b527 - hJun) ∧ (9460 - b527 - hJun) ≤ 5) ∧
      (-5 ≤ (9460 - b527 - hJul) ∧ (9460 - b527 - hJul) ≤ 5) ∧
      (-5 ≤ (9370 - b528 - hJun) ∧ (9370 - b528 - hJun) ≤ 5) ∧
      (-5 ≤ (9360 - b528 - hJul) ∧ (9360 - b528 - hJul) ≤ 5) ∧
      (-5 ≤ (9400 - b529 - hJun) ∧ (9400 - b529 - hJun) ≤ 5) ∧
      (-5 ≤ (9390 - b529 - hJul) ∧ (9390 - b529 - hJul) ≤ 5) := by
  refine ⟨9460, 9370, 9400, -5, -5, ?_⟩
  omega

end Conde1963.SsrEditionSurvivors
