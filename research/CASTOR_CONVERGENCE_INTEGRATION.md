# 🦫 Numerical step-refinement diagnostic integrated from PR #5

Atomic Castor slice from source HEAD `274d060c5b3bd9eaa23b2a05738393f9686e3eba`.
Adds `orbitConvergence.ts` and five synthetic tests; existing `orbitPhysics.ts`
is provided by already merged #75. The CI workflow adds both test files.

It runs RK4 with progressively halved step widths, compares velocity,
position, event kind and elapsed time, and explicitly reports
`EVENT_CONFLICT`, `NOT_RESOLVED`, or `STABLE` under caller-specified
tolerances. A synthetic 3000-second step missing a threshold event
demonstrates why unchecked coarse time steps are unsafe.

These tests do not constitute empirical orbital calibration; the original
NASA/Goddard Satellite Situation Report 15 Nov 1963 p.8 (NTRS
https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
records only the day of decay for 1963-003B. No primary 528 terminal state
or meteorological uncertainty model is supplied; a threshold event is
not a ground impact. 527/529 historical holdouts remain NOT_RUN.

This slice does not merge the remaining large draft PR #5. Review by
Gavião happens retrospectively as directed in AGENTS.md.
