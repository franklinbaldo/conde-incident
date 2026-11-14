import Lean

/-!
# Structural certification of the synthetic circular MCMC prototype

These theorems describe exact, finite arithmetic. They do NOT formalize
floating-point sampling, the random-number generator, rank-Rhat, ESS, a
1963 observation model, or a historical posterior.

The state weights here are *unnormalized* and the integer proposal counts are
symmetric. In ordinary Metropolis-Hastings, the accepted off-diagonal flow is
`q(i,j) * min(w(i),w(j))` after the symmetric Hastings ratio cancels. We prove
its detailed balance and equal total incoming/outgoing accepted flow, without
silently assuming that an arbitrary asymmetric proposal has that property.

The angular proof is on the grid Z / 360000 Z, at millidegree resolution.
It proves the exact likelihood *gauge* for an unconstrained common lineage
offset. A concentrated offset prior can break that symmetry as a modeling
assumption; such a prior is not evidence of a physical 1963 anchor.
-/
namespace Conde1963.CircularMCMC

/-- An unnormalized target mass at each state and proposal multiplicities.
    Proposals are not automatically symmetric: the hypothesis is explicit. -/
def acceptedFlow {State : Type} (weight : State → Nat)
    (proposal : State → State → Nat) (src dst : State) : Nat :=
  Nat.min (weight src) (weight dst) * proposal src dst

/-- Exact detailed balance for symmetric proposals: the target-weighted
    accepted cross-state mass is reversible. No convergence is implied. -/
theorem acceptedFlow_detailed_balance {State : Type}
    (weight : State → Nat) (proposal : State → State → Nat)
    (symmetry : ∀ x y, proposal x y = proposal y x)
    (i j : State) :
    acceptedFlow weight proposal i j = acceptedFlow weight proposal j i := by
  simp [acceptedFlow, Nat.min_comm, symmetry i j]

/-- For an arbitrary *finite list* of states, reversibility balances the
    incoming and outgoing accepted flow at each state. This is not a theorem
    about RNG behavior, mixing, or normalized stay-put probabilities. -/
theorem acceptedFlow_list_balance {State : Type}
    (weight : State → Nat) (proposal : State → State → Nat)
    (symmetry : ∀ x y, proposal x y = proposal y x)
    (i : State) (states : List State) :
    (states.map (fun j => acceptedFlow weight proposal i j)).sum =
    (states.map (fun j => acceptedFlow weight proposal j i)).sum := by
  induction states with
  | nil => rfl
  | cons j rest ih =>
    simp only [List.map_cons, List.sum_cons]
    rw [acceptedFlow_detailed_balance weight proposal symmetry i j, ih]

/-- A concrete counterexample: without symmetric proposals the off-diagonal
    MH flow formula must not be used as a general Hastings correction. -/
theorem asymmetric_proposal_counterexample : acceptedFlow (fun _ : Bool => 2)
    (fun x y => if x == y then 0 else if x then 3 else 1)
    true false ≠
    acceptedFlow (fun _ : Bool => 2)
    (fun x y => if x == y then 0 else if x then 3 else 1)
    false true := by decide

/-- Only frozen model prediction and a lineage identifier are included. -/
structure CircularRow where
  observedMilliDeg : Int
  predictedMilliDeg : Int
  lineage : Nat
  deriving Repr

/-- Wrapped residual on the millidegree circle. One *shared* offset per group. -/
def residual (row : CircularRow) (phase : Int)
    (offset : Nat → Int) : Int :=
  (row.observedMilliDeg - row.predictedMilliDeg - phase - offset row.lineage) % 360000

/-- Shifting phase and counter-shifting *all* lineage offsets does not alter
    any conditional observation, even at the 0/360 degree seam. -/
theorem residual_gauge_invariant (row : CircularRow)
    (phase delta : Int) (offset : Nat → Int) :
    residual row (phase + delta) (fun g => offset g - delta) =
    residual row phase offset := by
  simp only [residual]
  congr 1
  omega

def residualVector (rows : List CircularRow) (phase : Int)
    (offset : Nat → Int) : List Int :=
  rows.map (fun row => residual row phase offset)

/-- A whole dependent corpus is invariant, not merely one duplicated datum. -/
theorem residualVector_gauge_invariant (rows : List CircularRow)
    (phase delta : Int) (offset : Nat → Int) :
    residualVector rows (phase + delta) (fun g => offset g - delta) =
    residualVector rows phase offset := by
  induction rows with
  | nil => rfl
  | cons row rest ih =>
    simp only [residualVector, List.map_cons] at *
    rw [residual_gauge_invariant, ih]

/-- Any specified conditional likelihood that depends solely on the wrapped
    residual vector has the same score along the whole gauge orbit. -/
theorem likelihood_gauge_invariant (Score : Type)
    (likelihood : List Int → Score) (rows : List CircularRow)
    (phase delta : Int) (offset : Nat → Int) :
    likelihood (residualVector rows (phase + delta)
      (fun g => offset g - delta)) =
    likelihood (residualVector rows phase offset) := by
  rw [residualVector_gauge_invariant]


/-- A shift with *fixed* bias does change a residual: the compensating
    transformation is essential, so a fixed externally calibrated anchor
    would change the inference problem. This example is entirely synthetic. -/
theorem fixed_bias_can_break_gauge :
    residual ⟨0, 0, 0⟩ 1 (fun _ => 0) ≠
    residual ⟨0, 0, 0⟩ 0 (fun _ => 0) := by decide

/-- No number of observations from the same unanchored lineage can identify
    an absolute phase: every proposed phase change has a compensating offset.
    This is structural non-injectivity, *not* a statement about a calibrated
    posterior, and says nothing about the geographical location of reentry. -/
theorem unanchored_phase_has_compensator (rows : List CircularRow)
    (phase delta : Int) (offset : Nat → Int) :
    ∃ offset' : Nat → Int,
      residualVector rows (phase + delta) offset' =
      residualVector rows phase offset := by
  exact ⟨(fun g => offset g - delta),
    residualVector_gauge_invariant rows phase delta offset⟩

end Conde1963.CircularMCMC
