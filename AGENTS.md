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

**🐘 Elefante is coordinator, not exclusive merger.** Assign priorities, create/distribute issues, call or hand off to agents, reconcile interfaces between teams, resolve integration dependencies and surface stuck work. Prefer agents to merge their own completed PRs. Elefante may integrate genuinely cross-team changes or repair conflicts, but does not need to approve, review or merge every independent PR. It maintains the overall backlog, not ownership of every implementation.

**Scope across the team:** 🐙 Polvo, 🦫 Castor, 🐢 Tartaruga, 🦊 Raposa, 🦉 Coruja, 🦡 Texugo, 🦅 Gavião and 🐘 Elefante follow the same small-PR and author-merge rules for their own code/docs; review audits are retrospective and independently evidenced. Scientific status, negative findings, evidence-matrix IDs and source dependencies remain mandatory. Use the existing single active issue per agent, rather than new duplicate issues merely to split a PR.

## Next targets
- PR #1: evidence-first site, cumulative C01–C238 research matrix, SGP4 baseline fixes, Lean core and CI; inspect, validate, integrate in a controlled manner.
- Full Lean archive from original compiled package: `Evidence.lean`, 154 propositions / 151 labels, including C44–C46 collisions.
- Original TLEs: 527/528/529 historical epochs and provenance, calibrated dynamics, holdout baseline versus coupled multi-target fit.
- Genealogy: *Diário de Notícias* (Salvador) 9 Nov, *Jornal da Bahia* 11 Nov, *O Jornal* (Rio) 7–12 Nov, FBIS and diplomatic A-628 attachments; avoid counting repetition as confirmation.
