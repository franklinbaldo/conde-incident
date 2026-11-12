import Conde1963.Interactions

/-!
# Conditional scientific outcomes (issue #15)

This module NEVER says where NORAD 528 physically fell. It specifies the
minimal logical certificates needed to publish any geographic conclusion
after independently justified sources, calibrated physical integration and
holdouts. A finite grid is not a complete continuous parameter space.

A missing predicted impact (Option.none) is not an impact elsewhere.
The metadata day C131/C197 is not admitted as a physical restriction.
-/

namespace Conde1963

/-- Every admissible state produces a *predicted* impact in the selected
    non-Conde window, and the window is geometrically disjoint from Conde.
    This is stronger than excluding Conde: it requires a predicted impact
    for every surviving parameter state. It makes no measured-event claim. -/
def IdentifiesOtherWindow {α : Type}
    (constraints : List (ParameterConstraint α))
    (impact : α → Option TimeLocation)
    (inOtherWindow inConde : TimeLocation → Prop) : Prop :=
  ImpactInside constraints impact inOtherWindow ∧
  (∀ event, inOtherWindow event → ¬ inConde event)

/-- A certified outside window logically excludes Conde *in that scenario*.
    Disjointness is a required premise, never guessed from a label. -/
theorem other_window_conditionally_excludes_conde {α : Type}
    (constraints : List (ParameterConstraint α))
    (impact : α → Option TimeLocation)
    (inOtherWindow inConde : TimeLocation → Prop)
    (outside : IdentifiesOtherWindow constraints impact inOtherWindow inConde) :
    ExcludesConde constraints impact inConde := by
  refine ⟨outside.1.1, ?_⟩
  intro p hp event hevent
  obtain ⟨other, hother, hwindow⟩ := outside.1.2 p hp
  have same : event = other :=
    Option.some.inj (hevent.symm.trans hother)
  exact outside.2 event (same.symm ▸ hwindow)

/-- An outside-window classification cannot coexist with a Conde-forced
    classification on one nonempty consistent constraint collection. -/
theorem other_window_and_forced_conde_conflict {α : Type}
    (constraints : List (ParameterConstraint α))
    (impact : α → Option TimeLocation)
    (inOtherWindow inConde : TimeLocation → Prop)
    (outside : IdentifiesOtherWindow constraints impact inOtherWindow inConde)
    (forced : ForcesConde constraints impact inConde) : False := by
  exact forced_and_excluded_conde_conflict constraints impact inConde
    forced (other_window_conditionally_excludes_conde
      constraints impact inOtherWindow inConde outside)

/-- A genuine new constraint preserves an old outside-window conclusion
    ONLY if at least one parameter state remains feasible. -/
theorem other_window_persists_under_consistent_narrowing {α : Type}
    (constraints : List (ParameterConstraint α))
    (extra : ParameterConstraint α)
    (impact : α → Option TimeLocation)
    (inOtherWindow inConde : TimeLocation → Prop)
    (old : IdentifiesOtherWindow constraints impact inOtherWindow inConde)
    (survives : HasCandidate (extra :: constraints)) :
    IdentifiesOtherWindow (extra :: constraints) impact inOtherWindow inConde := by
  refine ⟨⟨survives, ?_⟩, old.2⟩
  intro p hp
  exact old.1.2 p (narrowing_never_adds_parameters constraints extra p hp)

/-- If one admitted state predicts impact inside Conde and another state
    predicts impact outside OR predicts no impact, the resulting physical
    scenario is indecisive about *forced* versus *excluded* Conde. -/
def MixedCondeOutcomes {α : Type}
    (constraints : List (ParameterConstraint α))
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop) : Prop :=
  (∃ p event, Allowed constraints p ∧
      impact p = some event ∧ inConde event) ∧
  (∃ p, Allowed constraints p ∧
      (impact p = none ∨
        ∃ event, impact p = some event ∧ ¬ inConde event))

