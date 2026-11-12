# 🐙 Unresolved orbital-element lineages as a disjunction

**Issue:** [#15](https://github.com/franklinbaldo/conde-incident/issues/15). **PR:** [#17](https://github.com/franklinbaldo/conde-incident/pull/17). **Status:** mathematical proof obligations only, **NO physical geolocation**.

## Why the distinction matters

The published [C25#1, matrix line 118](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L118) summarizes a later Space-Track mirror. [C179#1, line 839](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L839) describes an AFSPC-attributed retrospectively formatted 1963 element set (RAAN 198.5261°, epoch 1963-10-27 14:40:16 UTC). They are **not independent primary TLEs**. The project's [AGENTS.md](https://github.com/franklinbaldo/conde-incident/blob/main/AGENTS.md) additionally flags a prior site value RAAN 284.1520° of unresolved original provenance. **Neither RAAN has been independently authenticated from original orbital tracking here**, and comparing the two bare RAAN numbers without source epochs, frames, definitions and raw records is not a valid inverse orbit solution.

The two branches are **alternative premises**, not two simultaneous independent constraints. Never average them or intersect them as if both measurements were independently verified. Nor does retaining both guarantee either is correct.

## Formal handoff (Lean 4.35.0)

`Conde1963/ScenarioAlternatives.lean` defines the feasible domain `Allowed common p ∧ (left p ∨ right p)`, with **all branch predicates unpopulated** pending source and physical validation. Theorems checked by `AxiomAudit.lean` enforce:

- The union contains every candidate satisfying either branch, and is nonempty iff at least one branch is nonempty. Its emptiness requires **both** branches empty, not merely their intersection empty.
- Additional common evidence can narrow the union but never add candidates. A surviving witness must still be produced before inferring consistency.
- A claim of Conde forced or excluded across the whole union requires the relevant property on **each** branch. A predicted inside-Conde event from one branch and outside-Conde event from another prevents either decisive global conclusion.
- A `Bool` countermodel has **two nonempty exclusive alternatives whose intersection is empty**. This is a logical counterexample, not reconstructed 1963 trajectory data.

These theorems do not prove that actual physical constraints are nonempty or tight, and the abstract `TimeLocation` type is not a certified numerical simulator.

## Contract and review gates

`python3 formal/scripts/evidence_registry.py --matrix research/evidence_matrix_C001-C238_2026-11-11.md --check formal/Conde1963/MatrixEvidence.lean --json /tmp/conde-evidence-contracts.json` exports `unresolved_element_scenarios_interface`. It includes stable C25#1/C179#1 links, both RAAN *claims* as strings, distinct branch identifiers, and default blocked gates (`historical_orbit_validation=NOT_RUN`, `original_tle_custody=NOT_VERIFIED`, `holdout_529_passed=false`, no numerical bounds, no chosen scenario). This is **not** a physically calibrated interval or observed orbital state.

Before Castor may populate a branch: obtain original source/complete epochs and lineage; reconcile orbital reference frames, units, RAAN definitions and temporal context; retain separate physical models and error enclosures for surviving branches; test independent holdouts (notably 529); establish nonempty global admissible domains and ground-impact validity. Only after all surviving branches yield consistent bounded results can a geographic statement be considered. If branches disagree, report **indeterminate**, not a pinpoint estimate. If both are inconsistent with subsequently validated evidence, diagnose inconsistent premises, not an impact site.

**Negative findings:** the original compiled ZIP (`Evidence.lean` and 154 propositions/151 labels) and independent SHA-1/SHA-256 remain unavailable. C44–C46 duplicate-label occurrences in the pinned matrix have **not** been merged. Primary tracking logs reconciling the two RAAN numbers, a calibrated 1963 atmospheric integration, a global enclosure and independent historical holdout are not available or executed in this slice. Import of the historical ZIP: `NOT_RUN`.

## Reproducibility

From the repository root: `cd formal && lake build && lake env lean Conde1963/AxiomAudit.lean`, and `python3 -m unittest discover -s formal/tests -v`. The CI should run these against the exact PR head, with explicit `#print axioms` and `sorryAx` audit. This mathematical proof suite is independent of a claim that a spacecraft fell in Conde.
