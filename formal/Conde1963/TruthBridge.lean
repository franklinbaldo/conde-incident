import Conde1963.PairedEnclosures

/-!
# Historical truth is not the simulator's self-reported prediction

C25#1 and C179#1 (matrix lines 118, 839) reference unverified
secondary orbital reproductions. Their conflicting RAAN source scenarios
remain alternatives. C131#1 / C197#1 (lines 502, 905) come from the
same NASA/Goddard 15 Nov 1963 bulletin: a catalogued decay DAY,
not an observed terminal position. C01#1 is a Tupi/FBIS report,
not an independently verified impact.

An ImpactEnvelope's soundForPredictions only says its reported event
fits its own bounds. It does NOT bound the unobserved actual event.
A distinct, EXTERNALLY JUSTIFIED bridge is required even for conditional
statements about hypothetical physical ground impacts. Nothing here
supplies that bridge, a calibrated model, a real ground event, a
numeric error tolerance, or a true geographic outcome.
-/

namespace Conde1963

/-- The required additional empirical premise: for every state in the
    union of still-viable source scenarios, any *hypothetical actual*
    ground impact is covered by the simulator's enclosure. This is not
    derivable from the simulator's self-soundness theorem. Its proof
    would require separately justified physics, data and error bounds.
    The field is intentionally NOT populated for the Conde case. -/
structure TruthLink (α : Type)
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) where
  actualImpact : α → Option TimeLocation
  actualCovered : ∀ p event,
    AlternativeAllowed common left right p →
    actualImpact p = some event →
    model.contains p event

/-- This is a logical verdict about the hypothetical *actual* impact
    mapping, not about model.predict. The source and physics audit gates
    are additional caller-premises, never automatic certifications. -/
