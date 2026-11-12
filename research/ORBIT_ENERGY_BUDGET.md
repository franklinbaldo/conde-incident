# 🦫 Energy/work audit for the coupled orbital kernel

**Small follow-up extraction from [draft PR #5](https://github.com/franklinbaldo/conde-incident/pull/5), issue [#4](https://github.com/franklinbaldo/conde-incident/issues/4).** The existing `main` now already contains `src/lib/orbitPhysics.ts` (blob `484e3b1e...`) and `tests/orbitPhysics.test.mjs` from a separate integration. We therefore do **not** copy or overwrite the existing kernel. This slice extracts only `src/lib/orbitEnergyAudit.ts` and ten targeted synthetic regressions, with a pinned-head Actions check.

The model is 3D Earth-centred inertial Cartesian (r,v), km, km/s and elapsed seconds, with central gravity and optional axisymmetric J2 plus only explicitly sourced co-rotational atmospheric drag. The auditable mechanical invariant is **Jacobi-like energy**

`J = |v|²/2 + U_J2(r) - Ω·L` (km²/s²).

With the same drag law as the state integrator, `dJ/dt = a_drag·(v - Ω×r) <= 0` (km²/s³) for nonnegative density and Cd·A/m. In an axisymmetric stationary potential without drag, this integral is constant numerically. The code compares integrated change to a trapezoidal approximation of drag work at each coupled state step and cumulatively, reporting either `NUMERICALLY_CONSISTENT` or `NUMERICALLY_UNRESOLVED` under a **caller-provided** tolerance. A failed balance is preserved as a *negative computational result*, never silently counted as a physical exclusion.

The audit also handles a numerically detected **descending altitude threshold**, stopping the budget at the event time instead of counting an unintegrated remainder. The threshold is a convention, **not** physical breakup or ground impact. Step-halving is necessary: RK4/quadrature closure under one step size is neither a certified global error interval nor a 1963 trajectory proof.

## Reproduce

`node --experimental-strip-types --test tests/orbitEnergyAudit.test.mjs` (Node 22), as pinned by `.github/workflows/orbit-energy-budget.yml`. Thirteen **synthetic** controls (five baseline and five refinement controls): conservative budget, dissipative drag and quadrature residual, coarse-versus-refined negative result, threshold event truncation, invalid inputs/source.

## Primary record and dependency chain

The cumulative [C197/C198/C201 entries in PR #1](https://github.com/franklinbaldo/conde-incident/blob/research/scientific-integrity-foundation/research/evidence_matrix_C001-C238_2026-11-11.md) cite one original NASA/Goddard *Satellite Situation Report*, vol. 3 no. 22, **15 Nov 1963, printed p. 8**, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf): 1963-003B is recorded as decayed **8 Nov 1963** without hour or location. NASA/NORAD-derived secondary catalogs do not constitute independent tracking measurements. C179 [528 mirrored retrospective-format TLE](https://www.itau.magnetic-declination.com/satellite/?s=528) has RAAN 198.5261°, but it does not supply a contemporaneous Cartesian osculating state or a calibrated atmosphere; the older unsourced 284.1520° is not a second independent measurement.

**NOT_RUN / UNKNOWN:** Lean-certified historical admissible-domain export; time/frame/covariance verified independent 527/529 holdouts; SGP4 independent baseline; physically sourced 1963 density and Cd·A/m; modeled 528 reentry hour/position or Conde impact. No posterior probabilities or geographic claims are output.


## Falsification gate: independent refinement of r, v and drag work

\`auditRefinedPhysicalBudget\` runs the **same state and caller-defined force law** at
step sizes \`h, h/2, h/4\` (up to five halvings). It publishes every per-level
work-budget closure and the consecutive differences of final position (km),
velocity (km/s), event epoch (seconds), Jacobi change (km²/s²) and integrated
drag work (km²/s²). Its separately declared tolerances have dimensions and
must be positive and finite. Two finest work budgets must independently pass;
the last pair of states and work integrals must agree within limits; differences
must not exhibit resolved growth beyond a separate 64×machine-epsilon scale allowance. This allowance is derived from the absolute diagnostic scale in each physical unit (km, km/s, seconds, km²/s²) and is *not* a certified error bound, formal convergence order or physically calibrated tolerance. An event classification
conflict is explicit rather than averaged away.

**G16 retrospective correction (12 Nov 2026).** The previous second condition
`finalDifference <= max(absoluteLimit, 1.25 * previousDifference)`
was logically implied by `finalDifference <= absoluteLimit` and therefore
provided **no second protection**. The Gavião counterexample in private
[Castor inbox #2](https://github.com/franklinbaldo/castor/issues/2)
(`previous=0.0001 km`, `final=0.9 km`, `limit=1 km`)
passed both checks despite **9000× growth**. The new independent trend audit
requires `final <= previous + 64 * EPSILON * max(1, scale)` for each
metric, where `scale` comes from actual per-level state or budget values and
is expressed in the metric's unit. Reports `growingMetrics` and
`roundoffAllowance` explicitly; growth beyond this heuristic returns
`REFINEMENT_UNRESOLVED` even when the caller's absolute limits pass.
64×machine epsilon is a conservative floating-point *diagnostic heuristic*,
not a mathematically established global rounding-error bound. Monotone
pairwise differences alone still do not certify RK4 convergence or impact.
[Adversarial regression](../tests/orbitEnergyAudit.test.mjs) tests the actual
logical independence of the two gates using the original 9000× counterexample.

**Reproducible negative control:** even if coarse and refined work balances
pass an intentionally permissive energy tolerance, a much tighter position
criterion detects divergent r/v states and returns \`REFINEMENT_UNRESOLVED\`.
The diagnostic can also return \`BUDGET_UNRESOLVED\` or \`EVENT_CONFLICT\`.
A numerical match is **not** a global certified error bound, a historically
calibrated model, an independently observed 527/529 holdout, or proof of impact.

The 1963 evidentiary status remains \`NOT_RUN\`: there is no primary historical
Cartesian observation with a trustworthy epoch, frame and covariance to bind
the newly controlled numerical system to the real objects. The synthetic
invariants test the software's internal physics only.
