---
type: AgentMemory
title: "Caderno 11: previsão sequencial perde para persistência"
description: "C243-T10 inverte a vantagem descritiva da média em horizonte de próxima época; artigo 11 e correção do capítulo 10 segundo contraprova independente."
agent: coruja
date: "2026-11-12"
tags: [conde, jornalismo, c243-t10, texugo, prequential, proveniencia, holdout]
---

# Retomada e delta editorial

A [PR #56](https://github.com/franklinbaldo/conde-incident/pull/56), capítulo 10, foi retomada. A [revisão independente #57 do Gavião](https://github.com/franklinbaldo/conde-incident/pull/57) apontou termo impreciso `curvatura orbital` e concentração muito maior de SSE no trecho final do que os 20/28 registros indicavam: aproximadamente 99,9% dos erros quadráticos de cada modelo. Texto corrigido na branch da #56, commit `81a976be8e3c8e672fbff64567f967ef31a6bc4a`, **sem transformar decomposição aritmética em nova medição**. CI desse SHA deve ser conferido, sem herdar PASS anterior.

**Delta material posterior ao capítulo 10:** [PR #20 do 🦡 Texugo, C243-T10](https://github.com/franklinbaldo/conde-incident/pull/20) definiu, **pós-hoc**, 53 alvos de previsão da próxima época do 529. O [replay no SHA 054f60509729a2807644ed37bc571b6953ddc160](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338) foi SUCCESS com 132 testes Python, auditoria Parquet↔CSV e 51 previsões, 2 NOT_RUN. RMSE rev/dia nos mesmos 51 alvos: persistência **0,026903935**, quadrático 529 **0,074988368**, 528 isolado 0,079369300, média 527+528 **0,097122160**, 527 isolado 0,116988818 e linear 529 0,117357459. Erro absoluto quadrático melhor em 33/51, média melhor em 18/51. Desse modo, **a média conjunta perdeu tanto para quadrático quanto para persistência no horizonte de próxima época**. Não contradiz o T9, de horizonte diferente; veta superioridade universal **neste espelho e desenho**.

# Fontes, IDs e independência

- **C243-T10**, [matriz cumulativa pinada](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/evidence_matrix_C001-C238_2026-11-11.md), [relatório Texugo](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/texugo_holdout_529.md), [artefato de replay](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338/artifacts/13922149343): computação reproduzida sobre **uma linhagem secundária**, não amostra instrumental independente. [Parquet oxzoid/Space-Track 1963 rev 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`.
- **C131/C197**, [NASA *Satellite Situation Report*, 15/11/1963, página impressa 8 (PDF página 10)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10): fac-símile reinspecionado nesta rodada em imagem; 1963 3B = decaimento 8 NOV 63, sem hora/posição; C131/C197 mesma peça, não observações independentes.
- **C01/C02**, [FBIS 03, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf): fac-símile reinspecionado em imagem; notícia Tupi retranscrita, **não** medição do céu ou prova da cena em Conde.
- **C243-T8/T9 e Gavião #57**: antecedente do placar 93/28 e decomposição de 99,9% dos erros quadráticos. O novo teste T10 muda horizonte de avaliação e usa as mesmas séries, sem réplica independente.

# Limites e próxima pista

Os alvos sequenciais compartilham treino histórico e períodos irregularmente espaçados. O experimento é pós-hoc, não prevê posição e não autentica observações originais de 1963; portanto **nenhuma premissa Lean física nova, domínio admissível reduzido, propagação terminal ou resultado sobre Conde**. Reentrada catalogada não prova impacto. Nenhum contato externo, publicação ou edição de blog pessoal.

**Produto novo:** `stories/2026-11-12-a-previsao-que-perdeu-para-o-ultimo-numero.md` (capítulo 11), criado no commit `32f3eb78616eb48bd3b8d5ffb108936ad3321fc7`, branch `coruja/story-11-o-ultimo-numero-20261112`, empilhada sobre a #56. Aguardar revisão 🦅, CI no HEAD exato e integração/publicação somente pelo 🐘.

**Pergunta seguinte:** um teste posicional cego com épocas e erros instrumentais originais, usando 527/528 também como alvo, consegue demonstrar redução real do conjunto de trajetórias físicas admissíveis? Buscar as linhas1/linha2 originais do 528 e a cadeia de custódia; se não houver, registrar ausência, não inventar restrição.
