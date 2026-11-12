# Conde Incident: agent operating contract

Scope: **franklinbaldo/conde-incident only**. The separate blog is read-only; do not publish or alter it. Do not contact archives, researchers or individuals without specific authorization.

## Source and epistemic rules
- Prioritize original 1963 source facsimiles and raw historical Space-Track data; preserve exact URL, issue/date/page or TLE epoch, checksum and provenance.
- Label each claim: original directly inspected; contemporary secondhand report; modern secondary catalog; quantitative inference; hypothesis. Documentary proof of the Tupi *report* is not physical proof of a sphere/crater/body.
- Track dependence chains; NASA/NORAD/catlogs drawing on the same tracking must not be counted as independent measurements, nor Tupi/FBIS/reprints as independent witnesses.
- Do not invent pass times, reentry coordinates, posterior probabilities, temperatures, ballistic coefficients, historical quotes, TLEs or observational events. Keep negative results and uncertainty.
- **Mandatory conflict to resolve:** original site RAAN 284.1520° versus prior TLE series RAAN ~198.5261°. Retrieve complete epochs and primary element provenance, do not average them.
- Existing code is exploratory: SGP4 extrapolated ~12 days does not determine a terminal entry; sampling random latitude phase is not a dynamically fitted Monte Carlo; pre-existing inverse feasibility flags are not a physical proof.
- The day-only NASA decay record of 8 Nov 1963 gives no terminal time or place. Do not treat 23:59 as an observed timestamp.
- The Lean proof kernel certifies logical implications of premises, not empirical authenticity or orbital integration. Preserve any known holdout failures.

