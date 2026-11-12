# Head-SHA integration gate (🐘 Elefante)

**Scope:** GitHub repository `franklinbaldo/conde-incident`; no changes to the personal blog, no deploy trigger, and no scientific observation added.

## Problem and verification target

As inspected on 2026-11-12, `main` at `eee7851d29e7bafa38ebcb36cab9da9dfa2f2afb` contains no `.github/workflows/` directory. The scientific pipeline proposal [#28](https://github.com/franklinbaldo/conde-incident/pull/28) had no PR workflow runs or commit statuses in the linked GitHub API. A review of its methodology by 🦅 Gavião explicitly withheld approval without a CI check. Its safe integration is blocked despite being independent of the scientific site branches.

## What this PR provides

`.github/workflows/integration-head.yml` runs on push and pull request, checks out **the actual PR head SHA** rather than GitHub's synthetic pull-request merge commit, and asserts the checked-out SHA. The web job installs the exact Bun lockfile, runs TypeScript and Vite build, and executes every `scripts/*.test.mjs` suite currently present. It explicitly reports that no such test suite exists when absent; it must never claim these tests passed if they did not exist.

The Lean job runs `lake build` when both the Lean toolchain file and Lake project manifest exist under `formal/`; it fails on a partial `formal/` directory and explicitly reports Lean absent otherwise. It uses the package's pinned Lean version, rather than accepting a floating version. This does **not** independently establish the historical truth of any assumption used in a theorem.

The workflow grants only `contents: read` and has **no Pages deployment permissions or actions**. Its own Node regression tests reject loss of exact-head validation or accidental addition of Pages write access. This is deliberately a cross-branch integration gate, not a replacement for the full scientific simulation/holdout CI or the editorial preview-build pipeline.

## Evidential status and limits

- Source: `main` at the SHA above, `AGENTS.md`, PRs [#1](https://github.com/franklinbaldo/conde-incident/pull/1), [#3](https://github.com/franklinbaldo/conde-incident/pull/3), [#28](https://github.com/franklinbaldo/conde-incident/pull/28), and GitHub Actions commit-run/status queries. **Direct repository/API inspection**, not an external historical observation.
- This test checks the PR head; it does **not** establish that the branch merges cleanly with an advancing `main`. Before integrating any other PR, confirm independent Gavião review, conflict resolution, and fresh CI for its final head.
- Scientific sequence: independently verified original → stable occurrence in the cumulative matrix (PR #1) → conditional Lean restriction → nonempty narrowed admissible domain → reproducible physics/holdouts → new evidence. This CI does not substitute for any one link of that chain.
- Pages source must separately be confirmed as GitHub Actions; then verify a successful `push/main` deploy **and** live HTTPS response for the exact published SHA. No such confirmation is asserted here. Do not merge this CI PR merely because its own check passes; independent Gavião review still applies.

## Next integration question

Can this isolated CI bootstrap be reviewed and merged first so the independent workflow in `main` evaluates scientific PR #28's **current** head? After that, can #28 get Gavião's final conditional-science signoff and reduce the documentation→Lean→simulation gap without mistaking compiled implications for empirical orbit reconstruction?
