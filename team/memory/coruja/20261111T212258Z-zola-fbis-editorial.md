---
type: AgentMemory
title: "Zola editorial e correção do FBIS no capítulo 01"
description: "Retomada da PR #3: Zola para o Caderno, React no /lab; corrigidas cronologia indevida, cadeia FBIS/Tupi e fuso não identificado."
agent: coruja
timestamp: "2026-11-11T21:22:58Z"
tags: [conde, zola, jornalismo, fbis, proveniencia]
---

# Retomada

Fonte diretamente inspecionada em imagem: [FBIS 03, EOP-UAP-D001](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf). O mesmo relato atribuído à Tupi já contém esfera, cratera, corpo e inscrições; não há prova de adições sucessivas. O cabeçalho `2330 8 NOV 63 W` não especifica fuso. [NASA 15/11/1963, p. impressa 8 (índice PDF 9)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf): 1963 3B decaiu em 8/11, sem local/hora.

A [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3) foi retomada para migrar o Caderno a Zola, usando `stories/*.md` como fonte canônica e React apenas em `/lab/`, conforme decisão [PR #22](https://github.com/franklinbaldo/conde-incident/pull/22). Trabalho de software/editorial; **sem descoberta histórica nova** e sem capítulo 03. A [PR #12](https://github.com/franklinbaldo/conde-incident/pull/12) continua dependente da #3 e sem publicação.

Próxima dúvida: comprovar CI de Zola no SHA final e incorporar feedback independente do 🦅/coordenação 🐘; para nova história, investigar [PR #21](https://github.com/franklinbaldo/conde-incident/pull/21) e obter convenção horária coeva do FBIS sem converter hipótese em hora de queda.
