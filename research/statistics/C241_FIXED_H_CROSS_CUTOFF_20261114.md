---
type: Experiment
title: "C241: H efetivo comum entre cortes King-Hele, teste de compatibilidade"
description: "Inversão determinística do dia civil contrafactual para H, com interseção de quatro origens do 637"
experiment_id: C241-FIXED-H-FALSIFIER-20261114
verification_status: RETROSPECTIVE_UTC_DAY_CONDITIONAL_ONLY
---

# Um H fixo explica todos os cortes históricos?

**Pergunta discriminante.** Se a aproximação King-Hele local, o mesmo `H_eff` e o rótulo NASA de dia **UTC** valessem simultaneamente nos quatro cortes já congelados do NORAD 637, existiria algum `H_eff > 0` compatível com todas as quatro origens? O teste é *condicional* e retrospectivo, não uma validação instrumental do modelo físico.

**Fontes e custódia.** Reutiliza `tools/c241_king_hele_day_holdout.py` e o Parquet secundário [oxzoid/Space-Track 1963 no commit 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. Replay confirmado sobre **4.567 linhas** e deduplicação já testada do `extract_pinned`. A NASA SSR de 15/11/1963, página impressa 8, informa o **dia 07/11/1963** para 637 e **08/11/1963** para 528, sem hora certificada: a convenção de fuso e a semântica da classificação não foram verificadas. As datas já eram conhecidas antes do desenho. Fonte, data de publicação e TLEs não são medições de hora terminal independentes.

## Álgebra e contrato

Dado o último estado pré-corte `(t0,n)` e a secante pré-corte positiva `dn/dt`, a aproximação local dá `v = |da/dt| = (2a/3n) (dn/dt)` km/dia, `a = [mu/(2pi n/86400)^2]^(1/3)`. Se **apenas contrafactualmente** a data NASA denotasse a janela UTC `[T, T+1 dia)`, os valores de H que fariam o proxy `t0+H/v` cair naquele dia formam `[v*(T-t0), v*(T+1 dia-t0))`, truncados a H positivo. O limite superior é **exclusivo**. Não ajustar H por cutoff: intersectar todos os intervalos, incluindo cortes sem estimativa como `NOT_ESTIMABLE`. A faixa 40–50 km é um *stress test* pressuposto, não prior ou intervalo medido. Os parâmetros de H dos objetos diferentes **não** são forçados a ser iguais.

## Replay histórico, 14/11/2026

| Origem UTC exclusiva, 637 | H km exigido: duas últimas épocas | H km exigido: mediana de três secantes |
| --- | ---: | ---: |
| 18/10/1963 | [36,73; 38,54) | [33,74; 35,41) |
| 23/10/1963 | [29,83; 31,71) | [28,51; 30,31) |
| 27/10/1963 | [41,74; 45,37) | [25,39; 27,59) |
| 30/10/1963 | [21,68; 23,96) | [21,68; 23,96) |

**Resultado:** para 637, a interseção dos quatro intervalos é **vazia nos dois métodos**, inclusive quando se permite qualquer H positivo, não apenas 40–50 km. Esse é um **resultado negativo do modelo simplificado de velocidade local e H constante entre origens**, condicionado à leitura UTC e aos dados de uma linhagem. Não falsifica a dinâmica atmosférica física, não mede H e não calibra erro temporal. A divergência pode resultar de secantes instáveis, atmosfera variável, atitude, ruído, aproximação ou interpretação do dia.

Para 528 existe **somente um corte**: H requerido `[38,16; 41,51)` km em ambos os métodos, com interseção `[40,00; 41,51)` na faixa exploratória. A compatibilidade retrospectiva de uma origem não valida H=40, não prevê hora física, nem identifica massa, densidade, trajetória ou impacto em Conde. Os mesmos números nos dois métodos não são observações independentes.

O script `tools/c241_king_hele_fixed_h_falsifier.py` produz JSON determinístico, registrando todos os cortes, variantes, origem, último índice de fonte, intervalos não arredondados e status. `tests/test_c241_king_hele_fixed_h_falsifier.py` inclui 15 testes de vazamento temporal, limites semiabertos, cortes faltantes, duplicatas, aproximação de arrasto não-decrescente e invariantes de incerteza. O workflow `c241-fixed-h-day-window.yml` repete download, SHA, testes normais/otimizados e verificação do resultado sobre bytes históricos.

**Inferência:** `active_constraint=false`; `historical_mcmc=NOT_RUN`; `terminal_time_sigma_hours=null`; `impact_geography=null`. Nenhum posterior foi ajustado, nenhuma região excluída. Este experimento aponta uma necessidade prioritária: reentradas de 1963 com **múltiplas órbitas pré-terminais instrumentadas** e intervalo terminal independente, mais horário e semântica precisos do boletim NASA, para calibrar erros fora da amostra. Referências: [Conde #647](https://github.com/franklinbaldo/conde-incident/issues/647), [Cervo #4](https://github.com/franklinbaldo/cervo/issues/4), [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396).


## R58: deslocamento comum do início do dia civil, sem escolher fuso

**Nova pergunta de sensibilidade:** a rejeição do H efetivo constante nos quatro cortes do 637 seria apenas um artefato de supor que o dia NASA começou à meia-noite UTC? Para separar a semântica do rótulo de um relógio observado, a rotina **common_h_under_day_shift** considera um único deslocamento contrafactual \(\delta\) do início da janela civil, idêntico para os quatro cortes do **mesmo evento**. Os domínios \([-14,+14]\) e \([-24,+24]\) horas são **faixas exploratórias explícitas**, não evidência do fuso de 1963 nem de um atraso editorial conhecido.

Para cada origem \(i\), o intervalo requerido se desloca conforme \(H_i(\delta)=[\max(0,a_i+v_i\delta/24),\,b_i+v_i\delta/24)\) km, onde \(v_i>0\) é a perda local aproximada de semieixo (km/dia) estimada **somente antes do corte**. A existência de um \(H>0\) comum equivale às desigualdades estritas \(b_j-a_i+(v_j-v_i)\delta/24>0\), para todos os pares \(i,j\), e \(b_i+v_i\delta/24>0\). O auditor resolve as inequações lineares no intervalo contínuo de \(\delta\), sem fazer varredura em grade, sem otimizar parâmetros nos holdouts e preservando os limites semiabertos.

**Replay de 14/11/2026**, sobre os mesmos 4.567 registros secundários com SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09, no IFRO, HEAD df8b1e0ba0d772971093475dc115606afc238d22 (testes preliminares; CI final deve validar novo HEAD):

| Secante pré-corte | Deslocamento ±14h | Deslocamento ±24h | Par de cortes incompatível em toda a faixa ±24h | Menor separação garantida, ±24h |
| --- | --- | --- | --- | ---: |
| Duas últimas épocas | Sem H comum | Sem H comum | origem 27/10 contra 30/10 | 16,44 km |
| Mediana de três secantes | Sem H comum | Sem H comum | origem 18/10 contra 30/10 | 9,17 km |

Os valores positivos da última coluna medem a distância **entre intervalos de H no proxy**, não distância de órbitas ou margens físicas observadas. A saída JSON inclui índices do par e máximo da folga \(upper_j-lower_i\) sobre a faixa, sempre negativa nos dois casos. Um contraexemplo sintético mostra que um deslocamento pode, em outros dados, recuperar compatibilidade; não é impossível por construção.

**Interpretação estreita:** para um deslocamento civil comum de até um dia em qualquer direção, a incompatibilidade do H constante no *modelo local específico* persiste. Isso reduz a plausibilidade de atribuir toda a divergência apenas à escolha de meia-noite UTC sob tais hipóteses. Não resolve se o rótulo NASA se refere à data de observação, de catalogação ou de outro evento; deslocamentos diferentes por origem, mudanças no modelo de arrasto e erros de catálogo não são testados aqui. Não se identifica H verdadeiro, sigma horário, massa, probabilidade ou geografia. **active_constraint=false**, **historical_mcmc=NOT_RUN**, **impact_geography=null**.

A suíte adversarial cobre fronteiras estritas, H positivo, velocidades iguais, deslocamento que resgata um caso sintético, origem faltante e limites inválidos. O workflow .github/workflows/c241-fixed-h-day-window.yml exige esses testes em Python normal/otimizado e repete o Parquet com SHA pinado antes de afirmar os resultados no HEAD real. Ver [Conde #647](https://github.com/franklinbaldo/conde-incident/issues/647) e [Cervo #4](https://github.com/franklinbaldo/cervo/issues/4).
