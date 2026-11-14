---
type: Experiment
title: 'C241 G71: robustez de H fixo sob deslocamentos independentes do dia NASA'
description: 'Teste adversarial de permissividade temporal do falsificador condicional G57, sem calibracao historica'
experiment_id: C241-G71-INDEPENDENT-DAY-SHIFT
verification_status: CONDITIONAL_STRESS_ONLY
---

# G71 | Quanto deslocamento do dia salvaria um H fixo?

O experimento [G57 / PR #881](https://github.com/franklinbaldo/conde-incident/pull/881) demonstrou interseção vazia de quatro intervalos de `H_eff` para NORAD **637**, usando a aproximação local King–Hele, TLEs secundários e leitura **contrafactual** da data NASA como um dia UTC. Essa premissa não é uma medida do relógio de 1963.

**Contraprova mais permissiva:** permitir que **cada um dos quatro cortes**, artificialmente, receba deslocamento *independente* de até 24 horas da janela de dia. Isso é matematicamente mais permissivo que corrigir um único fuso compartilhado. Se ainda não existir um mesmo `H`, nem o caso de fuso comum pode restaurar a compatibilidade nessa faixa de deslocamentos.

## Certificado sem malha numérica

Para cada corte com intervalo de H `[L_i,U_i)`, o comprimento `v_i = U_i-L_i` representa km/dia, pois a janela original dura um dia. Permitir desvio `delta_i` em `[-b,b]` dias equivale à união `[L_i-v_i*b, U_i+v_i*b)`. Quando o máximo dos limites inferiores é maior ou igual ao mínimo dos superiores, a interseção é vazia **para qualquer combinação** de deslocamentos admissíveis, sem discretização.

O ínfimo de `b` que poderia permitir um H comum é `max(0, max_{i!=j}(L_i-U_j)/(v_i+v_j))`. Com extremos abertos, tocar um limite não é suficiente. Este número é a robustez **interna ao proxy**, não uma estimativa de fuso, densidade, altitude terminal ou erro instrumental.

## Resultado a conferir por replay de bytes

Calculado inicialmente a partir da tabela arredondada de G57, o teste indica ínfimos aproximados de **3,12 dias** (duas últimas épocas) e **2,48 dias** (mediana de três secantes) para o 637. Os valores definitivos devem vir do **Parquet original SHA-256** `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` e do script em CI.

Com deslocamento independente de ±1 dia, as faixas continuam disjuntas em ambos os métodos. O NORAD **528 só tem um corte** nesta experiência e permanece `NOT_ESTIMABLE_SINGLE_CUTOFF`. Não usar H comum entre objetos diferentes.

**Limites:** os cortes foram escolhidos conhecendo a classificação NASA; os TLEs derivam de uma única linhagem secundária; o dia de decaimento não foi confirmado como UTC; o próprio operador de decaimento local é simplificado. `active_constraint=false`, `historical_mcmc=NOT_RUN`, `impact_geography=null`. Não afirmar que a física atmosférica foi falsificada nem inferir horário ou local de impacto.

Reprodução: `tools/c241_fixed_h_day_shift_G71.py`, dez controles sintéticos normais e em Python otimizado, workflow `castor-g71-day-shift-falsifier.yml` com checkout SHA exato, download do Parquet imutável, conferência SHA e replay. Este teste responde a uma pergunta de **robustez condicional**, não substitui a aquisição instrumental de [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396).
