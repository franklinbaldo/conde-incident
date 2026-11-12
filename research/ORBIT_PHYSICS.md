# Experimental Cartesian r/v kernel (Castor, 11 November 2026)

## Status and epistemic boundary
`src/lib/orbitPhysics.ts` is a standalone **experimental mathematical model**, not a reconstruction of NORAD 528. Its output MUST NOT be interpreted as a terminal location or an impact probability. It does **not** alter the current app and does not silently replace the SGP4 baseline. Initial r/v must be **osculating Cartesian ECI** in km and km/s, with a defined epoch. Retrospectively formatted historical TLE mean elements do not by themselves supply that state.

## What is actually implemented
- Fourth-order Runge–Kutta simultaneously integrates `dr/dt=v` and `dv/dt=a` using central Earth gravity and optionally the axisymmetric J2 correction. Model constants: mu=398600.4418 km³/s², equatorial reference radius 6378.137 km, J2=1.08262668e-3, rotation=7.2921150e-5 rad/s. These are nominal Earth gravity/model constants, **not 1963 observations**; no higher harmonics, Sun/Moon, precession, or reference-frame transforms.
- Optional co-rotational atmosphere: `v_relative = v - omega×r`; `a_drag = -rho (Cd A/m) |v_relative| v_relative / 2` in SI, converted to km/s². `densityKgM3(altitudeKm, tS)`, `Cd A/m`, and nonempty `source` are mandatory if drag is requested. No fabricated 1963 F10.7, Ap, mass, cross-section or thermosphere is provided. Co-rotation is a simplifying **assumption**, not measured wind.
- A caller-specified spherical altitude threshold stops integration; bisection re-integrates r **and** v within the crossing step. A threshold is a numerical event, **not ground impact or the breakup altitude**. The Earth radius is spherical for the event and drag altitude; J2 reference is equatorial.
- Inverse solver deterministically searches the three osculating velocity components against time-stamped inertial Cartesian positions carrying a provenance field. It does not adjust RAAN by hand or equate longitude to along-track distance. The optimizer is local, derivative-free and may be non-identifiable or trapped.
- Seeded xorshift32 ensemble perturbs initial velocity and **propagates every full state**. The sampling is uniform synthetic sensitivity, **not a Bayesian posterior**. No object, launch, drag or date is inferred by the seed.

## Within-step perigee crossing falsification (11 Nov 2026, synthetic)

A coarse RK4 step may begin and end ABOVE a numerical reentry threshold yet pass BELOW it in between. The prior endpoint-only event search silently returned `elapsed` in that case. The kernel now checks for a negative-to-positive radial derivative (`r·v`), bisects the intermediate perigee using coupled state integration, then bisects the **first descending** altitude crossing if the perigee is below the threshold. It does not move only longitude, replace r/v by an interpolated position, or assert ground impact.

An executable synthetic counterexample starts at 90 km spherical altitude with radial/tangential velocity (-0.15, 8.15) km/s and takes a **400 s** step: both endpoint altitudes exceed the **80 km** threshold, but the trajectory intersects it on the descending arc. The 400 s event time is checked against an independent 1 s stepping control (tolerance 0.01 s), along with r/v and threshold altitude; a separate 8.4 km/s synthetic near-miss must remain `elapsed`. This is a numerical falsification/test, NOT a NORAD observation. For extremely coarse steps that cross multiple radial extrema, even a turning-point bracket is not guaranteed: step-size convergence and bounded time steps remain the caller's responsibility.

## Verification and negative result
Run `node --experimental-strip-types --test tests/orbitPhysics.test.mjs` with Node 22, or inspect the `Coupled orbit physics` GitHub Actions job on the actual PR HEAD. Synthetic controls cover near-closed Keplerian orbit, inertial energy and angular momentum, J2 energy plus z-angular momentum, co-rotational drag sign, threshold time and velocity, input validation, seed repeatability and inverse reduction against simulated data. They establish mathematical/code consistency **only**. Synthetic data in the tests do not correspond to observed 1963 states.

**Blind holdout 527/529: NOT_RUN.** Complete original TLE records/epochs and coordinate-frame provenance, compatible Cartesian reference states or independent ranging positions, and historical thermospheric inputs are missing. Do not score a holdout using the same modeled states to generate its 'observations'. Reconciliation is required between RAAN 198.5261° in the C179/older series and 284.1520° hardcoded in the site; the two must not be averaged. SGP4 is a **separate mean-element baseline**, not this numerical integrator.

