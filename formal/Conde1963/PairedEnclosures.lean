import Conde1963.CertifiedCells

/-!
# Paired sound cell enclosures: logical consistency, not independent evidence

Two different finite cell covers may describe the SAME admissible union
of unresolved RAAN source scenarios. Each must separately prove coverage
of every surviving parameter and sound bounds on EVERY modeled event.
The covers need not use the same partition.

C25#1 (matrix L118) and C179#1 (L839) describe secondary orbit-element
reproductions; the 284.1520-degree site value is unresolved. They are
source alternatives, not measurements to intersect. C131#1 and C197#1
(L502/L905) are ONE NASA/Goddard publication documenting a catalogue
decay day, never an impact point. No original TLE custody is established.

The intersection of two SOUND event enclosures may give a tighter
conditional result even when neither alone separates Conde. If the
enclosures conflict everywhere, the model cannot predict a ground-impact
event for any surviving parameter; this does NOT establish that the
parameter domain itself is empty. Independent numerical validation,
holdouts and 1963 input authenticity remain separate empirical gates.
-/

namespace Conde1963

/-- For a modeled impact, two independently *proved* coverings both bound
    the SAME event. This is true even when their cells differ or overlap.
    No statistical or documentary independence follows from this theorem. -/
theorem paired_certified_bounds_for_prediction {α κ κ₂ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (first : CertifiedCellCover α κ model common left right)
    (second : CertifiedCellCover α κ₂ model common left right)
    (p : α) (hp : AlternativeAllowed common left right p)
    (event : TimeLocation) (predicted : model.predict p = some event) :
    ∃ a b, a ∈ first.cells ∧ b ∈ second.cells ∧
      first.eventBounds a event ∧ second.eventBounds b event := by
  obtain ⟨a, listedA, boundA⟩ :=
    predicted_event_has_certified_cell_bound
      model common left right first p hp event predicted
  obtain ⟨b, listedB, boundB⟩ :=
    predicted_event_has_certified_cell_bound
      model common left right second p hp event predicted
  exact ⟨a, b, listedA, listedB, boundA, boundB⟩

/-- Joint separation can exclude Conde even if neither individual
    enclosure is narrow enough. A calibrated ground-impact gate and
    a nonempty parameter domain remain mandatory. -/
theorem paired_enclosures_exclude_conde {α κ κ₂ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (first : CertifiedCellCover α κ model common left right)
    (second : CertifiedCellCover α κ₂ model common left right)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (separate : ∀ a b event, a ∈ first.cells → b ∈ second.cells →
      first.eventBounds a event → second.eventBounds b event →
      ¬ inConde event) :
    AlternativeEnclosureExclusion model common left right inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp event predicted
  obtain ⟨a, b, listedA, listedB, boundA, boundB⟩ :=
    paired_certified_bounds_for_prediction
      model common left right first second p hp event predicted
  exact separate a b event listedA listedB boundA boundB

/-- Bounds alone do not guarantee material survival or ground impact:
    a ground-impact prediction must exist for EVERY survivor. -/
theorem paired_enclosures_force_conde {α κ κ₂ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (first : CertifiedCellCover α κ model common left right)
    (second : CertifiedCellCover α κ₂ model common left right)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allImpact : ∀ p, AlternativeAllowed common left right p →
      ∃ event, model.predict p = some event)
    (inside : ∀ a b event, a ∈ first.cells → b ∈ second.cells →
      first.eventBounds a event → second.eventBounds b event →
      inConde event) :
    AlternativeEnclosureForcing model common left right inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp
  obtain ⟨event, predicted⟩ := allImpact p hp
  obtain ⟨a, b, listedA, listedB, boundA, boundB⟩ :=
    paired_certified_bounds_for_prediction
      model common left right first second p hp event predicted
  exact ⟨event, predicted, inside a b event listedA listedB boundA boundB⟩

/-- A different impact window additionally needs proven disjointness
    from Conde, including the sound numerical error enclosures. -/
theorem paired_enclosures_identify_other_window {α κ κ₂ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (first : CertifiedCellCover α κ model common left right)
    (second : CertifiedCellCover α κ₂ model common left right)
    (inOtherWindow inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allImpact : ∀ p, AlternativeAllowed common left right p →
      ∃ event, model.predict p = some event)
    (within : ∀ a b event, a ∈ first.cells → b ∈ second.cells →
      first.eventBounds a event → second.eventBounds b event →
      inOtherWindow event)
    (disjoint : ∀ event, inOtherWindow event → ¬ inConde event) :
    AlternativeEnclosureOtherWindow model common left right
      inOtherWindow inConde := by
  refine ⟨gate, survives, ?_, disjoint⟩
  intro p hp
  obtain ⟨event, predicted⟩ := allImpact p hp
  obtain ⟨a, b, listedA, listedB, boundA, boundB⟩ :=
    paired_certified_bounds_for_prediction
      model common left right first second p hp event predicted
  exact ⟨event, predicted, within a b event listedA listedB boundA boundB⟩

/-- If two sound covers have NO common possible event for any pair of
    listed cells, the shared model cannot predict an impact in the union.
    This is NOT proof that the underlying admissible parameter set is empty. -/
theorem disjoint_paired_bounds_forbid_predicted_impact {α κ κ₂ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (first : CertifiedCellCover α κ model common left right)
    (second : CertifiedCellCover α κ₂ model common left right)
    (incompatible : ∀ a b event, a ∈ first.cells → b ∈ second.cells →
      first.eventBounds a event → second.eventBounds b event → False)
    (p : α) (hp : AlternativeAllowed common left right p) :
    model.predict p = none := by
  cases predicted : model.predict p with
  | none => rfl
  | some event =>
    obtain ⟨a, b, listedA, listedB, boundA, boundB⟩ :=
      paired_certified_bounds_for_prediction
        model common left right first second p hp event predicted
    exact False.elim (incompatible a b event listedA listedB boundA boundB)

/-- A nonempty domain and universal impact prediction are incompatible
    with globally disjoint sound event bounds. The logical conflict
    demands auditing premises, not fabricating a new geographic answer. -/
theorem incompatible_paired_bounds_refute_universal_impact {α κ κ₂ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (first : CertifiedCellCover α κ model common left right)
    (second : CertifiedCellCover α κ₂ model common left right)
    (incompatible : ∀ a b event, a ∈ first.cells → b ∈ second.cells →
      first.eventBounds a event → second.eventBounds b event → False)
    (survives : AlternativeHasCandidate common left right)
    (allImpact : ∀ p, AlternativeAllowed common left right p →
      ∃ event, model.predict p = some event) : False := by
  obtain ⟨p, hp⟩ := survives
  obtain ⟨event, predicted⟩ := allImpact p hp
  have noImpact :=
    disjoint_paired_bounds_forbid_predicted_impact
      model common left right first second incompatible p hp
  rw [noImpact] at predicted
  cases predicted

/-- Sound joint bounds persist when genuine new documentary/physical
    constraints narrow the union; nonemptiness NEVER follows from this
    implication and must be re-established after each restriction. -/
theorem paired_bounds_survive_common_narrowing {α κ κ₂ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (first : CertifiedCellCover α κ model common left right)
    (second : CertifiedCellCover α κ₂ model common left right)
    (p : α)
    (hp : AlternativeAllowed (extra :: common) left right p)
    (event : TimeLocation) (predicted : model.predict p = some event) :
    ∃ a b, a ∈ first.cells ∧ b ∈ second.cells ∧
      first.eventBounds a event ∧ second.eventBounds b event := by
  exact paired_certified_bounds_for_prediction model common left right
    first second p
    (alternative_common_narrowing common extra left right p hp)
    event predicted

end Conde1963