def TruthExcludesConde {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (truth : TruthLink α model common left right)
    (inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  AlternativeHasCandidate common left right ∧
  ∀ p, AlternativeAllowed common left right p →
    ∀ event, truth.actualImpact p = some event → ¬ inConde event

def TruthForcesConde {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (truth : TruthLink α model common left right)
    (inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  AlternativeHasCandidate common left right ∧
  ∀ p, AlternativeAllowed common left right p →
    ∃ event, truth.actualImpact p = some event ∧ inConde event

def TruthIdentifiesOtherWindow {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (truth : TruthLink α model common left right)
    (inOtherWindow inConde : TimeLocation → Prop) : Prop :=
  GroundImpactAdmissible model.audit ∧
  AlternativeHasCandidate common left right ∧
  (∀ p, AlternativeAllowed common left right p →
    ∃ event, truth.actualImpact p = some event ∧ inOtherWindow event) ∧
  (∀ event, inOtherWindow event → ¬ inConde event)

/-- A real-world event can enter a certified cell only by ADDING the
    external TruthLink premise. The pre-existing predicted-event lemma
    cannot prove this implication on its own. -/
theorem hypothetical_actual_event_has_certified_cell_bound {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (truth : TruthLink α model common left right)
    (p : α) (hp : AlternativeAllowed common left right p)
    (event : TimeLocation) (actual : truth.actualImpact p = some event) :
    ∃ cell, cell ∈ cover.cells ∧ cover.eventBounds cell event := by
  obtain ⟨cell, listed, inside⟩ := cover.covers p hp
  exact ⟨cell, listed,
    cover.boundsSound p cell event hp listed inside
      (truth.actualCovered p event hp actual)⟩

/-- Exclude actual impact in Conde only if the external truth link,
    ground-impact audit, nonempty domain AND globally separating cells
    have all been independently justified. No impact elsewhere follows. -/
theorem certified_truth_excludes_conde {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (truth : TruthLink α model common left right)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (outside : ∀ cell event, cell ∈ cover.cells →
      cover.eventBounds cell event → ¬ inConde event) :
    TruthExcludesConde model common left right truth inConde := by
  refine ⟨gate, survives, ?_⟩
  intro p hp event actual
  obtain ⟨cell, listed, bounded⟩ :=
    hypothetical_actual_event_has_certified_cell_bound
      model common left right cover truth p hp event actual
  exact outside cell event listed bounded

/-- Forcing a *physical* Conde impact additionally needs a true ground
    impact for every admissible state. A predicted threshold is not one. -/
theorem certified_truth_forces_conde {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (truth : TruthLink α model common left right)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allActual : ∀ p, AlternativeAllowed common left right p →
      ∃ event, truth.actualImpact p = some event)
    (inside : ∀ cell event, cell ∈ cover.cells →
      cover.eventBounds cell event → inConde event) :
    TruthForcesConde model common left right truth inConde := by
  refine ⟨gate, survives, ?_⟩
  intro p hp
  obtain ⟨event, actual⟩ := allActual p hp
  obtain ⟨cell, listed, bounded⟩ :=
    hypothetical_actual_event_has_certified_cell_bound
      model common left right cover truth p hp event actual
  exact ⟨event, actual, inside cell event listed bounded⟩

/-- Another physical window needs universal actual impact, enclosure
    coverage and a proved disjointness from Conde. -/
theorem certified_truth_identifies_other_window {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (truth : TruthLink α model common left right)
    (inOtherWindow inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allActual : ∀ p, AlternativeAllowed common left right p →
      ∃ event, truth.actualImpact p = some event)
    (within : ∀ cell event, cell ∈ cover.cells →
      cover.eventBounds cell event → inOtherWindow event)
    (disjoint : ∀ event, inOtherWindow event → ¬ inConde event) :
    TruthIdentifiesOtherWindow model common left right truth
      inOtherWindow inConde := by
  refine ⟨gate, survives, ?_, disjoint⟩
  intro p hp
  obtain ⟨event, actual⟩ := allActual p hp
  obtain ⟨cell, listed, bounded⟩ :=
    hypothetical_actual_event_has_certified_cell_bound
      model common left right cover truth p hp event actual
  exact ⟨event, actual, within cell event listed bounded⟩

/-- Genuine extra evidence can restrict a truth-linked domain, but
    cannot fabricate a new survivor or a proof of nonemptiness. -/
def narrowTruthLink {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (truth : TruthLink α model common left right) :
    TruthLink α model (extra :: common) left right where
  actualImpact := truth.actualImpact
  actualCovered := by
    intro p event hp actual
    exact truth.actualCovered p event
      (alternative_common_narrowing common extra left right p hp) actual

/-- Once proved, a truth-linked exclusion survives an *admissible*
    narrowing. The narrowed domain must still have its own witness. -/
theorem certified_truth_exclusion_persists_with_witness {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (truth : TruthLink α model common left right)
    (inConde : TimeLocation → Prop)
    (old : TruthExcludesConde model common left right truth inConde)
    (survives : AlternativeHasCandidate (extra :: common) left right) :
    TruthExcludesConde model (extra :: common) left right
      (narrowTruthLink model common extra left right truth) inConde := by
  refine ⟨old.1, survives, ?_⟩
  intro p hp event actual
  exact old.2.2 p
    (alternative_common_narrowing common extra left right p hp)
    event actual

/-- If a surviving hypothetical state has no actual ground impact,
    nothing can force a physical ground-impact location across all states. -/
theorem absent_actual_impact_refutes_truth_forcing {α : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (truth : TruthLink α model common left right)
    (inConde : TimeLocation → Prop)
    (p : α) (hp : AlternativeAllowed common left right p)
    (absent : truth.actualImpact p = none) :
    ¬ TruthForcesConde model common left right truth inConde := by
  intro forced
  obtain ⟨event, actual, _⟩ := forced.2.2 p hp
  rw [absent] at actual
  cases actual

/-- Synthetic self-consistent forecast: its envelope always contains its
    *own* predicted event. No historical measurements are used. -/
def illustrativeSelfSoundForecast (forecast : TimeLocation) :
    ImpactEnvelope Unit where
  audit := castorCurrentDeclaredAudit
  predict := fun _ => some forecast
  contains := fun _ event => event = forecast
  soundForPredictions := by
    intro _ event predicted
    exact (Option.some.inj predicted).symm

/-- Crucial countermodel: perfect self-soundness does not bound a
    distinct hypothetical actual event. Symbolic arguments are NOT
    recovered orbital positions or historical facts. -/
theorem self_sound_forecast_does_not_cover_unlinked_reality
    (forecast actual : TimeLocation) (different : forecast ≠ actual) :
    (illustrativeSelfSoundForecast forecast).predict () = some forecast ∧
    ¬ (illustrativeSelfSoundForecast forecast).contains () actual := by
  constructor
  · rfl
  · intro claimed
    exact different claimed.symm

end Conde1963
