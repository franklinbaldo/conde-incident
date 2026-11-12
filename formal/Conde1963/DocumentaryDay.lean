import Conde1963.Constraints

/-!
# NASA documentary record versus the latent physical decay day

C131/C197 (same NASA/Goddard Satellite Situation Report, 15 Nov 1963,
printed p.8, NTRS 19640001198) record the catalogued day 1963-11-08.
They do not establish the method used to estimate decay or observe the
true reentry day, terminal epoch, position or ground impact.

The archival reading is a proposition about the document; the proposed
equality between physical and catalogued days is a distinct, falsifiable
hypothesis. Neither of the two citations is admitted as a physical filter.
-/

namespace Conde1963

/-- A value transcribed from the period report, NOT measured reentry time. -/
def NasaCatalogueDay : Nat := 19631108

/-- Documentary proposition: the published record states this day. -/
def NasaRecordStatesNovemberEighth : Prop := NasaCatalogueDay = 19631108

theorem nasa_record_states_november_eighth :
    NasaRecordStatesNovemberEighth := by
  rfl

/-- Scientific hypothesis to TEST: a latent candidate's physical decay
    day matches the catalogued day. This is not a documentary entailment. -/
def PhysicalDayMatchesCatalogue (c : ReentryCandidate) : Prop :=
  c.day = NasaCatalogueDay

/-- Same source, same proposed physical hypothesis. Neither is a hard
    input to the simulator before a justified observational error model. -/
def nasaDayC131 : SourcedConstraint ReentryCandidate :=
  { matrixLabel := "C131"
    occurrence := 1
    chain := .noradNasaCatalog
    grade := .originalInspected
    use := .scenarioOnly
    condition := PhysicalDayMatchesCatalogue }

def nasaDayC197 : SourcedConstraint ReentryCandidate :=
  { matrixLabel := "C197"
    occurrence := 1
    chain := .noradNasaCatalog
    grade := .originalInspected
    use := .scenarioOnly
    condition := PhysicalDayMatchesCatalogue }

def nasaDayConstraints : List (SourcedConstraint ReentryCandidate) :=
  [nasaDayC131, nasaDayC197]

/-- Reading the report twice does not impose the physical day. -/
theorem nasa_catalogue_is_not_a_hard_physical_filter
    (c : ReentryCandidate) :
    AllowedFromSources nasaDayConstraints c := by
  simp [AllowedFromSources, nasaDayConstraints, nasaDayC131, nasaDayC197]

/-- Even if explicitly selected as a hypothesis, the two source citations
    refer to the SAME equation, not two independent observations. -/
theorem nasa_two_citations_one_conditional_equation
    (c : ReentryCandidate) :
    (PhysicalDayMatchesCatalogue c ∧ PhysicalDayMatchesCatalogue c) ↔
      PhysicalDayMatchesCatalogue c := by
  exact and_self_iff

/-- A user may enable the hypothetical day-equality diagnostic.
    The .scenarioOnly use ensures the standard filterCandidateGrid does
    NOT turn the documentary reading into a hard physical input. -/
def nasaHypotheticalDayRule : ExecutableRule ReentryCandidate :=
  { source := nasaDayC131
    accepts := fun candidate => decide (candidate.day = NasaCatalogueDay)
    corresponds := by
      intro candidate
      simp [nasaDayC131, PhysicalDayMatchesCatalogue] }

def inventedOffDayExample : ReentryCandidate :=
  ⟨19631109, 900, .elsewhere, 90⟩

theorem nasa_hypothetical_rule_accepts_illustrative_examples :
    nasaHypotheticalDayRule.accepts condeCandidate = true ∧
    nasaHypotheticalDayRule.accepts anotherCandidate = true := by
  decide

theorem nasa_hypothetical_rule_rejects_illustrative_off_day :
    nasaHypotheticalDayRule.accepts inventedOffDayExample = false := by
  decide

theorem nasa_c131_c197_not_independent :
    ¬ Independent
      ⟨131, .originalInspected, .noradNasaCatalog⟩
      ⟨197, .originalInspected, .noradNasaCatalog⟩ := by
  simp [Independent]

