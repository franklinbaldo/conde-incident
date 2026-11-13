import Lean

namespace Conde1963.SsrCellRepairs

/-! C241-P19: original NASA print cells, not measured orbits.
The four dates denote *publications*, never tracking epochs.
The theorem refutes one freely discarded printed cell under the
restricted additive publication-offset model and E=5 centiminutes.
It does not establish any real-world misprint or constrain Theta. -/

theorem no_single_print_cell_exception
    (k : Nat) (baseA baseB hApr hJun hJul hAug : Int)
    (eaApr eaJun eaJul eaAug ebApr ebJun ebJul ebAug : Int)
    (aAprEq : k ≠ 0 → 9460 = baseA + hApr + eaApr)
    (aAprLo : k ≠ 0 → -5 ≤ eaApr)
    (aAprHi : k ≠ 0 → eaApr ≤ 5)
    (aJunEq : k ≠ 1 → 9460 = baseA + hJun + eaJun)
    (aJunLo : k ≠ 1 → -5 ≤ eaJun)
    (aJunHi : k ≠ 1 → eaJun ≤ 5)
    (aJulEq : k ≠ 2 → 9460 = baseA + hJul + eaJul)
    (aJulLo : k ≠ 2 → -5 ≤ eaJul)
    (aJulHi : k ≠ 2 → eaJul ≤ 5)
    (aAugEq : k ≠ 3 → 9460 = baseA + hAug + eaAug)
    (aAugLo : k ≠ 3 → -5 ≤ eaAug)
    (aAugHi : k ≠ 3 → eaAug ≤ 5)
    (bAprEq : k ≠ 4 → 9410 = baseB + hApr + ebApr)
    (bAprLo : k ≠ 4 → -5 ≤ ebApr)
    (bAprHi : k ≠ 4 → ebApr ≤ 5)
    (bJunEq : k ≠ 5 → 9370 = baseB + hJun + ebJun)
    (bJunLo : k ≠ 5 → -5 ≤ ebJun)
    (bJunHi : k ≠ 5 → ebJun ≤ 5)
    (bJulEq : k ≠ 6 → 9360 = baseB + hJul + ebJul)
    (bJulLo : k ≠ 6 → -5 ≤ ebJul)
    (bJulHi : k ≠ 6 → ebJul ≤ 5)
    (bAugEq : k ≠ 7 → 9330 = baseB + hAug + ebAug)
    (bAugLo : k ≠ 7 → -5 ≤ ebAug)
    (bAugHi : k ≠ 7 → ebAug ≤ 5)
    : False := by
  have disjoint : (k ≠ 0 ∧ k ≠ 1 ∧ k ≠ 4 ∧ k ≠ 5) ∨
      (k ≠ 2 ∧ k ≠ 3 ∧ k ≠ 6 ∧ k ≠ 7) := by omega
  rcases disjoint with h | h
  ·
    have haAprEq := aAprEq h.1
    have haAprLo := aAprLo h.1
    have haAprHi := aAprHi h.1
    have haJunEq := aJunEq h.2.1
    have haJunLo := aJunLo h.2.1
    have haJunHi := aJunHi h.2.1
    have hbAprEq := bAprEq h.2.2.1
    have hbAprLo := bAprLo h.2.2.1
    have hbAprHi := bAprHi h.2.2.1
    have hbJunEq := bJunEq h.2.2.2
    have hbJunLo := bJunLo h.2.2.2
    have hbJunHi := bJunHi h.2.2.2
    omega
  ·
    have haJulEq := aJulEq h.1
    have haJulLo := aJulLo h.1
    have haJulHi := aJulHi h.1
    have haAugEq := aAugEq h.2.1
    have haAugLo := aAugLo h.2.1
    have haAugHi := aAugHi h.2.1
    have hbJulEq := bJulEq h.2.2.1
    have hbJulLo := bJulLo h.2.2.1
    have hbJulHi := bJulHi h.2.2.1
    have hbAugEq := bAugEq h.2.2.2
    have hbAugLo := bAugLo h.2.2.2
    have hbAugHi := bAugHi h.2.2.2
    omega

/-- Ten retained cells admit a source-conditional exact integer witness. -/
theorem ten_retained_cells_fit :
    ∃ (baseA baseB baseC hApr hJun hJul hAug : Int),
      ((9460 - baseA - hJun) = -5) ∧
      (-5 ≤ (9460 - baseA - hJun)) ∧
      ((9460 - baseA - hJun) ≤ 5) ∧
      ((9460 - baseA - hJul) = 5) ∧
      (-5 ≤ (9460 - baseA - hJul)) ∧
      ((9460 - baseA - hJul) ≤ 5) ∧
      ((9460 - baseA - hAug) = 5) ∧
      (-5 ≤ (9460 - baseA - hAug)) ∧
      ((9460 - baseA - hAug) ≤ 5) ∧
      ((9410 - baseB - hApr) = 5) ∧
      (-5 ≤ (9410 - baseB - hApr)) ∧
      ((9410 - baseB - hApr) ≤ 5) ∧
      ((9370 - baseB - hJun) = -5) ∧
      (-5 ≤ (9370 - baseB - hJun)) ∧
      ((9370 - baseB - hJun) ≤ 5) ∧
      ((9360 - baseB - hJul) = -5) ∧
      (-5 ≤ (9360 - baseB - hJul)) ∧
      ((9360 - baseB - hJul) ≤ 5) ∧
      ((9430 - baseC - hApr) = 5) ∧
      (-5 ≤ (9430 - baseC - hApr)) ∧
      ((9430 - baseC - hApr) ≤ 5) ∧
      ((9400 - baseC - hJun) = 5) ∧
      (-5 ≤ (9400 - baseC - hJun)) ∧
      ((9400 - baseC - hJun) ≤ 5) ∧
      ((9390 - baseC - hJul) = 5) ∧
      (-5 ≤ (9390 - baseC - hJul)) ∧
      ((9390 - baseC - hJul) ≤ 5) ∧
      ((9380 - baseC - hAug) = -5) ∧
      (-5 ≤ (9380 - baseC - hAug)) ∧
      ((9380 - baseC - hAug) ≤ 5) := by
  refine ⟨0, -90, -70, 9495, 9465, 9455, 9455, ?_⟩
  omega

end Conde1963.SsrCellRepairs
