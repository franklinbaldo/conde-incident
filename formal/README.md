# Lean 4: Conde 1963

This folder starts the transfer of the previously compiled 11 November 2026 Lean 4.35.0 research archive.

`lake build` checks the **logical core**: provenance dependency, exact arithmetic from catalog statistics, holdout metric comparison and the failure of a date-only constraint to identify a geographic site.

**Important:** Compiling this code does not certify SGP4, a radar measurement, a TLE's authenticity or a trajectory to Conde.

The full historical package also contains `Evidence.lean`, the 154-entry structured registry, a generator and a 151-label cumulative matrix. Those larger files are **not yet incorporated** by this initial PR; their source archive remains the original compiled 2026-11-11 package. Never describe this subset as the full historical corpus.

The `last528` recorded RAAN (198.5261°) highlights a provenance conflict with the existing site (284.1520°). Both need verification against the primary TLE record before a terminal position can be claimed.
