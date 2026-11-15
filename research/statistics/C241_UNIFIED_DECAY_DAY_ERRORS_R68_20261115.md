---
type: Experiment
title: "C241 R68: tabela única de erros de dia do proxy King-Hele"
description: "64 linhas censuradas para NORAD 637, 292, 565 e 308 condicional, sem sigma horário"
experiment_id: C241-R68-UNIFIED-CENSORED-DAY-ERROR
verification_status: RETROSPECTIVE_CONDITIONAL_NOT_CALIBRATED
---

# R68: erro de previsão de dia, não distribuição calibrada

Pedido direto do 🐘 Elefante em [cervo#4](https://github.com/franklinbaldo/cervo/issues/4): consolidar, **sem inventar hora terminal**, as previsões já produzidas por [R54/#841](https://github.com/franklinbaldo/conde-incident/pull/841) e [R60/#924](https://github.com/franklinbaldo/conde-incident/pull/924). A equipe mantém a [fila canônica](../../docs/PRIORITIES.md); a frente #647 pertence ao Cervo, não à Tartaruga.

## Fonte e convenções

Os dois relatórios foram calculados sobre o mesmo **espelho secundário** de órbitas TLE de 1963, [oxzoid, revisão fixa 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), com SHA-256 integral c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. Não são sensores independentes. O 637 usa a data NASA 07/11/1963 (SSR de 15/11, p. impressa 8); 292 e 565 usam apenas pistas secundárias do KeepTrack de 26/11 e 24/11. O 308 usa pista secundária 30/10, sem converter o possível alias **OMEGA 1** da NASA de 1963 (29–30/10) em identidade instrumental provada. [NTRS SSR NASA](https://ntrs.nasa.gov/citations/19640003479), [KeepTrack 292](https://keeptrack.space/satellite/00292), [565](https://keeptrack.space/satellite/565), [308](https://keeptrack.space/satellite/00308).

**A tabela única é gerada como TSV e JSON nos artefatos do CI**, pelo script tools/c241_decay_day_error_r68.py, a partir dos JSONs R54 e R60 reexecutados no Parquet autenticado. Inclui 64 linhas objeto × método × corte × H = 40/50 km, quatro cortes por objeto, com 60 combinações distintas de origem/método/H. Dois cortes do 565 usam a **mesma origem**; as linhas duplicadas são marcadas como não independentes (new_distinct_origin=false). Métodos: última secante de duas épocas e mediana de três secantes anteriores ao corte. Cortes: 637 em 18, 23, 27 e 30/10; 292, 565 e 308 a 14, 10, 6 e 3 dias antes do rótulo secundário (00h UTC hipotética).

Defina erro como previsão menos instante real. **Somente no contrafactual** de que o dia impresso é um dia civil UTC, o instante real pertence a [D 00:00, D+1 00:00). Portanto, o erro pertence ao intervalo **(mín, máx]**: limite inferior aberto, superior fechado. São conjuntos de erro compatíveis com o rótulo, não intervalos de confiança nem σ instrumental. Sem confirmação do relógio e da semântica da data impressa, o erro histórico continua indeterminado.

## Amostra da tabela, última secante, primeiro corte de cada objeto

| NORAD | Dia publicado / classe | Corte UTC | H km | Previsão hipotética UTC | Erro em dias, (mín, máx] |
|---|---|---|---:|---|---|
| 637 | 07/11, NASA SSR | 18/10 | 40 | 08/11 19:25 | (0,809368; 1,809368] |
| 637 | 07/11, NASA SSR | 18/10 | 50 | 14/11 08:11 | (6,341339; 7,341339] |
| 292 | 26/11, secundária | 12/11 | 40 | 30/11 08:38 | (3,359786; 4,359786] |
| 292 | 26/11, secundária | 12/11 | 50 | 05/12 16:38 | (8,693229; 9,693229] |
| 565 | 24/11, secundária | 10/11 | 40 | 17/11 18:46 | (-7,218052; -6,218052] |
| 565 | 24/11, secundária | 10/11 | 50 | 20/11 20:42 | (-4,137233; -3,137233] |
| 308 | 30/10, **identidade OMEGA condicional** | 16/10 | 40 | 30/10 23:24 | (-0,024889; 0,975111] |
| 308 | 30/10, **identidade OMEGA condicional** | 16/10 | 50 | 03/11 23:24 | (3,975151; 4,975151] |

A faixa NASA **OMEGA 1, 29–30/10** é uma **alternativa documental de dois dias**, nunca um segundo holdout independente do 308. Sem crosswalk físico contemporâneo, o cálculo continua condicional. Os testes R57/R58/R60 mostram, no espaço de hipóteses declarado, ausência de **um único H constante** capaz de conciliar todas as origens com um deslocamento civil comum de ±24 horas. Isso testa a coerência interna de um proxy local, não falsifica a atmosfera real. Algumas linhas individualmente contêm erro zero; esse fato não conserta a incompatibilidade entre origens ou cria calibração.

## Reprodução e bloqueios científicos

No workflow de triagem histórica existente, executar R54 e R60 contra o Parquet conferido, gerar JSON + TSV R68 e verificar testes adversariais em Python normal e otimizado. Os testes rejeitam SHA trocado, vazamento de época pós-corte, promoção de data secundária, fuso inventado, origem duplicada inconsistente, taxa não positiva e erro em desacordo com a previsão. **Não** usar RMS, MAE ou estimativa de sigma horário sobre estas linhas correlacionadas e retrospectivas.

Contrato imutável de inferência: calibrated_terminal_holdouts=0, terminal_time_sigma_hours=null, historical_mcmc=NOT_RUN, active_constraint_528=false, impact_geography=null. Não há posterior de massa, probabilidade de queda nem restrição geográfica adicional de Conde. Próxima observação que mudaria o estado: instante/intervalo terminal independentemente atestado, sensor, escala temporal, convenção de decaimento e elementos pré-terminais sob protocolo de seleção congelado.
