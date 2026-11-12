# OKF 🦫/🐙 integration handoff · 12 Nov 2026

- Issue: #4 Castor; scope: a single independently mergeable part of draft PR #5.
- Original source HEAD: `274d060c5b3bd9eaa23b2a05738393f9686e3eba`.
- Copied intact: `src/lib/orbitPhysics.ts`, `tests/orbitPhysics.test.mjs`.
- Tests planned: exact-head workflow, 9 synthetic kernel tests, TypeScript/Vite.
- Scientific source: NASA SSR 15 Nov 1963 p. 8 (one catalogue source, date only).
- Negative: no primary observation for 528 state, historical density, 527/529
  observational holdout or impact location. Small integration is not a physical
  inference and does not subsume all of PR #5.
- Remaining task: separately integrate Castor convergence, admissibility,
  alternative fits, holdout bridge, audits and tests with dependencies.
- Revision: Gavião will audit this merged slice retrospectively per AGENTS.md.
