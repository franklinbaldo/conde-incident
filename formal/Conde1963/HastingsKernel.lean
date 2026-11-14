import Conde1963.CircularMCMC

namespace Conde1963.CircularMCMC

/-! ## Full finite Hastings transport with explicit rejection self-mass

Earlier lemmas certified only accepted pairwise flows, which alone are not a
Markov transition kernel. Here every row uses proposal counts summing to the
same positive denominator. Rejected attempts stay at the source state.
We prove nonnegative held mass, full row and column conservation, and
reversibility at the unnormalized integer-mass level. No sampling convergence
or historical posterior is implied. -/

/-- Sum of bidirectionally accepted proposal mass on a finite state space. -/
def acceptedRow {n : Nat} (weight : Fin n → Nat)
    (proposal : Fin n → Fin n → Nat) (i : Fin n) : Nat :=
  ∑ j : Fin n, hastingsFlow weight proposal i j

/-- Accepted mass cannot exceed the proposed mass if the proposal row totals
    the shared denominator; this is what makes the rejection stay valid. -/
theorem acceptedRow_le_capacity {n : Nat}
    (weight : Fin n → Nat) (proposal : Fin n → Fin n → Nat)
    (denom : Nat) (i : Fin n)
    (hrow : (∑ j : Fin n, proposal i j) = denom) :
    acceptedRow weight proposal i ≤ weight i * denom := by
  unfold acceptedRow
  calc
    (∑ j : Fin n, hastingsFlow weight proposal i j) ≤
      ∑ j : Fin n, weight i * proposal i j := by
        apply Finset.sum_le_sum
        intro j _
        exact hastingsFlow_le_forward weight proposal i j
    _ = weight i * (∑ j : Fin n, proposal i j) := by
      rw [Finset.mul_sum]
    _ = weight i * denom := by rw [hrow]

/-- Rejection mass remains at the source. Natural subtraction is legitimate
    exactly when the proposal row total has been checked. -/
def rejectedStay {n : Nat} (weight : Fin n → Nat)
    (proposal : Fin n → Fin n → Nat) (denom : Nat) (i : Fin n) : Nat :=
  weight i * denom - acceptedRow weight proposal i

/-- Full weighted transition including self-proposals AND rejected attempts.
    This is a finite exact transport at mass-times-proposal-count resolution. -/
def fullTransport {n : Nat} (weight : Fin n → Nat)
    (proposal : Fin n → Fin n → Nat) (denom : Nat)
    (i j : Fin n) : Nat :=
  hastingsFlow weight proposal i j +
    (if i = j then rejectedStay weight proposal denom i else 0)

/-- Every state sends exactly its weight times the common denominator.
    There is no mass leakage from omitted rejection self-loops. -/
theorem fullTransport_row_conservation {n : Nat}
    (weight : Fin n → Nat) (proposal : Fin n → Fin n → Nat)
    (denom : Nat) (i : Fin n)
    (hrow : (∑ j : Fin n, proposal i j) = denom) :
    (∑ j : Fin n, fullTransport weight proposal denom i j) =
    weight i * denom := by
  have hbound := acceptedRow_le_capacity weight proposal denom i hrow
  simp only [fullTransport, Finset.sum_add_distrib]
  have hstay : (∑ j : Fin n, if i = j then rejectedStay weight proposal denom i else 0) =
      rejectedStay weight proposal denom i := by simp
  rw [hstay]
  change acceptedRow weight proposal i +
    (weight i * denom - acceptedRow weight proposal i) = weight i * denom
  omega

/-- Even after adding rejection self-mass, the weighted full transport is
    pairwise reversible for asymmetric proposals. -/
theorem fullTransport_detailed_balance {n : Nat}
    (weight : Fin n → Nat) (proposal : Fin n → Fin n → Nat)
    (denom : Nat) (i j : Fin n) :
    fullTransport weight proposal denom i j =
    fullTransport weight proposal denom j i := by
  by_cases h : i = j
  · subst j; rfl
  · simp [fullTransport, h, Ne.symm h, hastingsFlow_detailed_balance]

/-- The incoming mass also equals stationary target weight times denominator.
    This closes the previous gap between accepted-flow balance and a full
    weighted finite-state Markov transport, conditional on common row totals. -/
theorem fullTransport_stationary {n : Nat}
    (weight : Fin n → Nat) (proposal : Fin n → Fin n → Nat)
    (denom : Nat) (i : Fin n)
    (hrow : (∑ j : Fin n, proposal i j) = denom) :
    (∑ j : Fin n, fullTransport weight proposal denom j i) =
    weight i * denom := by
  calc
    (∑ j : Fin n, fullTransport weight proposal denom j i) =
      ∑ j : Fin n, fullTransport weight proposal denom i j := by
        apply Finset.sum_congr rfl
        intro j _
        exact fullTransport_detailed_balance weight proposal denom j i
    _ = weight i * denom :=
      fullTransport_row_conservation weight proposal denom i hrow

/-- Two-state directed 3:1 proposal with normalized rows of four counts.
    The full transport has row masses 8 and 4, and holds 5 and 0 units.
    These are synthetic counts, not object masses or historical priors. -/
def twoStateWeight (i : Fin 2) : Nat := if i = 0 then 2 else 1

def twoStateProposal (i j : Fin 2) : Nat :=
  if i = 0 then (if j = 0 then 1 else 3)
  else (if j = 0 then 1 else 3)

theorem twoState_rows_equal_four :
    (∀ i : Fin 2, (∑ j : Fin 2, twoStateProposal i j) = 4) := by decide

theorem twoState_rejections_checked :
    rejectedStay twoStateWeight twoStateProposal 4 0 = 5 ∧
    rejectedStay twoStateWeight twoStateProposal 4 1 = 0 ∧
    fullTransport twoStateWeight twoStateProposal 4 0 1 = 1 ∧
    fullTransport twoStateWeight twoStateProposal 4 1 0 = 1 := by decide

end Conde1963.CircularMCMC
