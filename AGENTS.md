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

## Catalogacao cientifica em OKF (proposta sujeita a PR)

Cada rodada deve catalogar **todos os fatos novos, duvidas, resultados negativos, fontes, contradicoes e decisoes** em conceitos tipados de `knowledge/records/`, vinculados a uma `Rodada` e a memoria OKF `team/memory/<animal>/`. Use a tipologia e as specs em `knowledge/index.md` e `knowledge/.okf/specs/`; novos tipos devem nascer pelo `okf-parser init --infer-schema` antes de serem usados normativamente. O campo `verification` deve refletir o que foi **efetivamente** consultado, e a matriz cumulativa mantem IDs sem renumeracao silenciosa. Replays, simulacoes e hipotese nunca substituem prova primaria. A adocao so sera normativa apos revisao/CI e integracao desta proposta.
