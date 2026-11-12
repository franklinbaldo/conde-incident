# Conde Incident: agent operating contract

Scope: **franklinbaldo/conde-incident only**. The separate blog is read-only; do not publish or alter it. Do not contact archives, researchers or individuals without specific authorization.

## Decisão arquitetural editorial: SSG em Rust (11/11/2026, substitui Zola)
- O proprietário escolheu **SSG**, crate Rust `ssg` ([documentação](https://docs.rs/ssg/latest/ssg/)), para gerar o **Caderno de histórias e as páginas estáticas do Conde** a partir de Markdown com frontmatter YAML e templates MiniJinja. A decisão anterior por Zola foi revogada; **não** introduzir um pipeline Zola paralelo.
- Preservar o aplicativo científico React/Vite sob `/conde-incident/lab/`; a saída estática do SSG fornece a navegação para Evidências e Caderno. Reconciliar as PRs #1 e #3 sem perder nenhuma seção.
- A versão SSG é pré-1.0: fixar **versão exata** no workflow GitHub Actions, verificar o CLI efetivamente instalado no job e testar `ssg check`/`ssg build`/`ssg audit` com sintaxe conferida em `ssg --help`, sem supor compatibilidade entre atualizações.
- GitHub Pages deve publicar **somente após merge/push em `main`**. Em PR, apenas build e verificações. Validar todos os capítulos, links, assets e subpath `/conde-incident/`, e confirmar fonte Pages por GitHub Actions e deployment público real no SHA de `main`; nunca declarar publicação sem isso.
- Uma história nova por PR apenas com avanço verificável desde a anterior, fonte e grau de certeza, revisão independente do 🦅 Gavião e CI verde no SHA definitivo. 🦉 Coruja mantém os artigos e a migração editorial na PR #3; 🦊 Raposa mantém a navegação, apresentação e integração com o laboratório. Não modificar o blog pessoal.

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
