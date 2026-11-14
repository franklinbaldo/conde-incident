import Lean

/-!
G63: a joint measurement covariance, unlike two independently supplied
marginals, has cross blocks. The scalar instance below certifies the
cross-block identity and the fact that the diagonal-only approximation
can err in BOTH directions. It is a structural check of the numerical
4D receiver covariance projection, not an instrumental calibration.
-/
namespace Conde1963.CorrelatedReceiverNoise

/-- 1D A-B receiver contrast variance, with a symmetric cross covariance. -/
def contrastVariance (varA varB crossAB : Int) : Int :=
  varA + varB - (crossAB + crossAB)

/-- The perfect-common-mode case: same unit calibration noise in A and B. -/
theorem perfectly_correlated_measurements_cancel :
    contrastVariance 2 2 2 = 0 := by
  decide

/-- Opposite sensitivities amplify the contrast compared with zero cross. -/
theorem perfectly_anticorrelated_measurements_amplify :
    contrastVariance 2 2 (-2) = 8 := by
  decide

theorem zero_cross_independence_is_a_distinct_model :
    contrastVariance 2 2 0 = 4 := by
  decide

/-- The full cross-covariance cannot be replaced by marginals: a shared
latent state uses one perturbation with sensitivities ha and hb. -/
theorem shared_latent_receiver_contrast_identity (ha hb : Int) :
    (ha - hb) * (ha - hb) =
       ha * ha + hb * hb - (ha * hb + hb * ha) := by
  simp only [Int.mul_sub, Int.sub_mul]
  omega

end Conde1963.CorrelatedReceiverNoise
