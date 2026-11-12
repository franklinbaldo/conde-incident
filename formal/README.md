# Conde 1963 · Lean 4.35.0 minimal core

This deliberately small slice is extracted from [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), source HEAD `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`. It creates the compiler/toolchain foundation for the formal work in [Polvo PR #17](https://github.com/franklinbaldo/conde-incident/pull/17), without bringing the entire still-open PR stack into main.

Run `cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean`.
Core proofs distinguish records by source chain, count 119 unique mirrored epochs (20+45+54), and demonstrate a conditional date-only non-uniqueness claim. The holdout MAE values are transcribed historic inputs and **not separately reproduced by this proof**. The illustrative Conde/elsewhere `ReentryCandidate` values are *countermodels*, not observed events. The RAAN 198.5261° is a **secondary catalog reference**, not a certified physical constraint. The prior site's unsupported 284.1520° is retired from active inference, retained only in Git history.

**Source lineage:** secondary 527/528/529 mirrored orbital elements analyzed in PR #14, not independent original NORAD 1963 tracking; NASA/Goddard *Satellite Situation Report* 15 Nov 1963, printed p. 8 (https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) records a day of decay, not coordinates/time. C131/C197 are two IDs for this same document in the cumulative matrix still in PR #1.

**Not included yet:** the complete earlier `Evidence.lean` corpus of 154 propositions/151 labels, matrix C01-C238 as a standalone source file, full PR #17 modules, original ZIP, or historical simulation/holdouts. Import: NOT_RUN. No inference of impact or geographical probability.
