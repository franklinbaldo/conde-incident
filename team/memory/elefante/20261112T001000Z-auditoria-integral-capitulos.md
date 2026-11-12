---
type: AgentMemory
title: "Publicação exige verificar todos os capítulos Zola"
description: "Fatia empilhada sobre #7 fecha o falso positivo de capítulo posterior indisponível ou com Markdown errado."
agent: elefante
timestamp: "2026-11-12T00:10:00Z"
tags: [conde, pages, zola, revisao, evidencias]
---

# Observado e corrigido

Ao ler [#7](https://github.com/franklinbaldo/conde-incident/pull/7), encontrei um falso positivo: o auditor seguia somente o **primeiro** link datado de [#3](https://github.com/franklinbaldo/conde-incident/pull/3); um segundo capítulo indisponível não invalidava o resultado `PASS`. O template da [Coruja](https://github.com/franklinbaldo/conde-incident/blob/feature/coruja-reportage/templates/story.html) publica explicitamente fonte `stories/<slug>.md`. Por isso, nesta branch separada e empilhada sobre #7, alterei o verificador para inspecionar todos os cartões, permalinks e fontes correspondentes, acrescentei contraprovas para segundo artigo 404, ordem, duplicação, fonte incorreta e link externo, e documentei limite de 100 capítulos.

## Grau de verificação

**Inspeção estática de código:** realizada na #7 e nos templates da #3. **Testes no GitHub Actions do SHA final:** pendentes quando esta memória foi escrita; não afirmar PASS antes do run. **GitHub Pages source/deploy/site real:** NOT_VERIFIED, pois #1 e #3 ainda estão fora da main; consulta à API Pages neste contexto não teve permissão. **História e física:** nenhuma medição nova, nenhuma conclusão de impacto. SHA de trabalho antes desta memória: `b7eda4f1d781963e392e98a1758ef407566cddf7`.

## Próxima dúvida

Conseguir a revisão independente do Gavião, testar no HEAD final e, após publicação legítima, verificar cada capítulo real sem equiparar link disponível à autenticidade de qualquer afirmação. Em paralelo priorizar [#28](https://github.com/franklinbaldo/conde-incident/pull/28): ainda carece de run de CI, e a redução de parâmetros precisa exigir domínios não vazios, contraexemplos e limites físicos em vez de mera prova lógica condicional.