theorem mixed_outcomes_refute_both_decisive_conde_claims {α : Type}
    (constraints : List (ParameterConstraint α))
    (impact : α → Option TimeLocation)
    (inConde : TimeLocation → Prop)
    (mixed : MixedCondeOutcomes constraints impact inConde) :
    ¬ ForcesConde constraints impact inConde ∧
    ¬ ExcludesConde constraints impact inConde := by
  constructor
  · intro forced
    obtain ⟨p, hp, hpOutcome⟩ := mixed.2
    rcases hpOutcome with missing | outside
    · obtain ⟨event, hevent, _⟩ := forced.2 p hp
      rw [missing] at hevent
      cases hevent
    · obtain ⟨event, hevent, notConde⟩ := outside
      exact counterexample_refutes_forced_conde
        constraints impact inConde p hp event hevent notConde forced
  · intro excluded
    obtain ⟨p, event, hp, hevent, inside⟩ := mixed.1
    exact excluded.2 p hp event hevent inside

/-- No survivors under globally justified premises is inconsistent as a
    scenario, not a geographic discovery. These decisive classes require
    a witness and thus cannot coexist with global non-feasibility. -/
theorem contradictory_premises_preclude_decisive_classifications {α : Type}
    (constraints : List (ParameterConstraint α))
    (impact : α → Option TimeLocation)
    (inOtherWindow inConde : TimeLocation → Prop)
    (noModel : ¬ HasCandidate constraints) :
    (¬ ForcesConde constraints impact inConde) ∧
    (¬ ExcludesConde constraints impact inConde) ∧
    (¬ IdentifiesOtherWindow constraints impact inOtherWindow inConde) := by
  refine ⟨?_, ?_, ?_⟩
  · intro h
    exact noModel h.1
  · intro h
    exact noModel h.1
  · intro h
    exact noModel h.1.1

/-- The finite grid boundary: positive existence transfers from any
    inspected candidate to the full model; a grid with no survivors
    does NOT certify physical impossibility outside that grid. -/
def HasGridCandidate {α : Type}
    (grid : List α) (constraints : List (ParameterConstraint α)) : Prop :=
  ∃ p, p ∈ grid ∧ Allowed constraints p

theorem grid_witness_implies_global_witness {α : Type}
    (grid : List α) (constraints : List (ParameterConstraint α))
    (survives : HasGridCandidate grid constraints) :
    HasCandidate constraints := by
  obtain ⟨p, _, hp⟩ := survives
  exact ⟨p, hp⟩

/-- Tiny mathematical counterexample, never a historical orbit:
    a globally satisfiable model has no state on an empty search grid. -/
theorem grid_empty_does_not_mean_contradictory_premises :
    HasCandidate ([] : List (ParameterConstraint Unit)) ∧
    ¬ HasGridCandidate ([] : List Unit) [] := by
  constructor
  · refine ⟨(), ?_⟩
    intro constraint hmem
    cases hmem
  · intro h
    obtain ⟨p, hmem, _⟩ := h
    cases hmem

/-- An impact simulator can legitimately return None for every candidate.
    This *excludes a ground impact in Conde* within that chosen model
    but does not identify any alternative impact location. -/
def modelWithoutImpact (_ : Unit) : Option TimeLocation := none

theorem no_predicted_impact_excludes_conde_but_identifies_no_other_window :
    ExcludesConde ([] : List (ParameterConstraint Unit))
        modelWithoutImpact (fun _ => False) ∧
    ¬ IdentifiesOtherWindow ([] : List (ParameterConstraint Unit))
        modelWithoutImpact (fun _ => True) (fun _ => False) := by
  constructor
  · refine ⟨⟨(), ?_⟩, ?_⟩
    · intro constraint hmem
      cases hmem
    · intro p hp event hevent
      cases hevent
  · intro houtside
    have hp : Allowed ([] : List (ParameterConstraint Unit)) () := by
      intro constraint hmem
      cases hmem
    obtain ⟨event, hevent, _⟩ := houtside.1.2 () hp
    cases hevent

end Conde1963
