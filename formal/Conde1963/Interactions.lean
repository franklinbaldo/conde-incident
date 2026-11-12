import Conde1963.MatrixEvidence

/-!
# Evidence interaction: when can another record really constrain a solution?

A second citation, an independent source and a genuinely discriminating
physical restriction are three different things. These implications certify
only the stated predicates, never a historical measurement or a fitted orbit.

The currently admitted documentary predicate is NASA's reported DECAY DAY
(C131/C197, the same report). Neither the Conde story (C01) nor a source-ID
count supplies an independently measured terminal orbital position.
-/

namespace Conde1963

/-- Genuine narrowing has three obligations: a surviving solution, domain
    inclusion, and an explicit old solution excluded by the new rule.
    Nonempty is essential: an impossible model must not "identify" Conde. -/
def StrictReduction {α : Type}
    (before after : List (ParameterConstraint α)) : Prop :=
  HasCandidate after ∧
  (∀ p, Allowed after p → Allowed before p) ∧
  ∃ eliminated, Allowed before eliminated ∧ ¬ Allowed after eliminated

/-- A record that has not been admitted to the selected scenario adds
    no restriction, regardless of its matrix label or citation count.
    This is NOT a judgment on its historical importance. -/
theorem non_admitted_source_does_not_narrow {α : Type}
    (records : List (SourcedConstraint α))
    (extra : SourcedConstraint α)
    (unadmitted : extra.use ≠ .admitted)
    (p : α) :
    AllowedFromSources (extra :: records) p ↔
      AllowedFromSources records p := by
  constructor
  · exact source_narrowing_never_adds_parameters records extra p
  · intro old record membership admitted
    rcases List.mem_cons.mp membership with same | previous
    · subst record
      exact False.elim (unadmitted admitted)
    · exact old record previous admitted

/-- Repeating the exact same predicate cannot eliminate any new parameter,
    even when the two documentary rows have different labels. -/
theorem repeated_filter_preserves_domain {α : Type}
    (records : List (ParameterConstraint α))
    (rule : ParameterConstraint α) (p : α) :
    Allowed (rule :: rule :: records) p ↔
      Allowed (rule :: records) p := by
  constructor
  · exact narrowing_never_adds_parameters (rule :: records) rule p
  · intro old c membership
    rcases List.mem_cons.mp membership with same | previous
    · subst c
      exact old rule (by simp)
    · exact old c previous

theorem repeated_filter_not_strict {α : Type}
    (records : List (ParameterConstraint α))
    (rule : ParameterConstraint α) :
    ¬ StrictReduction (rule :: records) (rule :: rule :: records) := by
  intro strict
  obtain ⟨_, _, eliminated, admitted, rejected⟩ := strict
  exact rejected ((repeated_filter_preserves_domain records rule eliminated).2 admitted)

/-- A new rule really reduces the feasible domain only when a retained
    candidate satisfies it AND a formerly admitted candidate fails it.
    Both must be justified outside the theorem by measurements and physics. -/
theorem witnessed_filter_strictly_reduces {α : Type}
    (records : List (ParameterConstraint α))
    (extra : ParameterConstraint α)
    (survivor eliminated : α)
    (survivorOld : Allowed records survivor)
    (survivorNew : extra survivor)
    (eliminatedOld : Allowed records eliminated)
    (eliminatedNew : ¬ extra eliminated) :
    StrictReduction records (extra :: records) := by
  refine ⟨⟨survivor, ?_⟩, ?_, ⟨eliminated, eliminatedOld, ?_⟩⟩
  · intro rule membership
    rcases List.mem_cons.mp membership with same | previous
    · subst rule
      exact survivorNew
    · exact survivorOld rule previous
  · intro p h
    exact narrowing_never_adds_parameters records extra p h
  · intro h
    exact eliminatedNew (h extra (by simp))

/-- NASA rows C131 and C197 describe the same reported date;
    counting that observation twice cannot constitute strict reduction. -/
theorem nasa_double_citation_not_strict :
    ¬ StrictReduction [ReportedDecayDay]
        [ReportedDecayDay, ReportedDecayDay] := by
  exact repeated_filter_not_strict [] ReportedDecayDay

/-- Surviving modelled ground impacts both inside and outside Conde
    refute BOTH decisive classifications. This is an indeterminate
    counterexample, not evidence that either trajectory occurred. -/
theorem contrary_impact_witnesses_refute_decisive_conde {α : Type}
    (records : List (ParameterConstraint α))
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop)
    (insideCandidate outsideCandidate : α)
    (insideAllowed : Allowed records insideCandidate)
    (outsideAllowed : Allowed records outsideCandidate)
    (insideEvent outsideEvent : TimeLocation)
    (insideImpact : impact insideCandidate = some insideEvent)
    (insideRegion : inConde insideEvent)
    (outsideImpact : impact outsideCandidate = some outsideEvent)
    (outsideRegion : ¬ inConde outsideEvent) :
    ¬ ForcesConde records impact inConde ∧
    ¬ ExcludesConde records impact inConde := by
  constructor
  · exact counterexample_refutes_forced_conde
      records impact inConde outsideCandidate outsideAllowed
      outsideEvent outsideImpact outsideRegion
  · intro excluded
    exact excluded.2 insideCandidate insideAllowed insideEvent insideImpact insideRegion

/-- Even an already established conditional forced-location statement
    persists under a new rule ONLY if some candidate still survives. -/
theorem forcing_persists_under_consistent_narrowing {α : Type}
    (records : List (ParameterConstraint α))
    (extra : ParameterConstraint α)
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop)
    (wasForced : ForcesConde records impact inConde)
    (stillFeasible : HasCandidate (extra :: records)) :
    ForcesConde (extra :: records) impact inConde := by
  refine ⟨stillFeasible, ?_⟩
  intro p hp
  exact wasForced.2 p (narrowing_never_adds_parameters records extra p hp)

end Conde1963
