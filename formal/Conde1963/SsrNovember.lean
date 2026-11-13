import Lean

namespace Conde1963.SsrNovember

/-! Source-linked NASA 1963 3A / 3C November printed fields.
Integer units: centiminutes for nodal periods, half-kilometers for apogee.
Intervals assume nearest last printed digit; neither instrument sigma
nor a claim about NORAD 528's terminal orbit. -/

/-- 3C Nov15->Nov30 period drop exceeds 3A,
    only if published values are nearest-digit rounded. -/
theorem printed_november_period_3c_gt_3a
    (c15 c30 a15 a30 : Int)
    (hc15lo : 9255 ≤ c15) (hc15hi : c15 ≤ 9265)
    (hc30lo : 9215 ≤ c30) (hc30hi : c30 ≤ 9225)
    (ha15lo : 9455 ≤ a15) (ha15hi : a15 ≤ 9465)
    (ha30lo : 9455 ≤ a30) (ha30hi : a30 ≤ 9465) :
    (30 ≤ c15 - c30 ∧ c15 - c30 ≤ 50) ∧
    (-10 ≤ a15 - a30 ∧ a15 - a30 ≤ 10) ∧
    (a15 - a30 < c15 - c30) := by
  omega

/-- 3C Nov15->Nov30 apogee drop exceeds 3A,
    only if published values are nearest-digit rounded. -/
theorem printed_november_apogee_3c_gt_3a
    (c15 c30 a15 a30 : Int)
    (hc15lo : 839 ≤ c15) (hc15hi : c15 ≤ 841)
    (hc30lo : 779 ≤ c30) (hc30hi : c30 ≤ 781)
    (ha15lo : 1071 ≤ a15) (ha15hi : a15 ≤ 1073)
    (ha30lo : 1065 ≤ a30) (ha30hi : a30 ≤ 1067) :
    (58 ≤ c15 - c30 ∧ c15 - c30 ≤ 62) ∧
    (4 ≤ a15 - a30 ∧ a15 - a30 ≤ 8) ∧
    (a15 - a30 < c15 - c30) := by
  omega

end Conde1963.SsrNovember
