---
type: AgentMemory
title: "Gate conservador de domínios admissíveis"
description: "Fatia do Elefante: interseção racional exata, proveniência declarada e contraprovas; nenhuma localização inferida."
agent: elefante
timestamp: "2026-11-12T01:12:01Z"
tags: [conde, admissibilidade, lean, proveniencia, integracao]
---

# O que foi feito

O proprietário priorizou redução de parâmetros não identificados após fonte → matriz → Lean → restrições → modelo físico e holdout. A main ainda mantém a base antiga. A PR #28 define o fluxo, mas o Gavião registrou ausência de CI no SHA `2a3a429936802234e5c1522f610e54460d9b0786`. A PR #1 tem correção C197 pendente; a #3 recebeu LGTM editorial condicional à reconciliação com #1. Fonte: [#28](https://github.com/franklinbaldo/conde-incident/pull/28), [#1](https://github.com/franklinbaldo/conde-incident/pull/1), [#3](https://github.com/franklinbaldo/conde-incident/pull/3).

Criado neste branch o `scripts/audit-admissible-domain.mjs` com interseção de intervalos racionais exatos; recusa províncias inventadas, falsa independência e status Lean PASS não testado. `tests/admissible-domain.test.mjs` contém 15 casos adversariais. `research/ADMISSIBLE_DOMAIN_GATE.md` documenta limites. Nenhuma entrada real do NORAD 528 foi fabricada. O tool reporta `NOT_VERIFIED` Lean, `NOT_RUN` holdout, `NOT_INFERRED` local.

## Grau de verificação / limites

Revisão sintática e testes no GitHub Actions do SHA final desta PR **pendentes** no momento do registro. O script não autentica fonte, não compila Lean nem roda a física. Reentrada não é impacto. O endpoint de Pages não foi acessível pelo conector; workflow Zola ainda fora da main; deploy NOT_VERIFIED.

## Próxima pergunta

Após CI e revisão do Gavião, conectar o contrato a restrições derivadas de documentos efetivamente inspecionados e provas Lean compiladas, com domínios reais, intervalos correlacionados e holdouts sem vazamento. Priorizar correção C197 e o conflito C240/C241 antes de integrar matrizes.
