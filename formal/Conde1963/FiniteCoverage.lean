import Conde1963.ScenarioEnclosures

/-!
# Certified finite-screen boundary for unresolved orbital source branches

C25#1 (L118) and C179#1 (L839) describe SECONDARY orbital
material; the competing site RAAN remains unauthenticated. They are
alternative source scenarios, not simultaneous independently measured
constraints. C131#1 and C197#1 (L502/L905) reference ONE NASA/Goddard
15-Nov-1963 bulletin stating a catalogue decay day, not a terminal fix.

A grid can establish EXISTENCE when it contains a surviving parameter.
Its EMPTY output cannot establish global contradiction or eliminate a
source branch unless an independently justified exhaustive coverage proof
covers the ENTIRE admissible domain. Neither Bool reports nor this file
authenticate the documentary source, the physical model, ground impact,
continuous-domain coverage, or historical conditions.
-/

namespace Conde1963

/-- The Boolean classifier must be proved correct at every grid point.
    This is a logical obligation supplied by the caller, NOT a promise
    that its grid exhausts an unbounded/continuous parameter domain. -/
structure FiniteScenarioScreen (α : Type)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) where
  grid : List α
  accepts : α → Bool
  exactOnGrid : ∀ p, p ∈ grid →
    (accepts p = true ↔ AlternativeAllowed common left right p)

/-- Pass/fail list of *sampled* candidate states; never a fitted orbit. -/
def Passing {α : Type}
    {common : List (ParameterConstraint α)}
    {left right : ParameterConstraint α}
    (screen : FiniteScenarioScreen α common left right) : List α :=
  screen.grid.filter screen.accepts

/-- This must be separately DEMONSTRATED, not inferred from list length,
    tight grid spacing, or the absence of simulated impacts. -/
def DomainCoverage {α : Type}
    {common : List (ParameterConstraint α)}
    {left right : ParameterConstraint α}
    (screen : FiniteScenarioScreen α common left right) : Prop :=
  ∀ p, AlternativeAllowed common left right p → p ∈ screen.grid

/-- Soundness and completeness are relative ONLY to the supplied grid. -/
theorem passing_iff_sampled_admissible {α : Type}
    {common : List (ParameterConstraint α)}
    {left right : ParameterConstraint α}
    (screen : FiniteScenarioScreen α common left right) (p : α) :
    p ∈ Passing screen ↔
      p ∈ screen.grid ∧ AlternativeAllowed common left right p := by
  constructor
  · intro hp
    obtain ⟨sampled, accepted⟩ := List.mem_filter.mp hp
    exact ⟨sampled, (screen.exactOnGrid p sampled).1 accepted⟩
  · rintro ⟨sampled, admitted⟩
    exact List.mem_filter.mpr ⟨sampled,
      (screen.exactOnGrid p sampled).2 admitted⟩

/-- A surviving grid witness proves a NONEMPTY global conditional domain.
    This is one-way: an empty grid does NOT refute existence. -/
theorem passing_witness_proves_global_nonempty {α : Type}
    {common : List (ParameterConstraint α)}
    {left right : ParameterConstraint α}
    (screen : FiniteScenarioScreen α common left right)
    (p : α) (hp : p ∈ Passing screen) :
    AlternativeHasCandidate common left right := by
  exact ⟨p, (passing_iff_sampled_admissible screen p).1 hp |>.2⟩

/-- Empty sampled output excludes ALL candidates only if an externally
    proven domain-coverage theorem also holds. -/
theorem empty_passing_implies_empty_domain_with_coverage {α : Type}
    {common : List (ParameterConstraint α)}
    {left right : ParameterConstraint α}
    (screen : FiniteScenarioScreen α common left right)
    (coverage : DomainCoverage screen)
    (empty : Passing screen = []) :
    ¬ AlternativeHasCandidate common left right := by
  rintro ⟨p, admitted⟩
  have hp : p ∈ Passing screen :=
    (passing_iff_sampled_admissible screen p).2
      ⟨coverage p admitted, admitted⟩
  rw [empty] at hp
  cases hp

