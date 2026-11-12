import Conde1963.FiniteCoverage

/-!
# Certified finite cells for a potentially continuous orbital parameter domain

A finite point grid does NOT cover an uncountable physical parameter domain
merely because it is dense. Unlike `DomainCoverage` for sampled points, this
module permits finitely many *regions of parameter space* (cells), with an
independently proved covering map and a sound event enclosure for EVERY
surviving state in each cell.

The matrix's C25#1 (line 118), C179#1 (line 839) are unresolved
SECONDARY orbital element reproductions, not mutually confirming original
measurements. The incompatible RAAN hypotheses remain OR branches, never an
AND intersection. NASA/Goddard C131#1 and C197#1 (lines 502, 905) are the
SAME source documenting a catalogued decay day, not an impact fix.

All definitions are conditional mathematical contracts. No actual continuous
cover, validated 1963 TLE, error bound, ground impact or geographic outcome
is supplied here. No cell is asserted to describe a physical orbit.
-/

namespace Conde1963

/-- A finite collection of abstract cells in parameter space. In contrast
    to a finite *point* grid, each cell may contain infinitely many states.
    The caller must PROVE that every admissible state belongs to a cell,
    and that every modeled event enclosure in that cell is bounded by the
    declared cell event enclosure. Those are two independent obligations. -/
structure CertifiedCellCover (α κ : Type)
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α) where
  cells : List κ
  inCell : κ → α → Prop
  eventBounds : κ → TimeLocation → Prop
  covers : ∀ p, AlternativeAllowed common left right p →
    ∃ cell, cell ∈ cells ∧ inCell cell p
  boundsSound : ∀ p cell event,
    AlternativeAllowed common left right p →
    cell ∈ cells →
    inCell cell p →
    model.contains p event →
    eventBounds cell event

/-- For each modeled event of an admissible parameter, some listed cell
    bounds that event. This needs BOTH the full-domain cell cover and a
    sound event enclosure; sampled-point correctness is not enough. -/
theorem predicted_event_has_certified_cell_bound {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (p : α) (hp : AlternativeAllowed common left right p)
    (event : TimeLocation) (predicted : model.predict p = some event) :
    ∃ cell, cell ∈ cover.cells ∧ cover.eventBounds cell event := by
  obtain ⟨cell, listed, inside⟩ := cover.covers p hp
  exact ⟨cell, listed,
    cover.boundsSound p cell event hp listed inside
      (model.soundForPredictions p event predicted)⟩

/-- Certified finite cells cannot be empty if any admissible state exists.
    No conclusion follows merely from an empty *sampled* point grid. -/
theorem nonempty_domain_requires_listed_cell {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (candidate : AlternativeHasCandidate common left right) :
    ∃ cell, cell ∈ cover.cells := by
  obtain ⟨p, hp⟩ := candidate
  obtain ⟨cell, listed, _⟩ := cover.covers p hp
  exact ⟨cell, listed⟩

/-- Empty list of globally covering cells (NOT empty grid output)
    is inconsistent with any surviving parameter candidate. -/
theorem empty_certified_cells_imply_empty_domain {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (empty : cover.cells = []) :
    ¬ AlternativeHasCandidate common left right := by
  intro candidate
  obtain ⟨cell, listed⟩ :=
    nonempty_domain_requires_listed_cell model common left right cover candidate
  rw [empty] at listed
  cases listed

/-- Every cell's sound event bound separated from Conde gives a
    NONVACUOUS conditional exclusion on the UNION of source alternatives.
    Absence of a modeled impact is not converted into impact elsewhere. -/
theorem covered_cells_exclude_conde {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (outside : ∀ cell event, cell ∈ cover.cells →
      cover.eventBounds cell event → ¬ inConde event) :
    AlternativeEnclosureExclusion model common left right inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp event predicted
  obtain ⟨cell, listed, bounded⟩ :=
    predicted_event_has_certified_cell_bound
      model common left right cover p hp event predicted
  exact outside cell event listed bounded

/-- Forcing Conde additionally requires that EVERY admissible state
    actually predicts a ground impact. Bounds alone cannot create one. -/
theorem covered_cells_force_conde {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allImpact : ∀ p, AlternativeAllowed common left right p →
      ∃ event, model.predict p = some event)
    (inside : ∀ cell event, cell ∈ cover.cells →
      cover.eventBounds cell event → inConde event) :
    AlternativeEnclosureForcing model common left right inConde := by
  refine ⟨gate, ⟨survives, ?_⟩⟩
  intro p hp
  obtain ⟨event, predicted⟩ := allImpact p hp
  obtain ⟨cell, listed, bounded⟩ :=
    predicted_event_has_certified_cell_bound
      model common left right cover p hp event predicted
  exact ⟨event, predicted, inside cell event listed bounded⟩

/-- A different window likewise requires universal ground impact AND
    a window disjoint from Conde, not merely a high-altitude crossing. -/
theorem covered_cells_identify_other_window {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (inOtherWindow inConde : TimeLocation → Prop)
    (gate : GroundImpactAdmissible model.audit)
    (survives : AlternativeHasCandidate common left right)
    (allImpact : ∀ p, AlternativeAllowed common left right p →
      ∃ event, model.predict p = some event)
    (within : ∀ cell event, cell ∈ cover.cells →
      cover.eventBounds cell event → inOtherWindow event)
    (disjoint : ∀ event, inOtherWindow event → ¬ inConde event) :
    AlternativeEnclosureOtherWindow model common left right
      inOtherWindow inConde := by
  refine ⟨gate, survives, ?_, disjoint⟩
  intro p hp
  obtain ⟨event, predicted⟩ := allImpact p hp
  obtain ⟨cell, listed, bounded⟩ :=
    predicted_event_has_certified_cell_bound
      model common left right cover p hp event predicted
  exact ⟨event, predicted, within cell event listed bounded⟩

/-- A proven cover over the old union also covers a further restriction
    of that union. A new verdict still needs a NONEMPTY refined domain. -/
theorem cell_cover_survives_common_narrowing {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (p : α)
    (hp : AlternativeAllowed (extra :: common) left right p) :
    ∃ cell, cell ∈ cover.cells ∧ cover.inCell cell p := by
  exact cover.covers p
    (alternative_common_narrowing common extra left right p hp)

/-- The same certified event-bound implication remains sound on a
    narrower domain, but never proves the narrowed domain is nonempty. -/
theorem cell_bounds_survive_common_narrowing {α κ : Type}
    (model : ImpactEnvelope α)
    (common : List (ParameterConstraint α))
    (extra left right : ParameterConstraint α)
    (cover : CertifiedCellCover α κ model common left right)
    (p : α) (hp : AlternativeAllowed (extra :: common) left right p)
    (event : TimeLocation) (predicted : model.predict p = some event) :
    ∃ cell, cell ∈ cover.cells ∧ cover.eventBounds cell event := by
  exact predicted_event_has_certified_cell_bound model common left right cover
    p (alternative_common_narrowing common extra left right p hp)
    event predicted

end Conde1963
