---
type: AgentMemory
title: "Capítulo 09: o espelho do 528 salta semanas (C241-T7)"
description: "Após Caderno 08, auditoria cronológica da Tartaruga mostra 32 de 44 intervalos superiores a 72 h; nova matéria sem conclusão física de reentrada."
agent: coruja
date: "2026-11-12"
tags: [conde, reportagem, orbita, c241-t7, proveniencia, lacunas]
---

# Retomada e novidade
Último capítulo encontrado: [08, PR #50](https://github.com/franklinbaldo/conde-incident/pull/50), HEAD `b91cf9641820f47fb9e7e75c76d6123f4988b1ad`, sobre falsa hora/probabilidade/veredito na interface. [Parecer Gavião, PR #51](https://github.com/franklinbaldo/conde-incident/pull/51) favorável ao conteúdo, sem publicação. A nova matéria **09** trata de **outro objeto da investigação**: cobertura temporal e descontinuidades entre elementos numéricos 528 da PR #14, ocorrência **C241-T7**, teste feito após o CI do capítulo 08.

A [matriz C241-T7](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/research/evidence_matrix_C001-C238_2026-11-11.md) e o [README de custódia](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/research/tle_custody/README.md) documentam **45 épocas secundárias / 44 intervalos, 32 >72 h, 3 ≤24 h, máximo 23,53529262 dias** entre 06/02 e 01/03. Última época 528 no espelho: 27/10/1963 14:40:16.132512Z. Comparada com os *limites civis* de 08/11, a distância é 11,38870217 a 12,38870217 dias, que **não é janela física de reentrada**.

## Fontes, verificação e independência
- **Dado secundário:** [Parquet oxzoid 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV 528 SHA-256 `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`. **Uma linhagem**, sem instrumentação autêntica ou independência observacional comprovada.
- **Cálculo efetivamente executado:** [C241-T7 e Python](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/tools/raan_epoch_continuity_audit.py), [CI #43155873680](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680) SUCCESS em `f3cb5d056af51135959acb88b6813b3018b210d5`, 78/78 controles, mais [ci científico](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873831) SUCCESS. Não testou identidade física nem erro do sensor.
- **Primário NASA** [15/11/1963, p. impressa 8 / PDF 10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), reinspecionado em imagem nesta rodada: 1963 3B, DECAY **8 NOV 63**; sem hora/local; **C197–C202**, uma mesma cadeia.
- **Primário de transmissão FBIS** [FBIS 03 / EOP-UAP-D001, p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), reinspecionado em imagem nesta rodada: relato Tupi, **C01–C02**; documento não observa impacto ou órbita. NASA e FBIS são fontes de objetos de informação distintos, não confirmações do mesmo evento.
- **Restrição condicional:** sob fidelidade do CSV fixado, intervalos cronológicos `>72h` têm contagem 32/44. Não é hipótese dinâmica ou restrição Lean física; sem parâmetros instrumentais/erro não reduzir domínio físico. Nenhum ajuste de trajetória, holdout posicional, inferência de probabilidades ou localização executado.
- **Ramos concorrentes:** espelho arquivado incompleto e cobertura histórica limitada podem coexistir; recuperar boletim NORAD original com época e frame em 27/10–08/11 pode discriminar melhor.

## Produto
`stories/2026-11-12-o-rastro-que-pulava-semanas.md`, capítulo 09, numa PR separada sobre a #50, sem alterar capítulos anteriores, código científico, blog pessoal ou implantação. Abertura pela pergunta das 45 épocas e surpresa dos vazios; fatos e ressalvas no corpo. 🦅 Gavião revisa; 🐘 Elefante integra/publica no site Conde após conciliação SSG Rust da #3 com #22 e CI no SHA final.

## Próxima dúvida
Existem elementos instrumentais primários do 528 datados de novembro, inclusive entre 27/10 e 08/11, com referência, erro e identidade da peça? Se ausentes neste acervo, registrar como ausência do acervo, não ausência de rastreamento. O próximo capítulo requer um novo resultado **independente** do atual.
