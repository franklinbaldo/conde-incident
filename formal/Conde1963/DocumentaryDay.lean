import Conde1963.Constraints

/-!
# One actual documentary constraint; no synthetic historical measurements

The contemporary NASA/Goddard Satellite Situation Report (15 Nov 1963,
printed page 8, NTRS 19640001198), as indexed by matrix C131 and C197,
records 1963-003B as decayed on 8 November 1963. The report does NOT
supply terminal coordinates, a time-of-day or a ground impact.

These two matrix entries cite the SAME NASA report, not two independent
sensors. This module turns only the reported calendar day into a
*conditional* predicate. Hypothetical candidates below are logical
countermodels, never reconstructed orbital trajectories.
-/

namespace Conde1963

/-- Date in the NASA report, not an inferred impact place or timestamp. -/
def ReportedDecayDay (candidate : ReentryCandidate) : Prop :=
  candidate.day = 19631108

/-- Original contemporary report, matrix occurrence C131.
    `admitted` means admitted within the explicitly chosen date-only
    scenario, not a claim that a ground impact has been verified. -/
def nasaDayC131 : SourcedConstraint ReentryCandidate :=
  { matrixLabel := "C131"
    occurrence := 1
    chain := .noradNasaCatalog
    grade := .originalInspected
    use := .admitted
    condition := ReportedDecayDay }

/-- C197 restates the *same* NASA report with additional facsimile
    detail; preserving a separate matrix ID is NOT independent evidence. -/
def nasaDayC197 : SourcedConstraint ReentryCandidate :=
  { matrixLabel := "C197"
    occurrence := 1
    chain := .noradNasaCatalog
    grade := .originalInspected
    use := .admitted
    condition := ReportedDecayDay }

def nasaDayConstraints : List (SourcedConstraint ReentryCandidate) :=
  [nasaDayC131, nasaDayC197]

/-- The only accepted restriction in this documentary scenario is the day.
    The pair of entries cannot further shrink the domain relative to one
    entry, even though there are two distinct matrix IDs. -/
theorem nasa_repeat_is_same_day_predicate (c : ReentryCandidate) :
    AllowedFromSources nasaDayConstraints c ↔ ReportedDecayDay c := by
  simp [AllowedFromSources, nasaDayConstraints, nasaDayC131, nasaDayC197]

/-- Identical catalog-report genealogy does not create an independent
    tracking measurement. Source-chain assignments remain auditable claims. -/
theorem nasa_c131_c197_not_independent :
    ¬ Independent
      ⟨131, .originalInspected, .noradNasaCatalog⟩
      ⟨197, .originalInspected, .noradNasaCatalog⟩ := by
  simp [Independent]

/-- Both illustrative, mutually incompatible regions survive the
    *same* day-only document. These are NOT physical candidate orbits. -/
theorem nasa_day_allows_both_regions :
    AllowedFromSources nasaDayConstraints condeCandidate ∧
    AllowedFromSources nasaDayConstraints anotherCandidate ∧
    condeCandidate.region ≠ anotherCandidate.region := by
  simp [nasa_repeat_is_same_day_predicate, ReportedDecayDay,
        condeCandidate, anotherCandidate]

/-- Since both regions remain logically possible, the NASA date alone
    cannot identify one. An actual exclusion requires physical constraints. -/
theorem nasa_day_cannot_identify_region :
    ¬ UniquelyIdentifiesRegion ReportedDecayDay (fun _ => True) := by
  apply two_admissible_regions_preclude_unique
    ReportedDecayDay (fun _ => True) condeCandidate anotherCandidate
  · exact ⟨rfl, True.intro⟩
  · exact ⟨rfl, True.intro⟩
  · exact date_alone_does_not_identify_place.2.2

/-- No ground impact is observed in the date-only record. The constant
    `none` is a LOGICAL COUNTERMODEL, not a prediction that no impact
    occurred. It demonstrates why the date cannot FORCE ground impact. -/
def countermodelWithoutGroundImpact (_ : ReentryCandidate) : Option TimeLocation :=
  none

theorem nasa_day_does_not_force_ground_impact
    (inConde : TimeLocation → Prop) :
    ¬ ForcesConde [ReportedDecayDay] countermodelWithoutGroundImpact inConde := by
  intro forced
  have admitted : Allowed [ReportedDecayDay] condeCandidate := by
    simp [Allowed, ReportedDecayDay, condeCandidate]
  obtain ⟨event, hevent, _⟩ := forced.2 condeCandidate admitted
  cases hevent

end Conde1963
