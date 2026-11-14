import Lean

/-!
G62: exact covariance identity for two linearized optical bearings that
share a single latent state. J_a and J_b are sensitivities to the SAME error.
For a scalar latent noise with unit variance, contrast covariance has a
negative two-way cross term. The diagonal-only approximation silently
asserts independent replicas of the state and is not mathematically equal.
This is a structural theorem; numerical G61/G62 carries the actual 6D GCRS
state, and no covariance or optical record for 1963 NORAD 528 is calibrated.
-/
namespace Conde1963.SharedStateParallax

/-- One-dimensional exact instance of H_diff Σ H_diffᵀ, with Σ=1. -/
def sharedContrastVariance (ha hb : Int) : Int :=
  (ha - hb) * (ha - hb)

/-- What two unrelated latent states would produce instead. -/
def independentMarginalVariance (ha hb : Int) : Int :=
  ha * ha + hb * hb

/-- The missing cross covariance may NOT be silently discarded. -/
theorem covariance_includes_two_cross_terms (ha hb : Int) :
    sharedContrastVariance ha hb =
      independentMarginalVariance ha hb - (ha * hb + hb * ha) := by
  simp only [sharedContrastVariance, independentMarginalVariance,
    mul_sub, sub_mul]
  omega

/-- Two equally sensitive views of the same latent state have zero
first-order *differential* uncertainty, not two independent variances. -/
theorem identical_sensitivities_cancel_shared_noise (h : Int) :
    sharedContrastVariance h h = 0 := by
  simp [sharedContrastVariance]

/-- Numerical adversarial witness: independent-marginal treatment makes
positive uncertainty out of an exactly cancelled common perturbation. -/
theorem independence_approximation_changes_result :
    sharedContrastVariance 7 7 = 0 ∧
    independentMarginalVariance 7 7 = 98 := by
  decide

end Conde1963.SharedStateParallax
