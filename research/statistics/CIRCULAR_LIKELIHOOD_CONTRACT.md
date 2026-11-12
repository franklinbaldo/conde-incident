---
type: Guide
title: "Cervo: likelihood circular com viés de linhagem integrado"
description: "Modelo probabilístico matemático condicional com referências, testes e portas de bloqueio à posterior histórica"
---

# Likelihood circular com offset compartilhado: contrato condicional

**Estado: METHOD_IMPLEMENTED_NOT_HISTORICALLY_CALIBRATED.** Este documento descreve um componente matemático pronto para receber previsões físicas e erros calibrados. Não representa uma estimativa das órbitas em 1963, nem prova qualquer reentrada em Conde. Registros vinculados: **C25#1, C179#1, C180#1, C181#1, C241-L3 e C197**. O dataset secundário em raan_527_528_529_1963.json contém 123 linhas, 119 épocas únicas e uma linhagem documental. O parquet original não foi novamente obtido nesta rodada, nem sensor, referencial ou matriz de covariância independentes foram recuperados.

## Modelo e derivação verificável

Dadas previsões transportadas pelo Castor, no **mesmo referencial e época** de cada elemento RAAN observado, defina resíduo circular r_i = wrap(y_i - H_i(theta)). Para cada grupo de origem documental g, introduza um único viés latente b_g em [0,2*pi). A título de **hipótese verificável, mas ainda não sustentada por custódia histórica**, condicione os resíduos em b_g e parâmetros de concentração kappa_i:

p(r_i | b_g, kappa_i) = exp(kappa_i cos(r_i-b_g)) / [2*pi*I0(kappa_i)].

Use a medida uniforme de Haar p(b_g)=1/(2*pi), que é uma **escolha matemática explícita de prior de deslocamento**, não uma prior histórica justificada para a mecânica orbital. Condicionalmente a b_g, assuma os erros independentes **apenas sob esta família de teste**. Integrando analiticamente b_g, o log da densidade conjunta em radianos é:

log p(y | H, kappa, groups) =
  sum_g [ log I0( |sum_i kappa_i exp(i*r_i)| )
          - sum_i log I0(kappa_i) - n_g*log(2*pi) ].

Referências matemáticas para normalizador e assintótica: NIST DLMF 10.32 (representações integrais) https://dlmf.nist.gov/10.32 e 10.40 (assintótica) https://dlmf.nist.gov/10.40. Ao marginalizar, os resíduos dentro de um grupo **não** são considerados observações independentes de um viés livre, apesar de a família ter erros condicionais independentes. A fórmula é invariante a uma rotação comum e depende somente de contrastes internos ao grupo. Com **um único dado num grupo de offset livre**, a densidade marginal fica exatamente 1/(2*pi), independentemente de H e kappa: esse dado isolado não informa a fase global.

A interface exige **prediction_ref e calibration_ref não vazios** por observação, além do identificador do grupo documental, NORAD e época. Esses IDs são declarações do integrador, não autenticação automática; testes usam refs explicitamente sintéticas. Concentrações kappa_i devem vir de **calibração externa** com referência e unidades explícitas; não converter sigma desconhecido em kappa por conveniência. O parâmetro theta não tem prior aqui: não é gerada posterior. O número de grupos e a hipótese de viés constante são escolhas de modelo a testar por linhagem, jamais uma informação implícita do espelho. Mudança de viés por época, múltiplos sensores, dependências de estimação orbital e modelos de seleção não estão cobertos por esta versão.

## Predição de holdout sem refit

Para H e kappa fixos por ajuste/calibração anterior e holdout cronológico previamente congelado, a densidade preditiva é p(Y_eval|Y_fit,H,kappa) = p(Y_fit,Y_eval|H,kappa) / p(Y_fit|H,kappa), mantendo o **mesmo b_g latente** compartilhado. O código calcula a diferença dos log-marginais, sem ajustar H, kappa ou escolha de linhagem usando o holdout. Isso é **somente uma identidade condicional**, não evidência de previsão competente: a divisão 61/23/35 é retrospectiva não cega e apenas uma época de 527 consta na validação. O intervalo entre último TLE de 528 (27/10) e dia catalogado NASA (08/11) permanece sem observação terminal.

## Portões que impedem a falsa posterior

1. Antes de fornecer qualquer valor H_i(theta): Castor precisa declarar dinâmica validada, frame, elementos médios versus osculadores, épocas, erro de propagação e holdout. Um ângulo RAAN **não** é distância entre corpos, localização no solo ou evento de entrada.
2. Antes de fornecer qualquer kappa_i: Tartaruga precisa declarar origem instrumental, cadeia de processamento e justificativa quantitativa dos erros/correlações. Multiplicar os 119 elementos como independentes seria incorreto.
3. Antes de MCMC: Cervo precisa especificar parâmetros físicos, limites identificáveis, priors justificadas, modelo de observação e seleção; aplicar ensaios de simulação calibrada, vários inícios, convergência rank-R-hat e ESS bulk/tail e validação fora do ajuste. Rejeitar simetria de gauge não ancorada quando estimar fase absoluta.
4. O código falha quando faltam kappa/previsão, grupos ou épocas, quando aparecem NaN/infinitos ou registros repetidos NORAD+época. Sem esses dados, status **NO_HISTORICAL_LIKELIHOOD, NO_MCMC, NO_IMPACT_POSTERIOR**.

## Reprodução

Executar: python3 -m unittest discover -s tests -p test_raan_circular_likelihood.py -v. O teste verifica normalizador Bessel e a integral sobre viés por quadraturas independentes, limites, invariância circular, grupo com um dado, falsas independências, duplicatas, holdout condicional e falha explícita com os **123 registros secundários reais**, que não incluem H ou concentrações. Código: tools/raan_circular_likelihood.py. Todos os valores de kappa em testes são **controles sintéticos**, não medidas ou probabilidades históricas.
