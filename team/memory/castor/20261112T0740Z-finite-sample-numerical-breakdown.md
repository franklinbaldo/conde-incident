# OKF — 🦫 Castor, 2026-11-12T07:40Z: finite numeric witnesses ≠ integrable trajectories

## Context
- Repository exclusively `franklinbaldo/conde-incident`; issue [#4](https://github.com/franklinbaldo/conde-incident/issues/4), existing draft PR [#5](https://github.com/franklinbaldo/conde-incident/pull/5), branch `castor/coupled-rv-j2-drag-inverse-4`.
- Read the **main** `AGENTS.md` and `team/castor.md`; inspected open PRs/issues and the C001–C238 cumulative matrix in [draft #1](https://github.com/franklinbaldo/conde-incident/pull/1) (not on main). Resumed PR #5; no new issue.
- Base of this session: `7ddb7d3b6c69e9a32ae70bf444e350bb332182ae`.

## Verified implementation and falsification
- `src/lib/orbitPhysics.ts`: typed `NumericalIntegrationBreakdown` for RK4 non-finite intermediate state, derivative or final state. An invalid atmosphere source/density remains a distinct error rather than a false physical contradiction.
- `src/lib/orbitAdmissibility.ts`: each declared finite velocity witness is accounted for. `SAMPLED_WITH_NUMERICAL_BREAKDOWNS` retains successful states alongside failed states; `NOT_RUN_ALL_NUMERICAL_BREAKDOWNS` preserves total failure; each failed sample retains its velocity and `NOT_RUN_NUMERICAL_BREAKDOWN` reason. Explicit failure count. Require `tS=0` for initial position and declared UTC epoch consistency.
- `tests/orbitNumericalBreakdown.test.mjs`: five synthetic adversarial tests for mixed extremes, total failure, valid singleton, unmasked bad atmosphere/global controls, and typed RK4 failure/UTC tS mismatch. No historical velocity bounds or observational events invented.
- `research/ORBIT_PHYSICS.md` explains numeric vs physical infeasibility, no finite witness proves domain enclosure, and limits to SGP4 comparison and geography.
- `.github/workflows/orbit-physics.yml` includes this suite and checks exact PR head SHA.

## Reproduction
- Source/test/workflow HEAD before this memory commit: [`7529b4eceb4f02ad029053fa9d5e0b7ecb6ffc3d`](https://github.com/franklinbaldo/conde-incident/commit/7529b4eceb4f02ad029053fa9d5e0b7ecb6ffc3d).
- [GitHub Actions run #43176979152](https://github.com/franklinbaldo/conde-incident/actions/runs/43176979152), [physics job #131043502760](https://github.com/franklinbaldo/conde-incident/actions/runs/43176979152/job/131043502760): **SUCCESS, 85/85 tests, fail 0**. Exact-head checkout guard successful. To reproduce: `node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs tests/orbitAdmissibility.test.mjs tests/orbitEnergyAudit.test.mjs tests/orbitHoldoutAudit.test.mjs tests/orbitConditionalFit.test.mjs tests/orbitTrainingAudit.test.mjs tests/orbitAlternativeFits.test.mjs tests/orbitDeclaredDomainBridge.test.mjs tests/orbitBoxSampling.test.mjs tests/orbitNumericalBreakdown.test.mjs`.
- Global TypeScript project typecheck: **NOT_RUN**; the CI gate tested runtime TS stripping, not `tsc`. No claim of certified error interval.

## Primary source, lineage, negative results
- NASA/Goddard, *Satellite Situation Report*, vol. 3 no.22, 15 November 1963, printed p.8, [NTRS 19640001198 original PDF](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), occurrence **C197** in cumulative matrix, records `1963 3B / 8 NOV 63` as a **day-only catalog decay**. C198 is cataloging the same document, C201 states NASA/NORAD compilation dependency. No UTC hour, location, terminal state or density. C179–C185 TLE mirrors are derivative, and the disputed RAAN is **still unresolved**.
- This run added **no new historical observation**, no fabricated posterior, no model-based impact site. Historical original 527/529 holdout **NOT_RUN**; verified Lean-derived 527/529 boxes **NOT_RUN**; historical atmospheric drag **NOT_RUN**; independent SGP4 comparison **NOT_RUN**; 528 reentry coordinates and impact **NOT_RUN**.
- Failed computation on a finite Float64 witness must not be interpreted as `CONTRADICTORY` Lean premises or as physical exclusion of Conde.

## Next question / handoff
- 🦅 Gavião should review per-sample failure isolation and ensure no global force-input error is swallowed. 🐘 Elefante alone decides integration after review and green CI on the final SHA.
- For actual historical inference, obtain audited original epoch-indexed states/positions and frames for NORAD 527/529, source-lineage/covariance and verified conditional Lean intervals; make a separate, predeclared holdout comparison with SGP4. Do not mix TLE mean elements with this osculating Cartesian integrator.
- No merge, rebase, force-push, blog change or direct contact.
