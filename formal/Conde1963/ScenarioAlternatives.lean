import Conde1963.Enclosures

/-!
# Disjunctive orbital element scenarios, not a synthetic merged TLE

Provenance: the fixed matrix C25#1 (line 118) and C179#1 (line 839)
records *reproduced* orbit data, not independently authenticated primary
instrumental solutions. AGENTS.md records incompatible RAAN values
284.1520° versus approximately 198.5261°. Which element series is
valid, in which frame/epoch, is NOT established here.

The predicates below are alternatives supplied by an external source
audit. They are NOT claims that either series is correct, nor calibrated
trajectory restrictions. In particular A OR B must not silently become
A AND B; an inconsistent intersection proves neither alternative false.
No terminal location, impact or probability is asserted.
-/

namespace Conde1963

/-- Parameters satisfy common accepted premises and at least one
    unresolved alternative element-data scenario. -/
def AlternativeAllowed {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) (p : α) : Prop :=
  Allowed common p ∧ (left p ∨ right p)

def AlternativeHasCandidate {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) : Prop :=
  ∃ p, AlternativeAllowed common left right p

/-- Geographic verdicts are conditional on the *union* of the scenarios.
    Their logical definitions do not assign historical truth to either. -/
def AlternativeForcesConde {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop) : Prop :=
  AlternativeHasCandidate common left right ∧
  ∀ p, AlternativeAllowed common left right p →
    ∃ event, impact p = some event ∧ inConde event

def AlternativeExcludesConde {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop) : Prop :=
  AlternativeHasCandidate common left right ∧
  ∀ p, AlternativeAllowed common left right p →
    ∀ event, impact p = some event → ¬ inConde event

theorem left_branch_in_alternatives {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) (p : α)
    (h : Allowed (left :: common) p) :
    AlternativeAllowed common left right p := by
  exact ⟨narrowing_never_adds_parameters common left p h,
    Or.inl (h left (by simp))⟩

theorem right_branch_in_alternatives {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) (p : α)
    (h : Allowed (right :: common) p) :
    AlternativeAllowed common left right p := by
  exact ⟨narrowing_never_adds_parameters common right p h,
    Or.inr (h right (by simp))⟩

/-- A candidate in the union belongs to at least one actual branch,
    without combining incompatible source families. -/
theorem alternative_iff_either_branch {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) (p : α) :
    AlternativeAllowed common left right p ↔
      Allowed (left :: common) p ∨ Allowed (right :: common) p := by
  constructor
  · intro h
    rcases h.2 with hl | hr
    · left
      intro c hc
      rcases List.mem_cons.mp hc with eq | old
      · subst c
        exact hl
      · exact h.1 c old
    · right
      intro c hc
      rcases List.mem_cons.mp hc with eq | old
      · subst c
        exact hr
      · exact h.1 c old
  · intro h
    rcases h with hl | hr
    · exact left_branch_in_alternatives common left right p hl
    · exact right_branch_in_alternatives common left right p hr

theorem alternative_has_candidate_iff_branches {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) :
    AlternativeHasCandidate common left right ↔
      HasCandidate (left :: common) ∨
      HasCandidate (right :: common) := by
  constructor
  · rintro ⟨p, hp⟩
    rcases (alternative_iff_either_branch common left right p).1 hp with hl | hr
    · exact Or.inl ⟨p, hl⟩
    · exact Or.inr ⟨p, hr⟩
  · intro h
    rcases h with ⟨p, hp⟩ | ⟨p, hp⟩
    · exact ⟨p, left_branch_in_alternatives common left right p hp⟩
    · exact ⟨p, right_branch_in_alternatives common left right p hp⟩

theorem alternatives_empty_iff_both_branches_empty {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) :
    (¬ AlternativeHasCandidate common left right) ↔
      (¬ HasCandidate (left :: common) ∧
       ¬ HasCandidate (right :: common)) := by
  constructor
  · intro h
    constructor
    · intro hl
      exact h ((alternative_has_candidate_iff_branches common left right).2
        (Or.inl hl))
    · intro hr
      exact h ((alternative_has_candidate_iff_branches common left right).2
        (Or.inr hr))
  · intro h union
    rcases (alternative_has_candidate_iff_branches common left right).1 union with hl | hr
    · exact h.1 hl
    · exact h.2 hr

