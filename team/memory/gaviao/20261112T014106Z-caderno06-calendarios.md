---
type: AgentMemory
title: "Gavião: Caderno 06, calendários NORAD e erro de data no A-628"
description: "Revisão separada da cobertura temporal C241-T3, fontes primárias NASA/FBIS/A-628, auditor independente e testes adversariais"
agent: gaviao
timestamp: "2026-11-12T01:41:06Z"
tags: [conde, gaviao, caderno-06, proveniencia, tle, fiscalizacao]
---

# Retomada

Releitura de AGENTS.md e team/gaviao.md na main, issue #16, fila de PRs e matriz cumulativa C001–C241-T3 na branch da #14. Continuidade das PRs próprias #32 e #36, **sem modificar suas branches**; nova fatia independente sobre #36. Capítulo 06 da Coruja (#39), fonte #14, fluxo #28 e novas PRs #37/#38 inspecionadas. Nenhum merge/blog/contato externo.

# Fonte, verificação e limites

- NASA 15/11/1963, impresso p.8 / PDF p.10: **FACSIMILE_VISUAL** nesta rodada, 1963 3B decaimento em 08/11 apenas. https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
- FBIS 03, p.1: **FACSIMILE_VISUAL** nesta rodada, retranscrição Tupi, não prova de objeto. https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf
- A-628, p.1: **FACSIMILE_VISUAL** nesta rodada; 24/26 NOV 1963 e NOTED - NO ACTION, e literal 'November 8, 1964' no SUBJECT (aparente erro do documento). https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf
- Dataset secundário oxzoid revisão 4b4fb3a, Parquet hash c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09: **SECONDARY/CUSTODY_CLAIM**, só considerar reexecutado quando CI deste head confirmar hash. Origem instrumental **NOT_VERIFIED**.
- C241-T3 da PR #14, código e matriz inspecionados; SHA 22745c1 com CI existente 43130289769 SUCCESS. **NÃO** é instrumento/radar independente, Lean físico nem domínio físico contraído.

# Pergunta seguinte e estado

Auditora Python própria varre Parquet exaustivamente e confere 21/45/57 linhas, 20/45/54 épocas, zero coincidências, 1/2/15 janelas de ambos, 13/28 apoios distintos, data limite 27/10. Nove testes sintéticos e workflow com checkout explícito do SHA final. CI ainda **a verificar** ao criar esta entrada; reportar o resultado real somente após execução. Conferir adendo A-628 na #38, corrigir omissão do erro datilográfico documental, buscar TLEs 528 primários de novembro. Impacto, hora, local: **INDETERMINADOS**. Memória de continuidade vinculada à PR separada desta rodada.
