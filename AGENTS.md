# Conde Incident: agent operating contract

Scope: **franklinbaldo/conde-incident only**. The separate blog is read-only; do not publish or alter it. Do not contact archives, researchers or individuals without specific authorization.

## Source and epistemic rules
- Prioritize original 1963 source facsimiles and raw historical Space-Track data; preserve exact URL, issue/date/page or TLE epoch, checksum and provenance.
- Label each claim: original directly inspected; contemporary secondhand report; modern secondary catalog; quantitative inference; hypothesis. Documentary proof of the Tupi *report* is not physical proof of a sphere/crater/body.
- Track dependence chains; NASA/NORAD/catlogs drawing on the same tracking must not be counted as independent measurements, nor Tupi/FBIS/reprints as independent witnesses.
- Do not invent pass times, reentry coordinates, posterior probabilities, temperatures, ballistic coefficients, historical quotes, TLEs or observational events. Keep negative results and uncertainty.
- **Source-first RAAN rule (12/11/2026):** remove the old site's unsupported RAAN 284.1520° and associated synthetic vector from active orbital inputs (recoverable from Git). The only operational 528 **reference** is the documented secondary TLE literal RAAN 198.5261° at 1963-10-27 14:40:16.132512 UTC, C25#1/C179#1, with exact URL/hash in PR #14. It is **not** an exact physical constraint: treat true RAAN as a latent circular parameter and derive any narrowing from justified multi-epoch observations, J2 and calibrated drag; no invented priors, model error or MCMC posterior. Obtain primary custody when possible; do not turn an unsourced old constant into a competing observational scenario.
- Existing code is exploratory: SGP4 extrapolated ~12 days does not determine a terminal entry; sampling random latitude phase is not a dynamically fitted Monte Carlo; pre-existing inverse feasibility flags are not a physical proof.
- The day-only NASA decay record of 8 Nov 1963 gives no terminal time or place. Do not treat 23:59 as an observed timestamp.
- The Lean proof kernel certifies logical implications of premises, not empirical authenticity or orbital integration. Preserve any known holdout failures.

## Mandatory scientific pipeline: document → Lean → parameters → simulation

**All scientific and editorial agents follow this chain.** Lean 4.35.0 stores
and checks explicit admissibility constraints. It is not merely an archive of
theorems, a numerical optimizer, or proof that a premise is historically true.

1. **Document and trace.** Obtain an identifiable original observation, or
   explicitly classify a secondhand source. Add/update a stable occurrence in
   the cumulative evidence matrix: source URL, date/page or TLE epoch, units,
   extraction, checksum when available, uncertainty, independent chain and
   negative findings. C44–C46 are duplicated labels: use occurrence-specific
   keys, never silently collapse them. A report of a falling object is not
   itself proof of a ground impact.
2. **Translate into Lean.** For each evidentially justified inference, record
   its matrix ID/occurrence, source chain, assumptions, status (measured,
   conditional or hypothesis), physical dimensions, reference frame and
   uncertainty. Express the restriction as a predicate on typed simulation
   parameters. **Do not automatically convert every report into a hard
   constraint.** When a source conflicts with another, keep distinct
   scenarios until provenance resolves the conflict; do not average TLEs.
3. **Narrow feasible parameters.** Define the feasible set
   `Θₙ = {θ | C₁ θ ∧ ... ∧ Cₙ θ}`, with the extra constraint producing
   `Θₙ₊₁ ⊆ Θₙ`. Verify whether it remains nonempty. A contradiction is
   a diagnostic of inconsistent premises, not proof of any geography.
   Keep unconstrained parameters open. Lean checks logical implications;
   numerical witnesses, error bounds and physically certified enclosures
   must come from a reproducible solver/integrator with checked assumptions.
4. **Run simulations and falsify.** Castor consumes only admissible bounds
   and scenario labels, records deterministic seeds, calibration, units,
   numerical error and holdouts (notably NORAD 529/527); returns predictions,
   counterexamples and remaining parameter ranges. Feed supported refinements
   back into the matrix and Lean, iteratively. Sampling/Monte Carlo cannot
   prove absence of every feasible trajectory.
5. **Report one of five honest outcomes:** (a) Conde *excluded* if a nonempty,
   physically justified feasible set contains **no** candidate with a ground
   impact there; (b) Conde *forced* if **all** feasible candidates imply that
   impact; (c) another site and time/coordinate window identified if **all**
   feasible candidates fit that window; (d) underdetermined if alternatives
   survive; (e) contradictory if no candidates survive. Distinguish reentry
   from a proven impact. Never declare an exact hour/point unless precision
   is justified by observations plus model and numerical error bounds.
   An abstract Lean theorem is conditional on its premises, not evidence
   that a 1963 event actually occurred at the proven location.
6. **Keep the chain bidirectional and auditable:** evidence IDs → Lean
   predicates → numerical parameter bounds → reproducible simulation →
   new discriminating checks. Cite every transition and do not present
   exploratory or conditional results as historical fact.

**Agent handoff:** 🦉 Coruja and 🐢 Tartaruga identify and validate documents
and orbital records; 🐙 Polvo maintains formal constraints, dependency
proofs and `lake build`/`#print axioms`; 🦫 Castor connects their admitted
domains to the physical simulator and holdouts; 🦅 Gavião audits truth versus
assumptions and proof coverage; 🦡 Texugo challenges false precision/churn;
🐘 Elefante coordinates integration; 🦊 Raposa shows evidence-linked status
and uncertainty on the case site. The independent historical-research routine
may contribute new sources but never invent a formal restriction.
Keep publication and archive-contact restrictions from this file.

