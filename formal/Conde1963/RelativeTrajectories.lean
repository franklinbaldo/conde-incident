import Lean

/-!
C241-P10: simultaneous, three-object orbital-separation constraints.

At a common, calibrated ECI epoch t, candidate 528 positions must satisfy
the 527/528, 528/529 and 527/529 *distance intervals*, plus conservative
Cartesian displacement envelopes derived by an audited propagator.

Signed t supports backwards and forwards propagation from the reference
epoch. It is not a NASA report date. Millikilometres = 1-metre coordinate
units; squared distances have units m^2. No numerical interval here is
claimed to have been observed or calibrated in 1963.

The C179#1 528 element set is SECONDARY, and C197#1 gives only the
catalogued decay day. Without original epoch/frame/error evidence the
qualification gate is false, so these are candidate, NOT active, bounds.
-/

namespace Conde1963.RelativeTrajectories

structure CartesianMetres where
  x : Int
  y : Int
  z : Int
  deriving Repr, DecidableEq

/-- Exact squared Euclidean separation in square metres. -/
def squaredSeparation (a b : CartesianMetres) : Int :=
  (a.x - b.x) * (a.x - b.x) +
  (a.y - b.y) * (a.y - b.y) +
  (a.z - b.z) * (a.z - b.z)

structure SquaredSeparationBand where
  lower : Int
  upper : Int
  deriving Repr

def inDistanceBand (a b : CartesianMetres)
    (band : SquaredSeparationBand) : Prop :=
  0 ≤ band.lower ∧
  band.lower ≤ squaredSeparation a b ∧
  squaredSeparation a b ≤ band.upper

/-- Conservative absolute-offset bounds derived from propagated uncertainty. -/
structure OffsetEnvelope where
  x : Int
  y : Int
  z : Int
  deriving Repr

def withinAxis (candidate control radius : Int) : Prop :=
  control - radius ≤ candidate ∧ candidate ≤ control + radius

def withinEnvelope (candidate control : CartesianMetres)
    (radius : OffsetEnvelope) : Prop :=
  0 ≤ radius.x ∧ 0 ≤ radius.y ∧ 0 ≤ radius.z ∧
  withinAxis candidate.x control.x radius.x ∧
  withinAxis candidate.y control.y radius.y ∧
  withinAxis candidate.z control.z radius.z

/-- All pairs matter, including the 527/529 negative control. -/
structure ThreePairBands where
  b527_528 : SquaredSeparationBand
  b528_529 : SquaredSeparationBand
  b527_529 : SquaredSeparationBand

/-- These attestations are prerequisites, not proof of their own authenticity. -/
structure CalibrationStatus where
  epochsResolved : Bool
  commonEciFrame : Bool
  modelValidated : Bool
  uncertaintyCalibrated : Bool
  deriving Repr

def isCalibrated (s : CalibrationStatus) : Prop :=
  s.epochsResolved = true ∧
  s.commonEciFrame = true ∧
  s.modelValidated = true ∧
  s.uncertaintyCalibrated = true

structure ThreeTracks where
  /-- A signed second-offset from a common UTC reference epoch. -/
  position527 : Int → CartesianMetres
  position528 : Int → CartesianMetres
  position529 : Int → CartesianMetres
  separationBands : Int → ThreePairBands
  boundFrom527 : Int → OffsetEnvelope
  boundFrom529 : Int → OffsetEnvelope
  status : Int → CalibrationStatus

/--
A candidate for 528 must obey every pairwise distance band at the SAME
epoch, including the 527/529 control, and both 527/529 uncertainty envelopes.
The bounds are intentionally parameters awaiting physical calibration.
-/
def candidateAllowedAt (tracks : ThreeTracks) (t : Int)
    (candidate528 : CartesianMetres) : Prop :=
  let p527 := tracks.position527 t
  let p529 := tracks.position529 t
  let bands := tracks.separationBands t
  withinEnvelope candidate528 p527 (tracks.boundFrom527 t) ∧
  withinEnvelope candidate528 p529 (tracks.boundFrom529 t) ∧
  inDistanceBand p527 candidate528 bands.b527_528 ∧
  inDistanceBand candidate528 p529 bands.b528_529 ∧
  inDistanceBand p527 p529 bands.b527_529

def candidateActiveAt (tracks : ThreeTracks) (t : Int)
    (candidate528 : CartesianMetres) : Prop :=
  isCalibrated (tracks.status t) ∧
  candidateAllowedAt tracks t candidate528

/-- Quantified signed epochs allow both retrospective and future checks. -/
def trajectoryActiveAcross (tracks : ThreeTracks)
    (signedSecondOffsets : List Int) : Prop :=
  ∀ t, t ∈ signedSecondOffsets →
    candidateActiveAt tracks t (tracks.position528 t)

/--
A genuine geometric rejection criterion: if certified 527 and 529
envelopes are disjoint along X, NO possible 528 position can satisfy both.
This is useful even before fitting the 528 trajectory, and does not assume
the three orbiting objects remain close over time.
-/
theorem controls_exclude_candidate_if_x_envelopes_disjoint
    (tracks : ThreeTracks) (t : Int)
    (candidate528 : CartesianMetres)
    (hDisjoint :
      (tracks.position529 t).x + (tracks.boundFrom529 t).x <
      (tracks.position527 t).x - (tracks.boundFrom527 t).x) :
    ¬ candidateAllowedAt tracks t candidate528 := by
  intro hAllowed
  rcases hAllowed with ⟨h527, h529, _, _, _⟩
  rcases h527 with ⟨_, _, _, hX527, _, _⟩
  rcases h529 with ⟨_, _, _, hX529, _, _⟩
  rcases hX527 with ⟨hLo527, _⟩
  rcases hX529 with ⟨_, hHi529⟩
  omega

/--
One contradictory epoch in a proposed backward/forward trajectory
invalidates that entire candidate, provided the separation envelopes
are independently justified. No fabricated terminal location is inferred.
-/
theorem one_disjoint_epoch_rejects_trajectory
    (tracks : ThreeTracks) (epochs : List Int) (t : Int)
    (hMember : t ∈ epochs)
    (hDisjoint :
      (tracks.position529 t).x + (tracks.boundFrom529 t).x <
      (tracks.position527 t).x - (tracks.boundFrom527 t).x) :
    ¬ trajectoryActiveAcross tracks epochs := by
  intro hAll
  have hAt := hAll t hMember
  exact controls_exclude_candidate_if_x_envelopes_disjoint
    tracks t (tracks.position528 t) hDisjoint hAt.2

end Conde1963.RelativeTrajectories
