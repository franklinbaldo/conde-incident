---
type: Experiment
title: "C241: pesos de confiança e correlação nas trajetórias simuladas"
description: "Motor Python para penalizar desvios conforme erro assumido ou calibrado, aplicado à sensibilidade de 1,5 milhão de amostras ao redor de Conde, sem posterior histórica."
experiment_id: C241-MC-CONFIDENCE-WEIGHTS-20261113
verification_status: SYNTHETIC_SCENARIO_SENSITIVITY_NOT_HISTORICAL_POSTERIOR
---

# Pesos proporcionais à incerteza, não ao prestígio da fonte

**Problema:** não tratar igualmente um desvio de 1° numa observação com incerteza pequena e outro desvio de 1° numa observação pouco precisa. Para cada grandeza precisa existir ocorrência, observação, previsão do modelo, unidade, época, linhagem, desvio-padrão ou distribuição calibrada e justificativa da incerteza.

O motor Python [c241_confidence_weighted_heatmap.py](../../tools/c241_confidence_weighted_heatmap.py) implementa a penalização gaussiana multivariada:

\[
Q=\mathbf{r}^{T}\Sigma^{-1}\mathbf{r}, \qquad
w_{\mathrm{rel}}=\exp(-Q/2).
\]

A covariância compartilhada é obrigatória para múltiplos resíduos numa mesma linhagem. A matriz de correlação deve ser simétrica e definida positiva. Resíduos de RAAN são circulares. A função recusa σ ausente, zero, negativo, NaN e ocorrências repetidas. **Confiabilidade documental não é automaticamente um valor de σ**. Mesmo documentação original pode conter parâmetros derivados com covariância desconhecida.

## Experimento de sensibilidade, NÃO inferência histórica

A [grade anterior de 1.500.000 amostras sintéticas](c241_528_unweighted_2000km_scenarios.json) foi obtida de um modelo secular J2 e TLE secundário do NORAD 528 (27/10/1963), com doze combinações de aceleração orbital fictícia e fase inicial, amostradas na janela hipotética 7–8/11. O JSON reproduz os contadores agrupados de um relatório gerado anteriormente, cujo arquivo original, não armazenado aqui, tinha SHA-256 declarado **c6c32f55fbc2afd3c60c6f109ce8f5d4c979eb195600b0fc51ead400a0f8824d** e script de cálculo **d1049526868525a131e132fe9b0f0603da310d2331ed08a8700df019ebb22cd9**. Esses hashes identificam os arquivos de origem da sessão, mas o CI atual só verifica o **resumo versionado**, não repete o sorteio integral de 1,5 milhão de amostras. O TLE secundário tinha SHA-256 **18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd**.

O resultado medido é apenas o **percentual de pontos subsatélite no instante terminal hipotético** dentro de um raio geodésico de 2.000 km de Conde, Bahia. Não inclui ablação, sobrevivência dos detritos, deslocamento atmosférico ou impacto real.

| Peso de cenário | σ de fase (hipótese) | σ de n-dot (hipótese, rev/dia²) | Correlação assumida | Dentro de 2.000 km |
|---|---:|---:|---:|---:|
| Mistura igual anterior | Sem penalidade | Sem penalidade | Não aplicada | 1,6993% |
| Tolerância estreita | 25° | 0,006 | 0 | 1,8673% |
| Tolerância intermediária | 90° | 0,020 | 0 | 1,7652% |
| Tolerância larga | 180° | 0,050 | 0 | 1,7199% |
| Intermediária correlacionada | 90° | 0,020 | −0,5 | 1,7643% |
| Intermediária correlacionada | 90° | 0,020 | +0,5 | 1,7843% |

**Os valores de σ são escolhas para testar sensibilidade**, não estimativas instrumentais. Não se pode escolher a linha mais favorável a Conde como se fosse um resultado histórico. A comparação mostra que a ponderação é matematicamente relevante, mas o pequeno aumento neste experimento NÃO demonstra aumento real da probabilidade de queda.

## Fonte histórica e próxima pesquisa

O registro NASA de 8/11/1963 é fonte do **dia catalogado de decaimento**, não de um erro em horas observado. O TLE secundário não informa σ do sensor/solução orbital. Além disso, NASA e NORAD podem partilhar dados SPADATS e não serem duas medições independentes.

A [issue #647](https://github.com/franklinbaldo/conde-incident/issues/647) mantém aberta a pesquisa que buscará erros históricos reais por variável: inclinação, RAAN, n-dot, apogeu/perigeu, erro de propagação, época de medição, viés de fonte e janela terminal. Será preciso obter pares de medições/soluções órbita comparáveis em época e frame, incluir seleção e dependência, e verificar previsões fora da amostra. Somente depois substituir estes σ sintéticos por likelihood empiricamente sustentada e refazer o mapa de calor de 200 km.

## Migração científica Python

Esta fatia é um primeiro núcleo Python para análise probabilística, que permite integração futura com NumPy/SciPy, PyMC e ArviZ conforme a necessidade. O site editorial continua **SSG Rust/OKF**, podendo renderizar JSON e tabelas geradas por Python. Não é necessária uma reescrita completa do site ou um backend TypeScript para executar os cálculos científicos; remover componentes legados só após a substituição ter testes de paridade e proveniência.

## Reprodução e negativos

    python3 -m unittest discover -s tests -p test_c241_confidence_weighted_heatmap.py -v
    python3 tools/c241_confidence_weighted_heatmap.py --output /tmp/c241-confidence-sensitivity.json

Testes numéricos cobrem magnitude e sinal do resíduo, RAAN circular, anticorrelação/correlação, matriz singular, origem e duplicatas de registros. **Não há probabilidade histórica calibrada** de queda em Conde, nem nova medição de massa, área, Cd, densidade ou ablação.
