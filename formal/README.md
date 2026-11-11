# Lean 4: Conde 1963

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


## 🐙 Documentary day restriction: C131/C197 (11 November 2026)

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
