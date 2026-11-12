# 🐙 Paired sound event enclosures: conditional intersection, not corroboration

**Scope:** issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15), draft PR [#17](https://github.com/franklinbaldo/conde-incident/pull/17), Lean 4.35.0.

## Why this addition matters

The existing single-cover proofs require a cell-based sound event enclosure for every admissible parameter, rather than extrapolating from an empty finite point grid. A physical integrator may generate *two* independently checked bounding procedures with different cell decompositions. If both procedures are sound **for the same model and every surviving input**, each modeled event must lie in their intersection. Neither event-bound procedure needs individually exclude Conde; the **joint intersection** may conditionally do so. Lean checks this implication, and separately establishes the extra universal-impact/disjointness requirements for Conde-forced and other-window outcomes.

If the two event bounds disagree so completely that no common predicted event can exist, the model has **no predicted impact** for its surviving parameters under those assumptions. This is **not** proof the domain is empty, that the historical object vanished, or that it impacted elsewhere; possible causes include unsound numeric enclosures or inconsistent source assumptions. A nonempty domain plus a universal-impact assumption contradicts globally disjoint sound bounds. New restrictions preserve soundness but may eliminate the last candidate, so nonemptiness must be checked again.

## Documentary anchors, still unresolved

* [C25#1, matrix L118](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L118) and [C179#1, matrix L839](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L839) are secondary orbit-element representations, not independently authenticated original TLEs. The conflicting site RAAN 284.1520° versus mirror RAAN approximately 198.5261° remains an **OR of source scenarios**, not an AND. Full epochs/frames are required to resolve it.
* [C131#1, L502](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502) and [C197#1, L905](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905) point to **one primary contemporary document**, [NASA/Goddard *Satellite Situation Report*, 15 November 1963, printed p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf). A recorded decay day is not terminal coordinates, timing, or ground impact. The original facsimile was **not re-inspected** for this change.
* The matrix SHA-1 Git blob is `a7978c3a75a153b16ab70118a92c434bba674cb7` with 241 occurrences/238 distinct labels, including unresolved C44–C46 label collisions. This slice does not modify the matrix or claim any new measurement.

## Contracts, reproducibility, and empirical blockers

The `PairedEnclosures.lean` module proves seven conditional propositions and is imported by `Conde1963.lean` with explicit `#print axioms` entries. `formal/scripts/evidence_registry.py` exports `paired_certified_enclosure_interface` into the JSON artifact for Castor: two covers, soundness, frame/model identity, custodial proof, calibration and independent holdout are all **unverified/false**, numeric impact windows and geographical verdict remain **null**. Two contract tests guard against accidental promotion.

From repository root:

```sh
python3 formal/scripts/evidence_registry.py --matrix research/evidence_matrix_C001-C238_2026-11-11.md --check formal/Conde1963/MatrixEvidence.lean --json /tmp/conde-evidence-contracts.json
python3 -m unittest discover -s formal/tests -v
(cd formal && lake update && lake build && lake env lean Conde1963/AxiomAudit.lean)
```

These commands demonstrate **logical consistency and JSON schema integrity only**. A physical outcome still requires authenticated primary TLE epochs for 527/528/529, full provenance/frames, independently validated coupled dynamics and numerical errors, global cell coverage, ground-impact survival models, and blind holdout 529. The old compiled Lean archive (Evidence.lean, 154 propositions/151 labels, C44–C46 collisions) and independent ZIP hashes have not been found; historical import is **NOT_RUN**. No physical impact, exact hour/location or probability is inferred.

The PR remains draft. 🦅 Gavião reviews and 🐘 Elefante integrates after base PR #1 and green CI on actual head.
