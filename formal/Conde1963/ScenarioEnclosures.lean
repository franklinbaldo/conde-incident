import Conde1963.ScenarioAlternatives

/-!
# Error-bounded outcomes across unresolved source scenarios

C25#1 (matrix L118) and C179#1 (L839) refer to secondary orbital
material with unresolved original custody. The project's older
284.1520° RAAN is another unverified source scenario. This module
never intersects them, picks a winning branch, or assigns a real
orbit, impact, probability, time or coordinate.

The results are statements about *all* surviving parameter states,
conditional on a grounded physical simulator, its sound event
enclosures, a ground-impact audit and a nonempty admissible domain.
The audit record consists of caller-provided declarations and is
NOT historical authentication. C131/C197 are the SAME NASA/Goddard
15 Nov 1963 document, recording decay day only, NOT terminal position.
-/

namespace Conde1963

/-- Exclusion under an unresolved disjunction of orbital source scenarios. -/
def AlternativeEnclosureExclusion {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  AlternativeExcludesConde common left right model.predict inConde

/-- Forcing Conde requires *every* survivor in *every* viable branch
    to have a modeled ground impact in Conde. -/
def AlternativeEnclosureForcing {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  AlternativeForcesConde common left right model.predict inConde

/-- A different window requires all survivors to predict a ground impact
    within it, plus a proof of disjointness from Conde. -/
def AlternativeEnclosureOtherWindow {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inOtherWindow inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  AlternativeHasCandidate common left right ∧
  (∀ p, AlternativeAllowed common left right p →
    ∃ event, model.predict p = some event ∧ inOtherWindow event) ∧
  (∀ event, inOtherWindow event → ¬ inConde event)

/-- Coverage outside Conde in EACH surviving source branch gives a
    *conditional*, nonvacuous exclusion across their UNION. -/
theorem covered_alternative_envelope_excludes_conde {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (separate : ∀ p event, AlternativeAllowed common left right p →
      model.contains p event → ¬ inConde event) :
    AlternativeEnclosureExclusion model common left right inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp event predicted
  exact separate p event hp (model.soundForPredictions p event predicted)

/-- A nonempty union, modeled impact for EACH survivor, and a
    sound envelope contained in Conde give a conditional forced verdict. -/
theorem covered_alternative_envelope_forces_conde {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allImpact : ∀ p, AlternativeAllowed common left right p →
      ∃ event, model.predict p = some event)
    (inside : ∀ p event, AlternativeAllowed common left right p →
      model.contains p event → inConde event) :
    AlternativeEnclosureForcing model common left right inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp
  obtain ⟨event, predicted⟩ := allImpact p hp
  exact ⟨event, predicted,
    inside p event hp (model.soundForPredictions p event predicted)⟩

/-- Other-location claim across an unresolved UNION must cover each
    surviving alternative, not just one favorable ephemeris. -/
theorem covered_alternative_envelope_identifies_other_window {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inOtherWindow inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allImpact : ∀ p, AlternativeAllowed common left right p →
      ∃ event, model.predict p = some event)
    (within : ∀ p event, AlternativeAllowed common left right p →
      model.contains p event → inOtherWindow event)
    (disjoint : ∀ event, inOtherWindow event → ¬ inConde event) :
    AlternativeEnclosureOtherWindow model common left right
      inOtherWindow inConde := by
  refine ⟨gate, survives, ?_, disjoint⟩
  intro p hp
  obtain ⟨event, predicted⟩ := allImpact p hp
  exact ⟨event, predicted,
    within p event hp (model.soundForPredictions p event predicted)⟩

/-- A true new common restriction preserves exclusion only after a
    surviving parameter witness has been provided. -/
theorem alternative_enclosure_exclusion_persists_with_witness {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop)
    (old : AlternativeEnclosureExclusion model common left right inConde)
    (survives : AlternativeHasCandidate (extra :: common) left right) :
    AlternativeEnclosureExclusion model (extra :: common) left right inConde := by
  refine ⟨old.1, ⟨survives, ?_⟩⟩
  intro p hp event predicted
  exact old.2.2 p
    (alternative_common_narrowing common extra left right p hp)
    event predicted

theorem alternative_enclosure_forcing_persists_with_witness {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop)
    (old : AlternativeEnclosureForcing model common left right inConde)
    (survives : AlternativeHasCandidate (extra :: common) left right) :
    AlternativeEnclosureForcing model (extra :: common) left right inConde := by
  refine ⟨old.1, ⟨survives, ?_⟩⟩
  intro p hp
  exact old.2.2 p
    (alternative_common_narrowing common extra left right p hp)

theorem alternative_enclosure_other_window_persists_with_witness {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (inOtherWindow inConde : TimeLocation → Prop)
    (old : AlternativeEnclosureOtherWindow model common left right
      inOtherWindow inConde)
    (survives : AlternativeHasCandidate (extra :: common) left right) :
    AlternativeEnclosureOtherWindow model (extra :: common) left right
      inOtherWindow inConde := by
  refine ⟨old.1, survives, ?_, old.2.2.2⟩
  intro p hp
  exact old.2.2.1 p
    (alternative_common_narrowing common extra left right p hp)

/-- Only if the OTHER branch is PROVEN empty may a result from the left
    branch certify the union. Neither RAAN branch is ruled out by this
    theorem or by the present historical data. -/
theorem proven_empty_right_branch_allows_left_exclusion {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (leftExcludes : ExcludesConde (left :: common) model.predict inConde)
    (rightEmpty : ¬ HasCandidate (right :: common)) :
    AlternativeEnclosureExclusion model common left right inConde := by
  refine ⟨gate, ⟨(alternative_has_candidate_iff_branches common left right).2
    (Or.inl leftExcludes.1), ?_⟩⟩
  intro p hp event predicted
  rcases (alternative_iff_either_branch common left right p).1 hp with hl | hr
  · exact leftExcludes.2 p hl event predicted
  · exact False.elim (rightEmpty ⟨p, hr⟩)

/-- Two surviving conflicting model predictions prevent BOTH decisive
    geographic verdicts, even if the same declared audit gate is true. -/
theorem opposing_branch_witnesses_block_gated_verdicts {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inConde : TimeLocation → Prop)
    (pInside pOutside : α)
    (hin : Allowed (left :: common) pInside)
    (hout : Allowed (right :: common) pOutside)
    (eventInside eventOutside : TimeLocation)
    (impactInside : model.predict pInside = some eventInside)
    (impactOutside : model.predict pOutside = some eventOutside)
    (inside : inConde eventInside)
    (outside : ¬ inConde eventOutside) :
    ¬ AlternativeEnclosureForcing model common left right inConde ∧
    ¬ AlternativeEnclosureExclusion model common left right inConde := by
  have h := conflicting_branch_witnesses_leave_alternative_indeterminate
    common left right model.predict inConde
    pInside pOutside hin hout eventInside eventOutside
    impactInside impactOutside inside outside
  constructor
  · intro forced
    exact h.1 forced.2
  · intro excluded
    exact h.2 excluded.2

/-- Missing empirical gate blocks all three conditional verdict types.
    This is a LOGICAL gate, not a claim that a Boolean audit flag is true. -/
theorem missing_ground_audit_blocks_all_alternative_verdicts {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inOtherWindow inConde : TimeLocation → Prop)
    (missing : ¬ GroundImpactAdmissible model.audit) :
    (¬ AlternativeEnclosureExclusion model common left right inConde) ∧
    (¬ AlternativeEnclosureForcing model common left right inConde) ∧
    (¬ AlternativeEnclosureOtherWindow model common left right
      inOtherWindow inConde) := by
  exact ⟨(fun cert => missing cert.1),
    (fun cert => missing cert.1), (fun cert => missing cert.1)⟩

/-- Current declared Castor altitude-threshold status fails this gate.
    It does NOT assert that an impact was absent in November 1963. -/
theorem castor_declared_audit_blocks_all_alternative_verdicts {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (inOtherWindow inConde : TimeLocation → Prop)
    (current : model.audit = castorCurrentDeclaredAudit) :
    (¬ AlternativeEnclosureExclusion model common left right inConde) ∧
    (¬ AlternativeEnclosureForcing model common left right inConde) ∧
    (¬ AlternativeEnclosureOtherWindow model common left right
      inOtherWindow inConde) := by
  apply missing_ground_audit_blocks_all_alternative_verdicts
  intro gate
  have currentGate : GroundImpactAdmissible castorCurrentDeclaredAudit := by
    rw [← current]
    exact gate
  exact castor_current_threshold_blocks_ground_impact currentGate

end Conde1963