/-- The actual day equality is not a logical consequence of the records.
    The off-day model is synthetic and is NOT asserted historically true. -/
theorem reported_day_does_not_prove_actual_day :
    ¬ (∀ c, AllowedFromSources nasaDayConstraints c →
      PhysicalDayMatchesCatalogue c) := by
  intro h
  have hc := h inventedOffDayExample
    (nasa_catalogue_is_not_a_hard_physical_filter inventedOffDayExample)
  have hbad : ¬ PhysicalDayMatchesCatalogue inventedOffDayExample := by
    simp [PhysicalDayMatchesCatalogue, inventedOffDayExample, NasaCatalogueDay]
  exact hbad hc

/-- Conditional scientific verdicts require a NONEMPTY calibrated domain.
    They say what the model implies, not what happened in 1963. -/
def ConditionallyForcesNasaDay
    (admissible : ReentryCandidate → Prop) : Prop :=
  (∃ c, admissible c) ∧
  ∀ c, admissible c → PhysicalDayMatchesCatalogue c

def ConditionallyExcludesNasaDay
    (admissible : ReentryCandidate → Prop) : Prop :=
  (∃ c, admissible c) ∧
  ∀ c, admissible c → ¬ PhysicalDayMatchesCatalogue c

def DayRemainsUnderdetermined
    (admissible : ReentryCandidate → Prop) : Prop :=
  (∃ c, admissible c ∧ PhysicalDayMatchesCatalogue c) ∧
  (∃ c, admissible c ∧ ¬ PhysicalDayMatchesCatalogue c)

/-- Distinct model predictions are incompatible with calling the
    catalogue day forced for every surviving physical candidate. -/
theorem contrasting_candidates_preclude_forced_day
    (admissible : ReentryCandidate → Prop)
    (outside : ReentryCandidate)
    (hallowed : admissible outside)
    (hoff : ¬ PhysicalDayMatchesCatalogue outside) :
    ¬ ConditionallyForcesNasaDay admissible := by
  intro forced
  exact hoff (forced.2 outside hallowed)

/-- No nonempty model can both force and exclude the same day. -/
theorem forces_and_excludes_day_are_incompatible
    (admissible : ReentryCandidate → Prop)
    (forced : ConditionallyForcesNasaDay admissible)
    (excluded : ConditionallyExcludesNasaDay admissible) : False := by
  obtain ⟨c, hc⟩ := forced.1
  exact excluded.2 c hc (forced.2 c hc)

/-- The unfiltered documentary model has candidates on and off the
    catalogued date. Both are illustration-only countermodels. -/
theorem nasa_documentary_record_leaves_actual_day_underdetermined :
    DayRemainsUnderdetermined
      (AllowedFromSources nasaDayConstraints) := by
  refine ⟨⟨condeCandidate, nasa_catalogue_is_not_a_hard_physical_filter _, ?_⟩,
          ⟨inventedOffDayExample,
             nasa_catalogue_is_not_a_hard_physical_filter _, ?_⟩⟩
  · simp [PhysicalDayMatchesCatalogue, condeCandidate, NasaCatalogueDay]
  · simp [PhysicalDayMatchesCatalogue, inventedOffDayExample, NasaCatalogueDay]

/-- Geography is also underidentified, independent of the date hypothesis. -/
theorem nasa_documentary_record_does_not_identify_region :
    ¬ UniquelyIdentifiesRegion
       (AllowedFromSources nasaDayConstraints) (fun _ => True) := by
  apply two_admissible_regions_preclude_unique
    (AllowedFromSources nasaDayConstraints) (fun _ => True)
    condeCandidate anotherCandidate
  · exact ⟨nasa_catalogue_is_not_a_hard_physical_filter _, True.intro⟩
  · exact ⟨nasa_catalogue_is_not_a_hard_physical_filter _, True.intro⟩
  · exact date_alone_does_not_identify_place.2.2

end Conde1963
