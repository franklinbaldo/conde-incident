import Conde1963.SimulatorBridge

/-!
# Soundness obligations for error-bounded model outputs

The physical simulator has not supplied certified terminal enclosures.
An enclosure is a set of *possible predicted events* for EACH parameter
state, not a probability, an observed event or a finite-grid summary.

The `soundForPredictions` field is a proof obligation about the simulator's
own outputs. Its existence does not authenticate the simulator, initial
historical observations or material survival. `GroundImpactAdmissible`
is an additional required audit gate, and its Bool fields themselves
must be justified from external documentary/numerical validation.
-/

namespace Conde1963

/-- A parameter-indexed envelope must contain every event predicted by
    the model at that parameter. It may be broad or even unbounded.
    `audit` is DECLARED metadata, not historical proof by itself. -/
structure ImpactEnvelope (α : Type) where
  audit : SimulationAudit
  predict : α → Option TimeLocation
  contains : α → TimeLocation → Prop
  soundForPredictions : ∀ p event, predict p = some event → contains p event

/-- A physically gated, nonvacuous conditional exclusion. -/
def EnclosureExclusion {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  ExcludesConde constraints model.predict inConde

/-- A physically gated, nonvacuous conditional forcing. -/
def EnclosureForcing {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  ForcesConde constraints model.predict inConde

/-- An alternative location requires an actual predicted event for every
    survivor, a covered window and proven disjointness from Conde. -/
def EnclosureOtherWindow {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inOtherWindow inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  IdentifiesOtherWindow constraints model.predict inOtherWindow inConde

/-- If every potentially predicted event lies outside Conde, the
    *model-conditional* conclusion follows, including states with no
    predicted ground impact. No claim of impact elsewhere follows. -/
theorem covered_envelope_excludes_conde {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : HasCandidate constraints)
    (separate : ∀ p event, Allowed constraints p →
      model.contains p event → ¬ inConde event) :
    EnclosureExclusion model constraints inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp event hevent
  exact separate p event hp (model.soundForPredictions p event hevent)

/-- Existence of a ground-impact prediction for every admissible state is
    an extra obligation; a `none` output cannot be silently localized. -/
theorem covered_envelope_forces_conde {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : HasCandidate constraints)
    (allImpact : ∀ p, Allowed constraints p →
      ∃ event, model.predict p = some event)
    (inside : ∀ p event, Allowed constraints p →
      model.contains p event → inConde event) :
    EnclosureForcing model constraints inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp
  obtain ⟨event, hevent⟩ := allImpact p hp
  exact ⟨event, hevent, inside p event hp
    (model.soundForPredictions p event hevent)⟩

/-- An alternative time/place region is identified only in a fully
    gated conditional model whose predicted impacts all lie there.
    `disjoint` is a premise to prove from actual region boundaries. -/
theorem covered_envelope_identifies_other_window {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inOtherWindow inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : HasCandidate constraints)
    (allImpact : ∀ p, Allowed constraints p →
      ∃ event, model.predict p = some event)
    (within : ∀ p event, Allowed constraints p →
      model.contains p event → inOtherWindow event)
    (disjoint : ∀ event, inOtherWindow event → ¬ inConde event) :
    EnclosureOtherWindow model constraints inOtherWindow inConde := by
  refine ⟨gate, ⟨⟨survives, ?_⟩, disjoint⟩⟩
  intro p hp
  obtain ⟨event, hevent⟩ := allImpact p hp
  exact ⟨event, hevent, within p event hp
    (model.soundForPredictions p event hevent)⟩

/-- A window intersecting Conde blocks the UNIFORM SEPARATION certificate.
    Intersection alone does NOT establish that any true predicted impact is
    at that point. -/
theorem overlap_refutes_uniform_envelope_separation {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inConde : TimeLocation → Prop)
    (p : α) (event : TimeLocation)
    (hp : Allowed constraints p)
    (covered : model.contains p event)
    (inside : inConde event) :
    ¬ (∀ q loc, Allowed constraints q →
      model.contains q loc → ¬ inConde loc) := by
  intro allOutside
  exact allOutside p event hp covered inside

/-- A declared numerical audit with missing gates cannot be laundered into
    a certified geographic verdict merely by attaching an envelope. -/
theorem missing_ground_audit_blocks_enclosure_exclusion {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inConde : TimeLocation → Prop)
    (missing : ¬ GroundImpactAdmissible model.audit) :
    ¬ EnclosureExclusion model constraints inConde := by
  intro conclusion
  exact missing conclusion.1

/-- The Castor source snapshot explicitly has only an altitude-threshold
    event and missing independent historical validation. It cannot satisfy
    the gated conditional envelope verdict on its declared audit status. -/
theorem castor_declared_audit_blocks_enclosure_exclusion {α : Type}
    (model : ImpactEnvelope α)
    (constraints : List (ParameterConstraint α))
    (inConde : TimeLocation → Prop)
    (current : model.audit = castorCurrentDeclaredAudit) :
    ¬ EnclosureExclusion model constraints inConde := by
  intro conclusion
  have gated : GroundImpactAdmissible castorCurrentDeclaredAudit := by
    rw [← current]
    exact conclusion.1
  exact castor_current_threshold_blocks_ground_impact gated

/-- Pure symbolic counterexample. Inspecting only the non-impact candidate
    of a finite grid cannot exclude Conde across the full Bool domain.
    `event` is an abstract argument, NOT a claimed time or coordinate. -/
def illustrativeFiniteGridPrediction
    (event : TimeLocation) (p : Bool) : Option TimeLocation :=
  if p then none else some event

theorem finite_sample_nonimpact_does_not_exclude_globally
    (event : TimeLocation) :
    (∀ p : Bool, p ∈ [true] →
      illustrativeFiniteGridPrediction event p = none) ∧
    ¬ ExcludesConde ([] : List (ParameterConstraint Bool))
      (illustrativeFiniteGridPrediction event) (fun _ => True) := by
  constructor
  · intro p hp
    have isTrue : p = true := by simpa using hp
    subst p
    simp [illustrativeFiniteGridPrediction]
  · intro excluded
    have allowed : Allowed ([] : List (ParameterConstraint Bool)) false := by
      intro c hc
      cases hc
    have predicted : illustrativeFiniteGridPrediction event false =
        some event := by simp [illustrativeFiniteGridPrediction]
    exact excluded.2 false allowed event predicted trivial

end Conde1963
