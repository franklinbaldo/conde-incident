import Lean

namespace Conde1963.SsrJackknife

/-! C241-P22. Source-locked publication leave-one-out editorial
model; not instrument errors, not tracking epochs, Theta unchanged.
The independently established 527/529 contrast supplies each lower
bound; an explicit witness attains it for every retained printed cell. -/

def within (value baseline offset radius : Int) : Prop :=
  -radius ≤ value - baseline - offset ∧
  value - baseline - offset ≤ radius

/-- Deleting 1963-04-30 still forces E >= 120 centiminutes. -/
theorem without_0430_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9400 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    120 ≤ E := by
  omega

/-- Exact attaining witness for all 20 retained cells. -/
theorem without_0430_witness :
    ∃ (b527 b528 b529 h0630 h0731 h0815 h1015 h1115 h1130 h1215 h1231 : Int),
      within 9460 b527 h0630 120 ∧
      within 9460 b527 h0731 120 ∧
      within 9460 b527 h0815 120 ∧
      within 9460 b527 h1015 120 ∧
      within 9460 b527 h1115 120 ∧
      within 9460 b527 h1130 120 ∧
      within 9460 b527 h1215 120 ∧
      within 9460 b527 h1231 120 ∧
      within 9370 b528 h0630 120 ∧
      within 9360 b528 h0731 120 ∧
      within 9330 b528 h0815 120 ∧
      within 9240 b528 h1015 120 ∧
      within 9400 b529 h0630 120 ∧
      within 9390 b529 h0731 120 ∧
      within 9380 b529 h0815 120 ∧
      within 9330 b529 h1015 120 ∧
      within 9260 b529 h1115 120 ∧
      within 9220 b529 h1130 120 ∧
      within 9160 b529 h1215 120 ∧
      within 8920 b529 h1231 120 := by
  refine ⟨9460, 9310, 9160, 120, 110, 100, 50, -20, -60, -120, -120, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-06-30 still forces E >= 128 centiminutes. -/
theorem without_0630_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    128 ≤ E := by
  omega

/-- Exact attaining witness for all 20 retained cells. -/
theorem without_0630_witness :
    ∃ (b527 b528 b529 h0430 h0731 h0815 h1015 h1115 h1130 h1215 h1231 : Int),
      within 9460 b527 h0430 128 ∧
      within 9460 b527 h0731 128 ∧
      within 9460 b527 h0815 128 ∧
      within 9460 b527 h1015 128 ∧
      within 9460 b527 h1115 128 ∧
      within 9460 b527 h1130 128 ∧
      within 9460 b527 h1215 128 ∧
      within 9460 b527 h1231 128 ∧
      within 9410 b528 h0430 128 ∧
      within 9360 b528 h0731 128 ∧
      within 9330 b528 h0815 128 ∧
      within 9240 b528 h1015 128 ∧
      within 9430 b529 h0430 128 ∧
      within 9390 b529 h0731 128 ∧
      within 9380 b529 h0815 128 ∧
      within 9330 b529 h1015 128 ∧
      within 9260 b529 h1115 128 ∧
      within 9220 b529 h1130 128 ∧
      within 9160 b529 h1215 128 ∧
      within 8920 b529 h1231 128 := by
  refine ⟨9460, 9342, 9176, 126, 86, 76, 26, -44, -84, -128, -128, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-07-31 still forces E >= 128 centiminutes. -/
theorem without_0731_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    128 ≤ E := by
  omega

/-- Exact attaining witness for all 20 retained cells. -/
theorem without_0731_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0815 h1015 h1115 h1130 h1215 h1231 : Int),
      within 9460 b527 h0430 128 ∧
      within 9460 b527 h0630 128 ∧
      within 9460 b527 h0815 128 ∧
      within 9460 b527 h1015 128 ∧
      within 9460 b527 h1115 128 ∧
      within 9460 b527 h1130 128 ∧
      within 9460 b527 h1215 128 ∧
      within 9460 b527 h1231 128 ∧
      within 9410 b528 h0430 128 ∧
      within 9370 b528 h0630 128 ∧
      within 9330 b528 h0815 128 ∧
      within 9240 b528 h1015 128 ∧
      within 9430 b529 h0430 128 ∧
      within 9400 b529 h0630 128 ∧
      within 9380 b529 h0815 128 ∧
      within 9330 b529 h1015 128 ∧
      within 9260 b529 h1115 128 ∧
      within 9220 b529 h1130 128 ∧
      within 9160 b529 h1215 128 ∧
      within 8920 b529 h1231 128 := by
  refine ⟨9460, 9342, 9176, 126, 96, 76, 26, -44, -84, -128, -128, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-08-15 still forces E >= 128 centiminutes. -/
