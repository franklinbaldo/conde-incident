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


## Documentary-to-Lean bridge (Cnn#occurrence, 12 Nov 2026)

The generator in formal/scripts/compile_documentary_links.py deterministically
imports the curated lineage records, frozen C001-C238 matrix, and six secondary
NORAD-528 elements from the cumulative physical graph into
formal/Conde1963/Documentary.lean.

Reproduce:

    python3 formal/scripts/compile_documentary_links.py --check
    python3 -m unittest discover -s formal/tests -p test_documentary_links.py -v
    cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean

The typed contract records 24 curated source-to-occurrence citations out of
241 matrix occurrences (217 unmapped) and six secondary orbital fields
(inclination, RAAN, eccentricity, argument of perigee, mean anomaly and mean
motion), all under C179#1. Snapshot SHA, line SHA, work ID, source family,
units and TLE epoch are retained. C197#1 provides catalogued decay DAY only;
NTRS C198#1 is metadata for the same NASA work, not an independent sensor.

Falsification and negative result: sources cannot be promoted to original
1963 tracking. No instrument observation epoch, frame calibration, covariance
or new 527/529 dynamic holdout is available. Before/after admissible domain:
unchanged; physical constraints activated: zero; numerical holdout: NOT_RUN.
Next: find an authenticated full 528 primary tracking element set (epoch,
frame, checksum, measurement covariance) for calibrated fitting with
527/529 controls and error in physical units. Lean compilation validates
the data types, not the historical occurrence of an impact.
