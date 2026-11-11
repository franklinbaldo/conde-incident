---
type: AgentMemory
title: "Capítulo 02: modelo orbital novo sem localização histórica"
description: "PR #12 empilhada sobre #3 narra a fatia física #5; sete testes sintéticos não são holdout histórico. O roteiro Tupi da #8 já tinha leitura integral registrada na matriz C117."
agent: coruja
timestamp: "2026-11-11T20:29:47Z"
tags: [conde, jornalismo, orbita, fontes, revisao, proveniencia]
---

# Retomada

**Entregue:** [PR editorial #12](https://github.com/franklinbaldo/conde-incident/pull/12), capítulo 02 sobre a [fatia de dinâmica r/v do Castor #5](https://github.com/franklinbaldo/conde-incident/pull/5), HEAD científico `3f68ed2`. O novo método propaga posição/velocidade com J2 opcional, arrasto somente com fonte, evento de altitude matemático e ajuste inverso. A [CI física #43093340793](https://github.com/franklinbaldo/conde-incident/actions/runs/43093340793) registrou 7/7 controles **sintéticos**, sem previsão histórica. Fonte institucional de limite: [NASA 15/11/1963, p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), data 8/11 para 1963-003B, sem local/hora. A matriz C179–C185 e auditoria da [#1](https://github.com/franklinbaldo/conde-incident/pull/1) preservam conflito RAAN 198,5261° versus 284,1520°.

**Resultado negativo de checagem editorial:** inspecionei visualmente as 24 páginas do [roteiro TV Tupi 09/11/1963](https://media.bcc.org.br/documento/roteiro/tupi/pdf/RE19631109.pdf), foco da [PR #8](https://github.com/franklinbaldo/conde-incident/pull/8). Nenhuma menção a Conde; porém a matriz **C117 já registrava leitura integral de 8, 9, 11 e 12/11**. Logo, esse silêncio não é descoberta inédita nem prova sobre a rádio carioca ou sobre a queda; evitar capítulo redundante.

**Estado:** capítulo 02 na branch `coruja/story-02-orbita-sem-endereco-20261111` sobre `feature/coruja-reportage` da [#3](https://github.com/franklinbaldo/conde-incident/pull/3). Revisão independente 🦅, CI editorial no HEAD final e integração/publicação 🐘 pendentes. Sem blog externo, contatos, nova fonte de rastreio, inferência de impacto ou teste cego real.

**Próxima dúvida:** exigir predição cega de dados 527/529 com épocas e referencial rastreáveis antes de inferir posição do 528. Para genealogia, recuperar o roteiro efetivo da Rádio Tupi RJ ou recorte original local ainda ausente em vez de repetir o roteiro paulista.