theorem without_0815_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    128 ≤ E := by
  omega

/-- Exact attaining witness for all 20 retained cells. -/
theorem without_0815_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0731 h1015 h1115 h1130 h1215 h1231 : Int),
      within 9460 b527 h0430 128 ∧
      within 9460 b527 h0630 128 ∧
      within 9460 b527 h0731 128 ∧
      within 9460 b527 h1015 128 ∧
      within 9460 b527 h1115 128 ∧
      within 9460 b527 h1130 128 ∧
      within 9460 b527 h1215 128 ∧
      within 9460 b527 h1231 128 ∧
      within 9410 b528 h0430 128 ∧
      within 9370 b528 h0630 128 ∧
      within 9360 b528 h0731 128 ∧
      within 9240 b528 h1015 128 ∧
      within 9430 b529 h0430 128 ∧
      within 9400 b529 h0630 128 ∧
      within 9390 b529 h0731 128 ∧
      within 9330 b529 h1015 128 ∧
      within 9260 b529 h1115 128 ∧
      within 9220 b529 h1130 128 ∧
      within 9160 b529 h1215 128 ∧
      within 8920 b529 h1231 128 := by
  refine ⟨9460, 9342, 9176, 126, 96, 86, 26, -44, -84, -128, -128, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-10-15 still forces E >= 128 centiminutes. -/
theorem without_1015_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    128 ≤ E := by
  omega

/-- Exact attaining witness for all 20 retained cells. -/
theorem without_1015_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0731 h0815 h1115 h1130 h1215 h1231 : Int),
      within 9460 b527 h0430 128 ∧
      within 9460 b527 h0630 128 ∧
      within 9460 b527 h0731 128 ∧
      within 9460 b527 h0815 128 ∧
      within 9460 b527 h1115 128 ∧
      within 9460 b527 h1130 128 ∧
      within 9460 b527 h1215 128 ∧
      within 9460 b527 h1231 128 ∧
      within 9410 b528 h0430 128 ∧
      within 9370 b528 h0630 128 ∧
      within 9360 b528 h0731 128 ∧
      within 9330 b528 h0815 128 ∧
      within 9430 b529 h0430 128 ∧
      within 9400 b529 h0630 128 ∧
      within 9390 b529 h0731 128 ∧
      within 9380 b529 h0815 128 ∧
      within 9260 b529 h1115 128 ∧
      within 9220 b529 h1130 128 ∧
      within 9160 b529 h1215 128 ∧
      within 8920 b529 h1231 128 := by
  refine ⟨9460, 9382, 9176, 126, 96, 86, 76, -44, -84, -128, -128, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-11-15 still forces E >= 128 centiminutes. -/
theorem without_1115_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    128 ≤ E := by
  omega

/-- Exact attaining witness for all 21 retained cells. -/
theorem without_1115_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0731 h0815 h1015 h1130 h1215 h1231 : Int),
      within 9460 b527 h0430 128 ∧
      within 9460 b527 h0630 128 ∧
      within 9460 b527 h0731 128 ∧
      within 9460 b527 h0815 128 ∧
      within 9460 b527 h1015 128 ∧
      within 9460 b527 h1130 128 ∧
      within 9460 b527 h1215 128 ∧
      within 9460 b527 h1231 128 ∧
      within 9410 b528 h0430 128 ∧
      within 9370 b528 h0630 128 ∧
      within 9360 b528 h0731 128 ∧
      within 9330 b528 h0815 128 ∧
      within 9240 b528 h1015 128 ∧
      within 9430 b529 h0430 128 ∧
      within 9400 b529 h0630 128 ∧
      within 9390 b529 h0731 128 ∧
      within 9380 b529 h0815 128 ∧
      within 9330 b529 h1015 128 ∧
      within 9220 b529 h1130 128 ∧
      within 9160 b529 h1215 128 ∧
      within 8920 b529 h1231 128 := by
  refine ⟨9460, 9342, 9176, 126, 96, 86, 76, 26, -84, -128, -128, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-11-30 still forces E >= 128 centiminutes. -/
theorem without_1130_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    128 ≤ E := by
  omega

