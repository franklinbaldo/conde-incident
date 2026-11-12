# 🦫 Energy/work audit for the coupled orbital kernel

**Small follow-up extraction from [draft PR #5](https://github.com/franklinbaldo/conde-incident/pull/5), issue [#4](https://github.com/franklinbaldo/conde-incident/issues/4).** The existing `main` now already contains `src/lib/orbitPhysics.ts` (blob `484e3b1e...`) and `tests/orbitPhysics.test.mjs` from a separate integration. We therefore do **not** copy or overwrite the existing kernel. This slice extracts only `src/lib/orbitEnergyAudit.ts` and its five targeted synthetic regressions, with a pinned-head Actions check.

The model is 3D Earth-centred inertial Cartesian (r,v), km, km/s and elapsed seconds, with central gravity and optional axisymmetric J2 plus only explicitly sourced co-rotational atmospheric drag. The auditable mechanical invariant is **Jacobi-like energy**

`J = |v|²/2 + U_J2(r) - Ω·L` (km²/s²).

With the same drag law as the state integrator, `dJ/dt = a_drag·(v - Ω×r) <= 0` (km²/s³) for nonnegative density and Cd·A/m. In an axisymmetric stationary potential without drag, this integral is constant numerically. The code compares integrated change to a trapezoidal approximation of drag work at each coupled state step and cumulatively, reporting either `NUMERICALLY_CONSISTENT` or `NUMERICALLY_UNRESOLVED` under a **caller-provided** tolerance. A failed balance is preserved as a *negative computational result*, never silently counted as a physical exclusion.

The audit also handles a numerically detected **descending altitude threshold**, stopping the budget at the event time instead of counting an unintegrated remainder. The threshold is a convention, **not** physical breakup or ground impact. Step-halving is necessary: RK4/quadrature closure under one step size is neither a certified global error interval nor a 1963 trajectory proof.

## Reproduce

`node --experimental-strip-types --test tests/orbitEnergyAudit.test.mjs` (Node 22), as pinned by `.github/workflows/orbit-energy-budget.yml`. Five **synthetic** controls: conservative budget, dissipative drag and quadrature residual, coarse-versus-refined negative result, threshold event truncation, invalid inputs/source.

## Primary record and dependency chain

The cumulative [C197/C198/C201 entries in PR #1](https://github.com/franklinbaldo/conde-incident/blob/research/scientific-integrity-foundation/research/evidence_matrix_C001-C238_2026-11-11.md) cite one original NASA/Goddard *Satellite Situation Report*, vol. 3 no. 22, **15 Nov 1963, printed p. 8**, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf): 1963-003B is recorded as decayed **8 Nov 1963** without hour or location. NASA/NORAD-derived secondary catalogs do not constitute independent tracking measurements. C179 [528 mirrored retrospective-format TLE](https://www.itau.magnetic-declination.com/satellite/?s=528) has RAAN 198.5261°, but it does not supply a contemporaneous Cartesian osculating state or a calibrated atmosphere; the older unsourced 284.1520° is not a second independent measurement.

**NOT_RUN / UNKNOWN:** Lean-certified historical admissible-domain export; time/frame/covariance verified independent 527/529 holdouts; SGP4 independent baseline; physically sourced 1963 density and Cd·A/m; modeled 528 reentry hour/position or Conde impact. No posterior probabilities or geographic claims are output.
