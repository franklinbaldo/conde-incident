---
type: MemoriaOperacional
title: Taxonomia do caso Conde
date: 2026-11-11
agent: Gaviao
---

# Encerramento da rodada OKF

Fontes normativas: AGENTS.md e team/gaviao.md na main, issue #16 e PRs #18/#23/#27. A matriz cumulativa continua na PR #1.
O projeto franklinbaldo/okf-parser v0.48.2 documenta init --infer-schema --write, check --require-spec --normative-spec e schema --format json.
Bootstrap no GitHub Actions run https://github.com/franklinbaldo/conde-incident/actions/runs/43118511883 PASS para o SHA 7db63b36bff4e6442163a2e786436799409a8c76; gerou 17 specs e 17 SQL no commit d1074beb822115da569aba5435243c4727519b80.

## Limites e tentativas

- O uv tool run no Jatoba excedeu o orcamento de memoria; a execucao foi transferida deliberadamente para GitHub Actions.
- Primeiro workflow falhou em sintaxe de permissions; corrigido antes do PASS.
- PDF NASA/FBIS, ZIP historicos e calculos orbitais nao foram reexecutados. Metadados vistos no GitHub usam VERIFIED_REPO; afirmacoes declaradas pelas PRs, REPORTED_REPO; hipotese HYPOTHESIS; execucao ausente, NOT_RUN.
- C240/C241 seguem em conflito entre as branches #20 e #25, sem renumeracao automatica.

## Proxima duvida

Como migrar a matriz por ID global e SHA de origem sem duplo registro de testemunhas?

## Links

- Catalogo: ../../knowledge/index.md
- Registro de Rodada: ../../knowledge/records/rodada-20261111-bootstrap.md
- Branch: gaviao/okf-taxonomy-20261111

