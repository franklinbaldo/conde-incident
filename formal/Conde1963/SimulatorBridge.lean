import Conde1963.Outcome

/-!
# Bridge from existing simulator outputs to Lean proof obligations

Inspected implementations:
* main scientific stack: src/lib/astrodynamics.ts, monteCarlo.ts,
  inverseSolver.ts and norad528_reconstruction.py at PR #17 parent
  (historical TLE/SGP4 baseline and geometric synthetic sampling).
* Castor draft #5 at 3074ae0f014ce33a2c81dacb2a7400f92f4a4359:
  orbitPhysics.ts (Cartesian RK4/J2/drag with explicit atmosphere),
  orbitConvergence.ts, orbitAdmissibility.ts, orbitHoldoutAudit.ts,
  orbitEnergyAudit.ts (conditional numerical diagnostics, NOT
  historical observational validation).

This module does NOT check source files or certify JavaScript numerical
implementation. It defines the *logic* that any export from the simulator
must satisfy before claiming historical skill or an impact in Conde.
Source-level checks live in formal/scripts/simulation_bridge_audit.py.
-/

namespace Conde1963

inductive SimulationOrigin where
  | syntheticTerminalGeometry
  | retrospectiveSgp4
  | coupledCartesianRV
  deriving Repr, DecidableEq, BEq

inductive NumericalEvent where
  | elapsed
  | chosenAltitudeThreshold
  | proposedGroundImpact
  deriving Repr, DecidableEq, BEq

/-- A machine-readable report about validation states. Every Bool is a
    DECLARATION from the caller, not verified by Lean just by its presence.
    Validation is conditional on defensible independent source proofs. -/
structure SimulationAudit where
  origin : SimulationOrigin
  event : NumericalEvent
  historicalInputCustody : Bool
  epochFrameUnitsChecked : Bool
  independentHoldoutPassed : Bool
  quantifiedNumericalError : Bool
  calibratedPhysicalForces : Bool
  materialSurvivalEstablished : Bool
  deriving Repr, DecidableEq

/-- Logical preconditions for interpreting a model's output as a historical
    terminal-orbit prediction, NOT a certified prediction by themselves. -/
def HistoricallyAdmissible (r : SimulationAudit) : Prop :=
  r.origin = .coupledCartesianRV ∧
  r.historicalInputCustody = true ∧
  r.epochFrameUnitsChecked = true ∧
  r.independentHoldoutPassed = true ∧
  r.quantifiedNumericalError = true ∧
  r.calibratedPhysicalForces = true

/-- Stronger: atmospheric threshold and ground contact are different events.
    Ground claims require a validated material/impact model. -/
def GroundImpactAdmissible (r : SimulationAudit) : Prop :=
  HistoricallyAdmissible r ∧
  r.event = .proposedGroundImpact ∧
  r.materialSurvivalEstablished = true

theorem synthetic_terminal_geometry_cannot_certify_history
    (r : SimulationAudit)
    (h : r.origin = .syntheticTerminalGeometry) :
    ¬ HistoricallyAdmissible r := by
  intro admitted
  have same : r.origin = .coupledCartesianRV := admitted.1
  rw [h] at same
  cases same

theorem retrospective_sgp4_cannot_certify_history
    (r : SimulationAudit)
    (h : r.origin = .retrospectiveSgp4) :
    ¬ HistoricallyAdmissible r := by
  intro admitted
  have same : r.origin = .coupledCartesianRV := admitted.1
  rw [h] at same
  cases same

theorem absent_independent_holdout_precludes_history
    (r : SimulationAudit)
    (h : r.independentHoldoutPassed = false) :
    ¬ HistoricallyAdmissible r := by
  intro admitted
  have passed : r.independentHoldoutPassed = true := admitted.2.2.2.1
  rw [h] at passed
  cases passed

theorem numerical_agreement_does_not_replace_input_custody
    (r : SimulationAudit)
    (h : r.historicalInputCustody = false) :
    ¬ HistoricallyAdmissible r := by
  intro admitted
  have passed : r.historicalInputCustody = true := admitted.2.1
  rw [h] at passed
  cases passed

theorem altitude_threshold_not_ground_impact
    (r : SimulationAudit)
    (h : r.event = .chosenAltitudeThreshold) :
    ¬ GroundImpactAdmissible r := by
  intro supported
  have same : r.event = .proposedGroundImpact := supported.2.1
  rw [h] at same
  cases same

