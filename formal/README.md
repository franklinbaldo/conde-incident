## 🐙 C241-T10: a numerical RAAN test instead of more generic simulator axioms

[`RaanEpochConstraint.lean`](Conde1963/RaanEpochConstraint.lean) checks the *actual
transcribed numerical discrepancy* from [Tartaruga's audited C241-T10,
PR #14 at commit 1934198e](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/tools/tle_raan_epoch_offset_j2_audit.py).
RAANs 284.1520° / 198.5261°, 16.132608 seconds of epoch difference, and
0.0001° combined rounding tolerance imply **at least
458,578.620394... degrees/day** to bridge the shortest circular gap by epoch
offset alone. The Lean kernel checks that this required rate is strictly
between 458,578 and 458,579 degrees/day. The Python
[`raan_epoch_contract.py`](scripts/raan_epoch_contract.py) recomputes the
threshold with exact `Fraction`, exports an explicit machine-readable
contract, and tests angular wraparound and failure cases.

**What was actually reduced:** the conditional explanatory family
`same-object + same-node + same-frame + epoch-offset only`, *if* its independently
justified maximum absolute RAAN rate is below that threshold. No physical
orbit family has yet been eliminated: the legacy RAAN/frame has **no primary
1963 provenance**, the secondary TLE is a single mirror chain, and no validated
rate envelope has been imposed. Thus 284.1520° and 198.5261° remain
unresolved alternatives, not averaged data or double observations. This test
adds no proof of Conde, impact or reentry. It avoids repeat proofs about whether
simulators demonstrate historical truth.

Source lineage: [matrix C25#1 L118](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L118),
[C179#1 L839](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L839),
and [C241-T10 at source commit](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/research/evidence_matrix_C001-C238_2026-11-11.md).
Original primary institutional documentary source:
[NASA/Goddard Satellite Situation Report 15 Nov 1963 printed p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
(C131#1/C197#1, one source): catalogued decay **day** only; not an
independent orbital RAAN or impact observation. This session did not reinspect
the NASA facsimile. The historical `Evidence.lean` archive remains NOT_RUN.

CI on PR head: `cd formal && lake build && lake env lean Conde1963/AxiomAudit.lean`,
`python3 -m unittest discover -s formal/tests -v`; workflow exports
`conde-raan-epoch.json` for Castor in `conde-evidence-contracts`.

---

## 🐙 Truth-to-simulation boundary: self-soundness is NOT historical impact

**New:** [`Conde1963/TruthBridge.lean`](Conde1963/TruthBridge.lean) closes an
epistemic gap in the prior model envelopes. `ImpactEnvelope.soundForPredictions`
only proves that a simulator's OWN prediction lies inside a reported
enclosure. It does not prove that the unknown 1963 physical outcome lies
inside that enclosure. A symbolic countermodel formally demonstrates the
difference without fabricated coordinates.

The distinct `TruthLink.actualCovered` premise must be justified externally
for every admissible state before an enclosure can say anything about a
**hypothetical actual** ground-impact event. Seven audited Lean theorems give
conditional exclusion, forcing and other-window criteria, monotonicity under
consistent refinement, and the necessity of an actual ground-impact event
to force a location. The truth link has **not been instantiated**, and the
existing `GroundImpactAdmissible` Boolean record is a declared audit, not an
empirically authenticated certificate. Neither layer proves a historical
event merely by being syntactically accepted or compiled.

The `truth_bridge_interface` in the exported Castor JSON fails closed:
no actual event or window, no proof of the physical link, no verified
continuous global coverage, no authenticated primary TLE custody or
independent 529 holdout. Its theorem names are checked against the
`#print axioms` audit by `test_truth_bridge_contract.py`. It is a
typed obligation to implement and validate, **not** a new orbital result.

**Documentary lineage, unchanged and not freshly re-inspected:**
[C01#1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L19)
records a Tupi/FBIS report, not a ground observation;
[C25#1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L118)
and [C179#1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L839)
reflect reproduced AFSPC-orbital material, not independent primary TLEs;
[C131#1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502)
and [C197#1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905)
cite **one** NASA/Goddard *Satellite Situation Report*, 15 Nov 1963,
printed p. 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
which records a decay date but no impact location/time. The registry still
preserves 241 occurrences and C44-C46 duplicate labels. Original
historical `Evidence.lean` ZIP / 154 propositions / 151 labels and
authenticated original digests remain **NOT_RECOVERED / NOT_RUN**.

Run on the PR's actual head:

```bash
python3 formal/scripts/evidence_registry.py --check formal/Conde1963/MatrixEvidence.lean --json /tmp/conde-evidence-contracts.json
cd formal && lake build && lake env lean Conde1963/AxiomAudit.lean
python3 -m unittest discover -s tests -v
```

# New: exhaustive-grid proof boundary

See [FiniteCoverage](finite_coverage.md) for seven formal obligations separating a verified *finite* screen from proof of a globally empty admissible domain, including a synthetic false-negative countermodel and a fail-closed Castor JSON handoff.

# Lean 4: Conde 1963

## 🐙 Model error envelopes and evidence-gated geographic claims (issue #15)

`Conde1963/Enclosures.lean` specifies a **per-parameter predicted-event
envelope**, not a statistical confidence interval or a historical impact
observation. A future calibrated propagator must provide a proof obligation
`ImpactEnvelope.soundForPredictions`: each event predicted under an
admissible parameter choice must lie in that choice's error envelope.
Merely listing grid outputs does **not** prove this property over the
complete continuous domain.

There are three explicitly *conditional* implications, all requiring
`GroundImpactAdmissible` (custody, frame/epoch/units, holdout, quantified
error, physical forces, **material survival and ground-impact event**) and
`HasCandidate`:

- `covered_envelope_excludes_conde`: all covered possible events are
  outside Conde; does **not** assert an impact anywhere else.
- `covered_envelope_forces_conde`: each survivor predicts an actual
  ground-impact event and its entire envelope is inside Conde.
- `covered_envelope_identifies_other_window`: every survivor predicts
  a ground-impact event in a specified other window **proved disjoint**
  from Conde, not an invented coordinate or date.

Proofs also show that an envelope overlapping Conde cannot establish
*uniform envelope separation*, the currently declared Castor threshold-only
audit cannot satisfy the ground-impact gate, and observing `none` on a
finite sample cannot establish global exclusion. These are logical
obligations **conditional on the simulator and admitted assumptions**, not
proofs of calibrated numerical integration, instrument custody, material
survival or actual ground impact. A future `GroundImpactAdmissible`
Boolean report must be independently checked, not trusted because its
bits were set to `true`.

The `conde-evidence-contracts` JSON now contains `enclosure_interface`
with proof names and mandatory inputs for 🦫 Castor. Its region, UTC window,
global coverage and empirical validation fields remain `null` / `false`.
It does **not** promote the day recorded by NASA to a physical-day filter.

**Document lineage reused rather than reinspected during this slice:**
[C01 Tupi/FBIS](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L19)
is evidence of a report, not physical impact;
[C131](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502)
and [C197](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905)
both cite the **same** NASA/Goddard *Satellite Situation Report*,
15/11/1963, printed p. 8
([NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)).
It records an 8 November decay **date** without a terminal time or site.
The frozen research matrix is blob `a7978c3a75a153b16ab70118a92c434bba674cb7`;
C44–C46 each appear twice with different meanings; all 241 occurrences
remain preserved. The original compiled Lean 4.35.0 ZIP containing
`Evidence.lean` / 154 propositions / 151 labels and independent custody
digests is still absent: historical import `NOT_RUN`.

CI at the actual PR head runs `lake build`, `lake env lean
Conde1963/AxiomAudit.lean` (seven additional printed theorem dependencies),
`python3 -m unittest discover -s tests -v`, full matrix registry export,
and the Web lint/build. No physical result or historical confidence is
returned by this addition.


## 🐙 Epistemic correction: catalogue date is NOT the physical event date

**Current normative interpretation, superseding any older text below that
treated the NASA catalogue day as an admitted physical constraint.**

- **Proven documentary statement:** NASA/Goddard's 15 Nov 1963 report
  records 1963-003B as decayed on **8 Nov 1963**. Matrix C131/C197 are
  two references to that **same document**, not independent observations.
- **Unproven scientific hypothesis:** the true physical orbital decay
  occurred on that same day. We do not know the operational method by which
  NORAD/NASA assigned the date, its error distribution, last positive track,
  first failed acquisition, actual reentry time or location.
- **Separate questions:** whether orbital decay occurred; its UTC interval;
  whether material survived; whether anything impacted Conde. A recorded
  catalogue date is not proof of any subsequent ground impact.
- **Lean:** `nasa_record_states_november_eighth` certifies the transcribed
  *documentary* value as a defined fact. `PhysicalDayMatchesCatalogue`
  is only a scientific proposition on a latent candidate. The C131/C197
  constraints have `use := .scenarioOnly`, so `AllowedFromSources` does
  **not** narrow physical parameters on that basis. Theorems provide
  explicit nonempty conditional verdicts: `ConditionallyForcesNasaDay`,
  `ConditionallyExcludesNasaDay`, `DayRemainsUnderdetermined`.
- **ALL 241 matrix occurrences:** every Lean row now has a mandatory
  `EpistemicUncertainty` marker, and the JSON contract provides
  `epistemic_uncertainty`, `uncertainty_basis`, `numeric_error_bounds`
  (`null`, never fabricated) and the source text plus permalink.
  C01 marks an **existing news report with physical occurrence unverified**;
  C131/C197 mark a **catalogue day with actual day unknown**; the other
  **238 occurrences are explicitly pending itemized uncertainty assessment
  in this formal transfer**, retaining the matrix's original caveats.
  Pending review does NOT declare those 238 false or lacking historical value.
- **Scope of CI proof:** information accounting and implications of assumed
  constraints, not authenticity, NORAD operational inference, an orbital
  prediction, or a calibrated statistical confidence interval.

A valid future day test must use independent observations, dated epochs,
verified custody, a physically validated propagation model and holdouts.
Only then may an error-bounded date hypothesis be admitted or rejected
**conditional on those justified premises**. If no parameters survive,
report contradictory premises; if on-day and off-day candidates both survive,
report indeterminate. Do not force a verdict with an unsupported date axiom.


## 🐙 Conditional outcomes and empty-grid guard (issue #15)

`Conde1963/Outcome.lean` now separates five possible scientific
**reporting classes** as logical obligations, never observed outcomes:

- **Contradictory premises** requires `¬ HasCandidate constraints`
  over the justified model domain; exhausting a *finite grid* is NOT
  proof of global inconsistency.
- **Conde forced** requires `ForcesConde`: a nonempty admissible
  domain and a predicted ground impact in Conde for **every** survivor.
- **Conde excluded** requires `ExcludesConde`: a nonempty domain
  and no modeled ground impact in Conde, but it does **not** imply
  impact elsewhere. A simulator returning `none` is a concrete
  logical countermodel to that inference.
- **Other window** requires `IdentifiesOtherWindow`: all survivors
  predict a ground impact in a stated time/place region **proved
  disjoint** from Conde. Hence `other_window_conditionally_excludes_conde`.
  Do not supply a made-up alternative window.
- **Indeterminate** has a sufficient witness `MixedCondeOutcomes`:
  one survivor with Conde impact and another survivor with either an
  outside impact or **no impact**. The theorem
  `mixed_outcomes_refute_both_decisive_conde_claims` rejects both
  forced and excluded verdicts in that case. Other kinds of uncertainty
  remain possible, so this is *not* an exhaustive decision procedure.

The theorems establish consistency under additional constraints,
pairwise incompatibility of contrary verdicts, and the difference
between global model satisfiability and finite grid coverage. No
historical trajectory is encoded or asserted here.

The machine-readable `outcome_interface` in the existing CI
`conde-evidence-contracts` JSON lists the five Lean obligations,
required documentary and numerical inputs, and **null**
`current_result`, `calibrated_model` and
`numerical_impact_window`. This is a typed handoff to 🦫 Castor,
not a claim that an orbital fit has been run. The matrix rows retain
their commit-pinned citations, C44–C46 distinct occurrences and
individual uncertainty/pending-review markers.

**Source lineage reused, not reauthenticated this round:**
NASA/Goddard *Satellite Situation Report*, 15 Nov 1963, p. 8,
[NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
matrix C131/C197 (one report, two citations); the FBIS/Tupi
transcription in C01 is a documentary report, not physical impact
evidence. Source matrix commit `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`,
Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7`.
The original `Evidence.lean` ZIP (154 propositions / 151 labels),
original independently recorded digests and the RAAN conflict
remain unresolved.

Reproduce in the PR head:

```bash
python3 formal/scripts/evidence_registry.py \
  --check formal/Conde1963/MatrixEvidence.lean \
  --json /tmp/conde-evidence-contracts.json
cd formal
lake build
lake env lean Conde1963/AxiomAudit.lean
python3 -m unittest discover -s tests -v
```

This folder starts the transfer of the previously compiled 11 November 2026 Lean 4.35.0 research archive.

`lake build` checks the **logical core**: provenance dependency, exact arithmetic from catalog statistics, holdout metric comparison and the failure of a date-only constraint to identify a geographic site.

**Important:** Compiling this code does not certify SGP4, a radar measurement, a TLE's authenticity or a trajectory to Conde.

The full historical package also contains `Evidence.lean`, the 154-entry structured registry, a generator and a 151-label cumulative matrix. The cumulative matrix **C01–C238** is now imported at `research/evidence_matrix_C001-C238_2026-11-11.md`. The larger generated `Evidence.lean` and structured formal registry are **not yet incorporated**; their source archive remains the original compiled 2026-11-11 package. Never describe this subset as the full historical corpus.

The `last528` recorded RAAN (198.5261°) highlights a provenance conflict with the existing site (284.1520°). Both need verification against the primary TLE record before a terminal position can be claimed.


## 🐙 Conditional proof slice (issue #15)

`Conde1963/Provenance.lean` proves that a *nonempty* admissible set
containing two different regions does **not** uniquely identify the region;
adding a physical constraint helps only if it actually removes the ambiguity.
It also formalizes the consequence of two records assigned to the same
provenance chain. The candidates are pedagogical countermodels, **not** 1963
trajectories. `Conde1963/AxiomAudit.lean` lists proof kernel dependencies in CI.

Source lineage (all references are to the [cumulative matrix](../research/evidence_matrix_C001-C238_2026-11-11.md), **not** fresh primary-source inspections in this PR):

- **C01:** Rádio Tupi/Federal Broadcast Information Service: the original
  preserved item is a report, not independent proof of a physical impact.
  [FBIS facsimile](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf).
- **C131 and C197:** NASA/Goddard, *Satellite Situation Report*,
  15 Nov 1963, printed p. 8 (PDF zero-based index 9, viewer page 10), NTRS `19640001198`,
  [source PDF](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf).
  The day of decay, 8 Nov 1963, is reported; time and region are not.
  C131 and C197 refer to the **same NASA document**, not independent measurements.
- **C139–C142:** catalog link of 527/528/529 and proposed joint dynamics:
  a shared launch or field does not constrain the individual final phase
  without independent dated observations, calibrated physics and holdouts.

The original Lean ZIP with the reported 154 propositions, 151 labels and
C44–C46 collisions is **not present** in this repository or the PR #1 tree.
Do not invent `Evidence.lean`, a registry or a generator from its summary.
`scripts/audit_zip.py` is a read-only **ingestion gate**, not an importer:

```bash
cd formal
python3 -m unittest discover -s tests -v  # synthetic structural regression
python3 scripts/audit_zip.py /path/to/ORIGINAL.zip \\
  --sha1 SHA1_FROM_PROVENANCE --sha256 SHA256_FROM_PROVENANCE
lake build
lake env lean Conde1963/AxiomAudit.lean
```

Actual original-ZIP audit/import: **NOT_RUN** until original bytes and separately
recorded hashes are supplied. A caller can compute matching hashes for a fake
ZIP, so passing this gate is now reported as `STRUCTURE_PASS_ONLY`, never as
independent historical provenance. Neither the hashes nor the 154/151 structure
establishes the authenticity or semantics of the original corpus. The tool checks ZIP member integrity, two
independent digest algorithms, count/label consistency and duplication, and
reports available generator candidates without executing them. It does **not**
check proposition semantics, distinguish two texts with the same ID, or certify
the authenticity of the source. If the original registry uses another explicit
key, pass `--label-key`; do not guess its schema or silently deduplicate.

`#print axioms` is made visible in the Actions log. An absence of `sorryAx`
for these theorems does not demonstrate orbital or documentary validity.

## Matrix citation integrity and an observation-decoder theorem (issue #15)

The frozen cumulative matrix has Git **blob** SHA-1
`a7978c3a75a153b16ab70118a92c434bba674cb7` in base PR #1
(commit `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`).
Run `python3 formal/scripts/verify_matrix_refs.py
research/evidence_matrix_C001-C238_2026-11-11.md` from the repository root.
CI checks this exact blob plus C01 **line 19**, C131 **line 502**,
C197 **line 905**, and the separate pairs C44 (164/175), C45 (165/176),
C46 (166/177). The C197 row uses Markdown bold in its label, which the
checker parses. The former site link to C01 **line 20** actually pointed
to **C02** and was corrected. New matrix revisions must be assessed and
pinned explicitly, never auto-renumbered. This is a snapshot/row-location
audit, **not** proof of historical source authenticity or recovery of the
unavailable historical Lean ZIP.

Two additional theorems prove that **no deterministic day-only decoder**
is correct on both illustrated admissible states if they share a day
yet have different regions. This is about an observational equivalence
class, not the NORAD 528 terminal orbit or any inferred probability.
`AxiomAudit.lean` also prints their axiom dependencies.


## 🐙 Evidence-driven constraint pipeline (issue #15)

The normative flow is defined in `AGENTS.md` (policy PR #28):
**verified document/record and lineage → evidence matrix ID+occurrence →
Lean proposition with explicit premises → feasible physical parameter domain →
reproducible simulator → falsifying observations and updated constraints**.

`Conde1963/Constraints.lean` provides a strictly conditional interface:

- `SourcedConstraint` distinguishes matrix label **and occurrence**
  (C44–C46 are ambiguous otherwise), source chain, evidential grade,
  accepted scenario versus hypothesis, and a predicate on an arbitrary
  typed parameter vector. No measured value is fabricated.
- `Allowed`, `HasCandidate` and monotonicity theorems prove that
  adding restrictions cannot enlarge the admissible set. If no
  candidate survives, **premises are inconsistent** and no geographic
  conclusion follows from that empty set.
- `ExcludesConde`, `ForcesConde`, `UniqueImpact` and `ImpactInside`
  are separate outcomes requiring nonempty feasible parameter sets.
  In particular, a NASA calendar day does **not** force an hour or
  location. A modeled atmospheric reentry is not proof of ground impact.
- `ExecutableRule` ties a Boolean predicate to its declarative
  condition through an explicit equivalence proof. `filterCandidateGrid`
  returns executable surviving numerical parameter choices, and
  `filter_grid_never_creates_candidates` proves it cannot add any
  unlisted choice. **Finite-grid exhaustiveness does not establish
  continuous-space exhaustiveness or physical model validity.**

The Castor integration should supply typed numerical inputs, accepted
source-backed filters, justified bounds and certified solver/numerical
errors. Before publishing any conclusion about Conde or another site,
the analysis must check feasibility, holdout data (including NORAD 529),
model assumptions, the reentry/ground-impact distinction and how
precisely any time/location window is supported.

**Present status:** these are machine-checked logical rules and a
finite-grid interface, NOT calibrated orbital integration, independent
verification of every historical source, recovery of the 154/151 Lean
archive, or an observed position/time of a 1963 impact.


## Historical note (superseded): documentary-day filter C131/C197 (11 November 2026)

`Conde1963/DocumentaryDay.lean` instantiates the abstract parameter
interface with one *historically sourced, limited* condition: the NASA/Goddard
*Satellite Situation Report* (15 November 1963, printed p. 8,
[NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)),
as pinned in matrix [C131 (L502)](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502)
and [C197 (L905)](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905),
reports a **decay date** of 8 Nov 1963 for 1963-003B/NORAD 528.

C131 and C197 describe the **same** NASA source, not independent
tracking stations. The proven `nasa_repeat_is_same_day_predicate` shows
that using both references does not restrict the scenario further than
using the documented day once. The executable Boolean day filter
`nasaReportedDayRule` is proved equivalent to its Lean predicate and
accepts two *illustrative* region-different candidates, rejecting a
synthetic off-day candidate. These cases do not represent recovered TLEs,
measured orbital states, or impact locations.

**Crucial type/semantics limit:** this candidate's `day` field is
interpreted *only within a scenario equating it to the NASA-recorded decay
day*. It is **not** a proof of ground-impact date or a calibrated time
of atmospheric passage. This report gives no terminal hour, coordinates,
ballistic coefficient, region, or physical link to the reported Conde
sphere. `nasa_day_cannot_identify_region` and the no-ground-impact
countermodel prove conditional non-identifiability, **not** that Conde
is physically excluded or that impact failed to happen.

Proof/test commands (GitHub Actions at the actual PR head):

```bash
cd formal
lake build
lake env lean Conde1963/AxiomAudit.lean
```

Historical source facsimile was **not reinspected in this slice**.
Source identification, wording and lineage were read from the versioned
research matrix, blob SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7`.
The original historical `Evidence.lean` / 154-proposition ZIP and
its independent custody hashes remain unavailable: historical import
**NOT_RUN**.


## Historical note (superseded physical-role semantics): 241 documentary occurrences

The **pinned** 2026-11-11 matrix has 238 distinct numeric IDs but **241
actual Markdown evidence rows**. C44, C45 and C46 each occur twice with
*different meanings*. Neither deduplication nor arbitrary renumbering is
acceptable. `Conde1963/MatrixEvidence.lean` retains every exact tuple
`(labelNumber, occurrence, matrixLine, physicalRole)`, so each item links
to the primary research *matrix* at pinned commit
`38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`
(blob `a7978c3a75a153b16ab70118a92c434bba674cb7`).

Each occurrence is a **traceability record, not a proven measurement**.
The precise Markdown row and its original described verification/lineage
remain intact in the source matrix. The JSON export preserves each entire
row and its section, with a SHA-pinned citation and an explicitly unverified
status for **new primary-source inspection in this run**:

```bash
python3 formal/scripts/evidence_registry.py \
  --check formal/Conde1963/MatrixEvidence.lean \
  --json /tmp/conde-evidence-contracts.json
cd formal
lake build
lake env lean Conde1963/AxiomAudit.lean
python3 -m unittest discover -s tests -v
```

The `conde-evidence-contracts` JSON artifact from GitHub Actions is a typed
handoff to 🦫 Castor for joining documentary rows to any independently
verified physical inputs. It contains **241** unambiguous citations and
source text, with no invented coordinates, timestamps, TLEs or probabilities.

Of those 241 entries, **239 are `contextOnly` for terminal-state
physics**, meaning *not yet mapped to a justified orbital predicate*, not
false or unimportant documents. C131 and C197 cite the **same NASA catalogue
day**; both are `scenarioOnly`, not admitted physical measurements.
`every_row_is_nonphysical_without_additional_premises` proves that
documentary indexing alone does not filter a candidate trajectory,
`matrix_does_not_force_nasa_reported_day` gives a synthetic off-day
countermodel, and `full_matrix_does_not_identify_region` rejects
identifying a unique site from these inputs. None of this establishes
that other records could never constrain a calibrated physical model.

Promoting further rows requires a separate evidential review: direct
inspection of an original, instrument/epoch/units, lineage, quantitative
mapping with errors, nonempty and reduced feasible domain, coupled physical
simulation with holdouts, and a new reviewed Lean predicate. Documentary
date is not impact date; a recorded decay is not a crater. Results
`CONDE_EXCLUDED`, `CONDE_FORCED`, `OTHER_WINDOW`,
`INDETERMINATE` or `CONTRADICTORY_PREMISES` remain conditional
classifications, not claimed findings here.

**Negative results:** full original Lean ZIP (`Evidence.lean`, 154
propositions / 151 labels and generator) remains unavailable; import
`NOT_RUN`. No original 1963 facsimile was reinspected for this registry;
historical source authentication `NOT_RUN`. Physical orbit holdouts and
ground-impact determination `NOT_RUN`. CI validates ID preservation,
regression logic, generated contracts and conditional proof kernel only.


## 🐙 Interactions between evidence (issue #15; conditional proofs)

`Conde1963/Interactions.lean` distinguishes a **second citation** from
a **second discriminating constraint**. Its machine-checkable definition
`StrictReduction` requires (1) a surviving parameter solution,
(2) containment in the original feasible domain and (3) one **explicitly
excluded** formerly admissible solution. The counterexample criterion
`witnessed_filter_strictly_reduces` formalizes the minimum mathematical
evidence needed to establish actual reduction. The witnesses in a real
application must come from a calibrated numerical model with uncertainty
bounds and independent dated observations, not hypothetical coordinates.

- The NASA day in [C131](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502) and [C197](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905) is one publication, not two positional observations. `nasa_double_citation_not_strict` rules out pretend reduction by duplication.
- The Tupi/FBIS story [C01](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L19), crater dimensions (C02), ground geology (C44 occurrence 1) and conditional penetration estimates (C46 occurrence 1) could be **coupled** only after primary physical measurements and a demonstrably calibrated material/impact model. These rows are *not yet* accepted terminal-state filters.
- The secondary launch catalog and derived orbital discussion (C139–C141), plus the **unexecuted** coupled-model proposal (C142), could constrain a shared-dynamics hypothesis **only** if the different objects' epochs and original element custody are verified, the RAAN 198.5261°/284.1520° conflict resolved and the model survives a withheld 529 holdout. A second object is not a second independent source when its catalog descends from shared tracking. No joint filter is admitted at present.
- Independent witnesses or documents do not by themselves imply stronger physical narrowing; `non_admitted_source_does_not_narrow` prevents speculative hypotheses from silently entering a selected scenario. If impact paths in and out of Conde both survive, `contrary_impact_witnesses_refute_decisive_conde` blocks forced/excluded conclusions. Contradiction or no survivors is not a false proof of a place.

**Source provenance:** these cross-links reuse the pinned matrix (Git blob
`a7978c3a75a153b16ab70118a92c434bba674cb7`), not a new facsimile
inspection. NASA's 15 Nov 1963 *Satellite Situation Report*, p. 8,
NTRS 19640001198, supplies only a **published catalogue date** here.
The equality between that date and physical decay remains a
`scenarioOnly` hypothesis and is NOT an admitted hard filter.
C44–C46 have two distinct meanings each and require occurrence-specific
provenance. No verified terminal state, uncertainty bound, ground impact
or historical Lean `Evidence.lean` archive was added by this module.


## 🐙 Simulator ↔ Lean bridge: source audit and conditional proof obligations

### Source code examined (read only, not re-run against 1963 data)

The actual legacy simulator under the [pinned scientific foundation](https://github.com/franklinbaldo/conde-incident/tree/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b)
contains `src/lib/astrodynamics.ts`, `monteCarlo.ts`,
`inverseSolver.ts`, `constants.ts` and `norad528_reconstruction.py`.
`formal/scripts/simulation_bridge_audit.py` pins their *real Git blob
SHA-1 values* and checks 10 known source patterns. It fails if a file drifts
without an explicit renewed review. This is a **static code inspection**:
passing does not validate SGP4, JavaScript execution, physical accuracy, or
any orbital hypothesis.

The legacy `propagateState(528)` gate stops after
`1963-11-08T23:59:59Z`, although C131/C197 cite only the **NASA catalogued
day**, not an observed terminal UTC instant. Other legacy limitations:

- Synthetic phase and hardcoded RAAN 284.152° in `monteCarlo.ts`, versus
  the mirror-derived 198.5261° in [C179](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L839).
  Reported sampling frequencies must not be labeled historical probabilities.
- `computeGroundTrackWithUncertainty` constructs illustrative envelopes
  and a `sigmaKm` from **assumed growth formulas**, not calibrated
  statistical coverage. The terms are an exploratory visualization.
- `computeInterTrackProximity` can substitute illustrative positions on
  absent points, including `distanceToCondeKm: 0`; `bracketingVerdict`
  contains an unsupported certainty claim. Neither constitutes a
  physically validated corridor around NORAD 528.
- `computeInversePasses` explicitly marks an SGP4 closest approach as
  **unvalidated**, not a terminal observed pass.

The more physical model is in **Castor's draft [PR #5](https://github.com/franklinbaldo/conde-incident/pull/5)**,
inspected at commit
[`3074ae0f`](https://github.com/franklinbaldo/conde-incident/commit/3074ae0f014ce33a2c81dacb2a7400f92f4a4359).
Its `orbitPhysics.ts` supports coupled osculating Cartesian r/v (km, km/s),
central gravity, J2 and explicit source-supplied co-rotating atmosphere and
`Cd*A/m`; it brackets the model's chosen descending altitude threshold.
`orbitConvergence.ts` and `orbitEnergyAudit.ts` assess step-halving and
Jacobi-like drag-work budgets. `orbitAdmissibility.ts` samples *bounded
scenario boxes*, and `orbitHoldoutAudit.ts` explicitly guards against
numerical ranking reversals on withheld data. These are **more meaningful
numerical contracts**, not automatic historical calibration. Its types
still report `NOT_RUN`/`NOT_VERIFIED` for historical holdouts,
authenticity, independent observations and rigorous error enclosures.
Nothing from Castor's unmerged branch was copied or modified here.

### What enters Lean

`Conde1963/SimulatorBridge.lean` adds a `SimulationAudit` typed gate:
`HistoricallyAdmissible` requires a coupled Cartesian model, authentic
dated source/epoch/frame, blind independent holdout, quantified numerical
error and calibrated forces. `GroundImpactAdmissible` additionally
requires a distinct ground-impact event and validated material survival.
Theorems show that a synthetic terminal phase, unvalidated SGP4 baseline,
failed custody/holdout, or a *chosen atmospheric threshold* cannot meet
these obligations merely by arithmetic or by declaration.

The exact mathematical part independently checkable today is limited:
`countWithin_monotone` and `cumulative_radii_monotone` certify finite
sample counts at radii 50/100/250/500 km; **they imply no posterior**.
`scaled_drag_power_nonpositive` proves a signed-power algebraic invariant
in exact integer-scaled variables corresponding *only to the sign* of
Castor's `-500 rho (Cd A/m) ||v_rel||³` power when those factors are
nonnegative. It is **not** a formal verification of RK4, the real-number
force law, density measurements or the program's execution.

### What flows back to Castor

GitHub Actions exports `conde-simulation-bridge.json` alongside the
existing 241-entry `conde-evidence-contracts.json`. Every code finding
has a pinned source URL, Git blob SHA, related matrix IDs and a
`blocking_limitation`, while the Castor adapter describes the exact
source head and validation prerequisites. Physical results, time,
coordinates and probability deliberately remain **null/NOT_RUN**.
Until original Cartesian observations, explicit units/epoch, calibrated
drag, holdout and numerical error are verified, neither script nor Lean
permits an evidence-backed claim that Conde is forced or excluded.

Repeat the gates on the **actual PR head**:

```bash
python3 formal/scripts/simulation_bridge_audit.py --root . --json /tmp/conde-simulation-bridge.json
cd formal
lake build
lake env lean Conde1963/AxiomAudit.lean
python3 -m unittest discover -s tests -v
```

**Source provenance:** the NASA/Goddard original publication of
15 November 1963, printed p. 8,
[NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf),
is represented by C131/C197, two references to one record; its facsimile
was not re-inspected in this engineering slice. C25/C179–C185 from a
Space-Track-derived mirror share tracking ancestry and are not fresh
independent 1963 radar measurements. The ZIP archive
`Evidence.lean` with 154 propositions/151 labels and custody digests
is still **NOT_AVAILABLE / import NOT_RUN**.