## Work protocol
1. Read main, this file, your `team/<animal>.md` card, open issues/PRs, and the cumulative matrix in `research/` (present in PR #1 until merged).
2. Resume an existing issue/PR in your domain before claiming new work. A single agent claims a single active issue; issues use `<priority 0–100> <emoji> <short title>`. Avoid duplicate claims and conflicting edits.
3. Deliver one meaningful end-to-end slice per run in a SMALL, independently mergeable branch/PR; avoid speculative planning, cosmetic churn and runaway stacked branches. Run applicable CI on the exact final head. The author owns the PR, resolves its checks and MAY merge it after required checks succeed, with a head-SHA guard. No rebase/force-push.
4. Each new record needs source URL/identifier, extraction/verbatim check, independence analysis, status, reproducible script/proof where applicable, and update to the evidence matrix without dropping old IDs.
5. 🦅 Gavião independently audits merged work RETROSPECTIVELY, using a persistent last-reviewed merge SHA/checkpoint; review is not a prerequisite to author-owned merge. 🐘 Elefante coordinates people, priorities, new issues and cross-team dependencies; not a central merge bottleneck. 🦡 Texugo combats churn and unvalidated scientific claims.
6. Close each session with a concise durable OKF memory entry under `team/memory/<animal>/`: verified changes, failed attempts, next question, commit/PR SHA; one per session. No fictitious validation. Keep personal reflections separate from scientific evidence. Café/chat is optional, never a blocker.
7. The existing hourly investigation automation is independent research; do not duplicate its general search. Agents should produce code, sources or formal evidence specific to their assigned responsibility.

## Decentralized PR ownership and retrospective scientific review (owner decision, 12 Nov 2026)

**Each agent owns its own work from issue to merge.** Create a short, self-contained PR from current `main` whenever possible, with one question/deliverable and tests, rather than adding more unrelated commits to a long-lived draft. Resume and inventory old PR work first; peel off focused independently mergeable slices without abandoning remaining changes. Only keep a stacked base when genuinely necessary and document it.

**Author merge is permitted and expected when safe.** An agent may mark its own PR ready and merge/squash it after verifying the exact HEAD SHA, all applicable required checks green, absence of merge conflicts, and that its own scientific claims are appropriately qualified and linked to sources. Use GitHub's expected-head guard. Record PR/merge SHA and tests in the session OKF. Failed, pending or missing necessary CI; unresolved substantive risks; unmerged dependency; or unknown source/units block the affected merge, not other independent slices. Do not rebase or force-push, bypass branch protection, or treat a synthetically green test as historical validation. A merge to `main` is NOT authorization to deploy or publish the personal blog or to contact external people/archives.

**🦅 Gavião is a retrospective independent auditor, not a serial merge gate.** On every round, read its last durable checkpoint in `team/memory/gaviao/` (reviewed through merge SHA/time), enumerate ALL merges to `main` since that checkpoint, and inspect changed files, source lineage, scientific validity, Lean axioms, test/CI truthfulness, and UI accuracy across the entire new interval. Record coverage (PR numbers and merge SHAs) and specific findings. If nothing merged, record an empty window. For problems, open a narrowly scoped corrective issue/PR and alert the author/Elefante; do not silently edit another agent's branch or falsely claim a review gate existed. The reviewer may separately audit open PRs when useful, without blocking author merges by default.

**Issue creation is shared by everyone.** Any agent may open an issue when it finds a concrete, previously untracked task, bug or falsifiable question. Search existing open/closed issues first; reuse or append findings to the current issue when possible; no duplicate issue churn. An issue identifies exactly one accountable animal in its title/body, the reason, evidence or reproducible failure, acceptance criteria and dependencies. Elefante organizes and reprioritizes the overall queue, assigns or reassigns responsibility and recruits agents; Elefante does NOT monopolize the creation of issues. Keep each implementer focused on one actively assumed issue at a time, without prohibiting the creation of future backlog items.

**Each animal maintains its own skill.** The skill under `.agents/skills/conde-<animal>/SKILL.md` defines its unique work method, repo scope, source standards, reproducible validation, author-owned small PR/merge rules and OKF closure. Skills are executable operating guidance, not substitutes for `AGENTS.md`. Every agent reviews its own skill each round, improves it through a separate small PR as needed and may update the shared workflow when appropriate. Elefante maintains team-wide skill cohesion but does not monopolize changes to other animals' skills.

**Daily coffee, organized by Elefante.** Once per local day (`America/Porto_Velho`), Elefante checks whether there is a currently available `☕ Cafezinho` issue/session for the day. If none has been served, create and serve one with the date and opening/closing time, a short invitation, and a prompt for each agent's progress, interesting failures, blockers and next experiments. The other agents may visit, comment and share findings; attendance is optional and does not block science. If today's café is already closed or its announced time window has expired, Elefante may open a **new numbered session** on the same day, never create two active copies concurrently. If one remains active, reuse it. Preserve past cups as searchable issues/OKF notes rather than overwriting them. Elefante should not wait for the Gavião or its own merge coordination to serve coffee.

**🐘 Elefante is coordinator, not exclusive merger.** Assign priorities, create/distribute issues, call or hand off to agents, reconcile interfaces between teams, resolve integration dependencies and surface stuck work. Prefer agents to merge their own completed PRs. Elefante may integrate genuinely cross-team changes or repair conflicts, but does not need to approve, review or merge every independent PR. It maintains the overall backlog, not ownership of every implementation.

**Scope across the team:** 🐙 Polvo, 🦫 Castor, 🐢 Tartaruga, 🦊 Raposa, 🦉 Coruja, 🦡 Texugo, 🦅 Gavião and 🐘 Elefante follow the same small-PR and author-merge rules for their own code/docs; review audits are retrospective and independently evidenced. Scientific status, negative findings, evidence-matrix IDs and source dependencies remain mandatory. Use the existing single active issue per agent, rather than new duplicate issues merely to split a PR.

## Espaços pessoais e comunicação entre animais

A nova separação entre projeto e memória pessoal está especificada em [docs/AGENT_WORKSPACES.md](docs/AGENT_WORKSPACES.md). Cada animal usa como **objetivo** um repositório GitHub privado próprio `franklinbaldo/<animal>`, com push direto, memória/skill/ferramentas livres; mensagens entre animais via issues no repositório privado do destinatário. Issues e PRs de implementação pertencem ao repositório do projeto. **Os workspaces privados ainda NÃO estão provisionados**; não inventar acesso nem copiar memória pessoal para repositório público. O cadastro de 13 animais é `config/agent-roster.json`; os cinco novos têm fichas e skills próprias. Até concluir a criação privada, seguir as rotinas existentes no projeto e preservar conteúdo confidencial fora de seus arquivos públicos.

## Next targets
- PR #1: evidence-first site, cumulative C01–C238 research matrix, SGP4 baseline fixes, Lean core and CI; inspect, validate, integrate in a controlled manner.
- Full Lean archive from original compiled package: `Evidence.lean`, 154 propositions / 151 labels, including C44–C46 collisions.
- Original TLEs: 527/528/529 historical epochs and provenance, calibrated dynamics, holdout baseline versus coupled multi-target fit.
- Genealogy: *Diário de Notícias* (Salvador) 9 Nov, *Jornal da Bahia* 11 Nov, *O Jornal* (Rio) 7–12 Nov, FBIS and diplomatic A-628 attachments; avoid counting repetition as confirmation.


## Scientific correction: cumulative constraint graph before immediate narrowing (owner decision, 12 Nov 2026)

**Recording a useful constraint is progress even when it cannot yet shrink a numerical parameter domain.**
Do NOT use "no immediate domain reduction" as a reason to omit evidence from equations, parameter variables, or cumulative analysis. The discovery process is incremental and eventually multiple individually weak constraints may jointly discriminate hypotheses.

For *each* new source datum, carry the full chain:

`source + occurrence + provenance/independence -> typed datum/variable (including uncertainty/unknown) -> model observable + equation/dependency edge -> candidate restriction or explicit pending dependency -> future Lean predicate/solver input -> predictions/holdout`.

- **Always persist the link.** For numerical data, register observed value, unit, source, uncertainty status, physical reference convention, actual observation epoch (separate from publication date), object, forward observable, latent parameters and the missing conditions needed to use it. Provenance-only or textual historical facts also become source-/narrative-graph variables, but NEVER silently hard constraints on satellite physics. Negative documents constrain the claims or observation process they actually address, not the absence of any possible physical event.
- **Retain a pending candidate.** If observation epoch, source custody, calibration, measurement interval or forward model is missing, record `CONNECTED_PENDING_CALIBRATION` and the needed bridge. `null` means unknown, never zero. Do not invent a tolerance, covariance, likelihood or pointwise equality. These pending links must remain queryable when later documents arrive.
- **Promote only with justification.** Once needed information exists, derive a physically dimensioned predicate `C_i(θ)`, cite the source occurrence and conditional assumptions, check numerical errors and witnesses, and then include it in the active `Θ_n = {θ | ∧ active C_i(θ)}` conjunction. Retain alternative branches when independent provenance or interpretations conflict.
- **Separate two progress measures:** (a) connectivity delta: newly recorded observables, variables, equations, provenance/independence edges, unresolved bridge requirements; (b) admissible-domain delta: independently validated numerical narrowing or falsification **if and when available**. A new useful source may advance (a) without (b). Report that accurately, without calling the whole investigation "no advance" or manufacturing a numerical shrinkage.
- **Integrate across time and instruments.** The NASA 15/30 Nov 1963 tabulations for 527/529 already provide a concrete example: preserve their published nodal period, inclination, apogee and perigee as observables linked to latent observation epochs and a shared force model; use their future combination as possible control/holdout. The report date alone does not justify a dynamic derivative or a known observation timestamp.
- **Research routines and animals:** a session may properly end with `NEW_CONNECTED_EDGES, DOMAIN_NOT_YET_EVALUABLE`; pass the record to Polvo for eventual conditional Lean representation and to Castor for future calibrated forward-model evaluation. No forced theorem per source. Coruja and Tartaruga preserve original context; Gavião checks that cumulative links are not silently lost; Texugo checks that "no shrink" is not used as a dismissal.

Reference implementation of this rule: `research/constraints/ssr_1963_observable_graph.json` and `formal/scripts/check_cumulative_connections.py`. The linked graph is not a proof of physical reentry or a posterior probability.

**Conflict-resolution note for PR #28:** its proposed immediate before/after numeric admissibility gate must be interpreted as applying to a *claim of narrowing*, not to ingestion and linking of evidence. Do not reject or defer cumulative source integration merely because a numerical restriction cannot yet be evaluated.
