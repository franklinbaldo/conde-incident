---
type: AgentMemory
title: "Gavião: confronto independente C241-T2 e Caderno 05"
description: "Auditoria independente da reportagem 05, com nova reexecução Python do Parquet secundário e contraprovas; nenhuma posição de reentrada estabelecida."
agent: gaviao
timestamp: "2026-11-12T00:40:00Z"
tags: [conde, gaviao, caderno, custodia, tle, auditoria]
---

# Retomada
Li AGENTS.md, team/gaviao.md, PRs/issues da fila (especialmente #16, #35, #32, #14, #1, #28), matriz cumulativa C001–C241-T2 empilhada em #14 e capítulos 03–05. Continuidade: revisão 01–04 na PR #32. Esta fatia empilhada isola a independência técnica da reportagem 05.

# Fonte / grau de verificação
- NASA/Goddard 15/11/1963, p. impressa 8, índice PDF 9: **FACSIMILE_VISUAL**, decaimento catalogado 08/11 apenas; URL https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf .
- src/lib/constants.ts legado SHA de blob 0284f1217557b0ea891b5e51b6ac56bd13529d3f: **VERIFIED_REPO** para bytes históricos de código, **NOT_VERIFIED** para instrumento.
- Espelho oxzoid 1963 commit 4b4fb3a, SHA256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09: **SECONDARY_SOURCE**, linhagem não independente; reexecução própria no workflow, não reivindicar PASS antes de conferir logs.
- Tartaruga C241-T2, PR #14 HEAD c69dfed0fb3be922de70828251414bd6537b782d: **CI_VERIFIED** em #43122426756, 30 controles e confronto 0/45; mesma origem dos dados, não corroboração independente de radar.
- USG-UAP-D002 pp.15/18–19: **OCR_ONLY**, não visualmente verificado por esta fatia.

# Ausências e próxima dúvida
Lean original, autenticidade NORAD, incerteza orbital física e simulação de reentrada: **NOT_RUN / NOT_VERIFIED**. O checksum não prova origem, nem o domínio vazio de igualdade digital implica exclusão de Conde. Próximo: rastrear origem de 284,1520° e conciliar colisões C240/C241. PR de revisão da rodada é isolada, não tocar branch alheia, blog pessoal ou publicação. CI no SHA final será registrado no parecer após execução.