## Scientific progress gate: no circular proof churn

**Progress is measured by discriminating evidence and reduced uncertainty, not the number of Lean theorems, empty JSON interfaces or passing CI alone.** The distinction between a simulator and historical observation is already settled: do not create additional standalone proofs reasserting it. Formalize an implication only when it has a specific new empirical constraint, testable numerical consequence, concrete bug regression or historical archive import.

For each scientific PR, report: (1) source matrix ID plus occurrence, document lineage, epoch/frame/units and uncertainty; (2) the exact question and rival scenarios; (3) reproducible **before/after** admissible bounds, eliminated/surviving scenarios, and test/holdout errors with units; (4) nonempty domain/witness when claiming restriction; (5) negative result and specific missing measurement when not measurable. A narrowing assertion without actual numeric evidence must be **NOT_RUN**, not presented as achievement. Do not generate new formal gates whose inputs are all unverified and null merely to increase coverage.

Immediate discriminating targets: recover full epoch, source and reference conventions for the conflicting 528 RAAN reports (284.1520° and 198.5261°), then quantitatively compare viable element histories against available 527/528/529 time series, established baselines and holdouts. Cross-object mean-motion fits are retrospective model comparisons, not proof of physical coupling. If no empirical reduction is possible, pause tautological theorem expansion and produce a concise blocker specifying the missing data and its intended test. 🦡 Texugo should treat repeated restatement of known caveats as churn.

## Physical observable graph and cross-domain evidence

For each free physical parameter, systematically derive **observable quantities** by
unit-preserving equations and search the existing evidence matrix for measurements
of those observables. This is an operational method, not permission to convert
a source-free number into a measured fact. Each edge MUST carry:
`parameter -> equation -> derived quantity (SI units, frame, epoch, position/altitude)
-> measurement IDs and source chain -> residual and error interval -> feasible-domain update`.
Keep non-observed quantities free; a dimensional unit conversion alone does NOT
constitute a new independent constraint or extra witness.

Examples already linked to the case: C179 mean motion (rev/day) -> angular
frequency (rad/s) -> Kepler proxy semimajor axis/perigee -> J2 nodal rate;
C151 NOAA IGRA 8 Nov 1963 Recife pressure/wind -> Pa and horizontal wind
vector (east/north m/s); atmospheric density requires pressure AND
temperature from a collocated profile plus an equation of state; descent
displacement depends on wind as a function of position, time and altitude,
vertical speed, object mass/area and aerodynamic drag. C144-C146 are Navy
synoptic charts, not a directly measured Conde wind profile.

**Geographic and dynamic scope is a hard gate:** Recife wind cannot be used
as measured wind at Conde without separately justified spatiotemporal
transfer and uncertainty; surface storm winds cannot automatically invalidate
an orbital entry or prove/no-prove ground impact. Local winds may matter for
balloon drift or the terminal drift of a surviving fragment. Pressure map,
balloon wind, geomagnetic Ap and orbital precession belong to DIFFERENT
observation operators until the intermediate physical relations and errors
are calibrated. For model-only assumptions report sensitivity, not historical
posterior; for MCMC specify likelihood, priors, observation covariance,
dependence chains, seed and held-out predictions. Do not fabricate missing
wind/temperature/density, mass or fragment survival. Explicitly show the
before/after physically admissible ranges and refuse to claim reduction
when no calibrated observational inequality exists.

## Work protocol
1. Read main, this file, your `team/<animal>.md` card, open issues/PRs, and the cumulative matrix in `research/` (present in PR #1 until merged).
2. Resume an existing issue/PR in your domain before claiming new work. A single agent claims a single active issue; issues use `<priority 0–100> <emoji> <short title>`. Avoid duplicate claims and conflicting edits.
3. Deliver one meaningful, end-to-end slice per run, not speculative planning or cosmetic churn. Use an isolated branch and PR; build/check on final commit. Do not rebase, force-push or merge your own implementation PR.
4. Each new record needs source URL/identifier, extraction/verbatim check, independence analysis, status, reproducible script/proof where applicable, and update to the evidence matrix without dropping old IDs.
5. 🦅 Gavião reviews independently; 🐘 Elefante sets priorities and merges only after review, green CI on actual head and resolved conflicts. 🦡 Texugo combats churn and unvalidated scientific claims.
6. Close each session with a concise durable OKF memory entry under `team/memory/<animal>/`: verified changes, failed attempts, next question, commit/PR SHA; one per session. No fictitious validation. Keep personal reflections separate from scientific evidence. Café/chat is optional, never a blocker.
7. The existing hourly investigation automation is independent research; do not duplicate its general search. Agents should produce code, sources or formal evidence specific to their assigned responsibility.

## Next targets
- PR #1: evidence-first site, cumulative C01–C238 research matrix, SGP4 baseline fixes, Lean core and CI; inspect, validate, integrate in a controlled manner.
- Full Lean archive from original compiled package: `Evidence.lean`, 154 propositions / 151 labels, including C44–C46 collisions.
- Original TLEs: 527/528/529 historical epochs and provenance, calibrated dynamics, holdout baseline versus coupled multi-target fit.
- Genealogy: *Diário de Notícias* (Salvador) 9 Nov, *Jornal da Bahia* 11 Nov, *O Jornal* (Rio) 7–12 Nov, FBIS and diplomatic A-628 attachments; avoid counting repetition as confirmation.
