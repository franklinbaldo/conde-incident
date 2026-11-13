import Lean

namespace Conde1963.SsrOffsetThreshold

/-! Source-locked C241-P13, units: 0.01 minute. This is a *printing model*
threshold, not a measurement of the tracking system or a bound on Theta.
Publication dates do not identify orbital observation epochs. -/

/-- Even permitting independent residuals for both objects and both endpoint
editions, a single edition-wide additive bias demands >= 25 centiminutes of
residual budget for at least one cell. -/
theorem shared_edition_bias_requires_25_centimin
    (baseA baseC biasFirst biasLast errAFirst errALast errCFirst errCLast E : Int)
    (ha0 : 9460 = baseA + biasFirst + errAFirst)
    (ha2 : 9460 = baseA + biasLast + errALast)
    (hc0 : 9260 = baseC + biasFirst + errCFirst)
    (hc2 : 9160 = baseC + biasLast + errCLast)
    (ha0lo : -E ≤ errAFirst) (ha0hi : errAFirst ≤ E)
    (ha2lo : -E ≤ errALast) (ha2hi : errALast ≤ E)
    (hc0lo : -E ≤ errCFirst) (hc0hi : errCFirst ≤ E)
    (hc2lo : -E ≤ errCLast) (hc2hi : errCLast ≤ E)
    : 25 ≤ E := by
  omega

/-- All six published cells are attainable at exactly 25 centiminutes.
Together with the lower bound above, the minimax threshold is sharp. -/
theorem all_six_editions_attain_25_centimin :
    ∃ (baseA baseC biasFirst biasMiddle biasLast : Int),
      (9460 = baseA + biasFirst + (-25)) ∧
      (9460 = baseA + biasMiddle + (-5)) ∧
      (9460 = baseA + biasLast + (25)) ∧
      (9260 = baseC + biasFirst + (25)) ∧
      (9220 = baseC + biasMiddle + (5)) ∧
      (9160 = baseC + biasLast + (-25)) := by
  refine ⟨9500, 9250, -15, -35, -65, ?_⟩
  omega

end Conde1963.SsrOffsetThreshold