/-- Exact attaining witness for all 21 retained cells. -/
theorem without_1130_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0731 h0815 h1015 h1115 h1215 h1231 : Int),
      within 9460 b527 h0430 128 ∧
      within 9460 b527 h0630 128 ∧
      within 9460 b527 h0731 128 ∧
      within 9460 b527 h0815 128 ∧
      within 9460 b527 h1015 128 ∧
      within 9460 b527 h1115 128 ∧
      within 9460 b527 h1215 128 ∧
      within 9460 b527 h1231 128 ∧
      within 9410 b528 h0430 128 ∧
      within 9370 b528 h0630 128 ∧
      within 9360 b528 h0731 128 ∧
      within 9330 b528 h0815 128 ∧
      within 9240 b528 h1015 128 ∧
      within 9430 b529 h0430 128 ∧
      within 9400 b529 h0630 128 ∧
      within 9390 b529 h0731 128 ∧
      within 9380 b529 h0815 128 ∧
      within 9330 b529 h1015 128 ∧
      within 9260 b529 h1115 128 ∧
      within 9160 b529 h1215 128 ∧
      within 8920 b529 h1231 128 := by
  refine ⟨9460, 9342, 9176, 126, 96, 86, 76, 26, -44, -128, -128, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-12-15 still forces E >= 128 centiminutes. -/
theorem without_1215_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 8920 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    128 ≤ E := by
  omega

/-- Exact attaining witness for all 21 retained cells. -/
theorem without_1215_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0731 h0815 h1015 h1115 h1130 h1231 : Int),
      within 9460 b527 h0430 128 ∧
      within 9460 b527 h0630 128 ∧
      within 9460 b527 h0731 128 ∧
      within 9460 b527 h0815 128 ∧
      within 9460 b527 h1015 128 ∧
      within 9460 b527 h1115 128 ∧
      within 9460 b527 h1130 128 ∧
      within 9460 b527 h1231 128 ∧
      within 9410 b528 h0430 128 ∧
      within 9370 b528 h0630 128 ∧
      within 9360 b528 h0731 128 ∧
      within 9330 b528 h0815 128 ∧
      within 9240 b528 h1015 128 ∧
      within 9430 b529 h0430 128 ∧
      within 9400 b529 h0630 128 ∧
      within 9390 b529 h0731 128 ∧
      within 9380 b529 h0815 128 ∧
      within 9330 b529 h1015 128 ∧
      within 9260 b529 h1115 128 ∧
      within 9220 b529 h1130 128 ∧
      within 8920 b529 h1231 128 := by
  refine ⟨9460, 9342, 9176, 126, 96, 86, 76, 26, -44, -84, -128, ?_⟩
  simp only [within]
  omega

/-- Deleting 1963-12-31 still forces E >= 68 centiminutes. -/
theorem without_1231_lower_bound
    (b527 b529 hFirst hLast eaFirst eaLast ecFirst ecLast E : Int)
    (aFirst : 9460 = b527 + hFirst + eaFirst)
    (aLast : 9460 = b527 + hLast + eaLast)
    (cFirst : 9430 = b529 + hFirst + ecFirst)
    (cLast : 9160 = b529 + hLast + ecLast)
    (eaFirstLo : -E ≤ eaFirst) (eaFirstHi : eaFirst ≤ E)
    (eaLastLo : -E ≤ eaLast) (eaLastHi : eaLast ≤ E)
    (ecFirstLo : -E ≤ ecFirst) (ecFirstHi : ecFirst ≤ E)
    (ecLastLo : -E ≤ ecLast) (ecLastHi : ecLast ≤ E) :
    68 ≤ E := by
  omega

/-- Exact attaining witness for all 21 retained cells. -/
theorem without_1231_witness :
    ∃ (b527 b528 b529 h0430 h0630 h0731 h0815 h1015 h1115 h1130 h1215 : Int),
      within 9460 b527 h0430 68 ∧
      within 9460 b527 h0630 68 ∧
      within 9460 b527 h0731 68 ∧
      within 9460 b527 h0815 68 ∧
      within 9460 b527 h1015 68 ∧
      within 9460 b527 h1115 68 ∧
      within 9460 b527 h1130 68 ∧
      within 9460 b527 h1215 68 ∧
      within 9410 b528 h0430 68 ∧
      within 9370 b528 h0630 68 ∧
      within 9360 b528 h0731 68 ∧
      within 9330 b528 h0815 68 ∧
      within 9240 b528 h1015 68 ∧
      within 9430 b529 h0430 68 ∧
      within 9400 b529 h0630 68 ∧
      within 9390 b529 h0731 68 ∧
      within 9380 b529 h0815 68 ∧
      within 9330 b529 h1015 68 ∧
      within 9260 b529 h1115 68 ∧
      within 9220 b529 h1130 68 ∧
      within 9160 b529 h1215 68 := by
  refine ⟨9460, 9342, 9296, 66, 36, 26, 16, -34, -68, -68, -68, ?_⟩
  simp only [within]
  omega

end Conde1963.SsrJackknife
