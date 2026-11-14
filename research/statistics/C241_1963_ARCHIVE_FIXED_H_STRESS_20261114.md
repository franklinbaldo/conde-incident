---
type: Experiment
title: "C241 R60: quatro controles de data secundária desafiam H fixo"
description: "Experimento retrospectivo com cortes e deslocamentos de calendário, sem calibração temporal"
experiment_id: C241-1963-ARCHIVE-FIXED-H-STRESS-R60
verification_status: SECONDARY_CALENDAR_DAY_CONDITIONAL_PROXY
---

# R60: quatro falsificações condicionais e uma não estimabilidade

Este experimento reutiliza quatro pistas secundárias do R59, e não medições instrumentais. Fonte: [Parquet 1963 pinado](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09, uma linhagem documental. Os rótulos [292](https://keeptrack.space/satellite/00292), [308](https://keeptrack.space/satellite/00308), [565](https://keeptrack.space/satellite/565), [668](https://keeptrack.space/satellite/00668) não comprovam horário UTC, sensor ou independência do catálogo. Seleção retrospectiva após consultar datas; nenhum holdout cego.

**Contrato:** origens em 14/10/6/3 dias antes da meia-noite UTC hipotética do dia anunciado; selecionar estritamente épocas pré-corte. Avaliar separadamente secante das últimas duas épocas e mediana das três últimas secantes. Colapsar cortes repetidos que usem a mesma origem. Para cada origem, converter vida terminal hipótese em intervalo necessário de altura efetiva H pelo proxy King-Hele linearizado. Testar a interseção positiva desses intervalos, com deslocamento comum do relógio em [-24,+24] horas ou deslocamentos independentes por corte em [-1,+1] dia. Essas hipóteses não representam estimativa de fuso ou erro histórico. Um certificado negativo rejeita exclusivamente a aproximação com H fixo e esta interpretação de dia.

## Resultado no Parquet pinado, sem inferência probabilística

| NORAD | Origens distintas | Relógio comum ±24h (últimas duas / mediana três) | Relógios independentes ±1d (últimas duas / mediana três) |
|---|---:|---|---|
| 292 | 4 | incompatível / incompatível | inconclusivo / incompatível |
| 308 | 4 | incompatível / incompatível | incompatível / inconclusivo |
| 565 | 3 | incompatível / incompatível | incompatível / incompatível |
| 668 | 4 | incompatível / NÃO ESTIMÁVEL | incompatível / NÃO ESTIMÁVEL |

No 565, cortes 14 e 10 dias selecionam a mesma última época e foram colapsados. Para o 668, a mediana não dispõe das épocas pré-corte suficientes, portanto **não** se usa apenas o subconjunto que couber. No 308, com últimas duas épocas, a folga negativa máxima sob relógio comum é -9,25 km de H proxy; nem deslocamentos independentes ±1 dia eliminam a lacuna de 4,25 km. Para 565, mediana de três, as lacunas são 19,50 km e 14,43 km respectivamente. Esses números são separações matemáticas de intervalos do proxy, **não** altitudes observadas, horas de queda ou erros físicos calibrados.

Os novos casos mostram que a aproximação local falha sob diversos cortes em mais objetos, enquanto especificam quais observações poderiam discriminá-la: horários/intervalos terminais instrumentais **independentes** para 292 e 308, época e fuso verificados, e elementos anteriores rastreados com incerteza e sensores identificados. Depois, congelar modelo físico e critérios de seleção antes de avaliar qualquer erro preditivo.

Reprodução: executar script c241_1963_archive_fixed_h_stress.py com --parquet /path/tle_1963.parquet --output /path/stress.json --check. Workflow R59 integra os testes, hash e mutante do corpus. MCMC histórico permanece NOT_RUN. Sigma horário, massa individual e probabilidade ou geografia de impacto permanecem null; active_constraint_528=false. Nada nesta análise restringe Conde.
