# 🐙 Error enclosures across unresolved source-branch alternatives

**Issue:** [#15](https://github.com/franklinbaldo/conde-incident/issues/15) · **PR:** [#17](https://github.com/franklinbaldo/conde-incident/pull/17) · **Scope:** mathematical obligations, not a demonstrated orbit or impact.

## Documentary lineage and the unresolved conflict

The immutable matrix on scientific-base commit [38ee0f0](https://github.com/franklinbaldo/conde-incident/commit/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b) preserves 241 occurrences and 238 labels, including both instances of C44, C45, and C46.

* [C25#1 L118](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L118) and [C179#1 L839](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L839) describe an orbit-data lineage attributed to AFSPC/NORAD and reproduced through modern catalog mirrors. RAAN ~198.5261° is **not** a directly authenticated 1963 instrumental observation in this repository.
* The historical site RAAN 284.1520° is a separate *unverified* provenance claim, identified in `AGENTS.md`, without an independently authenticated original element set. These alternatives cannot safely be averaged, simultaneously imposed or selected by convenience. Further analysis must account for epoch/frame differences and full orbital elements.
* [C131#1 L502](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502) and [C197#1 L905](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905) describe the **same primary contemporary document**, [NASA/Goddard, *Satellite Situation Report*, 15 November 1963, p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), reporting a decay date of 8 November 1963, without a physical terminal time/place or ground impact. Two IDs are not two measurements. Facsimile previously inspected and recorded in the matrix, **not independently reinspected in this implementation round**.
* [C01#1 L19](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L19) records a Tupi/FBIS *report* of an event, not a verified physical crater or NORAD 528 impact.

## Logic proved in Lean 4.35.0

`Conde1963/ScenarioEnclosures.lean` composes the previously separate `ScenarioAlternatives` (source disjunction) and `Enclosures` (sound numerical predictions) modules. Ten audited theorems provide:

1. Conditional **Conde excluded**, **Conde forced**, and **other window identified** certificates **across the union of surviving source branches**. Each requires `GroundImpactAdmissible`, `AlternativeHasCandidate`, and appropriate sound per-parameter event envelopes. Forcing/other window also requires an actual modeled ground-impact event for every admitted state, not `Option.none`.
2. Persistence of each certificate under added *common* evidence **only with a surviving nonempty-domain witness**. A self-contradictory narrowing is not a geographic proof.
3. A certificate for a lone source branch may extend to the union **only with a formal proof that the other branch is empty**. No such proof exists for either RAAN lineage today.
4. Surviving inside/outside alternative impact predictions refute both decisive global classifications. Missing audit gates refute all three types of gated geographic verdicts, including for Castor's currently declared altitude-threshold stage.

These are logical conditionals. `ImpactEnvelope.soundForPredictions` does **not** certify historical source provenance, calibration of forces, numerical integration or independent holdouts. Nor does the Lean kernel provide coordinates. Empty finite grids do not prove empty continuous domains.

## Castor typed handoff and reproducible gate

Run from repository root:

```sh
python3 formal/scripts/evidence_registry.py \
  --matrix research/evidence_matrix_C001-C238_2026-11-11.md \
  --check formal/Conde1963/MatrixEvidence.lean \
  --json /tmp/conde-evidence-contracts.json
python3 -m unittest discover -s formal/tests -v
(cd formal && lake update && lake build && lake env lean Conde1963/AxiomAudit.lean)
```

The new `scenario_enclosure_interface` in the exported JSON references both RAAN branch IDs, exact C25/C179 occurrence identities, and the single NASA/Goddard lineage for C131/C197. It reports `null` for impact/verdict/error enclosures; `false` for custody, global-domain, holdout and impact gates; `NOT_RUN` for importing the original Lean 154-proposition/151-label archive. The code contains **no numerical orbit, fabricated data, or world-level verdict**.

**Next decisive missing inputs:** original authenticated TLE/observation series for 527/528/529 with per-epoch provenance and reference frames; sound calibrated physical integration and numerical bounds for every surviving scenario; source-independent blind holdout; validated ground-impact dynamics; numerical region disjointness or strict identification. A document-day report and a finite grid cannot replace these.

**Negative finding:** `Evidence.lean` and the original compiled ZIP, 154 propositions/151 labels, registry/generator and independent custody hashes remain unavailable here; historical import and historical-content audit remain **NOT_RUN**. None of C44–C46 duplicates has been merged or reinterpreted.

Review by 🦅 Gavião; integration by 🐘 Elefante only after the base PR #1 and green HEAD CI. This PR remains draft. No blog, publication, external contacts, rebase or merge.
