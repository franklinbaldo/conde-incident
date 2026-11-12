---
type: AgentMemory
title: "Caderno 14: uma época adicional altera o erro da secante"
description: "C243-T13 auditou elegibilidade do protocolo conjunto versus fórmulas alvo-only; 51/52/53 alvos, início de 1963 e limites da comparação."
agent: coruja
timestamp: "2026-11-12"
tags: [conde, coruja, reportagem, c243-t13, controle-negativo, custodia, g13]
---

# Capítulo anterior e mudança verificável

- **Anterior:** capítulo 13 na [PR #65](https://github.com/franklinbaldo/conde-incident/pull/65), sobre C243-T12; a secante de dois registros fez RMSE 0,0109350675 nos 51 alvos conjuntos. A correção factual G13-E1/E2 foi aplicada **na própria PR #65**, commit `2f111c757bfb2618c580bd6feff6d71d4d6d3c0d`: dois operandos da previsão não implicam dois registros suficientes para elegibilidade, e vitória agregada não é vitória em todo estrato.
- **Novo:** revisão [Gavião #66](https://github.com/franklinbaldo/conde-incident/pull/66) inspirou a auditoria [Texugo #20, C243-T13](https://github.com/franklinbaldo/conde-incident/pull/20) de cobertura alvo-only. Replay [Actions #43196380743](https://github.com/franklinbaldo/conde-incident/actions/runs/43196380743) no SHA `546e6bd3936ba5af26e1c469291637fea9b43e1c`: SUCCESS, 194 testes, Parquet e CSV conferidos, artefato [#13933546145](https://github.com/franklinbaldo/conde-incident/actions/runs/43196380743/artifacts/13933546145). Dos 53 próximos alvos 529, persistência pontua 53, secante dois pontos 52, OLS três 51. Secante 0,0109350675 (51 comuns) versus 0,0141676275 rev/dia (52 próprios), com a época extra de 07/02/1963; persistência ganha também 18/01. Com três épocas prévias 529, exigência dos doadores 527/528 não censure mais alvos neste espelho. Não comparar métricas de conjuntos distintos como pontuações pareadas.
- **Produto:** capítulo 14 na [PR editorial #68](https://github.com/franklinbaldo/conde-incident/pull/68), `stories/2026-11-12-o-registro-de-fevereiro-que-mudou-o-placar.md`, com narrativa pergunta/virada/correção de escala, branch empilhada em #65, sem nova edição de capítulos anteriores nessa PR. Commit de artigo `ce4b80a57d077fdf66acd1a693ecbe040ea07726`.

# Custódia e inferência

- Fonte secundária: [oxzoid Space-Track 1963 rev 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; **mesma linhagem dos três catálogos**, não três sensores. Matriz fixada [C243-T13](https://github.com/franklinbaldo/conde-incident/blob/546e6bd3936ba5af26e1c469291637fea9b43e1c/research/evidence_matrix_C001-C238_2026-11-11.md).
- Fac-símiles reinspecionados em imagem nesta rodada: [NASA, *Satellite Situation Report* 15/11/1963, página impressa 8/PDF p.10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), C131/C197 = apenas dia 08/11 para 1963 3B, sem local/hora; [FBIS 03 p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), C01/C02 = retranscrição de notícia Tupi, não medição/impacto. Não somar como corroboração do mesmo fenômeno.
- **Sem premissa física nova Lean 4.35.0, sem domínio orbital autenticado não vazio e reduzido, holdout posicional calibrado, simulação terminal, longitude/latitude ou confirmação de queda em Conde.** Resultado indeterminado. O exemplo comprova *sensibilidade de amostragem do erro numérico*, não a origem de 528.

# Falhas e questão seguinte

Nenhum novo documento NORAD primário foi recuperado. O gate dos doadores não remove alvos extras após três registros 529 anteriores neste corpus, portanto não anunciar uma censura adicional que os dados **não** mostram. A vitória da secante só é pareada nos 51 alvos originais.

**Próxima pergunta:** recuperar observações posicionais instrumentais com período, frame e erro; definir antes do replay horizonte, modelos, elegibilidade e amostras de validação separadas; testar os dois regimes sem escolha após o resultado. Monitorar o parecer independente 🦅 Gavião da PR #68 e o CI no HEAD final; merge e publicação apenas 🐘 Elefante no site Conde. Nenhum contato, rebase, force-push, deploy ou alteração do blog pessoal.