theorem missing_survival_model_not_ground_impact
    (r : SimulationAudit)
    (h : r.materialSurvivalEstablished = false) :
    ¬ GroundImpactAdmissible r := by
  intro supported
  have passed : r.materialSurvivalEstablished = true := supported.2.2
  rw [h] at passed
  cases passed

/-- The present Castor API declares independent observation authenticity and
    historical holdout NOT_VERIFIED/NOT_RUN. This literal audit is a
    SOURCE-CODE STATUS, not a claim about eventual results. -/
def castorCurrentDeclaredAudit : SimulationAudit :=
  { origin := .coupledCartesianRV
    event := .chosenAltitudeThreshold
    historicalInputCustody := false
    epochFrameUnitsChecked := false
    independentHoldoutPassed := false
    quantifiedNumericalError := false
    calibratedPhysicalForces := false
    materialSurvivalEstablished := false }

theorem castor_current_declared_status_blocks_historical_claim :
    ¬ HistoricallyAdmissible castorCurrentDeclaredAudit := by
  exact absent_independent_holdout_precludes_history
    castorCurrentDeclaredAudit rfl

theorem castor_current_threshold_blocks_ground_impact :
    ¬ GroundImpactAdmissible castorCurrentDeclaredAudit := by
  exact altitude_threshold_not_ground_impact
    castorCurrentDeclaredAudit rfl

/-- Integer-distance counts model ONLY finite output samples. The source
    Monte Carlo samples a free terminal phase and is not a posterior. -/
def countWithin (radiusKm : Nat) : List Nat → Nat
  | [] => 0
  | distanceKm :: rest =>
      (if distanceKm ≤ radiusKm then 1 else 0) +
      countWithin radiusKm rest

theorem countWithin_monotone (distances : List Nat)
    (small large : Nat) (h : small ≤ large) :
    countWithin small distances ≤ countWithin large distances := by
  induction distances with
  | nil => simp [countWithin]
  | cons d ds ih =>
      by_cases hs : d ≤ small
      · have hl : d ≤ large := Nat.le_trans hs h
        simp [countWithin, hs, hl]
        omega
      · by_cases hl : d ≤ large
        · simp [countWithin, hs, hl]
          omega
        · simpa [countWithin, hs, hl] using ih

theorem countWithin_bounded_by_sample_size
    (distances : List Nat) (radiusKm : Nat) :
    countWithin radiusKm distances ≤ distances.length := by
  induction distances with
  | nil => simp [countWithin]
  | cons d ds ih =>
      by_cases hd : d ≤ radiusKm
      · simp [countWithin, hd]
        omega
      · simp [countWithin, hd]
        omega

/-- The only certified fact about increasing radii is monotone *counts*
    within the SAME sample, not probability of a historical reentry. -/
theorem cumulative_radii_monotone (distances : List Nat) :
    countWithin 50 distances ≤ countWithin 100 distances ∧
    countWithin 100 distances ≤ countWithin 250 distances ∧
    countWithin 250 distances ≤ countWithin 500 distances := by
  exact ⟨countWithin_monotone distances 50 100 (by omega),
         countWithin_monotone distances 100 250 (by omega),
         countWithin_monotone distances 250 500 (by omega)⟩

/-- Nonnegative factor times a squared speed gives a nonpositive
    drag-power sign in an exact integer-scaled abstraction. This is ONLY
    the sign algebra behind Castor's relative-wind drag power
    -500*rho*(CdA/m)*|v_rel|^3; it does not certify floating-point RK4,
    dimensional conversion, density values, or integrated orbital energy. -/
def scaledDragPower (nonnegativeFactor speedSquared : Nat) : Int :=
  -(Int.ofNat (nonnegativeFactor * speedSquared))

theorem scaled_drag_power_nonpositive
    (nonnegativeFactor speedSquared : Nat) :
    scaledDragPower nonnegativeFactor speedSquared ≤ 0 := by
  change -(Int.ofNat (nonnegativeFactor * speedSquared)) ≤ 0
  have factorNonnegative : (0 : Int) ≤ (↑nonnegativeFactor : Int) := by omega
  have speedNonnegative : (0 : Int) ≤ (↑speedSquared : Int) := by omega
  have productNonnegative : (0 : Int) ≤
      (↑nonnegativeFactor : Int) * (↑speedSquared : Int) :=
    mul_nonneg factorNonnegative speedNonnegative
  have castNonnegative : (0 : Int) ≤
      Int.ofNat (nonnegativeFactor * speedSquared) := by
    simpa using productNonnegative
  omega

end Conde1963