/-- A filter never manufactures a new physical state absent from its grid. -/
theorem passing_never_creates_parameter {α : Type}
    {common : List (ParameterConstraint α)}
    {left right : ParameterConstraint α}
    (screen : FiniteScenarioScreen α common left right)
    (p : α) (hp : p ∈ Passing screen) :
    p ∈ screen.grid :=
  (passing_iff_sampled_admissible screen p).1 hp |>.1

/-- An empty EXHAUSTIVE screen of the right branch is sufficient to prove
    that branch impossible. Screening the other branch is irrelevant. -/
theorem exhaustive_empty_right_screen_eliminates_right_branch {α : Type}
    (common : List (ParameterConstraint α))
    (right : ParameterConstraint α)
    (screen : FiniteScenarioScreen α common right (fun _ => False))
    (coverage : DomainCoverage screen)
    (empty : Passing screen = []) :
    ¬ HasCandidate (right :: common) := by
  intro rightHas
  obtain ⟨p, hp⟩ := rightHas
  have inUnion : AlternativeAllowed common right (fun _ => False) p :=
    left_branch_in_alternatives common right (fun _ => False) p hp
  exact (empty_passing_implies_empty_domain_with_coverage
    screen coverage empty) ⟨p, inUnion⟩

/-- Only AFTER a coverage proof eliminates the rival orbital scenario may
    exclusion proved in the left scenario become a GLOBAL exclusion; a
    validated ground-impact gate and nonempty left branch are still needed. -/
theorem exhaustive_right_screen_licenses_left_exclusion {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (leftExcluded : ExcludesConde (left :: common) model.predict inConde)
    (screen : FiniteScenarioScreen α common right (fun _ => False))
    (coverage : DomainCoverage screen)
    (empty : Passing screen = []) :
    AlternativeEnclosureExclusion model common left right inConde := by
  apply proven_empty_right_branch_allows_left_exclusion
    model common left right inConde gate leftExcluded
  exact exhaustive_empty_right_screen_eliminates_right_branch
    common right screen coverage empty

/-- Tiny symbolic countermodel: examining [true] misses the admissible
    false state. These are Boolean LOGICAL states, not 1963 observations. -/
def illustrativeLeftBranch (p : Bool) : Prop := p = false
def illustrativeRightBranch (_ : Bool) : Prop := False

def illustrativeIncompleteScreen :
    FiniteScenarioScreen Bool [] illustrativeLeftBranch illustrativeRightBranch :=
  { grid := [true]
    accepts := fun _ => false
    exactOnGrid := by
      intro p hp
      have htrue : p = true := by simpa using hp
      subst p
      simp [AlternativeAllowed, Allowed, illustrativeLeftBranch,
        illustrativeRightBranch] }

/-- A perfectly correct finite screen may be empty while the global union
    is NONEMPTY. In particular, the coverage obligation is genuinely extra. -/
theorem empty_sample_does_not_eliminate_unseen_branch :
    Passing illustrativeIncompleteScreen = [] ∧
    AlternativeHasCandidate [] illustrativeLeftBranch illustrativeRightBranch ∧
    ¬ DomainCoverage illustrativeIncompleteScreen := by
  constructor
  · rfl
  constructor
  · refine ⟨false, ?_⟩
    simp [AlternativeAllowed, Allowed, illustrativeLeftBranch]
  · intro coverage
    have admitted : AlternativeAllowed []
        illustrativeLeftBranch illustrativeRightBranch false := by
      simp [AlternativeAllowed, Allowed, illustrativeLeftBranch]
    have sampled : false ∈ illustrativeIncompleteScreen.grid :=
      coverage false admitted
    simp [illustrativeIncompleteScreen] at sampled

end Conde1963
