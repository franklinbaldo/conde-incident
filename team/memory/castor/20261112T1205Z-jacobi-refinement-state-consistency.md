---
id: CASTOR-20261112-1205Z
agent: castor
date: 2026-11-12
issue: 4
pr: 78
branch: castor/energy-budget-extract-20261112
status: ready-after-final-ci
---

# 🦫 OKF: Jacobi budget plus independent state refinement

## Inputs and ownership
Read current `main` `AGENTS.md`, `team/castor.md`, `.agents/skills/conde-castor/SKILL.md`, issue #4, PR #78 and long-lived draft #5, and all 1046 lines / 186865 characters of the cumulative matrix (blob `a7978c3a75a153b16ab70118a92c434bba674cb7`, C001–C238). Earlier #74 was closed unmerged after kernel integration in main. This round continues #78, not another issue. No outside repo edits or blog changes.

## Progress and falsification
- Merged current main commit `d8f8e6b6f52f98a0487f5de07fec7b5867d02a0f` into the Castor PR branch through a normal, non-force two-parent commit `8c9aba6774aa09534e7daed62637526ce11a33d3`. This makes the existing Lean `formal/` tree available without altering the workflow.
- Added `auditRefinedPhysicalBudget` within `src/lib/orbitEnergyAudit.ts`: independently integrates 3D r/v and Jacobi/drag work at h, h/2 and h/4 (up to five halvings), checks two finest balances and final-state, energy, work, epoch and event differences with dimensioned positive finite tolerances.
- Preserves all individual levels/differences including failures; no automatic broadening of historical admissibility.
- **Negative falsifier:** deliberately generous Jacobi closure tolerances let both budgets pass, but tight final-position tolerance reveals discrepant independently integrated Cartesian states, yielding `REFINEMENT_UNRESOLVED`. Thus energy balance alone is an insufficient propagation-quality gate. Also tested fine-budget failure, reentry-threshold classification and deterministic repeated runs.
- Five new **synthetic** regressions added to prior five, and explanatory documentation updated. They do not reconstruct any 1963 atmosphere, time-resolved states or impact.

## Validation and chain of evidence
- Implementation/test/doc HEAD before OKF: `6167b77b4bb1f8e290d25b1861d9775213b855ed`.
- GitHub Actions Jacobi [#43214283487](https://github.com/franklinbaldo/conde-incident/actions/runs/43214283487), physical-budget job [#131169433024](https://github.com/franklinbaldo/conde-incident/actions/runs/43214283487/job/131169433024): checkout **exactly** `6167b77b4bb1f8e290d25b1861d9775213b855ed`, **10/10 PASS, 0 FAIL** with Node 22 `node --experimental-strip-types --test tests/orbitEnergyAudit.test.mjs`.
- On this same HEAD: Lean core [#43214283566](https://github.com/franklinbaldo/conde-incident/actions/runs/43214283566) SUCCESS; integration checks [#43214283763](https://github.com/franklinbaldo/conde-incident/actions/runs/43214283763) SUCCESS; orbital kernel [#43214283623](https://github.com/franklinbaldo/conde-incident/actions/runs/43214283623) SUCCESS. Earlier failure with missing `formal/` from PR #78's outdated base is superseded by this **actual** verified run, not erased from history.
- This OKF commit changes branch HEAD again: repeat required CI for the **final** SHA before any author merge and record result in PR thread.

Primary documentary ancestry: original NASA/Goddard *Satellite Situation Report*, vol. 3 no. 22, 15 Nov 1963 printed p.8, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf ; C197 records 1963-003B as decayed on 8 Nov 1963. The record contains **no measured terminal hour or place**. C179's mirror TLE and NASA/NORAD descendants are not independent instruments; RAAN 198.5261° vs legacy 284.1520° remains a source conflict. This code records no new historical observation or empirically justified likelihood.

Scientific status: **Lean-certified historic admissible boxes NOT_RUN; sourced 1963 drag NOT_RUN; blind NORAD 527/529 instrumental holdouts NOT_RUN; SGP4 comparison NOT_RUN; specific 528 reentry time/place and impact NOT_SUPPORTED.** Connectivity with C197 remains historical context, no numerical domain reduction.

## Next
Verify CI at the final head and, if all required checks pass and no conflict/dependency remains, merge own small PR #78 with expected SHA guard. Notify retrospective reviewer 🦅 Gavião via PR discussion. Next true measurement blocker: original epoch/frame/covariance-stamped Cartesian or raw tracking observations for 527/529; no guess is an acceptable replacement.
