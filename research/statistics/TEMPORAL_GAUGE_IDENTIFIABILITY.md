---
type: Guide
title: "🦌 Cervo: posto temporal e dois gauges de RAAN em C241"
description: "Observabilidade condicional de fases, deriva catalográfica e holdouts, issue #257, sem posterior histórica"
---

# Duas simetrias temporais: não são medidas de incerteza

**Estado: CONDITIONAL_EXACT_STRUCTURAL_ONLY.** Issue [#257](https://github.com/franklinbaldo/conde-incident/issues/257), continuação da [PR #244](https://github.com/franklinbaldo/conde-incident/pull/244). Nenhum sensor, órbita, TLE original, erro, prior ou observação de novembro de 1963 foi acrescentado. Entradas: o mesmo extrato secundário de uma única linhagem **C25#1, C179#1, C180#1, C181#1, C241-L3**, com 123 linhas brutas, quatro duplicadas e 119 épocas únicas (NORAD, UTC). O hash do parquet original é **declarado por extração anterior**, não revalidado aqui.

## Hipótese que testamos, não dinâmica orbital

Fixe uma função F_j(t) desconhecida, sem computá-la/calibrá-la, e considere apenas o desenho local da série circular:

    Omega_j(t) = wrap_360(F_j(t) + alpha_j + beta_j*tau + b + d*tau)

Para j=527/528/529, tau conta dias exatos desde 1963-01-01T00:00:00Z; alpha_j é fase; beta_j é taxa hipotética; b é zero angular comum do catálogo, *não verificado*; d é deriva hipotética deste zero. As transformações (alpha_j,b) -> (alpha_j+a,b-a) e (beta_j,d) -> (beta_j+c,d-c) preservam a predição no círculo em **todas** as épocas. Os dois vetores racionais nulos são (1,1,1,0,0,0,-1,0) e (0,0,0,1,1,1,0,-1).

A matriz usa só coeficientes conhecidos 0,1,tau e timestamps até microssegundos. **Não ajusta RAAN**, nem assume independência entre épocas. O posto racional é propriedade *local* do modelo aditivo com F fixada. Mesmo uma taxa estruturalmente identificável neste modelo não é deriva orbital física; wrapping de 360 graus pode introduzir **aliases globais**. Posto não prova identificabilidade de dinâmica física, precisão nem posterior.

## Resultado, inclusive retenção 527

Os blocos cronológicos estavam definidos **após inspeção**: não são cegos, e compartilham a mesma linhagem documental.

| Bloco | 527/528/529 | Offset constante, posto/7 | Offset e deriva livres, posto/8 | Âncora só fase 528, posto/8 | Duas âncoras, fase e taxa 528, posto/8 |
|---|---|---|---|---|---|
| Fit | 15 / 24 / 22 | 6/7 | **6/8** | 7/8 | **8/8** |
| Validação | 1 / 13 / 9 | 5/7 | **5/8** | 6/8 | **7/8** |
| Avaliação | 4 / 8 / 23 | 6/7 | **6/8** | 7/8 | **8/8** |
| Total | 20 / 45 / 54 | 6/7 | **6/8** | 7/8 | **8/8** |

**Duas nulidades** no ajuste: uma relativa ao zero absoluto e uma relativa à deriva documental livre. Uma âncora externa somente de fase quebraria apenas o primeiro gauge, uma de taxa apenas o segundo; para posto 8 no modelo de oito incógnitas seriam necessárias as duas **independentemente calibradas**, sem afirmar que existam. O bloco de validação contém apenas **uma época do NORAD 527**. Não separa sua fase e taxa nesse bloco, mesmo com duas âncoras hipotéticas em 528, portanto sobra uma nulidade. Com dados reais, relações adicionais podem surgir do operador físico do Castor, ainda ausente neste desenho.

## Custódia, teste e próximos elos

- Código: [raan_temporal_gauge.py](../../tools/raan_temporal_gauge.py), aritmética de tempo racional, dois gauges verificados, SHA-256 e checagem do manifesto via raan_lineage_identifiability.build_report.
- Replay imutável: [raan_temporal_gauge_C241.json](raan_temporal_gauge_C241.json). Testes adversariais: [test_raan_temporal_gauge.py](../../tests/test_raan_temporal_gauge.py).
- Grafo cumulativo: [raan_temporal_gauge_candidate_C241.json](../constraints/raan_temporal_gauge_candidate_C241.json) conecta fase, taxa, b, d, época, fonte, predição física e duas âncoras faltantes. active_constraint=false.
- Comandos: python3 -m unittest discover -s tests -p test_raan_temporal_gauge.py -v; python3 tools/raan_temporal_gauge.py --input research/statistics/raan_527_528_529_1963.json --split research/statistics/raan_chronological_holdout_1963.json --check research/statistics/raan_temporal_gauge_C241.json.

**Dependências:** 🐢 Tartaruga para sensor, calibração angular/temporal e covariância; 🦫 Castor para observável de RAAN média catalográfica físico. Sem ambos, prior histórica, erros, mecanismo de seleção e likelihood não estão justificados. **MCMC histórico, escores de holdout, probabilidades de Conde e redução do domínio geográfico: NOT_RUN / NOT_EVALUABLE.** NASA C197 fornece só dia registrado de decaimento, não a localização da queda.
