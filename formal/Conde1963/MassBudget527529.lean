import Lean

/-!
C241: conditional mass budget for catalog objects 527/528/529.

C61 describes roughly 1176 kg of associated total system mass in a MODERN
secondary GCAT-derived catalogue. It DOES NOT prove that this amount was
the closed inventory of precisely three intact orbiting objects at separation.
The mass units below are exact integers in grams, conditional on using
1176 kg as a true reference inventory. Unassigned matter X may include
other pieces, losses and material not individually catalogued, with care
to keep the budget at one common reference epoch.

The reporter's reference-mass error is a DIFFERENT variable from real mass X.
No historical upper bound on X or measurement uncertainty has been recovered.
-/

namespace Conde1963.MassBudget527529

def referenceGrams : Nat := 1176000

/-- Closed *hypothetical* inventory with an untracked-mass reservoir X.
The equation itself requires a valid reference epoch and source definition. -/
def ClosedBudget (m527 m528 m529 residual : Nat) : Prop :=
  m527 + m528 + m529 + residual = referenceGrams

/-- With three positive components and the hypothetical exact reference
inventory, each weighs strictly less than 1176 kg. -/
theorem each_below_assumed_reference
    (a b c x : Nat) (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (h : ClosedBudget a b c x) :
    a < referenceGrams ∧ b < referenceGrams ∧ c < referenceGrams := by
  simp only [ClosedBudget, referenceGrams] at h ⊢
  omega

/-- The tracked sum cannot exceed the reference inventory, but need not
be equal to it if X is positive. -/
theorem tracked_sum_le_reference
    (a b c x : Nat) (h : ClosedBudget a b c x) :
    a + b + c ≤ referenceGrams := by
  simp only [ClosedBudget, referenceGrams] at h ⊢
  omega

theorem tracked_sum_eq_reference_iff_no_residual
    (a b c x : Nat) (h : ClosedBudget a b c x) :
    a + b + c = referenceGrams ↔ x = 0 := by
  simp only [ClosedBudget, referenceGrams] at h ⊢
  omega

/-- Even an exact total does not establish that residual X is small.
This is a logical counterexample, NOT a suggested mass assignment. -/
theorem large_residual_consistent_with_total :
    ∃ a b c x : Nat,
      0 < a ∧ 0 < b ∧ 0 < c ∧
      ClosedBudget a b c x ∧ 2 * x > referenceGrams := by
  refine ⟨200000, 100000, 100000, 776000, by omega, by omega, by omega, ?_, by omega⟩
  change 200000 + 100000 + 100000 + 776000 = 1176000
  omega

/-- Include a signed reference-total error epsilon (in grams).
When an external source someday supplies |epsilon| ≤ tolerance and
a justified bound 0 ≤ X ≤ residualCap, only then is there a bounded
interval for the sum of masses of the three tracked objects.
The bounds below are mathematical consequences of ASSUMPTIONS. -/
theorem conditional_tracked_sum_interval
    (a b c x : Nat) (epsilon : Int) (tolerance residualCap : Nat)
    (hbudget :
      (a : Int) + (b : Int) + (c : Int) + (x : Int) =
        (1176000 : Int) + epsilon)
    (hepsLo : -(tolerance : Int) ≤ epsilon)
    (hepsHi : epsilon ≤ (tolerance : Int))
    (hx : x ≤ residualCap) :
    (1176000 : Int) - (tolerance : Int) - (residualCap : Int) ≤
        ((a + b + c : Nat) : Int) ∧
    ((a + b + c : Nat) : Int) ≤ (1176000 : Int) + (tolerance : Int) := by
  omega

/-- Under strictly positive *other* cataloged masses, a single piece
cannot consume the entire reference inventory, even if X=0. -/
theorem individual_less_than_reference_plus_error
    (a b c x : Nat) (epsilon : Int) (tolerance : Nat)
    (ha : 0 < a) (hb : 0 < b) (hc : 0 < c)
    (hbudget :
      (a : Int) + (b : Int) + (c : Int) + (x : Int) =
        (1176000 : Int) + epsilon)
    (hepsHi : epsilon ≤ (tolerance : Int)) :
    (a : Int) < (1176000 : Int) + (tolerance : Int) ∧
    (b : Int) < (1176000 : Int) + (tolerance : Int) ∧
    (c : Int) < (1176000 : Int) + (tolerance : Int) := by
  omega

end Conde1963.MassBudget527529
