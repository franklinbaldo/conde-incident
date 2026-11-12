# Standalone Cartesian orbital kernel (extracted from PR #5)

This intentionally small **extract of PR #5**, linked to [issue #4](https://github.com/franklinbaldo/conde-incident/issues/4), makes the coupled 3D osculating state r/v and force integration independently testable on `main`. It adds `src/lib/orbitPhysics.ts` and a pinned-head GitHub Actions test, but **does not** include reentry detection, inverse fitting, Monte Carlo, domain auditing, a UI, SGP4, or a historical forecast. Further pieces still live in draft [PR #5](https://github.com/franklinbaldo/conde-incident/pull/5). Do **not** merge the old monolithic file over this extract without reconciling it.

## Physical/units contract

- Inertial Cartesian position **km**, velocity **km/s**, elapsed time **s**; acceleration **km/s²**. Both position and velocity are advanced by RK4 with the *same* stage derivatives. `tS` is elapsed time, not UTC metadata; actual epoch and reference-frame transformations must be supplied/validated by callers.
- Adopted mathematical Earth constants: gravitational parameter 398600.4418 km³/s², equatorial radius 6378.137 km, J2 1.08262668e-3, spin 7.2921150e-5 rad/s. These are **model choices**, not observations of NORAD 527/528/529.
- Gravity is central plus optionally J2. `potentialKm2S2` and `specificEnergyKm2S2` use the same conservative J2 potential as `accelerationKmS2`; `angularMomentumZ` is the conserved symmetry-axis component.
- No historical atmosphere is enabled by default. Optional co-rotating drag requires a named density function (kg/m³) and Cd·A/m (m²/kg), and converts km/s to SI before returning km/s². The drag-power diagnostic acts on `E - ω Lz`. Synthetic constant-density tests are not an atmospheric reconstruction.
- `NumericalIntegrationBreakdown` is **not** physical impossibility. Positive finite step and finite osculating inputs are required. Convergence controls must be applied before interpreting any longer simulation.

## Reproduction and evidentiary limits

Node 22: `node --experimental-strip-types --test tests/orbitKernel.test.mjs`. The exact-head `Coupled orbit kernel (independent slice)` workflow runs this command on GitHub Actions. Tests cover conservation, J2 potential gradient, simultaneous position/velocity step refinement, drag sign, unit conversions and failures. All test states are synthetic.

Matrix [C179–C185, C197–C202](https://github.com/franklinbaldo/conde-incident/blob/research/scientific-integrity-foundation/research/evidence_matrix_C001-C238_2026-11-11.md): C179 elements for 528 are a **retrospective secondary mirror** (https://www.itau.magnetic-declination.com/satellite/?s=528), not a primary 1963 observation of a Cartesian osculating state. NASA/Goddard [*Satellite Situation Report*, 15 Nov 1963, printed p. 8, NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), C197, documents cataloged decay of 1963-003B on **8 Nov**, but no observed hour/position. NASA/NORAD/mirrors may share tracking lineage and do not constitute three independent sensors.

**NOT_RUN**: authenticated epoch-and-frame-tagged 527/529 independent blind holdouts; Lean 4.35.0-verified historical admissible-domain export; SGP4 baseline comparison; physical 1963 density calibration; location/time of 528 reentry. RAAN 198.5261° from mirrored elements and the unsourced legacy 284.1520° are not independent measurements to average. This numerical kernel supports **no inference of impact in Conde**.
