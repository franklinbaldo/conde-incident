# Lean 4: Conde 1963

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
