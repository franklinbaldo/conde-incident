---
id: CASTOR-20261112-1110Z
agent: castor
date: 2026-11-12
issue: 4
pr: 74
branch: castor/orbit-core-slice-20261112
status: submitted-draft-not-merged
---

# 🦫 OKF: standalone r/v RK4 J2 kernel extracted from PR #5

## Verified work and scientific question

Owner requested that the 64-commit/44-file draft #5 be peeled into small independently reviewable slices. Inspected current `main` `AGENTS.md`, `team/castor.md`, `.agents/skills/conde-castor/SKILL.md`, issue #4, draft PR #5 and discussion, and cumulative C001–C238 matrix in open draft PR #1 (not present on `main`). No new issue opened.

Extracted the **same physical kernel** from source `src/lib/orbitPhysics.ts` on PR #5 (blob `484e3b1ea70ecba3aa14ab898c168e4a8c6efc3f`) into a fresh branch off `main`. It implements central+optional J2 Cartesian 3D r/v RK4, consistent potential/energy/Lz, co-rotating drag *only with caller-supplied source+rho+CdA/m*, and rejection of invalid and nonfinite numerical states. It is a small physical primitive, **not** a model of terminal reentry, fitted 1963 atmosphere, calibrated inverse orbit, Monte Carlo posterior or SGP4 replacement.

Files: `src/lib/orbitPhysics.ts`, `tests/orbitKernel.test.mjs`, `.github/workflows/orbit-core.yml`, `research/ORBIT_KERNEL_EXTRACT.md`, this OKF. Seven synthetic tests cover km/km/s/s and acceleration conversion, one-orbit conserved energy and Lz, J2 potential-force gradient, J2 conservation, joint r/v convergence by step halving, sourced-only drag and Jacobi dissipation, and invalid inputs/numerical overflow.

## Reproducible tests (real GitHub CI)

`node --experimental-strip-types --test tests/orbitKernel.test.mjs` (Node 22), exact proposed head verified using `git rev-parse HEAD` in workflow.

- First checked head `4e16101071fca993bfd706ab31128b77f889bb71`, Actions [#43206223626](https://github.com/franklinbaldo/conde-incident/actions/runs/43206223626): **6 PASS, 1 FAIL**. Counterexample: Node `assert.strictEqual(-0,0)` fails although physical acceleration zero is signed IEEE-754 zero; this was a mistaken test assertion, not a force failure.
- Fix commit `de1d8182377b14c8b5960e20dad996b9164da159` compares `Math.abs(a[1])`/`Math.abs(a[2])` with 0. Actions [#43206305022](https://github.com/franklinbaldo/conde-incident/actions/runs/43206305022) physical-kernel job **SUCCESS**; integration checks [#43206305086](https://github.com/franklinbaldo/conde-incident/actions/runs/43206305086) web + Lean jobs **SUCCESS**. This OKF commit creates a new final HEAD; its own exact-HEAD run must be inspected before any claim of final-head PASS.

## Provenance and controls

Matrix C197/198/201: primary NASA/Goddard *Satellite Situation Report*, 15 Nov 1963, p. 8, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf records **8 Nov 1963** cataloged decay of 1963-003B, *not* a timestamp, reentry position or impact observation. Mirror C179 https://www.itau.magnetic-declination.com/satellite/?s=528 and C180 529 are secondary NORAD-family data; shared catalog lineage is not independent triangulation. The TLE format was introduced after 1963; an epoch in a retrospective-format TLE does not establish a 1963 primary osculating state. RAAN discrepancy remains a provenance question, not two independent measurements to average. These documentary records were **not** re-read as raw position measurements in this slice.

Historical certified Lean boxes, independent epoch/frame/covariance 527/529 blind holdout, historic drag density and CdA/m, independent SGP4 comparison, and 528 terminal coordinates remain **NOT_RUN**; no inference of Conde geography or impact.

## Next and handoff

[PR #74](https://github.com/franklinbaldo/conde-incident/pull/74) is a new small draft under the **same active issue #4**; PR #5 remains intact as a large unmerged draft. Gavião to independently inspect J2 force/potential consistency and thresholds; Elefante coordinates integration, avoiding overwriting this primitive with the old monolithic PR #5. Follow-up separate slice may add reentry event and constrained domains, reusing this base rather than branching indefinitely. No merge, rebase, force-push, blog edit, or external contact.
