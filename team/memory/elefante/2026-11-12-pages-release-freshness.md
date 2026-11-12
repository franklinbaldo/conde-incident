---
id: elefante-2026-11-12-pages-freshness
agent: elefante
date: 2026-11-12
scope: conde-incident
issue: 6
kind: integration-memory
status: proposed-not-merged
---

# 🐘 Gate de frescor do GitHub Pages, rodada 12/11

## Contexto de retomada

Lidos `AGENTS.md` e `team/elefante.md` da `main`, PRs/issues abertas,
matriz C01–C238 da PR #1, auditoria científica e fila editorial.
Retomada a pilha #7 → #33 → #46; nova fatia dependente da #46,
isolada em `elefante/pages-freshness-main-head-20261112`.
Não alterar branches da Coruja ou do Gavião.

## Mudança proposta, verificabilidade

O auditor podia aprovar um run/deployment de um SHA antigo
depois de a `main` avançar ou o Pages publicar uma versão mais nova.
Pior: um deployment anterior `success` no mesmo SHA podia mascarar
um novo deployment pendente; o mesmo se aplica a run de publicação
anteriormente verde seguido de falha no mesmo SHA.

A nova fatia confronta o HEAD da `main`, o deployment mais recente
do ambiente `github-pages` e o run mais recente
`Publish Conde site` no SHA auditado. Exige `success` no status
mais recente do **mesmo deployment atual**. Testes adversariais
cobrem avanço de `main`, deployment mais novo, status pendente,
run falho posterior e ausência de observação.

## Fontes e status

- Fonte de controle: APIs de [branches](https://docs.github.com/en/rest/branches/branches),
  [deployments](https://docs.github.com/en/rest/deployments/deployments),
  [status de deployment](https://docs.github.com/en/rest/deployments/statuses)
  e [runs](https://docs.github.com/en/rest/actions/workflow-runs).
- Grau de verificação: inspeção do código no SHA base
  `3106904594330815c27471d8b02835c1a6686edd` da PR #46;
  os testes são sintéticos, aguardando Actions do SHA final desta PR.
- Publicação externa: **NOT_VERIFIED**. Repositório principal ainda
  sem Pages implantado; PRs #1 e #3 continuam draft e dependem de
  reconciliação, #22 exige SSG Rust, #28 define fluxo científico
  mas ainda sem CI/merge. Nenhuma nova observação histórica foi criada.

## Dependências científicas mantidas

A matriz C01–C238 ainda está na PR #1, não na main. C197 requer
conserto do índice da página NASA; RAAN 284.1520° versus 198.5261°
segue conflitante. #14 cuida da custódia TLE 527–529, #17 do Lean
condicional, #20 dos holdouts, #5 do integrador físico,
#37 → #43 dos domínios alternativos. Não concluir impacto a partir
de reentrada; não combinar cenários TLE independentes sem custódia.

## Próxima dúvida

Após revisão independente de Gavião e CI verde no SHA exato,
integrar na sequência contratual, testar a correlação run↔deployment
e confirmar o Pages configurado para **GitHub Actions** com URL pública
efetivamente servida. Os metadados não fornecem checksum dos bytes
HTML do site; investigar atestação de artefato sem falso positivo.
