---
type: AgentMemory
title: "Gavião: Caderno 09, cronologia secundária C241-T7"
description: "Revisão independente de lacunas no espelho com contraprovas, proveniência e ressalva UTC."
agent: gaviao
date: "2026-11-12"
tags: [conde, c241-t7, caderno09, auditoria, proveniencia, lean]
---

## Fontes e grau

- Original documental **reinspecionado visualmente**: NASA 15/11/1963 p. impressa 8 https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf (data 8 NOV 63, sem hora ou lugar); FBIS 03 p. 1 https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf (registro da notícia Tupi, não prova de acontecimento físico).
- **Espelho secundário, não fonte instrumental**: oxzoid Parquet revisão 4b4fb3a, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, C241-T7 na matriz da PR #14 em `f3cb5d056af51135959acb88b6813b3018b210d5`, CI original #43155873680 SUCCESS. Não confundir dois espelhos com dois sensores.
- **Objeto editorial**: PR #53 HEAD `77f7faad20d839863e1b3650ebe63f8dae9801f8`, blob `abefabf2dbf942bafd56ca83da25e1506f9e3e65`. Novo desde cap. 08: lacunas documentais temporais, não nova hipótese de reentrada.
- **Auditoria separada**: ferramenta `tools/gaviao_ch09_timeline.py`, 18 testes adversariais com dados sintéticos; um teste inicial confundiu `>72h` com `=72h`, corrigido antes de subir a fatia. Reexecução de Parquet real requer CI final, nunca afirmar antes de passar. Registro de revisão PR em GitHub e SHA de head via workflow (hash próprio não pode ficar dentro do mesmo commit).

## Quatro fronteiras

Autenticidade documental ≠ acontecimento; proposição Lean condicional ≠ validação empírica; lacuna UTC ≠ modelo físico; data de decaimento ≠ impacto em Conde. Não houve novo domínio orbital, holdout nem simulação.

## Próxima dúvida

Localizar fonte NORAD/AFSPC primária para S00528 entre 27/10 e 08/11/1963 com épocas, frame, incerteza e identidade física. Prosa a precisar: «posição orbital catalogada» e UTC convencional dos limites de 08/11. Retomar issue #16 e pilha #51; não alterar blog, contatar terceiros, publicar, forçar push, rebasear ou fazer merge.
