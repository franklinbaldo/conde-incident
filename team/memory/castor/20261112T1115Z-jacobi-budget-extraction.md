---
id: CASTOR-20261112-1115Z
agent: castor
date: 2026-11-12
issue: 4
pr: 78
branch: castor/energy-budget-extract-20261112
status: draft-unmerged
---

# OKF 🦫: Jacobi energy/work audit peeled from draft #5

## Work and concurrency

Read `main` `AGENTS.md`, `team/castor.md`, `.agents/skills/conde-castor/SKILL.md`, issue #4, open PRs, draft #5/review comments and cumulative C001–C238 research matrix in **draft PR #1**, because the matrix is not in `main`.

An initial attempt extracted the full RK4 r/v kernel into [PR #74](https://github.com/franklinbaldo/conde-incident/pull/74), with exact-head physics run [#43206482393](https://github.com/franklinbaldo/conde-incident/actions/runs/43206482393), **7/7 PASS**. Earlier run [#43206223626](https://github.com/franklinbaldo/conde-incident/actions/runs/43206223626) was **6/7** because the synthetic assertion `strictEqual(-0,0)` was overstrict; repaired without changing the dynamics. During this run, another integration added to `main` the **entire** original `src/lib/orbitPhysics.ts` (blob `484e3b1ea70ecba3aa14ab898c168e4a8c6efc3f`) and its tests. PR #74 would have **overwritten the integrated full module with a subset**, hence it was explicitly **closed unmerged**, with notice to reviewers. This concurrent integration invalidated the previous independent-slice proposal, but the negative/churn lesson is preserved.

New **four-file PR #78** branches from updated `main`, reuses its identical physics blob, and extracts ONLY `src/lib/orbitEnergyAudit.ts` (source blob `e383221d8dd96bd7f20b3b47fcc9a9469528f0b8` from PR #5), `tests/orbitEnergyAudit.test.mjs` (source blob `4281bbae2eb2a2e3827ef718afd6c5c1f113f8e3`), one pinned-head workflow, and `research/ORBIT_ENERGY_BUDGET.md`. The extracted consumer tests a physically meaningful and falsifiable identity: `J = E - Ω Lz`, `dJ/dt = a_drag·v_relative` (km²/s³). Compares numerical RK4 J changes to the trapezoidal drag-work budget per step and cumulatively, controls energy/Lz in vacuum and reports residuals rather than a false exact conservation theorem. Stops the audit at an explicit descending altitude threshold; this is **not** impact evidence.

## Reproducible results and negative evidence

On proposed head `304995d0b4d96a3412ce3a4e5823b3cd73728baf`, GitHub [Jacobi workflow #43207047557](https://github.com/franklinbaldo/conde-incident/actions/runs/43207047557), [physical-budget job #131144750618](https://github.com/franklinbaldo/conde-incident/actions/runs/43207047557/job/131144750618): **SUCCESS, 5 PASS / 0 FAIL / 0 SKIPPED**, and literal checkout `304995d...` verified. Reproduce with Node 22 `node --experimental-strip-types --test tests/orbitEnergyAudit.test.mjs`. Separate [orbital kernel workflow #43207047434](https://github.com/franklinbaldo/conde-incident/actions/runs/43207047434) and [integration checks #43207047829](https://github.com/franklinbaldo/conde-incident/actions/runs/43207047829) also **SUCCESS**.

**External blocker, not caused by this change:** [Lean 4.35 core proof audit #43207047522](https://github.com/franklinbaldo/conde-incident/actions/runs/43207047522) **FAILURE**, job [#131144750188](https://github.com/franklinbaldo/conde-incident/actions/runs/43207047522/job/131144750188), because its workflow attempts `working-directory: formal` but that directory does **not exist** in this branch/base `main` (formal sources reside in separate draft PRs). Failure happens before `lake build`, so do not claim a proof failure or a green all-CI gate. Not editing the Lean workflow outside Castor's exclusive mission. This OKF file changes HEAD again: confirm CI on final head before any integration.

Five original **synthetic** regression tests: conservative J2 budget, drag-work closure, deliberately coarse-step discrepancy that decreases on refinement, partial event stopping, and invalid/unsourced force inputs. An apparently green coarse integration is NOT a bound on historical state error. No historical source/covariance was inserted into a numerical example.

## Source and lineage, what is *not* learned

Matrix **C197#1/C198#1/C201#1**: original NASA/Goddard *Satellite Situation Report*, vol.3 no.22, 15 Nov 1963, printed p.8, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf states cataloged decay of 1963-003B on **8 Nov** but neither hour nor coordinates. C179#1 mirror https://www.itau.magnetic-declination.com/satellite/?s=528 : secondary NORAD-family TLE with retrospective 1963 epoch, not independently observed 1963 Cartesian osculating r/v. NASA/NORAD/catalogs share dependency; historical RAAN discrepancy not resolved by averaging.

**NOT_RUN:** time/frame/covariance-stamped independent NORAD 527/529 blind holdouts, Lean-certified historical admissible domains, physically calibrated 1963 thermospheric density and CdA/m, SGP4 baseline comparison, 528 terminal hour/position or inference about Conde. A numerical threshold crossing says nothing about ground impact.

## Next

Independent 🦅 Gavião review of Jacobi work formula and thresholds; 🐘 Elefante reconcile pre-existing Lean gate and integrate if truly safe. Continue splitting only genuine unique modules of draft #5; do not overwrite the already merged core. No blog publication, archive contact, merge, rebase or force-push in this session.
