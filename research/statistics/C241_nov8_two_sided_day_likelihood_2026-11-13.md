---
type: Experiment
title: "C241: janela probabilística de 8 de novembro com incerteza antes e depois"
description: "Verossimilhança temporal bilateral da data NASA, com três cenários não calibrados, aplicação ao Monte Carlo e distribuição espacial sem corte artificial em 9/11."
experiment_id: C241-NOV8-TWO-SIDED-20261113
verification_status: CONDITIONAL_REPORTING_ERROR_NOT_HISTORICAL_POSTERIOR
---

# Dia 8, com erro nas duas pontas

A [fonte NASA C197#1, SSR de 15/11/1963](https://ntrs.nasa.gov/citations/19640001198), página impressa 8, reporta que o objeto 1963 3B decaiu em **8 NOV 63**. O documento não apresenta hora UTC de reentrada, desvio-padrão dos sensores, intervalo de confiança, regra de classificação da data ou evidência de chegada de material ao solo. O [ledger C197](../constraints/nasa_528_decay_precision_C197_20261113.json) mantém isso explícito. A fonte não garante que sua classificação se refira ao calendário UTC: este é um cenário declarado.

## Formulação

O rótulo é um **dia civil inteiro**, não um instante central em meia-noite. No cenário UTC, dia 8 = [1963-11-08 00:00Z, 1963-11-09 00:00Z). Supondo apenas para análise um erro gaussiano aditivo simétrico de escala sigma, a verossimilhança de um evento terminal em instante t é:

[
L_{\sigma}(t)=
\Phi\!\left(\frac{t_{\rm fim}-t}{\sigma}\right)
-\Phi\!\left(\frac{t_{\rm início}-t}{\sigma}\right).
]

Não é um corte duro: um evento real antes do dia 8 ou depois do dia 8 possui peso positivo. Sob **prior temporal plano e hipotético**, a densidade normalizada equivale à convolução do uniforme durante o dia 8 com uma normal de média zero, centrada em 8/11 ao meio-dia. Não equivale a uma posterior histórica, pois falta modelo calibrado do erro da NASA e da seleção de observações.

## Sensibilidade obrigatória

| Erro hipotético sigma | Antes de 8/11 | Durante 8/11 | Depois de 8/11 |
|---|---:|---:|---:|
| 6 horas | 9,97% | 80,05% | 9,97% |
| 12 horas | 19,52% | 60,95% | 19,52% |
| 24 horas | 31,56% | 36,87% | 31,56% |

Não afirmar que sigma=6, 12 ou 24 horas seja erro medido, muito menos que a data catalogada seja data observada de impacto. A simetria é uma escolha de modelo; uma regra catalográfica de atraso sistemático poderia exigir distribuição assimétrica. A antiga prova Lean de 7/11 a 8/11 está **condicionada a outra hipótese específica**, não deve truncar o mapa probabilístico atual.

## Ligação com mapa e Monte Carlo

O módulo [catalogDayLikelihood.ts](../../src/lib/catalogDayLikelihood.ts) calcula a verossimilhança e normaliza probabilidades em qualquer grade espacial, usando peso **da data em relação ao registro**, nunca a distância de Conde. A célula C recebe probabilidade condicional de cenário igual à soma dos pesos das trajetórias que nela chegam dividida pela soma de todos os pesos. O mesmo módulo reporta tamanho efetivo numérico da amostra e bloqueia modelo sem sigma fornecido.

O [Monte Carlo exploratório](../../src/lib/monteCarlo.ts) agora calcula automaticamente três **tabelas de sensibilidade**, mantendo separadas as contagens brutas e as frequências ponderadas. Os raios 100, 500 e 2.000 km em torno de Conde são somente critérios espaciais para sumarização; qualquer grade quadrada pode usar a função geral de ponderação. A [interface](../../src/components/MonteCarloVisualizer.tsx) exibe a distribuição bilateral e a frequência condicionada a 500 km para cada cenário, com aviso explícito de que não representa probabilidade histórica.

**Limite científico muito importante:** o Monte Carlo legado amostra parâmetros e fases arbitrários e contém uma RAAN não autenticada. Reponderar esse conjunto melhora a lógica da janela temporal, mas não conserta sua dinâmica, não fornece covariância NASA/NORAD nem probabilidade de fragmentação ou impacto. O cenário continua probabilidade condicional de um modelo exploratório. Para aplicar a janela à deposição efetiva no solo precisamos ainda de modelo de ablação, sobrevivência de material, tempo e deslocamento entre reentrada e impacto/deposição.

## Verificação

    node --import tsx --test tests/catalogDayLikelihood.test.mjs
    npm run lint

O workflow próprio executa testes e auditoria de fonte no HEAD exato. O [certificado JSON](../constraints/C241_nov8_two_sided_day_likelihood_2026-11-13.json) preserva as distinções epistemológicas e alternativas. Não derivar número de probabilidade histórica de Conde a partir da simples etiqueta NASA.

**Estado:** probabilidade temporal de cenários definida e reprodutível; sigma NASA **desconhecido**, posterior histórica de queda e mapa de impacto **não identificados**.
