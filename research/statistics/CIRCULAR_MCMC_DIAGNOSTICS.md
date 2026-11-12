---
type: Guide
title: "Cervo: diagnostics for circular MCMC draws, without historical inference"
description: "Reference rank-split R-hat and bulk/tail ESS guards for angular posterior chains; synthetic controls only"
---

# Diagnostics for circular Markov chains (method only)

**Status: DIAGNOSTICS_IMPLEMENTED; HISTORICAL_MCMC_NOT_RUN.** This is a numerical acceptance *component*, not a sampler, prior, orbital fit, posterior or reentry-site estimator. Context: documentary occurrence families **C25#1, C179#1, C180#1, C181#1, C241-L3**, and NASA's day-only decay catalog **C197**. The historical secondary source [RAAN catalog](raan_527_528_529_1963.json) contains 123 records / 119 distinct object-epoch pairs, all from a dependent lineage. Its [61/23/35 frozen time split](raan_chronological_holdout_1963.json) is **retrospective, not blind**; none of those rows is an MCMC draw. No orbital prediction `H(theta,t,frame)` or calibrated concentration exists here. This component never reads the historical source, so it cannot inadvertently generate an invented posterior.

## Exact interface and assumptions

Input: at least four distinct chains containing equally many 40–4096 finite angle samples each, in **degrees**, provided by an external sampler after **warmup has been removed**. No chain is silently padded or duplicated; a literal constant-projection input is rejected as undefined. The 4096 limit is deliberate for the standard-library reference O(n²) autocovariance computation. Input chains are assumed to target the **same specified, stationary** posterior distribution; this code cannot establish that precondition.

Each angle maps to `sin(Ω)` and `cos(Ω)`. For both projections separately:

1. Split each chain into halves; pool the projections, assign average ranks on ties; transform ranks with `Φ⁻¹((rank - 3/8)/(S - 1/4))`.
2. Compute split-R-hat on rank scores and on folded absolute deviations from the pooled median. Report the larger R-hat.
3. Estimate bulk ESS on rank scores and tail ESS using the minimum of ESS from the 5% and 95% indicator chains. Autocovariances use the split-chain within/between variance and Geyer initial-positive/initial-monotone paired-lag rule.
4. For a **numerical-only gate**, require worst projected rank/folded R-hat below 1.01, and both minimum ESS values at least 100 per original chain. Report all values, not only pass/fail. An accepted numerical gate is **necessary, never sufficient** for a historical posterior claim.

The projections avoid false discontinuities at 0°/360°. Unlike a coordinate-free diagnostic, projected R-hats can vary with an arbitrary rotation of the angular origin, so the maximum over sin/cos is a practical two-projection check **not a proof of rotational invariance or global mixing**. Additional observables and mode/jump diagnostics are essential for multimodal distributions. Rank/tail ESS is **not** the documentary effective sample size of historical catalog entries. Divergences, sampler energy/BFMI, trace/rank plots, and repeated independent runs require separate checks. Exact numerical equivalence with Stan/ArviZ is **not claimed**, especially for the finite-sample autocovariance convention.

The numerical definitions follow [Vehtari, Gelman, Simpson, Carpenter & Bürkner, *Bayesian Analysis* 16(2), 2021, DOI 10.1214/20-BA1221](https://doi.org/10.1214/20-BA1221) and the [Stan reference on posterior analysis](https://mc-stan.org/docs/reference-manual/analysis.html). A constant or degenerate projection is not mistakenly called converged. All test angles and pseudochains are **deterministic synthetic controls only**, not measurements.

## Historical prerequisites still missing

- **Tartaruga:** calibrate source-to-track lineage, epoch/time errors, referential convention and measurement covariance; do not turn TLE replicas into independent sensors.
- **Castor:** provide physically validated orbital forward mapping to *mean-element RAAN in the same frame and epoch*, propagation uncertainty and independent holdout performance; osculating RAAN is not interchangeable with a catalog mean TLE element.
- **Cervo:** derive identifiable physical parameterization/gauge, explicit defensible priors, selection model and likelihood calibration, run multiple actually distinct posterior chains and predictive holdouts without test leakage. Convergence diagnostics alone cannot fix a posterior driven entirely by a prior along an unidentifiable direction.

Use `python3 -m unittest discover -s tests -p 'test_raan_chain_diagnostics.py' -v`. The implementation is `tools/raan_chain_diagnostics.py`. Negative controls: chains trapped at separate circular modes are rejected by R-hat; persistent autocorrelation produces low ESS; no real historical posterior is produced. Results are not a geographical constraint on Conde, and `C197` gives **no measured reentry time or place**.
