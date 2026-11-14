import Conde1963.CircularMCMC

/-!
Full finite Hastings mass transport with explicit rejection stay.

For a finite list enumerating possible destinations, assume the proposal counts
from the source sum to a *common denominator* D. Corrected accepted mass
is min(wᵢqᵢⱼ, wⱼqⱼᵢ). The rejected remainder remains at the source.

This closes conservation and stationarity of the weighted mass transport,
not a proof of RNG code, mixing rates or a historical orbital posterior.
The list must enumerate states exactly once to interpret its aggregate as a
stochastic transition row. No historical 1963 data is used here.
-/

namespace Conde1963.CircularMCMC

/-- Total Hastings-accepted mass from i over a finite list of destinations. -/
def acceptedRow {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (i : State) : Nat :=
  (states.map (fun j => hastingsFlow weight proposal i j)).sum

/-- The accepted sum never exceeds the sum of forward proposal capacities.
    This does not assume q symmetric or positive in the reverse direction. -/
theorem acceptedRow_le_proposed {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (i : State) :
    acceptedRow states weight proposal i ≤
      weight i * (states.map (fun j => proposal i j)).sum := by
  induction states with
  | nil => simp [acceptedRow]
  | cons j rest ih =>
    simp only [acceptedRow, List.map_cons, List.sum_cons] at ih ⊢
    calc
      hastingsFlow weight proposal i j +
          (rest.map (fun j => hastingsFlow weight proposal i j)).sum ≤
        weight i * proposal i j +
          weight i * (rest.map (fun j => proposal i j)).sum :=
            Nat.add_le_add (hastingsFlow_le_forward weight proposal i j) ih
      _ = weight i *
          (proposal i j + (rest.map (fun j => proposal i j)).sum) := by
            rw [Nat.mul_add]

/-- The denominator D is not inferred from a single proposal cell.
    It is checked against the whole source row. -/
theorem acceptedRow_le_capacity {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (denom : Nat) (i : State)
    (hrow : (states.map (fun j => proposal i j)).sum = denom) :
    acceptedRow states weight proposal i ≤ weight i * denom := by
  have h := acceptedRow_le_proposed states weight proposal i
  rw [hrow] at h
  exact h

/-- Self-mass from rejected proposals, at an integer weighted mass scale. -/
def rejectedStay {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (denom : Nat) (i : State) : Nat :=
  weight i * denom - acceptedRow states weight proposal i

/-- A full pairwise mass transfer adds rejected attempts on the diagonal.
    State enumeration must contain every state exactly once to sum this into
    a normalized transition matrix. -/
def fullTransport {State : Type} [DecidableEq State] (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (denom : Nat) (i j : State) : Nat :=
  hastingsFlow weight proposal i j +
    (if i = j then rejectedStay states weight proposal denom i else 0)

/-- Aggregate outgoing mass counts the rejected self-stay exactly once. -/
def fullOut {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (denom : Nat) (i : State) : Nat :=
  acceptedRow states weight proposal i +
    rejectedStay states weight proposal denom i

/-- A valid common proposal row denominator makes the rejection remainder
    well-defined without Nat subtraction silently truncating an excess. -/
theorem fullTransport_row_conservation {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (denom : Nat) (i : State)
    (hrow : (states.map (fun j => proposal i j)).sum = denom) :
    fullOut states weight proposal denom i = weight i * denom := by
  have hbound := acceptedRow_le_capacity states weight proposal denom i hrow
  simp only [fullOut, rejectedStay]
  omega

/-- The full transport, including rejected proposals, is reversible
    pairwise even if proposal rates are asymmetric. -/
theorem fullTransport_detailed_balance {State : Type} [DecidableEq State]
    (states : List State) (weight : State → Nat)
    (proposal : State → State → Nat) (denom : Nat) (i j : State) :
    fullTransport states weight proposal denom i j =
      fullTransport states weight proposal denom j i := by
  by_cases h : i = j
  · subst j; rfl
  · simp [fullTransport, h, Ne.symm h, hastingsFlow_detailed_balance]

/-- Incoming accepted mass plus self-held rejection mass. -/
def fullIn {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (denom : Nat) (i : State) : Nat :=
  (states.map (fun j => hastingsFlow weight proposal j i)).sum +
    rejectedStay states weight proposal denom i

/-- Incoming mass preserves the unnormalized target weight, conditional on
    the proposal row sum. This is stationarity of exact finite mass transport,
    *not* a convergence theorem or a floating-point kernel audit. -/
theorem fullTransport_stationary {State : Type} (states : List State)
    (weight : State → Nat) (proposal : State → State → Nat)
    (denom : Nat) (i : State)
    (hrow : (states.map (fun j => proposal i j)).sum = denom) :
    fullIn states weight proposal denom i = weight i * denom := by
  have hs := hastingsFlow_list_balance weight proposal i states
  have hb := fullTransport_row_conservation states weight proposal denom i hrow
  simp only [fullIn, fullOut, acceptedRow] at *
  rw [← hs]
  exact hb

/-- A small asymmetric two-state proposal with common denominator 4. -/
def twoStateWeight (i : Bool) : Nat := if i then 2 else 1

def twoStateProposal (_i j : Bool) : Nat := if j then 1 else 3

theorem twoState_rows_equal_four :
    ∀ i : Bool,
      ([true, false].map (fun j => twoStateProposal i j)).sum = 4 := by decide

/-- Holds 5 and 0 units; directed off-diagonal accepted mass is 1 both ways.
    A source-only symmetric-Metropolis acceptance would fail this check. -/
theorem twoState_rejections_checked :
    rejectedStay [true, false] twoStateWeight twoStateProposal 4 true = 5 ∧
    rejectedStay [true, false] twoStateWeight twoStateProposal 4 false = 0 ∧
    fullTransport [true, false] twoStateWeight twoStateProposal 4 true false = 1 ∧
    fullTransport [true, false] twoStateWeight twoStateProposal 4 false true = 1 := by decide

end Conde1963.CircularMCMC