/-- Extra common evidence narrows, never expands, the union, but may
    eliminate one or both branches. The latter is a consistency problem. -/
theorem alternative_common_narrowing {α : Type}
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α) (p : α)
    (h : AlternativeAllowed (extra :: common) left right p) :
    AlternativeAllowed common left right p := by
  exact ⟨narrowing_never_adds_parameters common extra p h.1, h.2⟩

theorem alternative_common_narrowing_requires_witness {α : Type}
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (survives : AlternativeHasCandidate (extra :: common) left right) :
    AlternativeHasCandidate common left right := by
  obtain ⟨p, hp⟩ := survives
  exact ⟨p, alternative_common_narrowing common extra left right p hp⟩

/-- Verdict over a union requires every surviving branch to agree.
    One branch being decisive is insufficient for a union-wide claim. -/
theorem branches_force_alternative {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop)
    (leftForced : ForcesConde (left :: common) impact inConde)
    (rightForced : ForcesConde (right :: common) impact inConde) :
    AlternativeForcesConde common left right impact inConde := by
  refine ⟨(alternative_has_candidate_iff_branches common left right).2
    (Or.inl leftForced.1), ?_⟩
  intro p hp
  rcases (alternative_iff_either_branch common left right p).1 hp with hl | hr
  · exact leftForced.2 p hl
  · exact rightForced.2 p hr

theorem branches_exclude_alternative {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop)
    (leftExcludes : ExcludesConde (left :: common) impact inConde)
    (rightExcludes : ExcludesConde (right :: common) impact inConde) :
    AlternativeExcludesConde common left right impact inConde := by
  refine ⟨(alternative_has_candidate_iff_branches common left right).2
    (Or.inl leftExcludes.1), ?_⟩
  intro p hp event hevent
  rcases (alternative_iff_either_branch common left right p).1 hp with hl | hr
  · exact leftExcludes.2 p hl event hevent
  · exact rightExcludes.2 p hr event hevent

/-- Two admitted abstract predictions in opposite regions prevent either
    decisive location statement for the union of scenarios. They are
    *mathematical witnesses*, not recovered historical trajectories. -/
theorem conflicting_branch_witnesses_leave_alternative_indeterminate {α : Type}
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop)
    (pInside pOutside : α)
    (hin : Allowed (left :: common) pInside)
    (hout : Allowed (right :: common) pOutside)
    (eventInside eventOutside : TimeLocation)
    (impactInside : impact pInside = some eventInside)
    (impactOutside : impact pOutside = some eventOutside)
    (inside : inConde eventInside)
    (outside : ¬ inConde eventOutside) :
    ¬ AlternativeForcesConde common left right impact inConde ∧
    ¬ AlternativeExcludesConde common left right impact inConde := by
  constructor
  · intro forced
    obtain ⟨event, predicted, located⟩ :=
      forced.2 pOutside (right_branch_in_alternatives common left right pOutside hout)
    have same : event = eventOutside := Option.some.inj
      (predicted.symm.trans impactOutside)
    exact outside (same ▸ located)
  · intro excluded
    exact excluded.2 pInside
      (left_branch_in_alternatives common left right pInside hin)
      eventInside impactInside inside

/-- A deliberately tiny *countermodel* to intersecting unresolved
    elements: both exclusive branches have candidates but their conjunction
    has none. Bool is NOT a satellite parameter or empirical observation. -/
theorem intersecting_alternatives_can_falsely_erase_all_candidates :
    AlternativeHasCandidate ([] : List (ParameterConstraint Bool))
      (fun p => p = true) (fun p => p = false) ∧
    ¬ HasCandidate ([(fun p : Bool => p = true),
      (fun p : Bool => p = false)]) := by
  constructor
  · refine ⟨true, ?_⟩
    constructor
    · intro c hc
      cases hc
    · exact Or.inl rfl
  · intro h
    obtain ⟨p, hp⟩ := h
    have ht : p = true := hp (fun q => q = true) (by simp)
    have hf : p = false := hp (fun q => q = false) (by simp)
    rw [ht] at hf
    cases hf

end Conde1963
