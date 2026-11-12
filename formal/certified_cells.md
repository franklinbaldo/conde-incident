# 🐙 Certified cells: finite certificates for continuous parameter spaces

## Gap closed

The `FiniteCoverage.lean` proof has a deliberately very strong premise:
every admissible parameter vector must be **exactly a point of the grid**.
It cannot be inferred from a fine mesh over real-valued orbital states.
Even an empty, pointwise-correct grid cannot eliminate a competing RAAN
scenario without a separate theorem proving exhaustive coverage.

`Conde1963/CertifiedCells.lean` introduces a different, explicitly
conditional contract: a finite list of **cells** `κ`, each permitted to
contain infinitely many candidate states `α`.

A `CertifiedCellCover` requires TWO separate proofs:

1. `covers`: **every** parameter vector satisfying
   `AlternativeAllowed common left right` lies inside at least one
   enumerated cell. This obligation is global, not a density heuristic.
2. `boundsSound`: for every admissible state inside every applicable
   cell, **every** event contained in the parameter-indexed
   `ImpactEnvelope.contains` also lies in the cell's event enclosure.

The already existing `ImpactEnvelope.soundForPredictions` ties those
bounds to a modeled event, but neither that proof nor the cell coverage
checks the original observations or validates the numerical integrator.
`GroundImpactAdmissible` additionally requires all declared custody,
independent holdout, numerical-error, coupled-physics, and ground-impact
conditions. Those Booleans are not self-authenticating.

## Conditional outcomes and falsification

Eight theorems are registered in `AxiomAudit.lean`. Three combine
cell coverage, bound soundness, an explicitly nonempty **union** of
remaining source scenarios, and the empirical gate to establish
`CONDE_EXCLUDED`, `CONDE_FORCED`, or `OTHER_WINDOW` conditional
certificates. The latter two require every survivor to have a modeled
ground impact. The third also requires the alternative window to be
disjoint from Conde. An exclusion alone never proves an impact elsewhere.

An empty cell list PLUS a formally verified covering proof yields
an empty admissible domain, **not** a geographic verdict. Adding common
evidence preserves the old coverage and event bounds but may eliminate
every state; a new nonempty-domain witness must still be established.
The previously proved incomplete-grid counterexample still applies.

The `certified_cell_interface` in the JSON export for 🦫 Castor carries
the typed theorem names, source occurrence identifiers, required gates,
and `null`/false for every uncertified result. A future numerical
implementation must provide validated interval/validated ODE or equivalent
whole-domain enclosures, prove the cell cover, reconcile epoch/frame
custody, and pass independent 529 holdout checks before filling them.

## Documentary lineage and boundaries

- C25#1 (matrix L118) and C179#1 (L839) describe reproduced secondary
  orbital data; RAAN 284.1520° versus 198.5261° is unresolved. These
  are **alternative** branches, not independent simultaneous restrictions.
- C131#1 (L502) and C197#1 (L905) cite **one** NASA/Goddard
  [*Satellite Situation Report*, 15 Nov 1963, printed p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
  NTRS 19640001198. The source reports the catalogue decay **day**,
  not a terminal epoch, impact coordinate, or measured uncertainty.
  Its facsimile was not re-inspected for this code change.
- [Frozen cumulative evidence matrix at parent PR #1 commit](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md)
  Git blob SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7`,
  241 occurrences, 238 labels; duplicate C44–C46 occurrences retained.
- No original `Evidence.lean` ZIP, 154-proposition/151-label archive,
  generator or independently authenticated ZIP digests was recovered;
  **historical import remains NOT_RUN**.

No physical cell decomposition, numerical error enclosure, complete
instrumental TLE, fitted orbit, impact, terminal location or probability
is asserted.

## Reproduce on the PR's exact HEAD

```sh
cd formal
lake update && lake build
lake env lean Conde1963/AxiomAudit.lean
python3 -m unittest discover -s tests -v
cd ..
python3 formal/scripts/evidence_registry.py --check formal/Conde1963/MatrixEvidence.lean --json /tmp/conde-evidence-contracts.json
python3 formal/scripts/verify_matrix_refs.py research/evidence_matrix_C001-C238_2026-11-11.md
```

GitHub Actions `Scientific checks` also verifies the actual PR HEAD and
runs Web lint/build. A successful compilation proves the **conditional
logic** only, not the event of 1963.
