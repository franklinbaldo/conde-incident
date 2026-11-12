# 🦫 First independent slice of Castor PR #5

**Objective:** integrate the tested Cartesian dynamics kernel without adopting the
historical reconstruction or speculative terminal coordinates. Original source:
[PR #5](https://github.com/franklinbaldo/conde-incident/pull/5),
`src/lib/orbitPhysics.ts` and `tests/orbitPhysics.test.mjs` copied verbatim
from HEAD `274d060c5b3bd9eaa23b2a05738393f9686e3eba`.
The remaining #5 changes are NOT yet integrated.

The kernel supports (r,v) ECI RK4 propagation, central gravity, J2, optional
co-rotational atmospheric drag with explicitly sourced density and Cd*A/m,
numerical altitude-threshold event refinement, reproducible random ensemble,
and an inverse velocity fit. Its tests are **synthetic** and prove only software
behavior under provided assumptions. A numerical altitude crossing is neither
a demonstrated historical reentry nor impact.

**Primary documentary lineage, not a calibration of this model:** NASA/Goddard,
*Satellite Situation Report*, 15 Nov 1963, printed p. 8,
https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf ,
records the day 8 Nov 1963 for 1963-003B, with no terminal position or time.
The provenance matrix is in [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1)
at C131#1 / C197#1; both cite the *same* NASA report.
No atmospheric density from 1963 or primary NORAD elements are supplied.
Historical 527/529 holdout: NOT_RUN. Terminal coordinates: NOT_RUN.

**Validation:** `node --experimental-strip-types --test tests/orbitPhysics.test.mjs`
runs on the exact PR head in `.github/workflows/orbit-kernel.yml`.
`Integration checks (exact head)` additionally runs TypeScript + Vite.
The code does not replace or invoke the site SGP4 baseline. No blog changes.
