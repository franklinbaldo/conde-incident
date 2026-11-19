import Lean

/-!
Conditional negative-plate veto and trailing-loss non-exclusion certificate.

Motivated by `EXP-APPLAUSE-DR4-1963-PLATE-SEARCH` (Boyden Observatory plate 27600,
10 June 1963, 10-cm Tessar patrol camera, `NULL_DETECTION_NON_EXCLUSIONARY`),
where a sunlit SGP4 crossing of NORAD 528 produced a null Radon detection
(`SNR = +3.30` vs `+2.53` null control) with ~5 ms dwell time per PSF element.

All magnitudes here are **integer tenths of a magnitude** (`0.1 mag` units;
smaller values are brighter). Witness numbers are illustrative physical scales,
NOT calibrated 1963 photometry of NORAD 528. Lean certifies only the logical
implications of these premises, not empirical plate calibration or orbit fit.
-/

namespace Conde1963.OpticalPlateVeto

structure PlateObservation where
  crossedFOV : Prop
  sunlit : Prop
  steadyMagTenths : Int
  trailingLossTenths : Int
  plateStarLimitTenths : Int

/-- Effective trailed magnitude in tenths of a magnitude (smaller is brighter). -/
def effectiveTrailMagTenths (obs : PlateObservation) : Int :=
  obs.steadyMagTenths + obs.trailingLossTenths

/-- Photometric detectability requires the trailed magnitude to be at least as
bright as the plate's fixed-star limiting magnitude. -/
def photometricallyDetectable (obs : PlateObservation) : Prop :=
  effectiveTrailMagTenths obs ≤ obs.plateStarLimitTenths

/-- Sufficient conditions for a guaranteed streak detection on a plate:
geometric FOV crossing, solar illumination, and photometric detectability
after accounting for trailing loss. -/
def guaranteedDetection (obs : PlateObservation) : Prop :=
  obs.crossedFOV ∧ obs.sunlit ∧ photometricallyDetectable obs

/-- Conditional negative-plate veto: a verified non-detection excludes a
trajectory hypothesis `H` ONLY when `H` entails all three conditions
(FOV crossing, solar illumination, and photometric detectability). -/
theorem negative_plate_excludes_if_guaranteed
    (H detected : Prop) (obs : PlateObservation)
    (hModel : H → guaranteedDetection obs)
    (hDet : guaranteedDetection obs → detected)
    (hNull : ¬ detected) :
    ¬ H := by
  intro hH
  exact hNull (hDet (hModel hH))

/-- Monotonicity of trailing loss: increasing trailing loss (larger penalty)
for the same object brightness and plate limit can never turn an undetectable
streak into a detectable one. -/
theorem higher_trailing_loss_cannot_improve_detectability
    (obs1 obs2 : PlateObservation)
    (hMag : obs1.steadyMagTenths = obs2.steadyMagTenths)
    (hLim : obs1.plateStarLimitTenths = obs2.plateStarLimitTenths)
    (hLoss : obs1.trailingLossTenths ≤ obs2.trailingLossTenths)
    (hDet2 : photometricallyDetectable obs2) :
    photometricallyDetectable obs1 := by
  dsimp [photometricallyDetectable, effectiveTrailMagTenths] at *
  omega

/-- Countermodel against uncalibrated negative-plate exclusion:
a sunlit FOV crossing (`crossedFOV ∧ sunlit`) does NOT entail photometric
detectability when trailing loss pushes the effective magnitude fainter than
the plate limit (illustrative 10-cm patrol scale: steady mag 9.0, +8.0 mag
trailing loss, star limit 13.5 -> effective mag 17.0 > 13.5). -/
theorem non_detection_without_trailing_calibration_does_not_exclude :
    ∃ obs : PlateObservation,
      obs.crossedFOV ∧ obs.sunlit ∧ ¬ photometricallyDetectable obs := by
  refine ⟨⟨True, True, 90, 80, 135⟩, trivial, trivial, ?_⟩
  dsimp [photometricallyDetectable, effectiveTrailMagTenths]
  omega

/-- Non-vacuity witness: a bright object (illustrative Agena-class scale:
steady mag 3.0, +8.0 mag trailing loss, star limit 13.5 -> effective mag
11.0 <= 13.5) satisfies `guaranteedDetection`, so a verified non-detection
on such a plate acts as a valid conditional veto. -/
theorem bright_object_satisfies_guaranteed_detection :
    ∃ obs : PlateObservation, guaranteedDetection obs := by
  refine ⟨⟨True, True, 30, 80, 135⟩, trivial, trivial, ?_⟩
  dsimp [photometricallyDetectable, effectiveTrailMagTenths]
  omega

end Conde1963.OpticalPlateVeto
