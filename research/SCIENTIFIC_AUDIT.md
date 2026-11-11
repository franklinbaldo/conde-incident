# Scientific integrity audit — 11 Nov 2026

## Scope and status

This is a *source-audited reconstruction project*, not an established impact localization. The primary NASA Satellite Situation Report of 15 Nov 1963 lists **1963-003B** as decayed **8 Nov 1963** (printed p. 8). It supplies **no terminal time or location**. [Original NASA PDF](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf).

The Rádio Tupi story survives in an FBIS transcript. This is a primary record *of a broadcast*, not a primary observation of a crater, sphere, body or recovered hardware. Reprints and derivative diplomatic discussions are not counted as independent physical witnesses.

## Main critical findings in the imported app

1. `src/lib/astrodynamics.ts` applied a prescribed drop of up to 345 km and an arbitrary longitude shift **after** SGP4. These changes did not update velocity and were neither a numerical integration of drag nor a valid SGP4 output. **Corrected in this branch:** raw SGP4 baseline state is preserved. It still does not predict actual reentry after 12 days of unsupported extrapolation.
2. `src/lib/monteCarlo.ts` samples terminal argument of latitude uniformly, independently of initial mean anomaly, orbital mean motion and its sampled lifetime. Consequently, the simulated point is not the dynamically propagated endpoint of a sampled physical trajectory. Its fraction within 100 km of Conde is **not a posterior probability of an impact**, and must not be presented as such.
3. The Monte Carlo uses `-2.28 deg/day` for nodal regression. The classical secular J2 formula with the 528's included orbit gives approximately **-1.17 deg/day** at the stated epoch, making the hard-coded estimate substantially inconsistent with the same orbit's geometry.
4. `src/lib/inverseSolver.ts` treats longitude difference as along-track displacement and maps the displacement directly to mean anomaly and ballistic coefficient. In a near-polar orbit those are different dimensions; varying phase alone generally cannot repair a cross-track geographic offset.
5. `getTriangulationState` uses independently prescribed altitude, mean motion and nodal rates; there is no joint parameter fit to object observations. An object crossing a geographical latitude is not necessarily at that latitude at its terminal time.
6. The existing UI asserted an approximately 19:48 UTC pass at 91 km, 844 km east of Conde, and an approximate 0.0062% location probability. These figures are **exploratory outputs from unvalidated assumptions**, not archival observations.
7. Several chronology entries use exactly 23:59 for day-only catalog decay dates. This timestamp is a visualization placeholder, **not an observed decay time**.
8. The app labels some records *primary verified* without presenting original provenance for every orbital element, radar acquisition time, and physical specification. A valid TLE checksum certifies formatting, not authenticity.

## Serious conflict between historical orbit data sets

The application includes an October 27 TLE with RAAN **284.1520°**, eccentricity **0.0084200**, argument of perigee **142.3150°**, anomaly **218.4210°** and mean motion **15.74900000 rev/day**.

An earlier historical-series research extract reported an October 27 NORAD 528 TLE of RAAN **198.5261°**, eccentricity **0.0017147**, argument of perigee **104.7477°**, mean anomaly **255.4423°**, mean motion **15.7490146 rev/day**.

The two records should **not** be blended. The upstream historical TLE export used for the previous study comprised 21 records of 527, 45 of 528, and 57 of 529 (with duplicate epochs). Until their source, coordinate frame, parsing and exact epoch are reconciled, the UI's specific longitudes cannot be certified.

Historical-series provenance lead: [oxzoid Space-Track TLE history mirror](https://huggingface.co/datasets/oxzoid/space-track-tle-history); underlying Space-Track records require an explicit lineage audit.

## Previously completed Lean 4 work

An existing separate Lean 4.35.0 package (compiled on 11 Nov 2026, not yet imported verbatim here) formalized a provenance relation, 154 propositions under 151 evidence labels (including duplicated C44–C46), 119 distinct epochs, conditional orbital-frequency arithmetic and an example demonstrating **non-identifiability of place from a date-only event**. It *did not* certify a SGP4 ground track or solve physical reentry. Its provenance and mathematical conclusions should be carried forward without overstating its scope.

The previous joint-model validation found that a simple quadratic mean-motion baseline was **better** than the multi-target H60 model on the reserved late-October holdout (mean absolute error 0.01412 vs 0.02595 rev/day). Consequently, joint modeling cannot be called an improvement until it beats an independent holdout.

## Repair sequence

1. Audit every historical TLE against original epoch and primary fields; remove undocumented defaults from science output.
2. Preserve coupled state vectors and implement only physically coherent orbit integrators, with explicit reentry termination criteria; use SGP4 only as a baseline inside its verified validity range.
3. Replace Monte Carlo with a deterministic-seed, fully propagated ensemble, with explicit prior and likelihood for archival observations, before reporting any numerical impact probability.
4. Rewrite the inverse solver as a constrained fit in orbital state space, not a longitude slider; verify on 529 blind forecast windows before interpreting 528.
5. Bring the compiled Lean project and original evidence registry into version control intact, with reproducible `lake build` and explicit verification status.
6. Release only the claims supported by independent source documents or validated models. No publication or changes to the separate blog.

## Document leads

- [NASA, 15 Nov 1963 Satellite Situation Report](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
- [US State Department, 14 Nov 1963 diplomatic cable](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf)
- [Biblioteca Nacional, O Jornal, 9 Nov 1963 page reference](https://memoria.bn.gov.br/DocReader/110523_06/31712)
- [IGHB periodical library](https://www.ighb.org.br/biblioteca)
- [Primary investigation essay](https://franklinbaldo.github.io/pt/blog/conde-ufo-1963/)

No claim of a physical impact at Conde follows from the primary evidence or the current model.
