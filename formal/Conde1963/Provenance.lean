import Conde1963.Core

/-!
# Conditional identification and source lineage

These theorems concern the information content of *specified premises*.
They do not certify the historical truth of a document, a TLE, a fall,
or the calibration of a dynamical model. See matrix C01, C131, C197.
-/

namespace Conde1963

/-- The formal meaning of uniqueness includes a nonempty set of admissible
    states. Without the witness, an impossible model could be called unique. -/
def UniquelyIdentifiesRegion
    (date physics : ReentryCandidate → Prop) : Prop :=
  ∃ region : Region,
    (∃ c : ReentryCandidate, Admissible date physics c) ∧
    ∀ c : ReentryCandidate, Admissible date physics c → c.region = region

/-- Two admitted states in different regions refute a unique-location claim.
    No assumption is made that either state is an actual orbit. -/
theorem two_admissible_regions_preclude_unique
    (date physics : ReentryCandidate → Prop)
    (a b : ReentryCandidate)
    (ha : Admissible date physics a)
    (hb : Admissible date physics b)
    (different : a.region ≠ b.region) :
    ¬ UniquelyIdentifiesRegion date physics := by
  intro unique
  obtain ⟨region, _, all⟩ := unique
  exact different ((all a ha).trans (all b hb).symm)

/-- The date-only predicate from Core admits illustrative candidates in
    both regions. This is *not* a pair of reconstructed trajectories. -/
theorem date_only_precludes_unique_region :
    ¬ UniquelyIdentifiesRegion ConsistentWithDateOnly (fun _ => True) := by
  apply two_admissible_regions_preclude_unique
    ConsistentWithDateOnly (fun _ => True) condeCandidate anotherCandidate
  · exact ⟨date_alone_does_not_identify_place.1, True.intro⟩
  · exact ⟨date_alone_does_not_identify_place.2.1, True.intro⟩
  · exact date_alone_does_not_identify_place.2.2

/-- Adding physics constraints cannot establish uniqueness by fiat:
    if two different-region candidates survive *all* constraints, the
    combined model still does not identify the region. -/
theorem surviving_candidates_preclude_unique_after_constraint
    (date physics extra : ReentryCandidate → Prop)
    (a b : ReentryCandidate)
    (ha : Admissible date physics a)
    (hb : Admissible date physics b)
    (hea : extra a)
    (heb : extra b)
    (different : a.region ≠ b.region) :
    ¬ UniquelyIdentifiesRegion date (fun c => physics c ∧ extra c) := by
  apply two_admissible_regions_preclude_unique
    date (fun c => physics c ∧ extra c) a b
  · exact ⟨ha.1, ha.2, hea⟩
  · exact ⟨hb.1, hb.2, heb⟩
  · exact different

/-- A positive location claim must supply both an admitted witness and
    a bound on *every* admitted state. No orbital calculation is hidden. -/
theorem witness_and_exhaustive_region_bound_imply_unique
    (date physics : ReentryCandidate → Prop)
    (region : Region)
    (witness : ReentryCandidate)
    (hw : Admissible date physics witness)
    (every : ∀ c, Admissible date physics c → c.region = region) :
    UniquelyIdentifiesRegion date physics := by
  exact ⟨region, ⟨witness, hw⟩, every⟩

/-- Equal source chains mean no independent corroboration *in the
    adopted model of chains*. Chain assignments need documentary audit. -/
theorem shared_chain_is_not_independent
    (a b : Trace) (same : a.chain = b.chain) :
    ¬ Independent a b := by
  intro contrary
  exact contrary same

/-- Reprints within the radio/FBIS chain cannot create a new witness. -/
theorem radio_reprint_is_not_independent
    (t : Trace) (ht : t.chain = Chain.radioTupiFbis) :
    ¬ Independent tupi t := by
  exact shared_chain_is_not_independent tupi t (by
    simpa [tupi] using ht.symm)

end Conde1963
