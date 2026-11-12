---
type: AgentMemory
title: "🦊 Ablação da falsa precisão no resumo inicial"
description: "Resumo documental, IDs/Lean e propostas sintéticas rastreáveis, metadados cautelosos, salto de teclado"
date: 2026-11-12
agent: raposa
repository: franklinbaldo/conde-incident
issue: 9
pr: 24
verification: final_ci_pending
---

## Fontes e observação no código

- Li integralmente AGENTS.md e team/raposa.md na main, consultei issue #9, PRs #1/#3/#24/#28/#37/#43 e as memórias anteriores. Retomado HEAD 3eea5fb5026a158c113fcf05f66830d5f8027f8b da PR #24.
- Matriz cumulativa C001-C238 consultada na PR #1, commit 38ee0f01134f6a1ee07c9346945d058d2ad3ce0b: C01/C02 constituem uma cadeia Tupi-FBIS; C197-C202 registram o dia NASA 08/11/1963, sem hora/local; C44-C46 são IDs reutilizados e há conflito RAAN. Não houve nova inspeção de fac-símiles nem observação orbital.
- Problema confirmado por inspeção do código: apesar das correções no mapa, ExecutiveSummary.tsx (rota inicial padrão) ainda mostrava 19h48 UTC, chance ~0,006%, conclusão de impacto compatível, números balísticos não validados e frases de veredito/confirmado. index.html anunciava uma reconstrução orbital quantitativa, sugerindo validação inexistente.

## Fatia e verificações

- Refeito o resumo inicial com três cadeias rastreáveis (C01/C02, C197-C202, RAAN), links permanentes à aba Evidence, matriz e Lean condicional SHA-pinned. Situação científica agora explicitamente indeterminada, sem hora/local/probabilidade fictícios.
- Links a #37 e #43 fixados em SHAs para contratos algébricos/simuladores de domínios e cenários TLE alternativos; estas PRs continuam não integradas, com testes sintéticos, e não validam intervalos físicos ou exclusão geográfica. Link ao holdout 529 não o transforma em observação.
- HTML do laboratório ganhou idioma PT-BR, description, canonical e OG conservadores. Botão de saltar ao conteúdo move foco sem usar fragmento de URL reservado às rotas. Adicionados quatro testes Node de regressão científica, IDs/links, metadados e foco compatível com roteador. O workflow existente verifica Node, TypeScript/Vite, Zola e HTML.
- Grau de verificação: fontes e código INSPECIONADOS, SHA final e CI após a escrita deste cartão ainda PENDENTES. Teclado real, leitor de tela, mobile, Lean físico integrado, holdouts, publicação Pages: NOT_VERIFIED. Nenhum modelo físico, texto jornalístico, blog pessoal, captura histórica, contato externo, merge, rebase ou force-push.

## Próxima dúvida

Revisar as telas legadas de inversão/Monte Carlo/sensibilidade, que podem continuar confundindo saídas de modelos com observações, sem modificar o núcleo numérico. 🦅 revisão independente; 🐘 integração de #1/#3/#24 somente com CI no SHA integrado e revisão.
