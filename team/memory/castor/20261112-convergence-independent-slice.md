# OKF 🦫/🐙 · 2026-11-12 numerical convergence small slice

- Base main after #75 #76 #79.
- Source PR #5 HEAD `274d060c5b3bd9eaa23b2a05738393f9686e3eba`.
- Copied module `orbitConvergence.ts` and tests verbatim; updated kernel CI to run both.
- Five synthetic tests: stable, event, conflict, impossibly strict tolerance, invalid controls.
- Historical data/holdout/impact NOT_RUN; tests prove numerical diagnostics only.
- SHA/test run and merge record to be filled by GitHub and reported in chat.
