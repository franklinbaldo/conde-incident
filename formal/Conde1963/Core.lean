/-!
Case Conde (1963): logically certified provenance and underidentification bounds.
Ported from the separately compiled Lean 4.35.0 evidence package (11 Nov 2026).
This proves implications *of input records*, not the authenticity of a fall.
-/
namespace Conde1963

inductive Grade where
  | originalInspected | originalTextNotFacsimile | contemporarySecondhand
  | laterCatalog | derivedFromOrbitalElements | experimentalModel
  | conditionalInference | stillUnverified
  deriving Repr, DecidableEq, BEq, Inhabited

inductive Chain where
  | radioTupiFbis | diplomaticFollowup | noradNasaCatalog
  | jornalBahia | diarioNoticiasSalvador | jornalBrasil
  | experimentalOrbitModel | miscellaneous
  deriving Repr, DecidableEq, BEq, Inhabited

structure Trace where
  claimId : Nat
  grade : Grade
  chain : Chain
  deriving Repr

def Independent (a b : Trace) : Prop := a.chain ≠ b.chain
def tupi : Trace := ⟨1, .originalInspected, .radioTupiFbis⟩
def fbis : Trace := ⟨2, .originalInspected, .radioTupiFbis⟩
def nasa : Trace := ⟨131, .originalInspected, .noradNasaCatalog⟩
def laterCat : Trace := ⟨140, .laterCatalog, .noradNasaCatalog⟩

theorem no_double_count_tupi : ¬ Independent tupi fbis := by
  simp [Independent, tupi, fbis]

theorem no_double_count_tracking : ¬ Independent nasa laterCat := by
  simp [Independent, nasa, laterCat]

structure CatalogueObservation where
  norad : Nat
  uniqueEpochs1963 : Nat
  lastAvailableDay : Nat
  deriving Repr

def ob527 : CatalogueObservation := ⟨527, 20, 19631217⟩
def ob528 : CatalogueObservation := ⟨528, 45, 19631027⟩
def ob529 : CatalogueObservation := ⟨529, 54, 19631230⟩

theorem total_unique_epochs :
  ob527.uniqueEpochs1963 + ob528.uniqueEpochs1963 + ob529.uniqueEpochs1963 = 119 := by decide

theorem last_528_before_decay : ob528.lastAvailableDay < 19631108 := by decide

-- Exact arithmetic; orbital frequencies are not constant over the year.
def motion528JanE8 : Nat := 1525978323
def motion529JanE8 : Nat := 1522642839

theorem frequency_difference_e8 :
  motion528JanE8 - motion529JanE8 = 3335484 := by decide

-- The holdout comparison is a fixed empirical input, not a theorem of physics.
def quadraticMAEE5 : Nat := 1412
def jointH60MAEE5 : Nat := 2595

theorem joint_model_did_not_beat_quadratic_on_holdout :
  quadraticMAEE5 < jointH60MAEE5 := by decide

-- Historic element set extracted from an earlier 45-TLE dataset.
-- This RAAN is NOT the 284.1520-degree value hardcoded in the web app.
structure MeanOrbit where
  norad : Nat
  epoch : Nat
  nRevDayE8 : Nat
  inclinationE4 : Nat
  raanE4 : Nat
  deriving Repr

def last528 : MeanOrbit := ⟨528, 19631027, 1574901460, 818615, 1985261⟩

inductive Region where
  | conde | elsewhere
  deriving Repr, DecidableEq, BEq

structure ReentryCandidate where
  day : Nat
  minuteUTC : Nat
  region : Region
  argLatitudeDeg : Nat
  deriving Repr

def ConsistentWithDateOnly (c : ReentryCandidate) : Prop :=
  c.day = 19631108 ∧ c.minuteUTC < 1440 ∧ c.argLatitudeDeg < 360

def condeCandidate : ReentryCandidate := ⟨19631108, 900, .conde, 0⟩
def anotherCandidate : ReentryCandidate := ⟨19631108, 900, .elsewhere, 90⟩

theorem date_alone_does_not_identify_place :
  ConsistentWithDateOnly condeCandidate ∧
  ConsistentWithDateOnly anotherCandidate ∧
  condeCandidate.region ≠ anotherCandidate.region := by
  simp [ConsistentWithDateOnly, condeCandidate, anotherCandidate]

def Admissible (date physics : ReentryCandidate → Prop)
  (c : ReentryCandidate) : Prop := date c ∧ physics c

theorem more_constraints_never_expand
  (date physics : ReentryCandidate → Prop)
  (c : ReentryCandidate) (h : Admissible date physics c) : date c := h.1

end Conde1963