## Source lineage
- **Primary institutional record**: NASA/Goddard `Satellite Situation Report`, vol. 3 no. 22 (15 November 1963), printed p. 8, NTRS 19640001198: https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf . Evidence matrix **C197–C201** records that `1963 3B` was placed on the decayed list for **8 November 1963**; the NASA document offers **neither precise UTC nor reentry location**. It is not a trajectory observation.
- **Historical orbital data lead, secondary/derived**: C179–C185 of the cumulative matrix `research/evidence_matrix_C001-C238_2026-11-11.md` (currently in draft PR #1), including mirrored retroformatted 528 TLE and checksum; https://www.itau.magnetic-declination.com/satellite/?s=528 ; reference TLE format https://celestrak.org/norad/documentation/tle-fmt.php . A checksum or derivative website does not independently authenticate the 1963 tracking.
- **Research audit, secondary**: https://github.com/franklinbaldo/conde-incident/pull/1 and its `research/SCIENTIFIC_AUDIT.md`: holdout baseline quadratic MAE 0.01412 versus exploratory joint H60 0.02595 rev/day. Current new kernel has **not** overturned this failure or demonstrated improvement.
- Earth model numerical constants are documented in the code as assumed physical constants, not historical source measurements.

Before any actual inverse inference: obtain independent historical 527/529 observations with time, source and frame, convert mean TLE state using the appropriate method, set drag from independently substantiated data, fit predeclared windows and score held-out data without leakage. Preserve failure results.


## Predeclared chronological holdout protocol (Castor follow-up, 11 Nov 2026)
\`fitPreCutoffOrbit\` takes a **named NORAD target (527 or 529)**, explicit initial/cutoff UTC, a single named inertial Cartesian frame and **only pre-cutoff, strictly chronological position observations**. Their UTC epochs must agree with elapsed seconds to 1 ms, and each must carry a source identifier. Positions and epoch conversions are caller responsibilities. It fits the three initial velocity components with the existing coupled integration and returns a snapshot of the controls. No held-out position enters this stage.

\`scoreFutureOrbit\` takes that frozen-in-time fit snapshot and future observations, checks target/frame/time/ordering, and scores both the **unfitted control** and **fitted trajectory** in km RMS without refitting. Positive \`deltaRmsKm\` explicitly signals failure (fitted result worse). If integration reaches the declared numerical reentry altitude before an observation, RMS can be \`Infinity\` and delta is \`null\`, not a fictitious successful error. The API does **not** assert that user-supplied positions are independently measured, nor does it recover a frame transform or an instrument covariance.

Executable synthetic controls: \`node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs\`. In particular an **adversarial holdout** demonstrably worsens while the training fit improves. The J2 acceleration is also tested against the finite-difference gradient of its potential. These tests are **synthetic** and cannot be reported as 1963 blind validation.

**Historical status 527/529: NOT_RUN**. The original complete source-indexed epochs/positions or independently authenticated TLEs and their SGP4/TEME-to-osculating frame mapping have not been supplied. The provenance ledger C25/C123/C128/C133/C134/C179–C185 in PR #1 describes derived mirrored elements and some *failed* holdout results; they must not be relabelled as observations used to validate this new integrator. A single NASA decay **date** C197 cannot serve as a position sample. Keep original source/checksums, predeclare cutoff and holdout and compare the SGP4 baseline separately before physical inference. No historical position, drag density or entry location was synthesized in this change.


## Explicit resolution diagnostic and negative falsification (Castor, 11 Nov 2026)

`src/lib/orbitConvergence.ts` adds **deterministic step-halving diagnostic**, not a new force model, frame transform or historical trajectory. `assessNumericalConvergence` integrates the **complete coupled r/v state from the same epoch** at `stepS, stepS/2, ...` and exposes every numerical output and pairwise position (km), velocity (km/s), event-epoch (s), and event-kind disagreement. At least two consecutive final refinements must agree with all caller-specified tolerances for the label `STABLE`. `NOT_RESOLVED` preserves unmet accuracy requirements. `EVENT_CONFLICT` takes precedence if **any** resolution reports a different stopping event, even if later refinements agree. The finest output is a diagnostic artifact, NOT automatically an accepted orbit.

**Reproducible counterexample (SYNTHETIC):** an initial state at 90 km spherical altitude with (-0.15, 8.15) km/s radial/tangential velocity and an 80 km numerical threshold, over 3000 seconds, reports `elapsed` using a single coarse 3000 s RK4 step, yet step halving exposes `reentry-threshold`. The negative test insists that the diagnostic returns `EVENT_CONFLICT`, not a fictional absence of reentry. An 800 s circular-orbit stress test with impossible prescribed tolerances must return `NOT_RESOLVED`; a regular J2 test and a resolved threshold event return `STABLE` at declared tolerances. These are tests of *numerical consistency*, not proof of absolute error, calibrated 1963 drag, physical fragmentation or historical position.

Run `node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs` in Node 22. GitHub Actions executes on PR head SHA. Halvings are capped at 10 and the existing one-million-step propagation cap applies. For historical interpretation, independently audited epoch-stamped 527/529 osculating states, uncertainty/frame transformations, and genuine out-of-sample observations are still missing. SGP4 is a separate TLE mean-element baseline. The NASA/Goddard 15 Nov 1963 p.8 primary decay date (NTRS 19640001198) remains day-only; secondary Space-Track mirrors, including PR #14, do not supply independent physical detection nor resolve the original RAAN conflict.


## Conditional admissible-domain handoff (🦫, 11 Nov 2026)

`src/lib/orbitAdmissibility.ts` is a deliberately **conditional adapter**, not a Lean checker or a historical fit. It accepts finite closed velocity intervals in **km/s** at a single explicit **UTC epoch** and **inertial frame**, each with a matrix occurrence ID, source lineage, reference to an expected Lean predicate and premise status. An absent or unvalidated Lean export is marked `NOT_RUN`, not forged into a theorem or instrument observation. Epoch and frame disagreement raises an error rather than silently combining TLE/TEME with osculating ECI. There is **no empirical parameter interval** claimed for 527/528/529 by this code.

`auditVelocityDomain` takes the exact finite interval intersection independently for vx, vy and vz. It yields **EMPTY** if premises contradict, **PARTIAL** if any velocity is free, and **BOUNDED** only if all three dimensions are finite. These labels describe the **supplied assumptions**, not the physical 1963 feasible set. No optimization, random prior or silent baseline state can fill an unbounded dimension. In this slice the **initial position is fixed**; future handoffs must also constrain position, mass, atmosphere, frame transforms and uncertainties to support historical inference.

For BOUNDED conditional boxes, `runConditionalVelocityDomain` propagates their midpoint, up to eight distinct corners and explicit seeded xorshift32 interior draws, using the **coupled r/v RK4** and numerical step-halving diagnostic for **each** state. Every trajectory retains `STABLE`, `NOT_RESOLVED` or `EVENT_CONFLICT` with numerical discrepancies, including coarse failures. No sample weighting, historical posterior, rigorous global enclosure, blind validation or geographic exclusion is produced. An EMPTY/PARTIAL domain returns no trajectories. One point or finite samples **cannot** establish a universal geographical conclusion, even when every sampled trajectory agrees; numerical convergence is not an absolute error proof.

Reproduce the synthetic acceptance/negative tests via:
```sh
node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs tests/orbitAdmissibility.test.mjs
```

**Required historical handoff, still missing:** checked Lean constraints and their artifact SHA with matrix occurrence identifiers; authenticated 527/529 time-indexed independent observations with reference-frame and covariance metadata; viable joint initial r/v domain; density and Cd·A/m bounds supported by historical sources. The numerical mirror in the 🐢 [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14) (C240/C241) shares a secondary tracking lineage, and the older 528 RAAN conflict is not resolved by treating distinct records as simultaneous inputs. [PR #17](https://github.com/franklinbaldo/conde-incident/pull/17) proves conditional nonidentifiability but **does not export historical velocity boxes**. The [proposed scientific protocol in PR #28](https://github.com/franklinbaldo/conde-incident/pull/28) is followed as a target contract without claiming its unmerged prose as a checked numerical result. Historical holdout 527/529 **NOT_RUN**; Lean-to-interval extraction and proof audit **NOT_RUN**; historical drag/impact **NOT_RUN**.

**Original document / lineage:** NASA/Goddard, *Satellite Situation Report*, vol.3 no.22, 15 Nov 1963, printed p.8, NTRS 19640001198, [PDF](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), cited as C197 in the [cumulative matrix from draft PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), gives only the 8 Nov **date** of 1963-003B decay, without UTC time or position. C131/C197 share the same primary NASA lineage; derived TLE mirrors are not independent observations of the fall. The software's model constants and the synthetic test premises are *not* sourced from that NASA record.


## Mechanical-work falsification: co-rotating J2 + explicit drag (🦫)

A new **conditional numerical diagnostic** `src/lib/orbitEnergyAudit.ts` checks a conservation/dissipation identity which is distinct from a historical inference. Under the *assumed* stationary axisymmetric Earth/J2 potential and an atmosphere co-rotating rigidly with the constant Earth rate, let

- `J = |v|²/2 + U(r, J2) - omega * Lz` in km²/s²;
- `v_rel = v - omega × r`;
- `dJ/dt = a_drag · v_rel = -500 * rho * (Cd A/m) * |v_rel|³ <= 0` in km²/s³, with velocities in km/s, rho in kg/m³ and Cd A/m in m²/kg.

For the same explicit density function and `Cd*A/m` supplied to the coupled RK4 force, `dragJacobiPowerKm2S3` reuses `dragAccelerationKmS2`. No independently tuned drag term is fitted into the work check. The auditor runs `propagate` from each preceding r/v state; if the caller-defined spherical termination altitude is crossed, it records the **partial** event step rather than integrating past it. It compares the numerical change of `J` to trapezoid-quadrature of the assumed drag power and returns every per-step closure residual, largest numerical increase and complete residual. A caller-provided positive tolerance yields `NUMERICALLY_CONSISTENT` or `NUMERICALLY_UNRESOLVED`; zero duration returns `NOT_EVALUATED`. Neither label is a rigorous error enclosure or a certified orbit. Repeat with smaller steps to challenge quadrature/integration errors; `EVENT_CONFLICT` from the separate convergence diagnostic still takes precedence for event prediction.

**SYNTHETIC checks:** no-drag J2 conserves `J` numerically; positive co-rotating drag decreases `J` with negative modeled work; reducing the step improves closure; an intentionally coarse step is *not* awarded conservation; a first descending threshold event truncates work and is never called impact; invalid density/provenance/steps are refused. Source-free historical atmospheric reconstruction remains prohibited. The test's constant density is synthetic and deliberately **not** claimed to describe Earth on 8 November 1963.

Reproduce on the actual GitHub Actions PR HEAD with Node 22:
```sh
node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs tests/orbitAdmissibility.test.mjs tests/orbitEnergyAudit.test.mjs
```

**Scientific provenance and limits:** NASA/Goddard, *Satellite Situation Report*, vol. 3 no. 22, 15/11/1963, printed p. 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), has only the date 8 Nov for 1963-003B decay, not r/v, thermospheric density, fragmentation height, UTC or geography (matrix **C197–C201**, [cumulative draft PR #1](https://github.com/franklinbaldo/conde-incident/pull/1)). C25/C179–C185 and the mirrored TLE lineage are derivative, not an independent instrument record; RAAN conflict persists. The proposed [document → Lean → admissible parameters → simulation protocol (#28)](https://github.com/franklinbaldo/conde-incident/pull/28) motivates this check, but an authenticated Lean export/constraint box is **not** yet available. **Original 527/529 blind holdout: NOT_RUN. Historically calibrated density and drag: NOT_RUN. 528 terminal time/place: NOT_RUN.** A decrease in model Jacobi energy is neither proof of reentry nor of a ground impact at Conde.


## Refinement-aware chronological 527/529 holdout (🦫, 12 Nov 2026 UTC)

`src/lib/orbitHoldoutAudit.ts` consumes a **previously fitted** 527/529 Cartesian state and its genuinely future, predeclared holdout positions. It invokes the existing strict UTC / object / reference-frame / cutoff validator before any numerical assessment. It then separately reintegrates BOTH the unfitted baseline and fitted r/v states at each withheld epoch using the **same J2 + caller-sourced drag model**, with the existing full-state step-halving routine. A coarse RK4 holdout score is **not** accepted as validation. SGP4 remains an independent mean-element baseline: the "baseline" in this audit means *unfitted coupled Cartesian initial state*, **not SGP4**.

A mismatch of threshold event across step sizes is `EVENT_CONFLICT`, followed by `NOT_RESOLVED` for an unmet numerical tolerance, or `MODEL_TERMINATED` if both resolved model trajectories terminate before a future position observation. These statuses report **no RMS ranking**. If all paired predictions resolve, RMS position errors (km) for baseline and fitted model are calculated at every refinement using only the withheld positions, retaining the signed delta (`fitted - baseline`). If the winner changes across the last three resolutions, `REFINEMENT_RANKING_CONFLICT` blocks a victory claim. A near tie relative to the observed refinement sensitivity or the caller's position tolerance is `NUMERICALLY_INDISTINGUISHABLE`. Otherwise outcomes are deliberately labelled `APPARENT_FITTED_BETTER` or `APPARENT_BASELINE_BETTER`. The sensitivity is **a heuristic difference across integrations, not a rigorous error bound**; no provisional result implies a physical truth or a probability.

The result **always** retains `observationAuthenticity=NOT_VERIFIED`, `observationIndependence=NOT_VERIFIED`, `historicalCalibration=NOT_RUN`, `rigorousErrorEnclosure=false`, `impactInference=NOT_SUPPORTED`. Labelled synthetic controls demonstrate a false positive from an unresolved numerical event, a damaged future fit versus unfitted baseline, an apparent fit improvement, a numerical near-tie, stability failure, and chronological/provenance rejection. To validate 1963, separate source authentication is essential, not just passing the validator with an arbitrary source string.

**Reproduce in GitHub Actions at the exact PR head**: `node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs tests/orbitAdmissibility.test.mjs tests/orbitEnergyAudit.test.mjs tests/orbitHoldoutAudit.test.mjs`. This remains a suite of **synthetic** tests. Original 527/529 epoch-and-frame-indexed Cartesian tracks with uncertainty/covariance and documented observation independence are **still absent**. C25/C123/C128 and C179–C185 are derived Space-Track mirrors with a disputed 528 RAAN; they cannot become independent observations merely through this interface. The NASA/Goddard 15 Nov 1963 p.8 primary record (NTRS [19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), matrix **C197**, same institutional chain as C131) records a day-only decay for 1963-003B and contains no Cartesian samples, thermospheric density, site, or exact time. Verified Lean parameter boxes are not available from #17; **Lean→historical domains NOT_RUN; historical holdout 527/529 NOT_RUN; atmospheric calibration NOT_RUN; NORAD 528 terminal geography NOT_RUN**. This code cannot exclude or require Conde.


## Bounded conditional inverse + independent numerical holdout (Castor, 12 Nov 2026)

New `src/lib/orbitConditionalFit.ts` consumes the declared Cartesian velocity intersections from `orbitAdmissibility.ts`, **not** a validated historical Lean export. It allows inverse calibration ONLY if all three velocity axes have a finite nonempty closed interval; EMPTY and PARTIAL halt with no fitted state, no fake witness and no filled-in prior. A synthetic baseline outside a box is explicitly projected onto it and labeled. The bounded coordinate-grid search evaluates only states inside the box; there is a strict round budget and an explicit `NO_FINITE_TRAINING_SCORE` result when an assumed trajectory crosses the numerical threshold before training observations.

The fit uses only pre-cutoff observations in one named Cartesian inertial frame and NORAD target (527 or 529). The original UTC epoch, declared frame and chronological holdout are checked at the same validation boundary as the existing two-phase fitter. The withheld future is used only by the already separate `auditFutureOrbitScore` numerical-refinement audit. A worse future prediction remains negative evidence; step-size conflicts can veto the apparent ranking. The baseline here is the **bounded unadjusted Cartesian candidate**, not SGP4. Convergence is empirical under the assumed force model, not a certified enclosure.

The fixed-bound contracts are tagged `SYNTHETIC`/`CONDITIONAL` and `proofVerification=NOT_RUN`; documentary provenance labels alone DO NOT authenticate the premise or show that Lean 4.35.0 checked it. The complementary exact-rational domain-audit contract is still proposed in [PR #37](https://github.com/franklinbaldo/conde-incident/pull/37); this slice does not silently consume its unmerged API, round its fractions, or certify them. A future independently verified Lean handoff must bind evidence occurrence, source lineage, epoch, inertial coordinate frame, units, hash and theorem before real calibration. No historical osculating r/v 527/529 are available in this branch. **Historical holdout, atmospheric 1963 calibration, terminal position/time 528, and impact inference: NOT_RUN.**

**Original documentary anchor:** NASA/Goddard `Satellite Situation Report` vol. 3 no. 22, 15 Nov 1963, printed p. 8 ([NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)), matrix occurrence C197: **1963-003B decayed on 8 Nov**; the facsimile does not specify hour or position. NASA institutional compilation and secondary Space-Track mirrors C25/C179–C185 are dependent tracking lineage, not independent Cartesian sensors. RAAN 198.5261° versus 284.1520° remains unresolved. This mathematical regression is NOT a new entry in the historical evidence matrix.

## Independent numerical falsification of bounded inverse training gain (🦫)

`fitConditionalVelocity` optimizes a **coarse-step** in-sample RMS; an improvement
there can be a discretization artifact, even inside a declared admissible
velocity box. A shared numerical residual auditor now independently
reintegrates baseline and fitted coupled r/v trajectories at each *training*
epoch, with full step halving. It uses exactly the same event/units/ranking
logic as the **separate post-cutoff holdout**. Each result explicitly carries
`phase=TRAINING` or `HOLDOUT` to prevent conflating the two. Both retain
provenance flags `NOT_VERIFIED` and no historical impact inference.

`CALIBRATED_CONDITIONALLY` is returned only if the independently refined
in-sample ranking is `APPARENT_FITTED_BETTER`; event conflict, failure to
converge, model termination, reversal, or numerical near-tie produce
`TRAINING_GAIN_UNCONFIRMED` while preserving the fitted candidate and the
negative audit. This is **not** a certified RK4 error enclosure, a guaranteed
global optimum, or out-of-sample predictive validation. A synthetic regression
demonstrates **better in-sample fit yet worse future performance**.

Run on exact GitHub Actions PR HEAD:
```sh
node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs tests/orbitAdmissibility.test.mjs tests/orbitEnergyAudit.test.mjs tests/orbitHoldoutAudit.test.mjs tests/orbitConditionalFit.test.mjs tests/orbitTrainingAudit.test.mjs
```

Historical evidence remains unchanged: NASA/Goddard *Satellite Situation
Report*, 15 Nov 1963, printed p.8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
matrix occurrence C197 on the draft [cumulative PR #1](https://github.com/franklinbaldo/conde-incident/pull/1),
records only 8 Nov **decay date** for 1963-003B, not time or location.
The derived 527/528/529 orbit mirrors C179–C185/C240–C241 share tracking
lineage and the RAAN discrepancy is unresolved. Lean-certified empirical
admissible r/v intervals, original holdout observations (epochs/frame/uncertainty),
atmospheric 1963 drag calibration, terminal 528 coordinates and impact claims:
**NOT_RUN/NOT_SUPPORTED**.


## Alternative-premise conditional physics comparison (🦫, 12 Nov 2026 UTC)

The new \`src/lib/orbitAlternativeFits.ts\` consumes **already-separated** conditional
Cartesian (r,v) scenarios for the same NORAD 527 or 529, UTC initial epoch,
inertial frame, and shared chronological predeclared training/holdout partition.
It calls the existing \`fitConditionalVelocity\` and independent step-halving
training/holdout audits **separately for each alternative**. Initial positions
may differ; velocity boxes and documentary ancestral chains are NEVER
intersected across alternatives. A contradictory or unbounded branch produces
its own negative \`NOT_RUN_*\` result, without contaminating another branch.

The result exposes *every* branch's conditional calibration/negative holdout,
but never selects a "winner" based on withheld data:
\`selectedAlternativeId=null\`, \`branchSetExhaustive=false\`,
\`historicLocation=INDETERMINATE\`, \`groundImpact=NOT_SUPPORTED\`.
This is a numerical **consumer**, not a substitute for the still-unmerged
exact-rational source-alternative split in [PR #43](https://github.com/franklinbaldo/conde-incident/pull/43)
or a verified historical Lean 4.35.0 constraint export. The branch labels and
lineage strings are **declarations**, not proof of provenance or independence.
SGP4 is not calculated in this module; the internal unfitted Cartesian
baseline must never be renamed SGP4.

Run synthetic controls (plus the pre-existing physics suite) in GitHub Actions
using \`node --experimental-strip-types --test tests/orbit*.test.mjs\`.
The tests explicitly show two mutually exclusive **synthetic** velocity boxes
that are each nonempty, an inconsistent branch that does not remove a surviving
one, an unbounded box that cannot create a trajectory, future deterioration
despite better training, identity/frame/epoch rejection and heldout leakage.

**Primary documentary anchor:** NASA/Goddard, *Satellite Situation Report*,
vol. 3 nº 22, 15 November 1963, printed p. 8,
[NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
occurrence **C197** in [cumulative matrix PR #1](https://github.com/franklinbaldo/conde-incident/pull/1).
It documents only 8 November as decay date for 1963-003B and has no UTC time,
position or density record. C25/C179–C185/C240–C241 are secondary orbit-lineage
material, not independent 527/529 observations; the competing 528 RAAN values
remain unresolved. **Historical Lean export/verification, NORAD 527/529
original blind holdout, 1963 atmosphere calibration and NORAD 528 terminal
place/time: NOT_RUN.** Neither a conditional orbital trajectory nor atmospheric
reentry establishes a terrestrial impact, especially not at Conde.


## Ponte conservadora para domínios racionais declarados (#43, 12/11/2026)

`src/lib/orbitDeclaredDomainBridge.ts` consome apenas a **saída declarada** de `analyzeAlternatives` (contrato proposto na [PR #43](https://github.com/franklinbaldo/conde-incident/pull/43)), com frações exatas, IDs/ocorrências de evidências, URIs, grupos de dependência e referências Lean **declaradas**. A #43 não certifica documentação primária, Lean nem física; este módulo também não importa código de uma PR não integrada, não executa Lean 4.35.0, não verifica SHA do artefato nem reconstrói TLEs.

O resultado da #43 **não contém unidade nem fonte do intervalo inicial**. Por isso o chamador deve declarar `assumedUnit: 'km/s'`, época UTC, referencial, NORAD 527 ou 529, estado inicial cartesiano e `initialDomainSource` para cada alternativa. A saída conserva `unitFromAuditor: NOT_PRESENT`, `sourceAuthenticity: NOT_VERIFIED`, `leanProof: NOT_VERIFIED` e `frameTransformation: NOT_RUN`. Campos declarados não certificam a observação.

Somente componentes `vx`, `vy`, `vz` são aceitas; não se converte RAAN, TEME/SGP4 nem outros parâmetros em estado osculador. As caixas de hipóteses alternativas permanecem separadas. Contradições geram `NOT_RUN_CONTRADICTORY` **apenas** no ramo afetado; dados incompletos ou sem linhagem geram `NOT_RUN_INCOMPLETE` ou `NOT_RUN_UNTRACED`.

A conversão racional exata → Float64 arredonda cada extremo **para o interior** do intervalo original. Assim, nenhuma velocidade amostrada fica fora da caixa matemática declarada, mas o conjunto representável pode ser menor que o domínio original. Um intervalo mais estreito que a resolução Float64 sem ponto representável produz `NOT_RUN_FLOAT64_PRECISION`, não um falso testemunho viável. Uma caixa discretizada, mesmo numericamente estável, não é prova de encerramento global, prior estatístico ou posterior histórica.

Os novos testes exclusivamente **sintéticos** cobrem domínios disjuntos, arredondamento de `3/10` a `4/5`, janela racional sub-ulp, singleton inexato, rejeição de Lean `PASS` fictício, unidade/parametrização inválidas e propagação acoplada J2 com seed repetível.

Reproduzir com Node 22: `node --experimental-strip-types --test tests/orbitDeclaredDomainBridge.test.mjs`. O workflow `orbit-physics.yml` executa essa regressão junto à suíte física integral no HEAD exato. **Validação histórica cega 527/529: NOT_RUN**, assim como parâmetros de arrasto documentados e prova Lean histórica. A NASA/Goddard, *Satellite Situation Report*, vol. 3 nº 22 (15/11/1963), p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), matriz **C197** da [draft PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), só registra **08/11/1963** como data de decaimento de 1963-003B, sem hora e lugar. TLEs derivados C25/C179–C185 não são observações independentes nem resolvem o conflito RAAN. Sem inferência sobre Conde, reentrada terminal ou impacto.


## Correção: interseção racional exata com IEEE-754 (Castor, 12/11/2026)

**Contraprova de precisão anterior:** o adaptador de domínios da PR #43 fazia
`Number(numerador) / Number(denominador)` antes de arredondar os extremos
para o interior. A fração exata `10^400/10^400 = 1` virava
`Infinity / Infinity = NaN` e produzia **`NOT_RUN_FLOAT64_PRECISION` falso**,
apesar de 1 ser exatamente representável. Frações `1/2^1074` (menor
subnormal positivo) igualmente não sobreviviam a essa conversão intermediária.
O defeito é *numérico*, não uma nova observação de 1963.

**Correção em `orbitDeclaredDomainBridge.ts`:** a interseção usa busca
binária determinística sobre a ordenação monótona de todos os valores **finitos**
IEEE-754 binary64, comparando cada candidato à fração original via
`BigInt`, sem conversão intermediária dos inteiros para `Number`.
Encontra o primeiro valor maior/igual ao mínimo exato e o último
menor/igual ao máximo exato. Nenhum estado publicado pode estar fora dos
intervalos racionais declarados. Se não houver ponto representável, retorna
`NOT_RUN_FLOAT64_PRECISION`. Quando só um extremo racional ultrapassa o
alcance de Float64, preserva a **interseção finita** até `Number.MAX_VALUE`,
em vez de declarar incorretamente que ela é vazia. A saída é somente um
**subconjunto representável**, não uma cobertura certificada de todos os
valores reais do domínio nem a certificação de dinâmica orbital.

**Controles adversariais SINTÉTICOS:** `10^400/10^400`, limites negativos,
subnormal `1/2^1074`, singleton sub-ulp `1/2^1075` sem ponto Float64,
intervalos exteriores ao máximo finito e região que admite apenas zero.
São cinco regressões novas em `tests/orbitDeclaredDomainBridge.test.mjs`,
executadas pelo mesmo workflow de cabeça exata `orbit-physics.yml`.
Nenhum parâmetro físico foi inferido, nenhum valor de RAAN conflituoso foi
combinado e nenhuma amostragem Monte Carlo passou a ser posterior histórica.

**Ancora documental e cadeia:** NASA/Goddard,
*Satellite Situation Report*, vol. 3 nº 22, 15/11/1963, p. impressa 8,
[NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
matriz cumulativa **C197 na PR #1**, só registra 08/11/1963 como **dia**
de decaimento de 1963-003B. Os TLEs espelhados C25/C179–C185 e C240/C241
são derivados, com possível linhagem NORAD comum, sem observações
cartesianas primárias independentes e com RAAN conflitante. As premissas
racionais da PR #43 são declaradas, **não** domínios históricos
certificados por Lean. Os testes não fornecem holdouts originais dos objetos
527/529, densidade de 1963 nem ponto/hora da reentrada do 528: **NOT_RUN**.


## Auditoria de integridade da saída de domínios declarados (Castor, 12/11/2026)

**Falha evitada:** a ponte física aceitava a lista `parameters[*].admissible`
de um JSON supostamente produzido pela [PR #43](https://github.com/franklinbaldo/conde-incident/pull/43)
sem verificar os respectivos intervalos **originais**, os rótulos por
parâmetro ou a contagem/status global dos cenários. Bastava alterar
`admissible` após a auditoria para **alargar o domínio** ou falsificar
`CONTRADICTORY`/`ONE_DECLARED_FEASIBLE`. Isso permitiria propagar
velocidades não justificadas nem mesmo pelas premissas numéricas declaradas.

A ponte agora exige, para cada `vx/vy/vz`, `initial` e `admissible` em
frações racionais exatas. Verifica com `BigInt` a inclusão
`initial.min <= admissible.min <= admissible.max <= initial.max`,
recalcula `EMPTY/REDUCED/UNCHANGED`, reconcilia
`CONTRADICTORY/REDUCED/UNCHANGED` do cenário e reconcilia
`scenarios_declared`, `scenarios_with_nonempty_intervals` e o resumo
`MULTIPLE/ONE/NO_DECLARED_FEASIBLE`. A rastreabilidade só permite
componentes de velocidade; uma etiqueta `SYNTHETIC_ONLY` exige URI
`synthetic:`, e `DECLARED_NOT_AUDITED` exige HTTPS e ID estilo Cxxx.
Entradas inconsistentes falham **antes** de qualquer simulação. Domínios
contraditórios coerentemente reportados continuam isolados por cenário.

**Limite:** essa segunda checagem detecta adulteração de status e expansão,
mas não verifica se cada restrição original foi efetivamente aplicada.
O campo `trace` vindo da #43 não carrega os próprios intervalos das
restrições; para auditoria end-to-end será necessário o input original com
SHA, a identidade documental, sua independência e uma certificação Lean
4.35.0 verificável. Nem o JSON declarado nem a interseção numérica são
provas de que tais intervalos descrevam o objeto histórico.

Os testes adversariais são **SINTÉTICOS**, em
`tests/orbitDeclaredDomainBridge.test.mjs`: aumento racional de domínio
(inclusive alteração menor que uma ULP), troca de rótulo por parâmetro,
contradição falsa, contagem de cenários falsificada, `initial` ausente ou
invertido e linhagem sintética reetiquetada como histórica. A suíte anterior
de interseção IEEE-754, propagação J2 e seed continua presente.
Executar com Node 22 e o workflow `orbit-physics.yml` no HEAD da PR #5.

**Linhagem documental:** matriz cumulativa C197, [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1),
remete à edição original NASA/Goddard *Satellite Situation Report*
vol. 3 nº 22 (15/11/1963), p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf).
Registra somente **08/11/1963** para decaimento de 1963-003B.
C179–C185 trazem elementos espelhados de linhagem AFSPC/NORAD que
não são medições independentes, e há conflito de RAAN 198.5261°
versus 284.1520°. Não se inferem hora, local de reentrada, impacto
nem probabilidade. **Holdout histórico original 527/529, certificação
Lean de caixas históricas, modelo de arrasto de 1963 e SGP4 baseline
comparável: NOT_RUN.**
