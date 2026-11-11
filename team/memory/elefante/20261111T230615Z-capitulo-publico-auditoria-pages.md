---
type: AgentMemory
title: "Pages: validar capítulo publicado, não só link no índice"
description: "A auditoria pós-deploy passa a visitar o capítulo Zola e exigir corpo e referência ao Markdown; contraprovas passam, mas deploy segue não verificado."
agent: elefante
timestamp: "2026-11-11T23:06:15Z"
tags: [conde, zola, pages, publicacao, auditoria, contraprova]
---

# Fatia verificada

Retomei [issue #6](https://github.com/franklinbaldo/conde-incident/issues/6) e [PR #7](https://github.com/franklinbaldo/conde-incident/pull/7). A versão anterior de `scripts/check-pages-release.mjs` verificava apenas um caminho datado na listagem Zola; poderia aprovar uma listagem que apontasse para um capítulo inexistente. Em `3c647bc1dc5fbf14bf66d4b4f22c524f650e3fee`, a auditoria extrai o `href` canônico sob `/conde-incident/stories/`, faz GET da reportagem e exige HTTP 200, `full-story`, `story-body` e referência ao Markdown-fonte. A listagem não pode usar host externo como capítulo de primeira parte. O parser admite permalink absoluto Zola ou caminho local seguro.

[GitHub Actions #43117069713](https://github.com/franklinbaldo/conde-incident/actions/runs/43117069713), no SHA `3c647bc1dc5fbf14bf66d4b4f22c524f650e3fee`, executou **16 testes PASS e 0 FAIL**, incluindo quatro novas contraprovas/aceite. A etapa de deploy real ficou **SKIPPED** em `pull_request`, como previsto. Este registro acrescenta um commit; o CI no novo SHA deve ser reconfirmado antes de qualquer integração. Gavião ainda não revisou independentemente a #7.

# Fila e limites

Na `main` `eee7851d29e7bafa38ebcb36cab9da9dfa2f2afb` ainda não há `.github/workflows/pages.yml` nem Zola. A [#3](https://github.com/franklinbaldo/conde-incident/pull/3), HEAD `c84cce85e51252f9e589a851950385aea008e951`, migrou a publicação para Zola e teve comentário independente favorável do Gavião, mas continua Draft. A [#1](https://github.com/franklinbaldo/conde-incident/pull/1), HEAD `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`, ainda não recebeu aprovação científica global; a matriz C197 contém divergência de índice PDF apontada pela revisão. A matriz C01–C238 foi lida da branch #1, sem nova evidência histórica.

Fonte Pages via Actions: **NOT_VERIFIED** porque o endpoint `/pages` foi rejeitado pela conexão. O site público foi tentado sem resposta verificável. Nenhum workflow de `push/main` com deployment exitoso foi demonstrado; portanto **PUBLICADO: NOT_VERIFIED**. Os testes usam fixtures e demonstram falhas fechadas, não a existência de publicação. Não foi alterado blog pessoal, nem houve contatos ou novas observações orbitais.

**Próxima dúvida:** o Gavião confirma a nova comparação de link/listagem/template na #7? Após correção e revisão global #1, como reconciliar Zola/#3 com laboratório científico sem perder Evidências, e como aferir fonte Pages, deployment e HTML reais no SHA pós-merge?
