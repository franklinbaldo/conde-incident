# Refinement-aware chronological orbital holdout (🦫 Castor)

**Scope:** conditional numerical test on Cartesian osculating states in a single explicitly
named inertial frame, using the already merged coupled `r/v` RK4/J2 kernel
(`src/lib/orbitPhysics.ts`) and the step-halving diagnostic
(`src/lib/orbitConvergence.ts`). This is **not** SGP4 or a conversion of
TLE mean elements into Cartesian observations.

`auditFutureOrbitScore(fit, heldout, controls)` rejects chronological leakage
across the predeclared cutoff, mixed NORAD 527/529 identity, inconsistent UTC,
frames, malformed Cartesian positions and missing provenance strings. It
numerically propagates both an unfitted Cartesian baseline and the fitted
candidate at every holdout time. A first-threshold event conflict, unresolved
step-halving precision or model termination **blocks** residual rankings.

For stable trajectories it calculates RMS residuals in km at each refinement
level, preserves cases when the fitted solution is worse, and refuses to rank
near-ties or winners that reverse with step size. All nonfinite residuals are
`NOT_RESOLVED` rather than silent wins (including a synthetic overflow test
where finite input vectors overflow squared-error accumulation). Training
observations can be audited separately by `auditTrainingOrbitScore`, without
claiming independent prediction.

**Documentary lineage and limits:** [C197, C198, C201](evidence_matrix_C001-C238_2026-11-11.md)
derive from the original [NASA/Goddard Satellite Situation Report,
15 Nov 1963, printed p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf):
the record gives the **day** 8 Nov 1963 for 1963-003B decay, not an exact
UTC time, terminal position or impact. C179 and C180 are secondary historical
TLE/AFSPC-family references of different objects/epochs; they are **not**
time-tagged independent Cartesian positions in an identified common inertial
frame. NASA catalog statements and AFSPC tracking must not be counted as
independent measurements. The 527/529 original instrumental holdout,
authenticated frame/epoch/covariance and 1963 drag calibration remain
**NOT_RUN**. No historical geographic or impact inference is licensed.

The two test suites in `tests/orbitHoldoutAudit.test.mjs` and
`tests/orbitConvergence.test.mjs` use synthetic positions only. For local
reproduction use Node.js 22:

```sh
node --experimental-strip-types --test tests/orbitHoldoutAudit.test.mjs tests/orbitConvergence.test.mjs
```

This work is peeled from unresolved long-running draft PR #5 as an independent
small product slice under issue #4. It does not incorporate #5's unfinished
bound adapters or present any Lean proof as an empirical measurement.
