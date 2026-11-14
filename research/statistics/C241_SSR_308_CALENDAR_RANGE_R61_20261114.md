---
type: Experiment
title: "C241 R61: faixa impressa NASA 29–30 outubro e teste de H fixo do 308"
description: "Reavaliação condicional da hipótese de dia civil do NORAD 308 sem promover catálogo a observação terminal"
experiment_id: C241-SSR-308-RANGE-R61
verification_status: PENDING_CI_CONDITIONAL_PROXY
---

# R61: intervalo civil impresso muda o teste, não a identificabilidade terminal

A fonte contemporânea NASA/Goddard *Satellite Situation Report*, vol. 3, nº 24, de 15/12/1963, p. impressa 15, linha `A OMEGA 1 | US | 18 JUN | 29-30 OCT 63`, contém **dois dias civis impressos**. Fac-símile [NTRS 19640003479](https://ntrs.nasa.gov/citations/19640003479), SHA-256 `d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f`, manifesto [C241-L64](../tle_custody/nasa_ssr_terminal_control_308_C241-L64.md). A identidade Omega 1 → 1962-024A → NORAD 308 vem de crosswalk **secundário**; o número 308 não está impresso no documento.

## Desenho congelado

O experimento [R60](C241_1963_ARCHIVE_FIXED_H_STRESS_20261114.md) usava, contrafactualmente, a data secundária de 30/10/1963 como um dia UTC. Preservam-se exatamente suas quatro origens deduplicadas selecionadas antes dos cortes de 14, 10, 6 e 3 dias, os dois estimadores de secante, a linhagem e o hash do Parquet. Não recalcular origens a partir do resultado novo. Para cada intervalo `[L,U)` do parâmetro auxiliar H, com magnitude de decaimento local `v>0`, reinterpretar a faixa impressa de 29 a 30 como a **união** dos dois dias hipotéticos: `[max(0,L-v), U)`. Essa transformação é algebricamente válida somente quando o intervalo original inteiro tinha largura `v`, verificada pelo auditor.

Testar uma translação de relógio comum de ±24 h com o certificado exato de R58 e, em separado, translações independentes de ±1 dia, aplicando neste último caso a velocidade `v`, **não** a largura `2v` da faixa alargada. Todos esses relógios são cenários de estresse, não conversões de fuso verificadas.

O resultado permanece apenas compatibilidade ou incompatibilidade **da aproximação local H constante sob convenções de calendário postuladas**. O documento não fornece hora UTC, instrumento, incerteza, observação de reentrada, massa nem longitude de impacto. Duas datas impressas não são duas medições nem dois holdouts; não são autorizadas likelihood, posterior de massa, estimativa de erro horário ou restrição espacial para Conde.

## Execução, evidência e limiares

`python3 tools/c241_308_ssr_calendar_range_r61.py --r60 /tmp/c241-1963-fixed-h.json --ssr research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json --output /tmp/c241-ssr-308-range-r61.json`

O workflow `c241-1963-terminal-control-screen.yml` mantém a descarga do Parquet 1963 pinado, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, a produção do R60 e os controles negativos. Acrescenta replay R61, testes normais e otimizados, inspeção do schema e ausência de valores inferenciais. Não há teste preditivo calibrado, MCMC histórico é `NOT_RUN` e `active_constraint_528=false`.

Próxima evidência discriminante: registro primário ligando explicitamente NORAD 308 a Omega 1 e observação terminal com época, referencial temporal, estação/sensor e censura documentada. A mera faixa editorial não satisfaz esses requisitos.
