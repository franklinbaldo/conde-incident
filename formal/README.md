# Conde 1963 · Lean 4.35.0 minimal core

This deliberately small slice is extracted from [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), source HEAD `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`. It creates the compiler/toolchain foundation for the formal work in [Polvo PR #17](https://github.com/franklinbaldo/conde-incident/pull/17), without bringing the entire still-open PR stack into main.

Run `cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean`.
Core proofs distinguish records by source chain, count 119 unique mirrored epochs (20+45+54), and demonstrate a conditional date-only non-uniqueness claim. The holdout MAE values are transcribed historic inputs and **not separately reproduced by this proof**. The illustrative Conde/elsewhere `ReentryCandidate` values are *countermodels*, not observed events. The RAAN 198.5261° is a **secondary catalog reference**, not a certified physical constraint. The prior site's unsupported 284.1520° is retired from active inference, retained only in Git history.

**Source lineage:** secondary 527/528/529 mirrored orbital elements analyzed in PR #14, not independent original NORAD 1963 tracking; NASA/Goddard *Satellite Situation Report* 15 Nov 1963, printed p. 8 (https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) records a day of decay, not coordinates/time. C131/C197 are two IDs for this same document in the cumulative matrix still in PR #1.

**Not included yet:** the complete earlier `Evidence.lean` corpus of 154 propositions/151 labels, matrix C01-C238 as a standalone source file, full PR #17 modules, original ZIP, or historical simulation/holdouts. Import: NOT_RUN. No inference of impact or geographical probability.

## Legacy Evidence.lean custody (154 rows, 151 identifiers)

`Conde1963/Evidence.lean` preserves a **local candidate file**, recovered on
12 Nov 2026 from the agent's earlier Jatobá workspace, byte-identical to SHA-256
`ac2c1982f2f9bc66d31f3d39cc0247dd02e8815bfef457c5d7ff5a8d6eb6f3ee`.
The original ZIP, its build log and authorship chain have **not** been recovered.
It cannot be called an authenticated original compilation. `Core.lean` supplies the
missing `Outcome` compatibility type without changing the preserved file.

Run `python3 formal/scripts/audit_legacy_154.py` and
`python3 -m unittest discover -s formal/tests -p 'test_legacy_evidence.py' -v`.
The current matrix and archive agree in **146 of 154 row occurrences**, including
C44–C46's two occurrences each. **C144–C151 have been reused with different
meanings** by the cumulative C001–C238 snapshot; do not resolve references to
those eight codes without specifying a snapshot. See
[`research/constraints/legacy_evidence_154_custody.md`](../research/constraints/legacy_evidence_154_custody.md).

The Lean import is a compilation check of a historical *data registry*, not
154 independently proved propositions and not a restriction on the impact site.
